# 06 — Operating Systems (Linux)

## O que o professor pede
Um **Linux numa máquina virtual (VM)** que se **configura sozinho com scripts** e passa a rodar uma aplicação web do
projeto, com **monitoramento** (alertas de CPU, memória e disco), **logs de auditoria** e um **teste de falha**.
Entrega no Teams: **link do GitHub** + **vídeo de até 7 minutos** mostrando a configuração automática.

| Critério | Pontos | Arquivo | Pronto? |
|---|---|---|---|
| Script de infraestrutura (rede, DNS, IP) | 2 | `operating-systems\scripts\01_provisionar_infra.sh` | ✅ escrito |
| Script da aplicação (dependências, configurações) | 2 | `02_provisionar_app.sh` | ✅ escrito |
| Monitor com alertas de CPU, disco e memória | 2 | `03_monitor.sh` | ✅ escrito |
| Monitor como serviço tolerante a falhas | 1 | `systemd\aquaguard-monitor.service` | ✅ escrito |
| Logs de auditoria | 1 | `scripts\lib\comum.sh`, `05_relatorio_auditoria.sh` | ✅ escrito |
| Funcionamento completo | 2 | `00_provisionar_tudo.sh` + `04_teste_falha.sh` | ⚠️ **precisa rodar na VM e gravar** |

> ⚠️ **Importante:** os scripts foram escritos e revisados, mas **nunca rodaram num Linux de verdade** (o PC onde foram
> feitos não tem Linux). Esta é a matéria com **mais risco**. Comece cedo. Se algo der erro, a seção "Deu erro?" no final
> ajuda; anote a mensagem exata.

## Do que você precisa
- PC com **8 GB de RAM** ou mais e **40 GB livres** no disco.
- O projeto **publicado no GitHub** (veja `00_PREPARAR_COMPUTADOR`), porque a VM baixa o projeto de lá.
- ~2 horas (a maior parte é esperar instalar).

## Entendendo em 1 minuto
- **Máquina virtual:** um computador "de mentira" dentro do seu Windows. Programa: **VirtualBox** (grátis).
- **Ubuntu Server:** a versão do Linux que vamos instalar nela (só tela preta com texto, sem janelas — é normal).
- **SSH:** um jeito de controlar a VM a partir do Windows, numa janela onde **dá para colar comandos** (Ctrl+V).
- O script **`00_provisionar_tudo.sh`** faz tudo sozinho: configura rede/DNS/nome, firewall, auditoria, instala o .NET,
  baixa e testa o AquaGuard, cria os serviços que reiniciam sozinhos e liga o vigia (monitor).

---

## PARTE A — Criar a máquina virtual (≈ 40 min, quase tudo espera)

### A1. Baixar os programas
1. **VirtualBox:** https://www.virtualbox.org/wiki/Downloads ▸ **"Windows hosts"** ▸ instale com tudo padrão.
   (Se aparecer aviso sobre "Python Core" ou "interfaces de rede", clique **Sim/Yes** e continue.)
2. **Ubuntu Server 24.04 LTS:** https://ubuntu.com/download/server ▸ **"Download Ubuntu Server 24.04 LTS"** (arquivo `.iso`, ~3 GB).

### A2. Criar a VM
1. Abra o VirtualBox ▸ **Novo (New)**.
2. **Nome:** `aquaguard` · **ISO Image:** escolha o `.iso` baixado ·
   ✅ marque **"Skip Unattended Installation"** (Pular instalação desassistida) ▸ Próximo.
3. **Memória:** `4096 MB` · **Processadores:** `2` ▸ Próximo.
4. **Disco:** `30 GB` ▸ Próximo ▸ **Finalizar**.

### A3. Liberar o acesso do Windows à VM (redirecionamento de portas)
1. Selecione a VM `aquaguard` ▸ **Configurações (Settings)** ▸ **Rede (Network)** ▸ Adaptador 1 deve estar em **NAT**.
2. Clique em **Avançado ▸ Redirecionamento de Portas (Port Forwarding)** ▸ botão **+** e crie as duas linhas:

| Nome | Protocolo | Porta do Hospedeiro | Porta do Convidado |
|---|---|---|---|
| ssh | TCP | 2222 | 22 |
| web | TCP | 8080 | 80 |

3. **OK** ▸ **OK**.

