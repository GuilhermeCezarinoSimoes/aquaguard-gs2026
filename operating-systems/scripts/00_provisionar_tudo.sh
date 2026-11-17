#!/usr/bin/env bash
# =============================================================================
# 00 · Orquestrador — provisiona TUDO em uma VM Ubuntu limpa:
#   infraestrutura → aplicação → monitor como serviço → validação → relatório
# Uso (dentro da VM, na raiz do repositório clonado):
#   sudo bash operating-systems/scripts/00_provisionar_tudo.sh
# =============================================================================
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${DIR}/lib/comum.sh"
exigir_root

ENV_DESTINO=/etc/aquaguard/aquaguard.env
mkdir -p /etc/aquaguard
if [[ ! -f "${ENV_DESTINO}" ]]; then
  install -m 640 "${DIR}/../config/aquaguard.env.example" "${ENV_DESTINO}"
  log INFO "Configuração padrão copiada para ${ENV_DESTINO} (edite e rode novamente para personalizar)"
fi

# Copia os scripts para local fixo usado pelo serviço de monitoramento
rm -rf /opt/aquaguard-infra && mkdir -p /opt/aquaguard-infra
cp -r "${DIR}/.." /opt/aquaguard-infra/tmp && mv /opt/aquaguard-infra/tmp/* /opt/aquaguard-infra/ && rm -rf /opt/aquaguard-infra/tmp
chmod 750 /opt/aquaguard-infra/scripts/*.sh

passo "ETAPA 1/4 · Infraestrutura"  bash "${DIR}/01_provisionar_infra.sh" "${ENV_DESTINO}"
passo "ETAPA 2/4 · Aplicação"       bash "${DIR}/02_provisionar_app.sh" "${ENV_DESTINO}"

instalar_monitor() {
  install -m 644 "${DIR}/../systemd/aquaguard-monitor.service" /etc/systemd/system/
  systemctl daemon-reload
  systemctl enable --now aquaguard-monitor.service >/dev/null
  sleep 3
  systemctl is-active --quiet aquaguard-monitor && log OK "Monitor ativo (PID $(systemctl show -p MainPID --value aquaguard-monitor))"
}
passo "ETAPA 3/4 · Monitoramento como serviço" instalar_monitor
passo "ETAPA 4/4 · Relatório de auditoria"     bash "${DIR}/05_relatorio_auditoria.sh"

IP="$(hostname -I | awk '{print $1}')"
log OK "================ AquaGuard no ar ================"
log OK "Painel:   http://${IP}/"
log OK "Swagger:  http://${IP}/swagger"
log OK "Health:   http://${IP}/health"
log OK "Logs:     ${AQG_LOG_DIR}/   ·   journalctl -u aquaguard-api -f"
log OK "Teste de falha: sudo bash ${DIR}/04_teste_falha.sh"
