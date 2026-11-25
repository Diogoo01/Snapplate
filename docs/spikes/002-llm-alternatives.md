# Spike 002 — Alternativas ao Gemini

- **Issue:** #8
- **Estado:** Concluído (feito em conjunto com o S1)
- **Data de início / fim:** 2026-11-25 / 2026-11-25
- **Limite de tempo:** 3 h

O S2 foi feito em conjunto com o S1, com as mesmas fotos, o mesmo script e o
mesmo critério. Os resultados completos, a tabela comparativa e os limites de
cada plano gratuito estão em [001-gemini-vision.md](001-gemini-vision.md).

## Resumo
| Fornecedor / modelo | Acerto (prompt v2) | Latência típica | Disponibilidade | Privacidade |
|---|---|---|---|---|
| Gemini API — gemini-3.5-flash-lite | 71 % | ~2,5 s | 503 ocasionais | No EEE: dados não usados para melhorar produtos |
| OpenRouter — nemotron-3.5-super-vl:free | 68 % (21 extras) | ~37 s | Fiável no teste | Sem registo por omissão; depende do fornecedor |
| OpenRouter — gemma-4-31b-it:free | 52 % (v1, 2 fotos) | ~27 s | Quase sempre 429 | Idem |

Não testados: Groq e modelos no dispositivo.

## Conclusão
Nenhuma alternativa gratuita testada é melhor que o Gemini flash-lite. O
OpenRouter fica como alternativa possível, atrás da mesma interface, mas o
próprio FAQ diz que os modelos gratuitos não são adequados para produção.
Decisão resultante: [ADR-009](../decisions.md#adr-009--modelo-de-visão-gemini-35-flash-lite-via-gemini-api).
