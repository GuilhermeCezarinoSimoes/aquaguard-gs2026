#!/usr/bin/env bash
# =============================================================================
# 05 · Relatório de auditoria e acompanhamento
# Consolida: execuções dos scripts, alertas, últimas métricas, eventos do systemd,
# eventos do auditd (arquivos críticos) e acessos ao nginx → evidencias/
# =============================================================================
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${DIR}/lib/comum.sh"
exigir_root
set +e

SAIDA="${1:-${AQG_LOG_DIR}/relatorio_auditoria_$(date +%Y%m%d_%H%M%S).txt}"
{
  echo "=================== RELATÓRIO DE AUDITORIA AQUAGUARD ==================="
  echo "Gerado em: $(date)  ·  Host: $(hostname -f 2>/dev/null || hostname)  ·  Kernel: $(uname -r)"
  echo "Uptime: $(uptime -p)  ·  IP: $(hostname -I)"
  echo
  echo "--- 1. Serviços"
  systemctl --no-pager --lines=0 status aquaguard-api aquaguard-monitor nginx 2>/dev/null | grep -E "●|Active:|Main PID"
  echo "Reinícios automáticos da API: $(systemctl show -p NRestarts --value aquaguard-api)"
  echo
  echo "--- 2. Execuções de scripts (trilha de auditoria)"
  tail -n 40 "${AQG_AUDIT_LOG}" 2>/dev/null
  echo
  echo "--- 3. Alertas de infraestrutura"
  tail -n 30 "${AQG_LOG_DIR}/alertas.log" 2>/dev/null || echo "(nenhum alerta)"
  echo
  echo "--- 4. Últimas métricas"
  tail -n 10 "${AQG_LOG_DIR}/metricas.jsonl" 2>/dev/null
  echo
  echo "--- 5. Eventos systemd (últimas 2h)"
  journalctl -u aquaguard-api -u aquaguard-monitor --since "-2 h" --no-pager -o short-iso 2>/dev/null | grep -Ei "start|stop|kill|fail|restart" | tail -30
  echo
  echo "--- 6. auditd: alterações em arquivos críticos (chaves aquaguard_*)"
  # --input-logs + </dev/null: sem isso o ausearch pode ficar esperando entrada quando não está num terminal
  # (na 1ª execução real, dentro do 00_provisionar_tudo.sh, o relatório levou 664 s por esse motivo)
  timeout 60 ausearch --input-logs -k aquaguard_config -k aquaguard_servico -k aquaguard_binarios -k aquaguard_scripts \
    -ts today -i </dev/null 2>/dev/null | grep -E "^type=SYSCALL|name=" | tail -30 || echo "(sem eventos)"
  echo
  echo "--- 7. Acessos HTTP (nginx) — top 10 rotas"
  awk '{print $7}' /var/log/nginx/aquaguard_access.log 2>/dev/null | sort | uniq -c | sort -rn | head -10
  echo
  echo "--- 8. Firewall"
  ufw status numbered 2>/dev/null
} > "${SAIDA}"
log OK "Relatório gerado: ${SAIDA}"
