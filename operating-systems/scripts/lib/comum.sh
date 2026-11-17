#!/usr/bin/env bash
# Funções comuns: log padronizado, trilha de auditoria de execução e verificações.
# Uso: source "$(dirname "$0")/lib/comum.sh"

set -Eeuo pipefail

AQG_LOG_DIR="${AQG_LOG_DIR:-/var/log/aquaguard}"
AQG_AUDIT_LOG="${AQG_LOG_DIR}/auditoria_execucao.log"
AQG_SCRIPT="$(basename "${0}")"
AQG_INICIO="$(date +%s)"

mkdir -p "${AQG_LOG_DIR}"
chmod 750 "${AQG_LOG_DIR}" 2>/dev/null || true

_cor() { [[ -t 1 ]] && printf '\033[%sm' "$1" || true; }

# log NIVEL mensagem...  → terminal + arquivo do script + journald (tag aquaguard)
log() {
  local nivel="$1"; shift
  local linha
  linha="$(date '+%Y-%m-%dT%H:%M:%S%z') [${nivel}] [${AQG_SCRIPT}] $*"
  case "${nivel}" in
    ERRO|CRITICO) _cor 31 ;; ALERTA) _cor 33 ;; OK) _cor 32 ;; *) _cor 0 ;;
  esac
  echo "${linha}"; _cor 0
  echo "${linha}" >> "${AQG_LOG_DIR}/${AQG_SCRIPT%.sh}.log"
  command -v logger >/dev/null && logger -t aquaguard -p "user.$( [[ ${nivel} == ERRO || ${nivel} == CRITICO ]] && echo err || echo info)" "[${AQG_SCRIPT}] ${nivel}: $*" || true
}

# Registro de auditoria: quem executou, quando, com quais argumentos e o resultado.
auditar() {
  local evento="$1" detalhe="${2:-}"
  printf '%s|host=%s|usuario=%s|sudo_user=%s|script=%s|pid=%s|evento=%s|%s\n' \
    "$(date '+%Y-%m-%dT%H:%M:%S%z')" "$(hostname)" "$(id -un)" "${SUDO_USER:-}" \
    "${AQG_SCRIPT}" "$$" "${evento}" "${detalhe}" >> "${AQG_AUDIT_LOG}"
}

_ao_sair() {
  local codigo=$?
  local dur=$(( $(date +%s) - AQG_INICIO ))
  if [[ ${codigo} -eq 0 ]]; then
    auditar "FIM" "status=sucesso duracao=${dur}s"
  else
    auditar "FIM" "status=falha codigo=${codigo} duracao=${dur}s"
    log ERRO "Script terminou com erro (código ${codigo}). Veja ${AQG_LOG_DIR}/${AQG_SCRIPT%.sh}.log"
  fi
}
_ao_erro() { log ERRO "Falha na linha ${1}: comando '${2}'"; }

trap '_ao_sair' EXIT
trap '_ao_erro ${LINENO} "${BASH_COMMAND}"' ERR
auditar "INICIO" "args=$*"

exigir_root() {
  if [[ ${EUID} -ne 0 ]]; then
    echo "Execute como root: sudo $0 $*" >&2
    exit 1
  fi
}

# Carrega variáveis de ambiente do projeto (config/aquaguard.env)
carregar_config() {
  local arq="${1:-/etc/aquaguard/aquaguard.env}"
  if [[ -f "${arq}" ]]; then
    # shellcheck disable=SC1090
    set -a; source "${arq}"; set +a
    log INFO "Configuração carregada de ${arq}"
  else
    log ALERTA "Arquivo ${arq} não encontrado; usando valores padrão"
  fi
}

# Executa um passo com log e marca de tempo
passo() {
  local descricao="$1"; shift
  log INFO "▶ ${descricao}"
  "$@"
  log OK "✔ ${descricao}"
}
