/*
 * AquaGuard — Estação IoT de monitoramento de alagamento (ESP32)
 * FIAP Global Solution 2026.2 · CitizenTech · Physical Computing: IoT & IoB
 * Integrantes: Guilherme Cezarino Simoes (RM 557724) · Fabrini Soares (RM 557813) · João Both (RM 558690)
 *
 * O que faz
 *  - HC-SR04 instalado ACIMA do córrego/galeria mede a distância até a superfície da água.
 *    nível da água (cm) = ALTURA_INSTALACAO_CM - distância medida.
 *  - Potenciômetro simula o pluviômetro (0–100 mm/h).
 *  - Calcula o risco LOCALMENTE (funciona mesmo sem internet — edge computing):
 *      Normal  < 60% do nível de alerta e chuva < 10 mm/h
 *      Atenção ≥ 60% do nível de alerta ou chuva ≥ 10 mm/h
 *      Alerta  ≥ nível de alerta ou chuva ≥ 25 mm/h (ou água subindo + chuva forte)
 *      Crítico ≥ nível crítico ou chuva ≥ 50 mm/h (ou água acima do alerta + chuva forte)
 *    (mesmas regras do backend C# — classe CalculadoraRisco)
 *  - LEDs verde/amarelo/vermelho + LCD 16x2 informam quem está na rua; buzzer toca em Alerta/Crítico.
 *  - Botão: silencia o buzzer por 5 minutos (morador/agente já ciente).
 *  - Envia JSON para a API AquaGuard (POST /api/leituras) a cada 10 s; a API grava no banco,
 *    gera o alerta do bairro e o app mobile mostra ao cidadão.
 */
#include <WiFi.h>
#include <HTTPClient.h>
#include <WiFiClientSecure.h>
#include <Wire.h>
#include <LiquidCrystal_I2C.h>

// ---------------- Configuração ----------------
const char* WIFI_SSID = "Wokwi-GUEST";
const char* WIFI_PASS = "";
// URL pública da API (ex.: túnel https://xxxx.ngrok-free.app/api/leituras). Vazio = modo offline (só serial).
const char* API_URL = "";
const char* DEVICE_KEY = "";          // mesmo valor de AquaGuard:DeviceKey na API (opcional)
const char* CODIGO_SENSOR = "AQG-001"; // Córrego Três Pontes · Jardim Pantanal

const float ALTURA_INSTALACAO_CM = 200.0; // sensor a 2 m do fundo do córrego
const float NIVEL_ALERTA_CM = 80.0;
const float NIVEL_CRITICO_CM = 120.0;
const unsigned long INTERVALO_ENVIO_MS = 10000;
const unsigned long SILENCIO_MS = 5UL * 60UL * 1000UL;

// ---------------- Pinos ----------------
const int PIN_TRIG = 5, PIN_ECHO = 18, PIN_CHUVA = 34;
const int PIN_LED_VERDE = 25, PIN_LED_AMARELO = 26, PIN_LED_VERMELHO = 27;
const int PIN_BUZZER = 14, PIN_BOTAO = 4;

LiquidCrystal_I2C lcd(0x27, 16, 2);

enum Risco { NORMAL = 0, ATENCAO = 1, ALERTA = 2, CRITICO = 3 };
const char* NOME_RISCO[] = {"Normal", "Atencao", "Alerta", "Critico"};

unsigned long ultimoEnvio = 0, silenciadoAte = 0;
int falhasEnvio = 0;

// ---------------- Sensores ----------------
float medirDistanciaCm() {
  digitalWrite(PIN_TRIG, LOW);  delayMicroseconds(2);
  digitalWrite(PIN_TRIG, HIGH); delayMicroseconds(10);
  digitalWrite(PIN_TRIG, LOW);
  unsigned long dur = pulseIn(PIN_ECHO, HIGH, 30000UL); // timeout ~5 m
  if (dur == 0) return -1;                               // falha de leitura
  return dur * 0.0343f / 2.0f;
}

// Mediana de 5 amostras: filtra ruído/reflexos (folhas, gotas).
float medirNivelAguaCm() {
  float v[5]; int n = 0;
  for (int i = 0; i < 5; i++) { float d = medirDistanciaCm(); if (d > 0) v[n++] = d; delay(30); }
  if (n == 0) return -1;
  for (int i = 0; i < n; i++) for (int j = i + 1; j < n; j++) if (v[j] < v[i]) { float t = v[i]; v[i] = v[j]; v[j] = t; }
  float nivel = ALTURA_INSTALACAO_CM - v[n / 2];
  return constrain(nivel, 0, ALTURA_INSTALACAO_CM);
}

float medirChuvaMmH() { return analogRead(PIN_CHUVA) * 100.0f / 4095.0f; }

// ---------------- Regras (iguais ao backend) ----------------
Risco porLimites(float valor, float atencao, float alerta, float critico) {
  if (valor >= critico) return CRITICO;
  if (valor >= alerta) return ALERTA;
  if (valor >= atencao) return ATENCAO;
  return NORMAL;
}

