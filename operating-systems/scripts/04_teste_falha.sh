#!/usr/bin/env bash
# =============================================================================
# 04 · Testes de FALHA da infraestrutura AquaGuard
# Cada cenário provoca uma falha real e verifica a reação automática:
#   1. API morta com SIGKILL           → systemd reinicia (Restart=always)
#   2. Monitor morto com SIGKILL        → systemd reinicia o monitor
#   3. Pico de CPU (stress-ng)          → monitor gera ALERTA CPU e depois normaliza
#   4. Disco cheio (arquivo de teste)   → monitor gera ALERTA DISCO e depois normaliza
#   5. nginx parado                     → monitor gera ALERTA CRITICO; script restaura
# Resultado consolidado em /var/log/aquaguard/teste_falha_<data>.log
# =============================================================================
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${DIR}/lib/comum.sh"
exigir_root
set +e   # o teste deve continuar mesmo se um cenário falhar

RELATORIO="${AQG_LOG_DIR}/teste_falha_$(date +%Y%m%d_%H%M%S).log"
APROVADOS=0; REPROVADOS=0

resultado() {
  local cenario="$1" ok="$2" detalhe="$3"
  if [[ "${ok}" == "1" ]]; then APROVADOS=$((APROVADOS+1)); log OK "[APROVADO] ${cenario}: ${detalhe}"
  else REPROVADOS=$((REPROVADOS+1)); log ERRO "[REPROVADO] ${cenario}: ${detalhe}"; fi
  echo "$(date '+%F %T') | ${cenario} | $([[ ${ok} == 1 ]] && echo APROVADO || echo REPROVADO) | ${detalhe}" >> "${RELATORIO}"
}

esperar() {  # esperar <segundos> <comando de teste...>
  local max="$1"; shift
  for _ in $(seq 1 "${max}"); do "$@" && return 0; sleep 1; done
  return 1
}

api_ok() { curl -fsS --max-time 3 http://127.0.0.1/health 2>/dev/null | grep -q Healthy; }
alerta_registrado() { tail -n 20 "${AQG_LOG_DIR}/alertas.log" 2>/dev/null | grep -q "$1"; }

cenario_api_kill() {
  local pid_antes pid_depois
  pid_antes="$(systemctl show -p MainPID --value aquaguard-api)"
  log INFO "Matando a API (PID ${pid_antes}) com SIGKILL…"
  kill -9 "${pid_antes}"
  local t0=$SECONDS
  if esperar 30 api_ok; then
    pid_depois="$(systemctl show -p MainPID --value aquaguard-api)"
    resultado "1-API SIGKILL" 1 "reiniciada em $((SECONDS-t0))s (PID ${pid_antes} → ${pid_depois}; NRestarts=$(systemctl show -p NRestarts --value aquaguard-api))"
  else
    resultado "1-API SIGKILL" 0 "API não voltou em 30s"
  fi
}

cenario_monitor_kill() {
  local pid; pid="$(systemctl show -p MainPID --value aquaguard-monitor)"
  kill -9 "${pid}"
  if esperar 20 bash -c '[[ "$(systemctl show -p MainPID --value aquaguard-monitor)" != "'"${pid}"'" ]] && systemctl is-active --quiet aquaguard-monitor'; then
    resultado "2-Monitor SIGKILL" 1 "monitor reiniciado (PID ${pid} → $(systemctl show -p MainPID --value aquaguard-monitor))"
  else
    resultado "2-Monitor SIGKILL" 0 "monitor não reiniciou"
  fi
}

cenario_cpu() {
  log INFO "Gerando carga de CPU por 75s (stress-ng)…"
  stress-ng --cpu "$(nproc)" --timeout 75s >/dev/null 2>&1 &
  if esperar 90 alerta_registrado "CPU"; then resultado "3-Pico de CPU" 1 "alerta de CPU gerado: $(grep CPU "${AQG_LOG_DIR}/alertas.log" | tail -1)"
  else resultado "3-Pico de CPU" 0 "monitor não alertou CPU"; fi
  wait
}

cenario_disco() {
  local livre_kb alvo_kb arquivo=/var/lib/aquaguard/teste_disco_cheio.bin
  local uso_atual; uso_atual="$(df -P / | awk 'NR==2 {gsub("%","",$5); print $5}')"
  local limite="${AQG_LIMITE_DISCO:-85}"
  livre_kb="$(df -Pk / | awk 'NR==2 {print $4}')"
  local total_kb; total_kb="$(df -Pk / | awk 'NR==2 {print $2}')"
  # Ocupa o necessário para passar o limite + 2 pontos percentuais (mantendo ≥ 300 MB livres)
  alvo_kb=$(( total_kb * (limite + 2 - uso_atual) / 100 ))
  if (( alvo_kb <= 0 )); then resultado "4-Disco cheio" 1 "disco já acima do limite (${uso_atual}%)"; return; fi
  if (( livre_kb - alvo_kb < 300000 )); then resultado "4-Disco cheio" 0 "espaço insuficiente para teste seguro"; return; fi
  log INFO "Ocupando $((alvo_kb/1024)) MB em ${arquivo} (uso atual ${uso_atual}%, limite ${limite}%)…"
  fallocate -l "$((alvo_kb))K" "${arquivo}"
  if esperar 90 alerta_registrado "DISCO"; then resultado "4-Disco cheio" 1 "alerta de disco gerado com $(df -P / | awk 'NR==2 {print $5}') de uso"
  else resultado "4-Disco cheio" 0 "monitor não alertou disco"; fi
  rm -f "${arquivo}"
  log INFO "Arquivo de teste removido; uso voltou a $(df -P / | awk 'NR==2 {print $5}')"
}

cenario_nginx() {
  systemctl stop nginx
  if esperar 90 alerta_registrado "NGINX"; then resultado "5-nginx parado" 1 "alerta crítico gerado"
  else resultado "5-nginx parado" 0 "sem alerta"; fi
  systemctl start nginx
  esperar 10 api_ok && log OK "nginx restaurado; API acessível pelo proxy"
}

log INFO "Pré-condição: API $(api_ok && echo OK || echo FORA) · monitor $(systemctl is-active aquaguard-monitor)"
cenario_api_kill
cenario_monitor_kill
cenario_cpu
cenario_disco
cenario_nginx
log INFO "Resumo: ${APROVADOS} aprovados, ${REPROVADOS} reprovados · relatório ${RELATORIO}"
journalctl -u aquaguard-api -u aquaguard-monitor --since "-10 min" --no-pager | grep -Ei "started|stopped|killed|restart|main process" | tail -20 >> "${RELATORIO}"
[[ ${REPROVADOS} -eq 0 ]]
