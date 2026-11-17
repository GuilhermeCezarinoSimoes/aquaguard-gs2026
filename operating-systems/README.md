# AquaGuard · Operating Systems — Infraestrutura Linux

**Integrantes:** Guilherme Cezarino Simoes · Fabrini Soares

Infraestrutura Linux **provisionada automaticamente por Shell Script** para hospedar a aplicação WEB da CitizenTech
AquaGuard: a **API C# (.NET 8) com painel web e Swagger** (`../backend`), atrás de um proxy **nginx**, com
**monitoramento como serviço tolerante a falhas**, **alertas de CPU/memória/disco**, **logs de auditoria** e **teste de falha**.

```
            Internet / celular / ESP32
                     │ :80
              ┌──────▼──────┐   ufw: só 22 e 80
              │    nginx     │   proxy reverso + headers de segurança
              └──────┬──────┘
                     │ 127.0.0.1:5080
   systemd ──► aquaguard-api.service  (Restart=always, hardening, usuário sem shell)
                     │ SQLite /var/lib/aquaguard/aquaguard.db
   systemd ──► aquaguard-monitor.service (Type=notify, WatchdogSec, Restart=always)
                     └─► /var/log/aquaguard/{metricas.jsonl, alertas.log, *.log, auditoria_execucao.log}
   auditd   ──► regras -k aquaguard_* (config, serviços, binários, scripts)
```

## Estrutura
| Arquivo | Função | Critério do edital |
|---|---|---|
| `scripts/00_provisionar_tudo.sh` | Orquestrador: executa tudo em ordem numa VM limpa | Funcionamento completo (2 pts) |
| `scripts/01_provisionar_infra.sh` | Pacotes, **hostname**, `/etc/hosts`, **DNS** (systemd-resolved), **IP** (DHCP ou estático via netplan), fuso, usuário de serviço, **firewall UFW**, **auditd**, logrotate, journald persistente | Provisionamento de infra (redes, DNS, IP) — 2 pts |
| `scripts/02_provisionar_app.sh` | **.NET 8 SDK**, código, `dotnet test`, `dotnet publish`, **variáveis de ambiente** (`/etc/aquaguard/api.env`, chave IoT gerada), **systemd**, **nginx**, health check | Provisionamento da aplicação (dependências, configurações, orquestração) — 2 pts |
| `scripts/03_monitor.sh` | Coleta CPU (/proc/stat), memória (MemAvailable), disco (df), health HTTP, serviços; grava métricas JSONL; **alertas** na transição OK→ALERTA→OK | Monitoramento com alertas de CPU, Disco e Memória — 2 pts |
| `systemd/aquaguard-monitor.service` | Monitor como serviço: `Restart=always`, `WatchdogSec=120` (reinicia se travar), `StartLimitBurst` | Monitoramento como serviço tolerante a falhas — 1 pt |
| `systemd/aquaguard-api.service` | API com `Restart=always`, `ProtectSystem=strict`, `NoNewPrivileges`, `MemoryMax` | Tolerância a falhas da aplicação |
| `scripts/lib/comum.sh` | Log padronizado (arquivo + journald), **trilha de auditoria** de toda execução (quem, quando, args, resultado, duração), trap de erro | Logs de auditoria e execução — 1 pt |
| `scripts/05_relatorio_auditoria.sh` | Consolida execuções, alertas, métricas, journal, **auditd**, acessos nginx, firewall | Logs de auditoria |
| `scripts/04_teste_falha.sh` | 5 cenários: SIGKILL na API, SIGKILL no monitor, pico de CPU, disco cheio, nginx parado — com APROVADO/REPROVADO | Teste de falha |
| `config/aquaguard.env.example` | Todas as variáveis (rede, app, limites) | — |

## Como executar (VM)
Pré-requisito: VM **Ubuntu Server 22.04 ou 24.04** (VirtualBox/VMware/Hyper-V), 2 vCPU, 2 GB RAM, 15 GB de disco,
rede NAT com redirecionamento da porta 80 (ou modo bridge) e acesso à internet.

```bash
sudo apt-get update && sudo apt-get install -y git
git clone <URL-DO-REPOSITORIO> aquaguard && cd aquaguard
sudo bash operating-systems/scripts/00_provisionar_tudo.sh          # provisiona tudo (≈ 5–8 min)
sudo bash operating-systems/scripts/04_teste_falha.sh               # testes de falha
sudo bash operating-systems/scripts/05_relatorio_auditoria.sh       # relatório consolidado
```
Para IP estático/DNS próprios: edite `/etc/aquaguard/aquaguard.env` (`AQG_IP_ESTATICO=192.168.56.10/24`, `AQG_GATEWAY=...`)
e rode novamente — os scripts são **idempotentes**.

### Comandos úteis na demonstração
```bash
systemctl status aquaguard-api aquaguard-monitor nginx
journalctl -u aquaguard-api -f                 # logs da API
tail -f /var/log/aquaguard/alertas.log         # alertas
tail -n 5 /var/log/aquaguard/metricas.jsonl    # métricas
cat /var/log/aquaguard/auditoria_execucao.log  # quem executou cada script
sudo ausearch -k aquaguard_config -i           # auditd
curl http://localhost/health ; curl http://localhost/api/painel | jq
```

## Status de validação
- ✅ Sintaxe de todos os scripts validada (`bash -n`).
- ✅ A aplicação hospedada (API + painel) foi executada e testada (47 testes automatizados; ver `../backend`).
- ⏳ **Execução completa na VM Linux: pendente** — o computador de desenvolvimento é Windows sem WSL/Docker.
  A equipe deve rodar os comandos acima na VM, salvar as saídas em `../evidencias/operating-systems/`
  e gravar o vídeo (roteiro: `../docs/roteiros/roteiro_video_os.md`).
