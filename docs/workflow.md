# Fluxo de trabalho

## Ciclo de uma task
1. **Issue** — criada a partir do template (task, spike ou bug), com
   critério de aceitação.
2. **Branch** — a partir da `main`: `tipo/NN-descricao`.
3. **Trabalho** — commits pequenos (Conventional Commits).
4. **PR** — descrição com `Closes #NN` e checklist do critério de aceitação.
5. **CI** — build, testes unitários e lint têm de passar.
6. **Revisão** — o utilizador revê o diff e aprova por escrito (ex.: "aprovado")
   (no futuro, também um subagente revisor).
7. **Merge** — o Claude faz squash merge na `main` e apaga a branch, só depois
   da aprovação explícita desse PR (ADR-007). A issue fecha e passa a *Done*
   no board automaticamente.

## Decisões
Sempre que surge uma escolha técnica: 2–3 opções com prós e contras →
recomendação → escolha do utilizador → ADR em [decisions.md](decisions.md).

## Spikes
Para tecnologias desconhecidas. Usar o [template](spikes/_template.md):
pergunta, limite de tempo, critério de sucesso, resultado, conclusão.
O código de um spike é descartável e não entra na app tal como está.

## Definition of Done
Uma task está concluída quando:
- [ ] Os critérios de aceitação da issue estão cumpridos
- [ ] O CI está verde
- [ ] Há testes para a lógica nova (quando aplicável)
- [ ] A documentação afetada foi atualizada (ADR, arquitetura, roadmap)
- [ ] Nenhum segredo nem foto pessoal foi commitado
- [ ] O PR foi aprovado e integrado na `main`
