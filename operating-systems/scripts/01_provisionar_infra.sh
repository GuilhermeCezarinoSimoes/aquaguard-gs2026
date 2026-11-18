#!/usr/bin/env bash
# =============================================================================
# 01 · Provisionamento da INFRAESTRUTURA (rede, DNS, IP, hostname, segurança, auditoria)
# Ubuntu Server 22.04/24.04 · executar como root · idempotente (pode rodar várias vezes)
# =============================================================================
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${DIR}/lib/comum.sh"
exigir_root
carregar_config "${1:-/etc/aquaguard/aquaguard.env}"

: "${AQG_HOSTNAME:=aquaguard-srv01}" "${AQG_DOMINIO:=aquaguard.local}" "${AQG_TIMEZONE:=America/Sao_Paulo}"
: "${AQG_DNS_SERVIDORES:=1.1.1.1 8.8.8.8}" "${AQG_USUARIO:=aquaguard}" "${AQG_PORTA_API:=5080}"
: "${AQG_INTERFACE:=}" "${AQG_IP_ESTATICO:=}" "${AQG_GATEWAY:=}"

configurar_pacotes_base() {
  export DEBIAN_FRONTEND=noninteractive
  apt-get update -qq
  apt-get install -y -qq curl ca-certificates git jq ufw auditd audispd-plugins logrotate \
    net-tools dnsutils iproute2 sysstat stress-ng nginx >/dev/null
}

configurar_hostname() {
  hostnamectl set-hostname "${AQG_HOSTNAME}"
  # /etc/hosts: resolução local do servidor e do nome da API
  sed -i "/# aquaguard-inicio/,/# aquaguard-fim/d" /etc/hosts
  cat >> /etc/hosts <<EOF
# aquaguard-inicio
127.0.1.1   ${AQG_HOSTNAME}.${AQG_DOMINIO} ${AQG_HOSTNAME}
127.0.0.1   api.${AQG_DOMINIO} painel.${AQG_DOMINIO}
# aquaguard-fim
EOF
  timedatectl set-timezone "${AQG_TIMEZONE}"
}

configurar_dns() {
  # systemd-resolved: servidores DNS e domínio de busca via drop-in (não sobrescreve config do sistema)
  mkdir -p /etc/systemd/resolved.conf.d
  cat > /etc/systemd/resolved.conf.d/aquaguard.conf <<EOF
[Resolve]
DNS=${AQG_DNS_SERVIDORES}
FallbackDNS=9.9.9.9
Domains=${AQG_DOMINIO}
DNSSEC=allow-downgrade
EOF
  systemctl restart systemd-resolved
  { resolvectl status | grep -E "DNS Servers|DNS Domain" | head -4 || true; } | while read -r l; do log INFO "DNS: ${l}"; done
}

configurar_rede() {
  local iface="${AQG_INTERFACE:-$(ip -o -4 route show to default | awk '{print $5}' | head -1)}"
  log INFO "Interface principal: ${iface} · IP atual: $(ip -o -4 addr show "${iface}" | awk '{print $4}')"
  if [[ -n "${AQG_IP_ESTATICO}" ]]; then
    # IP estático via netplan (aplicado com 'netplan try' para rollback automático se a rede cair)
    cat > /etc/netplan/60-aquaguard.yaml <<EOF
network:
  version: 2
  ethernets:
    ${iface}:
      dhcp4: false
      addresses: [${AQG_IP_ESTATICO}]
      routes: [{to: default, via: ${AQG_GATEWAY}}]
      nameservers: {addresses: [$(echo "${AQG_DNS_SERVIDORES}" | sed 's/ /, /g')]}
EOF
    chmod 600 /etc/netplan/60-aquaguard.yaml
    netplan generate && netplan apply
    log OK "IP estático ${AQG_IP_ESTATICO} aplicado em ${iface}"
  else
    log INFO "AQG_IP_ESTATICO vazio: mantendo DHCP (adequado para VM com NAT/bridge)"
  fi
}

configurar_firewall() {
  ufw --force reset >/dev/null
  ufw default deny incoming
  ufw default allow outgoing
  ufw allow OpenSSH
  ufw allow 80/tcp comment 'AquaGuard painel/API via nginx'
  ufw deny "${AQG_PORTA_API}/tcp" comment 'Kestrel só via proxy reverso'
  ufw --force enable
  ufw status verbose | while read -r l; do log INFO "UFW: ${l}"; done
}

configurar_usuario_e_pastas() {
  id "${AQG_USUARIO}" &>/dev/null || useradd --system --home /var/lib/aquaguard --shell /usr/sbin/nologin "${AQG_USUARIO}"
  install -d -o "${AQG_USUARIO}" -g "${AQG_USUARIO}" -m 750 /var/lib/aquaguard /opt/aquaguard
  install -d -o root -g "${AQG_USUARIO}" -m 770 "${AQG_LOG_DIR}"
  install -d -m 750 /etc/aquaguard
}

configurar_auditoria() {
  # auditd: registra alterações em arquivos críticos e execução dos scripts do projeto
  cat > /etc/audit/rules.d/aquaguard.rules <<'EOF'
-w /etc/aquaguard/ -p wa -k aquaguard_config
-w /etc/systemd/system/aquaguard-api.service -p wa -k aquaguard_servico
-w /etc/systemd/system/aquaguard-monitor.service -p wa -k aquaguard_servico
-w /opt/aquaguard/ -p wa -k aquaguard_binarios
-w /opt/aquaguard-infra/scripts/ -p x -k aquaguard_scripts
-w /etc/passwd -p wa -k identidade
-w /etc/sudoers -p wa -k privilegios
EOF
  augenrules --load >/dev/null 2>&1 || service auditd restart
  systemctl enable --now auditd >/dev/null
  # Rotação dos logs do projeto (14 dias, compactados)
  cat > /etc/logrotate.d/aquaguard <<EOF
${AQG_LOG_DIR}/*.log {
  daily
  rotate 14
  compress
  missingok
  notifempty
  copytruncate
  su root ${AQG_USUARIO}
}
EOF
  # journald persistente (logs sobrevivem a reboot)
  mkdir -p /var/log/journal && systemctl restart systemd-journald
}

validar() {
  log INFO "Hostname: $(hostname -f 2>/dev/null || hostname)"
  getent hosts "api.${AQG_DOMINIO}" >/dev/null && log OK "api.${AQG_DOMINIO} resolve localmente" || log ERRO "api.${AQG_DOMINIO} não resolve"
  if getent hosts portal.inmet.gov.br >/dev/null; then log OK "DNS externo funcionando"; else log ALERTA "DNS externo sem resposta"; fi
  local regras
  regras="$(auditctl -l 2>/dev/null | grep -c aquaguard || true)"
  log OK "${regras} regras de auditoria AquaGuard ativas"
}

passo "Instalando pacotes base"                 configurar_pacotes_base
passo "Configurando hostname, /etc/hosts e fuso" configurar_hostname
passo "Configurando DNS (systemd-resolved)"      configurar_dns
passo "Configurando rede / IP"                   configurar_rede
passo "Criando usuário de serviço e diretórios"  configurar_usuario_e_pastas
passo "Configurando firewall (UFW)"              configurar_firewall
passo "Configurando auditd, logrotate, journald" configurar_auditoria
passo "Validando infraestrutura"                 validar
log OK "Infraestrutura provisionada com sucesso."
