# Roteiro — Vídeo Operating Systems (máx. 7:00)

Preparação: VM Ubuntu **limpa** (snapshot), repositório clonado, terminal com fonte grande.

| Tempo | Comando / tela | Fala |
|---|---|---|
| 0:00–0:30 | README da pasta | Objetivo: hospedar a API AquaGuard (aplicação WEB da disciplina de C#/SOA) com provisionamento automático. |
| 0:30–1:00 | `cat config/aquaguard.env.example` | Variáveis de infra, app e limites de monitoramento. |
| 1:00–3:00 | `sudo bash operating-systems/scripts/00_provisionar_tudo.sh` | Narrar as etapas enquanto rodam: pacotes; hostname e `/etc/hosts`; DNS no systemd-resolved; IP (DHCP/netplan); usuário de serviço; UFW; auditd/logrotate; .NET 8; `dotnet test` e `publish`; `/etc/aquaguard/api.env` (chave gerada); unit systemd; nginx; health check. (Acelere a gravação nos downloads.) |
| 3:00–3:40 | `hostnamectl`, `resolvectl status`, `ip a`, `ufw status`, `curl localhost/health`, navegador no IP da VM | Infra e app funcionando: painel e Swagger pelo nginx. |
| 3:40–4:30 | `systemctl status aquaguard-monitor`, `tail -f /var/log/aquaguard/metricas.jsonl` | Monitor como serviço (Restart=always, StartLimitBurst: volta sozinho se morrer); métricas a cada 30 s. |
| 4:30–6:00 | `sudo bash operating-systems/scripts/04_teste_falha.sh` + `tail -f alertas.log` em outro terminal | Kill -9 na API → volta sozinha; kill no monitor → volta; pico de CPU → ALERTA; disco cheio → ALERTA; nginx parado → CRITICO e restauração. Resultado APROVADO. |
| 6:00–6:45 | `cat /var/log/aquaguard/auditoria_execucao.log`, `sudo ausearch -k aquaguard_config -i`, `05_relatorio_auditoria.sh` | Logs de auditoria: quem rodou, quando, resultado; auditd em arquivos críticos. |
| 6:45–7:00 | — | Fechamento: critérios atendidos. |
