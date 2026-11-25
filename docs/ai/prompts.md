# Prompts da LLM

Prompts versionados usados pela app. Cada alteração relevante a um prompt
deve ser acompanhada de uma nova execução das avaliações ([evals.md](evals.md)).

> Prompts definitivos dependem ainda de D13 e D15 (spikes S3–S4). Abaixo, o
> prompt de identificação usado no spike S1, ponto de partida para a app.

### identify-ingredients — v2 (spike S1)
- **Objetivo:** listar os alimentos e bebidas numa foto de frigorífico/despensa.
- **Modelo:** `gemini-3.5-flash-lite` ([ADR-009](../decisions.md#adr-009--modelo-de-visão-gemini-35-flash-lite-via-gemini-api)), temperatura 0.
- **Entrada:** uma foto (JPEG).
- **Formato de saída:** `{"ingredients": [{"name": string, "confidence": 0..1}]}`
  (pedido no texto + `responseMimeType: application/json`; schema formal no S3).
- **Texto do prompt:** `PROMPTS["v2"]` em [`spike-s1/run.py`](../../spike-s1/run.py).
- **Resultado das avaliações:** 71 % de acerto em 7 fotos, ~2,5 s
  ([spike 001](../spikes/001-gemini-vision.md)).
- **Alterações face à v1:** percorrer a foto por zonas, ler rótulos de
  embalagens fechadas, ignorar o que não se come, não adivinhar recipientes
  opacos, nome genérico em vez de marca (v1: 64 %).

## Modelo de entrada
```markdown
### <nome-do-prompt> — vN
- **Objetivo:**
- **Modelo:**
- **Entrada:**
- **Formato de saída (schema):**
- **Texto do prompt:**
- **Resultado das avaliações:**
- **Alterações face à versão anterior:**
```
