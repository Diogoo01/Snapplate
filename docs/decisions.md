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
| D11 | LLM para identificar ingredientes | S1, S2 |
| D12 | Backend / proteção da chave | S5 |
| D13 | Origem das receitas | S4 |
| D14 | Cálculo de calorias | S4 |
| D15 | Formato da resposta da LLM | S3 |
| D16 | Testes unitários | — |
| D17 | Testes de UI | S8 |
| D18 | Lint e formatação | — |
| D19 | Detalhes do CI | S7 |
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
