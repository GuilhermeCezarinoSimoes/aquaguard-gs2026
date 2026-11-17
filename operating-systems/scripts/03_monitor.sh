#!/usr/bin/env bash
# =============================================================================
# 03 · Monitor de infraestrutura AquaGuard
# Coleta CPU, memória, disco e saúde da API a cada N segundos, grava métricas
# (JSON Lines) e gera ALERTAS quando limites são ultrapassados.
# Roda como serviço systemd (aquaguard-monitor.service) com Restart=always.
#   --uma-vez   executa uma única coleta (usado em testes/cron)
# =============================================================================
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${DIR}/lib/comum.sh"
carregar_config "/etc/aquaguard/aquaguard.env" >/dev/null

LIMITE_CPU="${AQG_LIMITE_CPU:-80}"
LIMITE_MEM="${AQG_LIMITE_MEM:-85}"
LIMITE_DISCO="${AQG_LIMITE_DISCO:-85}"
INTERVALO="${AQG_INTERVALO_MONITOR:-30}"
URL_HEALTH="${AQG_URL_HEALTH:-http://127.0.0.1:5080/health}"
METRICAS="${AQG_LOG_DIR}/metricas.jsonl"
ALERTAS="${AQG_LOG_DIR}/alertas.log"
ESTADO="/run/aquaguard-monitor"   # evita repetir o mesmo alerta a cada ciclo
mkdir -p "${ESTADO}"

cpu_uso() {
  # Diferença de /proc/stat em 1 s (mais preciso que load average)
  read -r _ u1 n1 s1 i1 w1 q1 sq1 st1 _ < /proc/stat
  sleep 1
  read -r _ u2 n2 s2 i2 w2 q2 sq2 st2 _ < /proc/stat
  local ocioso=$(( (i2 + w2) - (i1 + w1) ))
  local total=$(( (u2+n2+s2+i2+w2+q2+sq2+st2) - (u1+n1+s1+i1+w1+q1+sq1+st1) ))
  echo $(( total > 0 ? (100 * (total - ocioso)) / total : 0 ))
}

mem_uso() {
  awk '/MemTotal/ {t=$2} /MemAvailable/ {a=$2} END {printf "%d", (t-a)*100/t}' /proc/meminfo
}

disco_uso() {  # maior ocupação entre / e a partição de dados
  df -P / /var/lib/aquaguard 2>/dev/null | awk 'NR>1 {gsub("%","",$5); if ($5>m) m=$5} END {print m+0}'
}

api_status() {
  local codigo
  codigo="$(curl -s -o /dev/null -w '%{http_code}' --max-time 5 "${URL_HEALTH}" || true)"
  echo "${codigo:-000}"
}

servico_ativo() { systemctl is-active --quiet "$1" && echo "ativo" || echo "inativo"; }

# alertar CHAVE NIVEL mensagem — registra só na transição (OK→alerta e alerta→OK)
alertar() {
  local chave="$1" nivel="$2"; shift 2
  if [[ ! -f "${ESTADO}/${chave}" ]]; then
    touch "${ESTADO}/${chave}"
    echo "$(date '+%Y-%m-%dT%H:%M:%S%z') [${nivel}] ${chave}: $*" | tee -a "${ALERTAS}"
    log "${nivel}" "ALERTA ${chave}: $*"
    auditar "ALERTA" "${chave} $*"
  fi
}
normalizar() {
  local chave="$1"; shift
  if [[ -f "${ESTADO}/${chave}" ]]; then
    rm -f "${ESTADO}/${chave}"
    echo "$(date '+%Y-%m-%dT%H:%M:%S%z') [OK] ${chave}: normalizado ($*)" | tee -a "${ALERTAS}"
    log OK "${chave} normalizado ($*)"
  fi
}

verificar() {
  local nome="$1" valor="$2" limite="$3"
  if (( valor >= limite )); then
    alertar "${nome}" ALERTA "${valor}% (limite ${limite}%)"
  else
    normalizar "${nome}" "${valor}%"
  fi
}

coletar() {
  local cpu mem disco api svc_api svc_nginx carga top
  cpu="$(cpu_uso)"; mem="$(mem_uso)"; disco="$(disco_uso)"
  api="$(api_status)"; svc_api="$(servico_ativo aquaguard-api)"; svc_nginx="$(servico_ativo nginx)"
  carga="$(cut -d' ' -f1-3 /proc/loadavg)"
  top="$(ps -eo comm,%cpu --sort=-%cpu | awk 'NR==2 {print $1":"$2}')"

  printf '{"ts":"%s","host":"%s","cpu":%d,"mem":%d,"disco":%d,"load":"%s","api_http":"%s","svc_api":"%s","svc_nginx":"%s","top_proc":"%s"}\n' \
    "$(date '+%Y-%m-%dT%H:%M:%S%z')" "$(hostname)" "${cpu}" "${mem}" "${disco}" "${carga}" "${api}" "${svc_api}" "${svc_nginx}" "${top}" \
    >> "${METRICAS}"

  verificar CPU "${cpu}" "${LIMITE_CPU}"
  verificar MEMORIA "${mem}" "${LIMITE_MEM}"
  verificar DISCO "${disco}" "${LIMITE_DISCO}"
  if [[ "${api}" == "200" ]]; then normalizar API "HTTP 200"; else alertar API CRITICO "health check retornou HTTP ${api}"; fi
  [[ "${svc_nginx}" == "ativo" ]] && normalizar NGINX "ativo" || alertar NGINX CRITICO "nginx parado"

  log INFO "cpu=${cpu}% mem=${mem}% disco=${disco}% load=[${carga}] api=${api} servico_api=${svc_api} top=${top}"
}

if [[ "${1:-}" == "--uma-vez" ]]; then
  coletar
  exit 0
fi

log INFO "Monitor iniciado (intervalo ${INTERVALO}s; limites CPU ${LIMITE_CPU}% MEM ${LIMITE_MEM}% DISCO ${LIMITE_DISCO}%)"
trap 'log INFO "Monitor encerrado por sinal"; exit 0' TERM INT
# Type=notify: informa ao systemd que o serviço está pronto
[[ -n "${NOTIFY_SOCKET:-}" ]] && systemd-notify --ready || true
while true; do
  coletar || log ERRO "Falha na coleta (seguindo)"
  # Avisa o systemd que o monitor está vivo (WatchdogSec no .service)
  command -v systemd-notify >/dev/null && [[ -n "${NOTIFY_SOCKET:-}" ]] && systemd-notify WATCHDOG=1 || true
  sleep "${INTERVALO}"
done
