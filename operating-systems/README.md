# AquaGuard · Operating Systems — Infraestrutura Linux

**Integrantes:** Guilherme Cezarino Simoes (RM 557724) · Fabrini Soares (RM 557813) · João Both (RM 558690)

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
   systemd ──► aquaguard-monitor.service (Restart=always, RestartSec=5)
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
| `systemd/aquaguard-monitor.service` | Monitor como serviço: `Restart=always` (reinicia em 5 s se morrer ou for morto), `StartLimitBurst` | Monitoramento como serviço tolerante a falhas — 1 pt |
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
git clone https://github.com/GuilhermeCezarinoSimoes/aquaguard-gs2026.git aquaguard && cd aquaguard
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
- ✅ **Executado numa VM real em 18/11/2026** (VirtualBox, Ubuntu Server 24.04, host `aquaguard-srv01`, kernel 6.8):
  provisionamento completo com sucesso (infra 37 s, aplicação 122 s), API e monitor ativos, nginx servindo `/` e `/swagger`,
  UFW ativo (22 e 80 liberadas, 5080 bloqueada), regras auditd registrando execução dos scripts.
- ✅ **Teste de falha: 5 de 5 aprovados** — API morta com SIGKILL reiniciou em 5 s; monitor reiniciou; alerta de CPU (92 %);
  alerta de disco (90 %); alerta crítico com nginx parado.
  Evidências: `../evidencias/operating-systems/01_relatorio_auditoria_vm.txt` e `02_teste_falha_5_aprovados.log`.
- 🔧 Correção após o teste real: o `ausearch` do relatório ficava esperando entrada quando executado fora de um terminal
  (o relatório levou 664 s na 1ª execução); agora usa `--input-logs`, entrada vazia e limite de 60 s.
- ⏳ Falta gravar o vídeo (roteiro: `../docs/roteiros/roteiro_video_os.md`).