### A4. Instalar o Ubuntu (≈ 15 min)
Clique em **Iniciar (Start)**. Abre a janela da VM. Use as **setas** e **Enter**; **Espaço** marca opções.
1. "Try or Install Ubuntu Server" ▸ Enter (espere).
2. Idioma: **English** ▸ Enter. (Inglês evita problemas com os comandos.)
3. Se perguntar sobre atualizar o instalador: **Continue without updating**.
4. Teclado: Layout **Portuguese (Brazil)** ▸ **Done**.
5. Tipo: **Ubuntu Server** ▸ **Done**.
6. Rede: deixe como está (aparece um IP 10.0.2.15) ▸ **Done**. Proxy: vazio ▸ **Done**. Mirror: espere o teste ▸ **Done**.
7. Disco: **Use an entire disk** ▸ **Done** ▸ **Done** ▸ **Continue** (confirma apagar o disco **virtual**, não o seu).
8. Perfil (anote!):
   - Your name: `Aluno` · Server name: `aquaguard` · Username: `aluno` · Password: crie uma senha simples e **anote**.
9. Ubuntu Pro: **Skip for now** ▸ Continue.
10. SSH: ✅ **Install OpenSSH server** (Espaço para marcar) ▸ **Done**. Importante!
11. Snaps: não marque nada ▸ **Done**. Espere instalar (10–15 min).
12. Quando aparecer **Reboot Now**, aperte Enter. Se pedir "remove the installation medium", aperte **Enter** de novo.
13. Aparece `aquaguard login:`. **Pronto, o Linux está instalado.** Pode **minimizar** essa janela (não feche).

> Dica: no VirtualBox, menu **Máquina ▸ Criar Snapshot** agora, nome "limpa". Se algo der muito errado depois,
> você volta para este ponto em segundos ("Restaurar snapshot").

---

## PARTE B — Conectar pelo Windows e rodar os scripts (≈ 20 min)

### B1. Abrir a conexão
1. No Windows, abra o **Terminal** (ou PowerShell): tecla Windows ▸ digite `PowerShell` ▸ Enter.
2. Digite (ou cole) e aperte Enter:
   ```
   ssh aluno@localhost -p 2222
   ```
3. Na primeira vez pergunta "Are you sure you want to continue connecting?" ▸ digite `yes` ▸ Enter.
4. Digite a senha do Ubuntu (**ela não aparece enquanto digita** — é normal) ▸ Enter.
5. Aparece `aluno@aquaguard:~$`. Agora você está **dentro do Linux**. Para colar comandos: **botão direito do mouse** ou Ctrl+V.

### B2. Baixar o projeto e rodar tudo
Cole **uma linha por vez** e aperte Enter (troque `SEU-USUARIO` pelo do GitHub). Quando pedir senha (`sudo`), digite a do Ubuntu.
```
sudo apt-get update && sudo apt-get install -y git
git clone https://github.com/SEU-USUARIO/aquaguard-gs2026.git aquaguard
cd aquaguard
sudo bash operating-systems/scripts/00_provisionar_tudo.sh
```
O último comando leva **5 a 10 minutos**. Aparecem linhas `▶` (começou) e `✔` (terminou) para cada etapa.
**Se der certo, termina com** "AquaGuard no ar" e os endereços do Painel e do Swagger.

> ⚠️ A conexão pode cair quando o script ajusta o firewall/rede. Se cair: reconecte (B1) e rode de novo
> `cd aquaguard` e `sudo bash operating-systems/scripts/00_provisionar_tudo.sh` — os scripts podem rodar várias vezes.

### B3. Ver o site funcionando no seu navegador do Windows
Abra **http://localhost:8080** (painel) e **http://localhost:8080/swagger**. É o AquaGuard rodando **dentro do Linux**.

### B4. Teste de falha
```
sudo bash operating-systems/scripts/04_teste_falha.sh
```
Leva ~5 minutos. Ele "derruba" coisas de propósito (mata o servidor, enche o disco, sobrecarrega a CPU, para o nginx) e
confere se o sistema reage. No final: **"Resumo: 5 aprovados, 0 reprovados"**.

