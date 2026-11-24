# CLAUDE.md — Snapplate

Instruções para o Claude Code neste repositório. O contexto do produto está em
[docs/vision.md](docs/vision.md); aqui ficam as regras de trabalho.

## O projeto em uma linha
App Android (Kotlin) que transforma uma foto do frigorífico/despensa em ideias
de refeições com calorias por dose. Projeto a solo, de aprendizagem
(prioridade: **aprender > lançar rápido**), com orçamento **zero**.

## Regras obrigatórias
1. **Não tomar decisões técnicas sozinho.** Propor 2–3 opções com prós e
   contras, recomendar uma e esperar pela escolha do utilizador.
2. **Registar cada decisão** em [docs/decisions.md](docs/decisions.md) (formato ADR).
3. **Nada de funcionalidades sem aprovação.** Trabalhamos task a task
   (GitHub Issues); cada task tem critério de aceitação.
4. **Tecnologias desconhecidas passam por um spike** primeiro
   ([docs/spikes/](docs/spikes/)): pergunta, limite de tempo, critério de
   sucesso, conclusão.
5. **Só serviços com plano gratuito** utilizável sem pagar. Confirmar limites
   e condições (incluindo uso de dados) nos spikes.
6. **Propor ferramentas atuais da indústria**; sugerir skills/subagentes só
   onde acrescentam valor.

## Idioma
- Documentação, issues e PRs: **português (PT-PT)**.
- Código (classes, funções, variáveis) e mensagens de commit: **inglês**.

## Segurança (repositório público)
- Nunca commitar chaves, tokens, `local.properties`, keystores ou
  ficheiros de configuração com segredos. Segredos do CI vão para GitHub Secrets.
- Fotos reais usadas em avaliações da LLM ficam em `evals/photos/`
  (ignorada pelo git) — nunca no repositório.

## Fluxo de trabalho
Ver [docs/workflow.md](docs/workflow.md). Resumo: issue → branch
`tipo/NN-descricao` → commits (Conventional Commits) → PR com `Closes #NN`
→ CI verde → merge na `main`.

## Mapa da documentação
| Ficheiro | Conteúdo |
|---|---|
| [docs/vision.md](docs/vision.md) | Produto, MVP e fora do MVP |
| [docs/architecture.md](docs/architecture.md) | Arquitetura (preenchida à medida que se decide) |
| [docs/decisions.md](docs/decisions.md) | Registo de decisões (ADR) |
| [docs/roadmap.md](docs/roadmap.md) | Fases e próximos passos |
| [docs/conventions.md](docs/conventions.md) | Convenções de código, commits e branches |
| [docs/workflow.md](docs/workflow.md) | Como trabalhamos e Definition of Done |
| [docs/ai/](docs/ai/) | Prompts e avaliação da LLM |
| [docs/spikes/](docs/spikes/) | Spikes e respetivas conclusões |
| [docs/diagrams/](docs/diagrams/) | Diagramas |

## Estado atual
Fase 0 — Fundação. Ainda **não existe código Android**; a stack técnica está
por decidir (ver decisões "Propostas" em `docs/decisions.md`).
