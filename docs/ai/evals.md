# Avaliação da LLM (evals)

Como medimos se a identificação de ingredientes e as receitas são boas o
suficiente, de forma repetível.

> A detalhar no spike S1 e na decisão D21.

## Ideia geral
- Um conjunto fixo de fotos de teste, cada uma com a lista de ingredientes
  esperados.
- Um script corre o prompt em todas as fotos e calcula métricas
  (ex.: percentagem de ingredientes certos, ingredientes inventados, JSON válido).
- Corre-se sempre que o prompt ou o modelo mudam.

## Privacidade
As fotos ficam em `evals/photos/`, **ignorada pelo git** (repositório público).
No repositório só ficam os ficheiros de resultados esperados, sem imagens.