Risco calcularRisco(float nivel, float chuva) {
  Risco r1 = porLimites(nivel, NIVEL_ALERTA_CM * 0.6f, NIVEL_ALERTA_CM, NIVEL_CRITICO_CM);
  Risco r2 = porLimites(chuva, 10, 25, 50);
  Risco r3 = NORMAL;
  if (nivel >= NIVEL_ALERTA_CM * 0.6f && chuva >= 25) r3 = nivel >= NIVEL_ALERTA_CM ? CRITICO : ALERTA;
  return (Risco)max((int)r1, max((int)r2, (int)r3));
}

// ---------------- Atuadores ----------------
void sinalizar(Risco r) {
  digitalWrite(PIN_LED_VERDE, r == NORMAL);
  digitalWrite(PIN_LED_AMARELO, r == ATENCAO || r == ALERTA);
  digitalWrite(PIN_LED_VERMELHO, r >= ALERTA);
  bool silenciado = millis() < silenciadoAte;
  if (r == CRITICO && !silenciado) tone(PIN_BUZZER, 2000, 400);
  else if (r == ALERTA && !silenciado) tone(PIN_BUZZER, 1000, 150);
  else noTone(PIN_BUZZER);
}

void mostrarLcd(float nivel, float chuva, Risco r) {
  lcd.setCursor(0, 0);
  lcd.printf("Agua:%5.1fcm %s", nivel, WiFi.status() == WL_CONNECTED ? "W" : "-");
  lcd.setCursor(0, 1);
  lcd.printf("%-7s %4.0fmm/h", NOME_RISCO[r], chuva);
}

// ---------------- Rede ----------------
void conectarWifi() {
  WiFi.begin(WIFI_SSID, WIFI_PASS, 6);
  Serial.print("[wifi] conectando");
  for (int i = 0; i < 40 && WiFi.status() != WL_CONNECTED; i++) { delay(250); Serial.print("."); }
  Serial.println(WiFi.status() == WL_CONNECTED ? " ok " + WiFi.localIP().toString() : " falhou (modo offline)");
}

void enviarLeitura(float nivel, float chuva, Risco local) {
  char json[160];
  snprintf(json, sizeof(json), "{\"codigoSensor\":\"%s\",\"nivelAguaCm\":%.1f,\"chuvaMmH\":%.1f}", CODIGO_SENSOR, nivel, chuva);
  Serial.printf("[leitura] %s risco_local=%s\n", json, NOME_RISCO[local]);

  if (strlen(API_URL) == 0) return;               // modo offline
  if (WiFi.status() != WL_CONNECTED) { conectarWifi(); if (WiFi.status() != WL_CONNECTED) return; }

  HTTPClient http;
  WiFiClientSecure seguro;
  WiFiClient simples;
  bool https = strncmp(API_URL, "https", 5) == 0;
  // Protótipo: em produção, fixar o certificado raiz (setCACert) em vez de setInsecure().
  if (https) { seguro.setInsecure(); http.begin(seguro, API_URL); } else { http.begin(simples, API_URL); }
  http.addHeader("Content-Type", "application/json");
  if (strlen(DEVICE_KEY) > 0) http.addHeader("X-Device-Key", DEVICE_KEY);
  http.setTimeout(5000);
  int status = http.POST(json);
  if (status == 201) {
    falhasEnvio = 0;
    String corpo = http.getString();
    int i = corpo.indexOf("\"risco\":\"");
    Serial.printf("[api] 201 risco_api=%s\n", i >= 0 ? corpo.substring(i + 9, corpo.indexOf('"', i + 9)).c_str() : "?");
  } else {
    falhasEnvio++;
    Serial.printf("[api] falha status=%d (tentativas seguidas=%d) — mantendo alerta local\n", status, falhasEnvio);
  }
  http.end();
}

void setup() {
  Serial.begin(115200);
  pinMode(PIN_TRIG, OUTPUT); pinMode(PIN_ECHO, INPUT);
  pinMode(PIN_LED_VERDE, OUTPUT); pinMode(PIN_LED_AMARELO, OUTPUT); pinMode(PIN_LED_VERMELHO, OUTPUT);
  pinMode(PIN_BUZZER, OUTPUT); pinMode(PIN_BOTAO, INPUT_PULLUP);
  lcd.init(); lcd.backlight();
  lcd.print("AquaGuard"); lcd.setCursor(0, 1); lcd.print(CODIGO_SENSOR);
  conectarWifi();
  lcd.clear();
}

void loop() {
  if (digitalRead(PIN_BOTAO) == LOW) {
    silenciadoAte = millis() + SILENCIO_MS;
    noTone(PIN_BUZZER);
    Serial.println("[botao] buzzer silenciado por 5 min");
    delay(300);
  }

  float nivel = medirNivelAguaCm();
  float chuva = medirChuvaMmH();
  if (nivel < 0) {  // sensor com defeito: avisa e não envia dado inválido
    lcd.setCursor(0, 0); lcd.print("Falha sensor US ");
    Serial.println("[erro] HC-SR04 sem eco");
    delay(1000);
    return;
  }

  Risco r = calcularRisco(nivel, chuva);
  sinalizar(r);
  mostrarLcd(nivel, chuva, r);

  if (millis() - ultimoEnvio >= INTERVALO_ENVIO_MS || ultimoEnvio == 0) {
    ultimoEnvio = millis();
    enviarLeitura(nivel, chuva, r);
  }
  delay(500);
}