### B5. Relatório e evidências
```
sudo bash operating-systems/scripts/05_relatorio_auditoria.sh /tmp/relatorio_auditoria.txt
sudo tar czf /tmp/evidencias_os.tgz /var/log/aquaguard /tmp/relatorio_auditoria.txt
sudo chmod 644 /tmp/evidencias_os.tgz
exit
```
Agora, **no PowerShell do Windows** (já fora do Linux), traga os arquivos para o projeto:
```
cd $HOME\Desktop
scp -P 2222 aluno@localhost:/tmp/evidencias_os.tgz .
tar -xzf evidencias_os.tgz
```
Copie a pasta que apareceu na Área de Trabalho para `GS\evidencias\operating-systems\` e envie ao GitHub
(GitHub Desktop ▸ Commit ▸ Push).

---

## PARTE C — Gravar o vídeo (máx. 7:00)
Para o vídeo ficar bonito, **volte ao snapshot "limpa"** (VirtualBox ▸ Snapshots ▸ "limpa" ▸ Restaurar) e grave tudo
desde a Parte B2. Grave a tela do PowerShell (aumente a fonte com Ctrl + roda do mouse). Pode acelerar ou cortar a espera.

| Tempo | O que fazer na tela | O que falar |
|---|---|---|
| 0:00–0:30 | GitHub: pasta `operating-systems` e o README | "Vamos provisionar um servidor Linux automaticamente para hospedar a API web do AquaGuard." |
| 0:30–1:00 | `cat operating-systems/config/aquaguard.env.example` | "Este arquivo tem as variáveis: nome do servidor, DNS, IP, porta da aplicação e os limites de alerta." |
| 1:00–3:00 | `sudo bash operating-systems/scripts/00_provisionar_tudo.sh` | Leia as etapas conforme aparecem: "instala pacotes; configura o nome do servidor e o arquivo hosts; configura o DNS; a rede; cria um usuário só para o serviço; firewall; auditoria; instala o .NET; roda os testes; publica a aplicação; cria as variáveis de ambiente; cria o serviço no systemd; configura o nginx; verifica a saúde." |
| 3:00–3:40 | `hostnamectl` · `resolvectl status` · `ip a` · `sudo ufw status` · `curl localhost/health` · navegador em http://localhost:8080 | "A infraestrutura está configurada e a aplicação está no ar." |
| 3:40–4:30 | `systemctl status aquaguard-monitor` · `tail -n 5 /var/log/aquaguard/metricas.jsonl` | "O monitor roda como serviço do systemd: se ele cair, volta sozinho. A cada 30 segundos mede CPU, memória, disco e se a API responde." |
| 4:30–6:00 | `sudo bash operating-systems/scripts/04_teste_falha.sh` | "Agora o teste de falha: matamos a API e ela volta sozinha; matamos o monitor e ele volta; geramos pico de CPU e disco cheio e o monitor gera alerta; paramos o nginx e ele alerta como crítico." |
| 6:00–6:45 | `sudo cat /var/log/aquaguard/auditoria_execucao.log` · `sudo cat /var/log/aquaguard/alertas.log` | "Todo script registra quem executou, quando e o resultado. Aqui estão os alertas gerados." |
| 6:45–7:00 | — | "Infraestrutura provisionada, aplicação hospedada, monitorada e tolerante a falhas." |

Publique no YouTube (Não listado).

## O que enviar no Teams
```
Global Solution 2026.2 – CitizenTech – AquaGuard – Operating Systems
Integrantes: Guilherme Cezarino Simoes e Fabrini Soares
Repositório: https://github.com/SEU-USUARIO/aquaguard-gs2026 (pasta /operating-systems: scripts, configurações, README; evidências em /evidencias/operating-systems)
Vídeo (7 min): https://youtu.be/XXXXXXXX
```

## Deu erro?
| Problema | Solução |
|---|---|
| VirtualBox: "VT-x is disabled" / a VM não liga | A virtualização está desligada na BIOS. Reinicie o PC, entre na BIOS (F2/Del/F10) e ative "Intel VT-x" ou "AMD-V/SVM". Procure no YouTube "ativar virtualização" + modelo do seu PC |
| `ssh: connect ... refused` | A VM está desligada, ou faltou o redirecionamento (A3), ou o OpenSSH não foi marcado (A4 passo 10). Na janela da VM, faça login e rode `sudo apt install -y openssh-server` |
| `git clone` pede usuário/senha | O repositório está **privado**. No GitHub: Settings ▸ General ▸ Change visibility ▸ Public |
| Erro durante `00_provisionar_tudo.sh` | Rode de novo (os scripts podem repetir). Se o erro continuar, veja o arquivo indicado: `sudo tail -n 50 /var/log/aquaguard/02_provisionar_app.log` (ou `01_...`) e pesquise a mensagem |
| "API não respondeu em 30s" | `sudo journalctl -u aquaguard-api -n 50 --no-pager` mostra o motivo. Rodar `sudo systemctl restart aquaguard-api` e testar `curl localhost/health` |
| http://localhost:8080 não abre no Windows | Confira o redirecionamento "web 8080 → 80" (A3). Teste dentro da VM: `curl localhost/health` |
| Teste de disco "espaço insuficiente para teste seguro" | Aumente o disco virtual ou ignore este cenário (os outros 4 contam) |
