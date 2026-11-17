#!/usr/bin/env bash
# =============================================================================
# 02 · Provisionamento da APLICAÇÃO AquaGuard (API C# + painel web)
# dependências (.NET 8) → código → build/publish → variáveis → systemd → nginx → health check
# =============================================================================
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${DIR}/lib/comum.sh"
exigir_root
carregar_config "${1:-/etc/aquaguard/aquaguard.env}"

: "${AQG_USUARIO:=aquaguard}" "${AQG_DIR_APP:=/opt/aquaguard}" "${AQG_DIR_DADOS:=/var/lib/aquaguard}"
: "${AQG_PORTA_API:=5080}" "${AQG_DOMINIO:=aquaguard.local}" "${AQG_REPO_URL:=}" "${AQG_REPO_BRANCH:=main}"
: "${ASPNETCORE_ENVIRONMENT:=Production}" "${AQG_DEVICE_KEY:=}"
RAIZ_PROJETO="$(cd "${DIR}/../.." && pwd)"     # raiz do repositório (quando executado a partir do clone)
FONTE="${AQG_DIR_APP}/src"

instalar_dotnet() {
  if command -v dotnet >/dev/null && dotnet --list-sdks | grep -q '^8\.'; then
    log INFO ".NET 8 já instalado: $(dotnet --version)"; return
  fi
  export DEBIAN_FRONTEND=noninteractive
  apt-get update -qq
  # Ubuntu 22.04+ traz o SDK no repositório oficial; fallback para o script da Microsoft
  if ! apt-get install -y -qq dotnet-sdk-8.0 >/dev/null 2>&1; then
    curl -fsSL https://dot.net/v1/dotnet-install.sh -o /tmp/dotnet-install.sh
    bash /tmp/dotnet-install.sh --channel 8.0 --install-dir /usr/share/dotnet
    ln -sf /usr/share/dotnet/dotnet /usr/bin/dotnet
  fi
  log OK ".NET instalado: $(dotnet --version)"
}

obter_codigo() {
  rm -rf "${FONTE}"
  if [[ -n "${AQG_REPO_URL}" ]]; then
    git clone --depth 1 --branch "${AQG_REPO_BRANCH}" "${AQG_REPO_URL}" "${FONTE}"
  else
    mkdir -p "${FONTE}" && cp -r "${RAIZ_PROJETO}/backend" "${FONTE}/"
  fi
  log INFO "Código em ${FONTE} ($(find "${FONTE}/backend" -name '*.cs' | wc -l) arquivos C#)"
}

compilar_e_testar() {
  export DOTNET_CLI_TELEMETRY_OPTOUT=1 DOTNET_NOLOGO=1 HOME=/root
  pushd "${FONTE}/backend" >/dev/null
  dotnet restore --verbosity quiet
  dotnet test --verbosity quiet --nologo 2>&1 | tail -3 | while read -r l; do log INFO "testes: ${l}"; done
  dotnet publish src/AquaGuard.Api -c Release -o "${AQG_DIR_APP}/api" --nologo --verbosity quiet
  popd >/dev/null
  chown -R "${AQG_USUARIO}:${AQG_USUARIO}" "${AQG_DIR_APP}" "${AQG_DIR_DADOS}"
}

configurar_variaveis() {
  local chave="${AQG_DEVICE_KEY:-$(openssl rand -hex 24)}"
  # Arquivo lido pelo systemd (EnvironmentFile); permissão 640 — contém segredo
  cat > /etc/aquaguard/api.env <<EOF
ASPNETCORE_ENVIRONMENT=${ASPNETCORE_ENVIRONMENT}
ASPNETCORE_URLS=http://127.0.0.1:${AQG_PORTA_API}
ConnectionStrings__AquaGuard=Data Source=${AQG_DIR_DADOS}/aquaguard.db
AquaGuard__DeviceKey=${chave}
AquaGuard__Seed=true
DOTNET_CLI_TELEMETRY_OPTOUT=1
EOF
  chown root:"${AQG_USUARIO}" /etc/aquaguard/api.env
  chmod 640 /etc/aquaguard/api.env
  log INFO "Variáveis de ambiente gravadas em /etc/aquaguard/api.env (DeviceKey: ${chave:0:4}****)"
}

instalar_servico() {
  install -m 644 "${DIR}/../systemd/aquaguard-api.service" /etc/systemd/system/aquaguard-api.service
  systemctl daemon-reload
  systemctl enable aquaguard-api.service >/dev/null
  systemctl restart aquaguard-api.service
}

configurar_nginx() {
  cat > /etc/nginx/sites-available/aquaguard <<EOF
server {
    listen 80 default_server;
    server_name api.${AQG_DOMINIO} painel.${AQG_DOMINIO} _;
    access_log /var/log/nginx/aquaguard_access.log;
    error_log  /var/log/nginx/aquaguard_error.log;
    add_header X-Content-Type-Options nosniff;
    add_header X-Frame-Options DENY;
    client_max_body_size 1m;
    location / {
        proxy_pass http://127.0.0.1:${AQG_PORTA_API};
        proxy_set_header Host \$host;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_read_timeout 30s;
    }
}
EOF
  ln -sf /etc/nginx/sites-available/aquaguard /etc/nginx/sites-enabled/aquaguard
  rm -f /etc/nginx/sites-enabled/default
  nginx -t 2>&1 | while read -r l; do log INFO "nginx: ${l}"; done
  systemctl enable --now nginx >/dev/null && systemctl reload nginx
}

verificar_saude() {
  for i in $(seq 1 30); do
    if curl -fsS "http://127.0.0.1:${AQG_PORTA_API}/health" | grep -q Healthy; then
      log OK "API saudável após ${i}s (Kestrel) · proxy: $(curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1/health)"
      log OK "Painel: http://$(hostname -I | awk '{print $1}')/  ·  Swagger: http://$(hostname -I | awk '{print $1}')/swagger"
      return 0
    fi
    sleep 1
  done
  log ERRO "API não respondeu em 30s"; journalctl -u aquaguard-api -n 30 --no-pager
  return 1
}

passo "Instalando dependências (.NET 8 SDK)"         instalar_dotnet
passo "Obtendo código-fonte"                          obter_codigo
passo "Restaurando, testando e publicando a API"      compilar_e_testar
passo "Configurando variáveis de ambiente"            configurar_variaveis
passo "Instalando serviço systemd aquaguard-api"      instalar_servico
passo "Configurando proxy reverso nginx"              configurar_nginx
passo "Verificando saúde da aplicação"                verificar_saude
log OK "Aplicação AquaGuard provisionada."
