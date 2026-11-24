# Convenções

## Idioma
| O quê | Idioma |
|---|---|
| Documentação, issues, PRs | Português (PT-PT) |
| Código (classes, funções, variáveis, comentários no código) | Inglês |
| Mensagens de commit | Inglês |

## Commits — Conventional Commits
Formato: `tipo(âmbito opcional): descrição no imperativo`

| Tipo | Uso |
|---|---|
| `feat` | Nova funcionalidade |
| `fix` | Correção de bug |
| `docs` | Só documentação |
| `test` | Testes |
| `refactor` | Alteração sem mudar comportamento |
| `build` | Gradle, dependências |
| `ci` | GitHub Actions |
| `chore` | Manutenção geral |
| `spike` | Código exploratório de um spike |

Exemplos: `docs: add ADR for LLM provider`, `feat(scan): add photo picker`.
Referenciar a issue no corpo ou no PR (`Refs #12`, `Closes #12`).

## Branches
`tipo/NN-descricao-curta`, onde `NN` é o número da issue.
Exemplos: `docs/3-project-structure`, `spike/5-gemini-vision`, `feat/12-photo-picker`.

## Código Kotlin
A definir com as decisões D4–D7 e D18 (ex.: ktlint/detekt). Até lá, seguir as
[convenções oficiais do Kotlin](https://kotlinlang.org/docs/coding-conventions.html).
