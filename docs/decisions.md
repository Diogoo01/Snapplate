# Registo de decisões (ADR)

Cada decisão importante fica registada aqui. Uma decisão não se apaga: se
mudar, cria-se uma nova ADR que a **substitui** e a antiga passa a
`Substituída por ADR-NNN`.

**Estados:** `Proposta` · `Aceite` · `Rejeitada` · `Substituída`

## Índice
| ADR | Título | Estado | Data |
|---|---|---|---|
| [001](#adr-001--gestão-de-tasks-no-github-issues--projects) | Gestão de tasks no GitHub Issues + Projects | Aceite | 2026-11-24 |
| [002](#adr-002--estratégia-de-branches-github-flow) | Estratégia de branches: GitHub Flow | Aceite | 2026-11-24 |
| [003](#adr-003--repositório-público) | Repositório público | Aceite | 2026-11-24 |
| [004](#adr-004--sem-licença-por-agora) | Sem licença (por agora) | Aceite | 2026-11-24 |
| [005](#adr-005--fins-de-linha-lf-em-todo-o-repositório) | Fins de linha LF em todo o repositório | Aceite | 2026-11-24 |
| [006](#adr-006--ambiente-de-desenvolvimento-android-studio--claude-code) | Ambiente de desenvolvimento: Android Studio + Claude Code | Aceite | 2026-11-24 |
| [007](#adr-007--política-de-merge-o-claude-faz-merge-após-aprovação-explícita) | Política de merge: o Claude faz merge após aprovação explícita | Aceite | 2026-11-24 |
| [008](#adr-008--ci-um-único-job-gradle-no-github-actions) | CI: um único job Gradle no GitHub Actions | Aceite | 2026-11-24 |
| [009](#adr-009--modelo-de-visão-gemini-35-flash-lite-via-gemini-api) | Modelo de visão: Gemini 3.5 Flash-Lite via Gemini API | Aceite | 2026-11-25 |

## Decisões por tomar
| ID | Decisão | Depende de |
|---|---|---|
| D4 | UI (Compose vs Views) | — |
| D5 | Arquitetura da app | — |
| D6 | Modularização | — |
| D7 | Injeção de dependências | — |
| D8 | Rede e serialização | D11 |
| D9 | Captura de imagem | S6 |
| D10 | Persistência | — |
| D12 | Backend / proteção da chave | S5 |
| D13 | Origem das receitas | S4 |
| D14 | Cálculo de calorias | S4 |
| D15 | Formato da resposta da LLM | S3 |
| D16 | Testes unitários | — |
| D17 | Testes de UI | S8 |
| D18 | Lint e formatação | — |
| D20 | Atualização de dependências | — |
| D21 | Avaliação da LLM (evals) | S1 |
| D-DIAG | Ferramenta de diagramas | — |

---

## Modelo

```markdown
## ADR-NNN — Título
- **Estado:** Proposta | Aceite | Rejeitada | Substituída por ADR-NNN
- **Data:** AAAA-MM-DD
- **Spike relacionado:** docs/spikes/NNN-nome.md (se existir)

### Contexto
Que problema ou necessidade obriga a decidir.

### Opções consideradas
1. **Opção A** — prós / contras
2. **Opção B** — prós / contras

### Decisão
Opção escolhida e porquê.

### Consequências
O que muda, o que fica mais fácil, que custos ou riscos aceitamos.
```

---

## ADR-001 — Gestão de tasks no GitHub Issues + Projects
- **Estado:** Aceite
- **Data:** 2026-11-24
- **Spike relacionado:** S10 (familiarização com GitHub Issues e Projects)

### Contexto
O trabalho é dividido em tasks pequenas com critério de aceitação e feito
task a task. É preciso um sítio para as guardar e acompanhar.

### Opções consideradas
1. **GitHub Issues + Projects** — padrão da indústria; liga issues a PRs
   (`Closes #N`); templates; board kanban; acessível ao Claude Code via `gh`.
   Contra: fora do repositório, precisa de rede.
2. **TASKS.md no repositório** — simples, versionado, offline. Contra: não
   liga a PRs, difícil de gerir à medida que cresce.
3. **Ambos** — TASKS.md como índice. Contra: duplicação e risco de dessincronizar.

### Decisão
**GitHub Issues + Projects.** O utilizador já conhece o equivalente no GitLab;
um spike curto (S10) valida o fluxo no GitHub.

### Consequências
- Templates de issue em `.github/ISSUE_TEMPLATE/` (task, spike, bug).
- O Claude Code precisa do GitHub CLI (`gh`) instalado e autenticado.
- Spikes têm uma issue **e** um ficheiro em `docs/spikes/` com a conclusão.

---

## ADR-002 — Estratégia de branches: GitHub Flow
- **Estado:** Aceite
- **Data:** 2026-11-24

### Contexto
Queremos que o CI valide o trabalho antes de integrar.

### Opções consideradas
1. **GitHub Flow** — `main` sempre estável; branches curtas por task; merge
   via PR com CI verde. Contra: um pouco mais de cerimónia a solo.
2. **Trunk-based com commits diretos na `main`** — mais rápido. Contra: o CI
   só corre depois de integrar, contrariando o objetivo.

### Decisão
**GitHub Flow.**

### Consequências
- Uma branch e um PR por task; nome `tipo/NN-descricao` (ver
  [conventions.md](conventions.md)).
- Proteção da `main` (PR obrigatório + checks do CI) a configurar quando o CI existir.

---

## ADR-003 — Repositório público
- **Estado:** Aceite
- **Data:** 2026-11-24

### Contexto
O GitHub Actions tem minutos limitados em repositórios privados e as builds
Android são pesadas. O projeto é de aprendizagem.

### Opções consideradas
1. **Público** — minutos de CI ilimitados; secret scanning, push protection e
   CodeQL grátis; serve de portefólio. Contra: código e histórico visíveis;
   risco de expor segredos.
2. **Privado** — código fechado. Contra: limite mensal de minutos; passar a
   público mais tarde expõe todo o histórico.

### Decisão
**Público desde o início**, com mitigações ativas antes do primeiro push.

### Consequências
- `.gitignore` exclui `local.properties`, keystores, `.env`, `google-services.json`
  (até decisão do S5) e `evals/photos/`.
- Segredos do CI só em GitHub Secrets.
- Secret scanning e push protection ativos no repositório.
- Fotos pessoais nunca vão para o repositório.
- A licença é tratada na ADR-004.

---

## ADR-004 — Sem licença (por agora)
- **Estado:** Aceite
- **Data:** 2026-11-24

### Contexto
O repositório é público (ADR-003). Sem ficheiro `LICENSE`, o código fica com
todos os direitos reservados: pode ser visto, mas não copiado nem reutilizado.

### Opções consideradas
1. **Sem licença** — opção por omissão; o autor mantém todos os direitos.
   Contra: ninguém pode reutilizar o código legalmente.
2. **MIT** — permissiva e a mais comum; só exige manter a atribuição.
   Contra: qualquer pessoa pode reutilizar, incluindo comercialmente.
3. **Apache-2.0** — como a MIT, com cláusula explícita de patentes.
   Contra: mais longa; pouco relevante para um projeto pessoal.

### Decisão
**Sem licença por agora.** Pode ser revista a qualquer momento acrescentando
um ficheiro `LICENSE` (nova ADR que substitui esta).

### Consequências
- Não se cria ficheiro `LICENSE`; o repositório é criado sem licença.

---

## ADR-005 — Fins de linha LF em todo o repositório
- **Estado:** Aceite
- **Data:** 2026-11-24
- **Issue:** #2

### Contexto
O desenvolvimento é feito em Windows (CRLF) e o CI corre em Linux (LF). Scripts
como o `gradlew` falham com CRLF, e o git mostra avisos LF/CRLF a cada commit.

### Opções consideradas
1. **Tudo em LF** (`* text=auto eol=lf`, exceto `.bat`/`.cmd` em CRLF) — disco,
   repositório e CI iguais; acaba com os avisos. Contra: programas Windows muito
   antigos podem mostrar mal ficheiros LF.
2. **Nativo por sistema** (`* text=auto` + exceções para scripts) — CRLF no
   Windows. Contra: disco ≠ repositório; avisos continuam; cada script novo
   precisa de exceção.
3. **Mínima** (só `gradlew` em LF + binários) — simples. Contra: não resolve os
   avisos nem garante consistência.

### Decisão
**Tudo em LF** (opção 1), via `.gitattributes`.

### Consequências
- O `.gitattributes` na raiz define as regras, incluindo ficheiros binários.
- Ficheiros novos ficam em LF no disco, mesmo em Windows.

---

## ADR-006 — Ambiente de desenvolvimento: Android Studio + Claude Code
- **Estado:** Aceite
- **Data:** 2026-11-24
- **Issue:** #13

### Contexto
É preciso escolher onde se escreve, corre e depura a app, e que assistentes de
IA se usam, sem custos e sem duplicar ferramentas.

### Opções consideradas
1. **Android Studio + Claude Code** — IDE oficial para Android (emulador,
   previews do Compose, debugger, Gradle); um único agente de IA; o Claude Code
   tem extensão para IDEs JetBrains. Contra: dois programas abertos.
2. **Opção 1 + Gemini in Android Studio** — autocomplete e ajuda contextual
   gratuitos. Contra: dois assistentes de IA.
3. **Cursor para editar + Android Studio para correr** — ferramenta popular.
   Contra: dois editores e dois agentes; suporte fraco a Kotlin/Android;
   limites do plano gratuito.

### Decisão
**Android Studio + Claude Code.**

### Consequências
- O Android Studio é o IDE para correr, depurar e ver previews.
- O Claude Code é o único agente de IA que altera código no projeto.
- Revisitável se surgir interesse em comparar outras ferramentas (via spike).

---

## ADR-007 — Política de merge: o Claude faz merge após aprovação explícita
- **Estado:** Aceite
- **Data:** 2026-11-24
- **Issue:** #13

### Contexto
Com o GitHub Flow (ADR-002), cada task termina num PR. A trabalhar a solo, o
GitHub não permite que o autor aprove o próprio PR, por isso uma regra de
"aprovação obrigatória" na `main` não é utilizável.

### Opções consideradas
1. **O utilizador faz sempre o merge** no GitHub — controlo total. Contra:
   trabalho manual repetido.
2. **O Claude faz o merge após aprovação explícita do utilizador em cada PR**
   — o utilizador continua a rever e a decidir; o merge é automático.
   Contra: a revisão do diff continua a ser necessária (e desejável).
3. **Auto-merge do GitHub** quando o CI passa — padrão em equipas com CI forte.
   Contra: sem CI ainda não tem efeito; o CI passa a ser a única barreira.

### Decisão
**Opção 2 agora.** Quando existir CI forte (depois do spike S7, #3), rever para
a opção 3 ou uma combinação (CI verde obrigatório + aprovação em chat).

### Consequências
- O Claude só corre `gh pr merge --squash --delete-branch` depois de o
  utilizador escrever explicitamente que aprova **aquele** PR. Uma aprovação
  não vale para outros PRs.
- Merge sempre em *squash*; a branch é apagada.
- Quando o CI existir, a proteção da `main` exige os checks verdes.

---

## ADR-008 — CI: um único job Gradle no GitHub Actions
- **Estado:** Aceite
- **Data:** 2026-11-24
- **Spike relacionado:** [docs/spikes/007-github-actions-ci.md](spikes/007-github-actions-ci.md) (#3)

### Contexto
O spike S7 mostrou que um CI Android (build + testes unitários + lint) demora
~1 min 20 s com cache e é gratuito num repositório público. Falta decidir a
forma do workflow definitivo (decisão D19).

### Opções consideradas
1. **Um job, uma invocação do Gradle**
   (`./gradlew assembleDebug testDebugUnitTest lintDebug`) — mais simples e
   mais rápido no total (uma configuração e um restauro de cache). Contra:
   um só check no PR; é preciso ver o log para saber que passo falhou.
2. **Três jobs paralelos** (build, testes, lint) — checks separados no PR.
   Contra: cada job restaura ~600 MB de cache e configura o Gradle; mais
   lento no total para um projeto pequeno; mais complexo.

### Decisão
**Um único job** (opção 1). Rever para jobs paralelos se o build ficar lento.

### Consequências
- O workflow corre em `pull_request` **e** em `push` na `main` (só a `main`
  grava a cache do Gradle; os PRs reutilizam-na em modo só de leitura).
- JDK igual ao `toolchainVersion` de `gradle/gradle-daemon-jvm.properties`.
- `gradlew` com permissão de execução no git.
- A proteção da `main` passa a exigir este check verde.
- O workflow é criado na Fase 2, com o projeto Android definitivo; nessa altura
  revê-se a ADR-007 (auto-merge).

---

## ADR-009 — Modelo de visão: Gemini 3.5 Flash-Lite via Gemini API
- **Estado:** Aceite
- **Data:** 2026-11-25
- **Spike relacionado:** [docs/spikes/001-gemini-vision.md](spikes/001-gemini-vision.md)
  (#4) e [002-llm-alternatives.md](spikes/002-llm-alternatives.md) (#8)

### Contexto
A app precisa de um modelo de visão gratuito que identifique os ingredientes
numa foto (decisão D11). Os spikes S1 e S2 compararam quatro modelos com 7
fotos reais e duas versões do prompt.

### Opções consideradas
1. **`gemini-3.5-flash-lite` via Gemini API** — melhor acerto (71 %), ~2 s por
   foto, poucas invenções; no EEE as fotos não são usadas para melhorar os
   produtos. Contra: 503 ocasionais no plano gratuito; os termos exigem o
   plano pago para disponibilizar a app a utilizadores no EEE.
2. **`nvidia/nemotron-3.5-super-vl:free` via OpenRouter** — sempre disponível
   no teste; acerto parecido (68 %). Contra: 25–40 s por foto; inventa mais
   (21 extras com o prompt v2); 50–1000 pedidos/dia; o OpenRouter diz que os
   modelos gratuitos não são para produção.
3. **Modelos maiores (`gemini-3.8-flash`, `gemma-4-31b-it:free`)** — Contra:
   quase sempre indisponíveis (503/429) no plano gratuito.

### Decisão
**`gemini-3.5-flash-lite` via Gemini API** (opção 1), com o prompt v2 como
ponto de partida.

### Consequências
- O acerto (~71 %) fica abaixo do objetivo de 80 %: o passo de revisão do
  utilizador é essencial e tem de ser rápido (destacar pouca confiança,
  adicionar o que falta).
- O fornecedor de LLM fica isolado atrás de uma interface na app, para se
  poder trocar de modelo (ex.: OpenRouter) sem mexer no resto.
- A app trata 503/429 com novas tentativas com espera e uma mensagem clara.
- A proteção da chave depende do S5 (Firebase AI Logic / D12).
- Os limites gratuitos são por projeto e partilhados por todos os
  utilizadores: **15 pedidos/min e 500 pedidos/dia** (1 foto = 1 pedido).
  Suficiente para desenvolvimento e testers; a rever antes de publicar.
- **Risco aceite:** antes de publicar para utilizadores no EEE é preciso rever
  a restrição dos termos (plano pago, outro fornecedor ou distribuição
  limitada). Para desenvolvimento e aprendizagem, o plano gratuito serve.
- O prompt continua a ser melhorado no S3, medido com o mesmo script.
