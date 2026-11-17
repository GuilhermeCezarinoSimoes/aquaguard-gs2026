# Plano de Execução — até 19/11/2026 23h55

## Ordem adotada e justificativa
A ordem preliminar (IoT → Testing → OS → C# → Mobile → ML → Cyber) foi **revista**: com apenas 2 dias até o prazo, tudo que é
código foi feito primeiro (pelo agente, em paralelo ao tempo da equipe), e o que exige conta/login/gravação ficou para a equipe.

1. **Backend C# + SOA** primeiro — é a peça central: IoT envia para ele, o app consome, a VM Linux o hospeda, Testing o valida.
2. **ML** em seguida — o download dos dados reais do INMET (~1,5 GB brutos) rodou em segundo plano durante o backend.
3. **IoT** — reusa as regras e o contrato JSON da API.
4. **Mobile** — consome a API já pronta.
5. **Cybersecurity** — analisa os relatos produzidos pelo app/API.
6. **Operating Systems** — scripts que publicam a API pronta.
7. **Testing** — Features/Test Cases descrevem o que foi efetivamente implementado.

## Cronograma
| Quando | Responsável | Atividade | Situação |
|---|---|---|---|
| 17/11 | Agente | Leitura do edital, matriz de requisitos, estrutura | Concluído |
| 17/11 | Agente | Backend (47 testes), ML (notebook executado), IoT, Mobile, Cyber (37 testes), OS, Testing, docs | Concluído |
| 17/11 noite | Equipe | Revisar o projeto; **conversar com um morador** e registrar (`docs/pesquisa_campo.md`); publicar no GitHub | Pendente |
| 18/11 manhã | Equipe | Wokwi (circuito + link); Azure DevOps (import CSV, professor Admin, prints, PDF) | Pendente |
| 18/11 tarde | Equipe | VM Ubuntu: provisionamento + teste de falha + evidências; testar app no celular (Expo Go) | Pendente |
| 18/11 noite | Equipe | Gravar vídeos: IoT (4), Mobile (3), ML (5), OS (7), Cyber, Pitch (4) | Pendente |
| 19/11 até 18h | Equipe | Preencher links nos READMEs, ZIP de Cyber, revisão final, **envios no Teams** | Pendente |
| 19/11 18h–23h55 | Equipe | Margem de segurança | — |

## Divisão sugerida
| Integrante | Frentes |
|---|---|
| Guilherme Cezarino Simoes | GitHub, VM Linux (OS), backend/Swagger no vídeo, Cyber |
| Fabrini Soares | Wokwi (IoT), Azure DevOps (Testing), app no celular (Mobile), ML |
| Ambos | Conversa com morador, pitch, revisão final — cada um deve saber explicar o projeto inteiro |

## Riscos e mitigação
| Risco | Mitigação |
|---|---|
| Wokwi não alcança a API local | Demonstrar o circuito em modo offline (LEDs/LCD/Serial) + `simulador_payload.py`; opcional: `ngrok http 5080` |
| VM sem internet/pouca memória | 2 GB RAM, NAT; scripts idempotentes — rode de novo |
| Expo Go incompatível com o SDK | `npx expo start --web` como plano B (mostra o mesmo app) |
| Falta de tempo para vídeos | Roteiros cronometrados prontos em `docs/roteiros/` |
