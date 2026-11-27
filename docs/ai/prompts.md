# Prompts da LLM

Prompts versionados usados pela app. Cada alteração relevante a um prompt
deve ser acompanhada de uma nova execução das avaliações ([evals.md](evals.md)).

> O prompt das receitas depende ainda de D13 (spike S4). Abaixo, as versões do
> prompt de identificação, da mais recente para a mais antiga.

### identify-ingredients — v3 (spike S3)
- **Objetivo:** como a v2, mais quantidade estimada e qualidade da foto.
- **Modelo:** `gemini-3.5-flash-lite`, temperatura 0.
- **Entrada:** uma foto (JPEG).
- **Formato de saída (schema):** [`spike-s3/schema.json`](../../spike-s3/schema.json), enviado em `responseJsonSchema` ([ADR-010](../decisions.md#adr-010--formato-da-resposta-json-schema-na-api--validação-na-app)).
- **Texto do prompt:** `PROMPT` em [`spike-s3/run.py`](../../spike-s3/run.py).
- **Resultado das avaliações:** 50/50 respostas válidas; acerto médio 64 % (72 % sem schema) ([spike 003](../spikes/003-structured-output.md)).
- **Alterações face à v2:** regras para `quantity` (número + unidade de uma lista fixa) e para `photoQuality`; schema na API.

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
