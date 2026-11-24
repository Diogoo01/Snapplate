# Spike 010 — GitHub Issues e Projects

- **Issue:** #1
- **Estado:** Concluído
- **Data de início / fim:** 2026-11-24 / 2026-11-24
- **Limite de tempo:** 1 h (não cronometrado; feito ao longo da sessão de arranque)

## Pergunta
O fluxo GitHub Issues + Projects funciona bem para nós, vindo do GitLab?

## Critério de sucesso
- [x] Uma task pequena percorre o fluxo completo: issue → branch → PR →
  `Closes #N` → merge → issue fechada automaticamente
- [x] O board do Projects mostra a issue a mover-se entre colunas
  (Todo → In Progress → Done)
- [x] Diferenças face ao GitLab que importam estão anotadas

## Abordagem
1. Criar labels (`task`, `spike`, `decision`), milestones (Fase 0, Fase 1) e
   templates de issue/PR.
2. Criar o board "Snapplate" no GitHub Projects e ligá-lo ao repositório.
3. Fazer duas tasks reais pelo fluxo do [workflow.md](../workflow.md):
   #2 (`.gitattributes`, PR #12) e #13 (ADR-006/007, PR #14).

## Resultados
- O fluxo completo funcionou nas duas tasks: `Closes #N` fechou a issue no
  merge e a automação do Projects moveu-a para **Done** sem intervenção.
- O utilizador criou a vista **Board** e viu as issues a mudar de coluna.
- Opinião do utilizador: o conceito é o mesmo do GitLab; a interface do GitLab
  é um pouco mais intuitiva para iniciantes.

### Diferenças face ao GitLab que importam
| Tema | GitHub | GitLab |
|---|---|---|
| Board | **GitHub Projects** pertence ao utilizador/organização e liga-se a repositórios; abre em vista de tabela, a vista Board cria-se à parte | Issue Boards pertencem ao projeto e existem por omissão |
| Automação do board | *Workflows* do Projects (ex.: issue fechada → Done) já ativos | Baseada em labels/listas do board |
| Fechar issues | `Closes #N` no PR | `Closes #N` no MR (igual) |
| Aprovar o próprio PR | **Não é permitido** — afeta regras de proteção a solo (ver ADR-007) | Configurável |
| CLI | `gh`; Projects exige o scope extra `project` (`gh auth refresh -s project`) | `glab` |

### Fricções encontradas (já resolvidas)
- Depois de instalar o `gh` foi preciso abrir um terminal novo (PATH).
- O `git push` ficava à espera do Git Credential Manager; resolve-se com
  `gh auth setup-git` ou usando o `gh` como credential helper.

## Limites e condições do plano gratuito
Issues, Projects, labels, milestones e templates são gratuitos em
repositórios públicos.

## Conclusão
**Sim, o fluxo funciona.** Mantém-se a ADR-001 (GitHub Issues + Projects) sem
alterações ao [workflow.md](../workflow.md). Os passos manuais repetidos em
cada task (ler a issue, criar a branch, mover no board, abrir o PR, fazer o
merge e confirmar o fecho) são candidatos ao skill `/task` no spike S9 (#11).
