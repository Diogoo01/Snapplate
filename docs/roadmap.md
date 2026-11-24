# Roadmap

Sem prazo fixo. As fases avançam quando os critérios de saída são cumpridos.

## Fase 0 — Fundação *(concluída)*
- [x] Estrutura de pastas e documentação
- [x] Repositório git local
- [x] Repositório público no GitHub
- [x] Spike S10 — GitHub Issues e Projects
- [x] Templates de issue e board do projeto
- [x] Decisão da licença (ADR-004: sem licença por agora)

**Saída:** repositório no GitHub com as primeiras issues criadas.

## Fase 1 — Spikes e decisões *(atual)*
Ordem sugerida: S7 → S1 → S3 → S5 → S4 → S2 → S6 → S8 (S9 em paralelo).
Fechar as decisões D4–D21 à medida que os spikes concluem.

**Saída:** todas as decisões necessárias ao MVP aceites; `architecture.md` e
primeiro diagrama atualizados.

## Fase 2 — Esqueleto da app
- Projeto Android criado com a stack escolhida
- CI no GitHub Actions (build, testes unitários, lint) com proteção da `main`
- Skills e subagentes iniciais do Claude Code

**Saída:** app "vazia" a compilar e CI verde em cada PR.

## Fase 3 — MVP
1. Foto (captura/escolha)
2. Identificação e revisão de ingredientes
3. Receitas com calorias por dose

**Saída:** fluxo completo a funcionar num telemóvel real.

## Depois do MVP (por priorizar)
Diário de refeições · Favoritos · Código de barras · Sincronização na cloud
