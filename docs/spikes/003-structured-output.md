# Spike 003 — Structured output com JSON Schema

- **Issue:** #5
- **Estado:** Concluído
- **Data de início / fim:** 2026-11-25 / 2026-11-27
- **Limite de tempo:** 2 h (dentro do limite)

## Pergunta
O structured output (JSON Schema) do Gemini devolve JSON válido de forma
consistente?

## Critério de sucesso
- [x] 50 chamadas com o mesmo schema, 0 respostas que falhem a validação
  → **50/50 válidas**
- [x] Schema de ingredientes definido (nome, quantidade estimada, confiança)
  → [`spike-s3/schema.json`](../../spike-s3/schema.json)

## Abordagem
1. Schema da resposta ([`spike-s3/schema.json`](../../spike-s3/schema.json)):
   - `photoQuality`: `rating` (`good` | `poor`) e `reason` (texto curto), para
     a app pedir outra foto quando for má;
   - `ingredients[]`: `name`, `quantity` (`amount` > 0 e `unit`, uma de
     `unidade`, `g`, `kg`, `ml`, `l`, `embalagem`) e `confidence` (0–1);
   - sem campos extra (`additionalProperties: false`).
2. Script descartável [`spike-s3/run.py`](../../spike-s3/run.py), que
   reutiliza o do S1. Modelo `gemini-3.5-flash-lite` ([ADR-009](../decisions.md#adr-009--modelo-de-visão-gemini-35-flash-lite-via-gemini-api)),
   temperatura 0, prompt v2 do S1 acrescentado com as regras de quantidade e
   de qualidade da foto. Dois modos, com o mesmo prompt:
   - **prompt:** o formato vai só descrito no texto (+ `responseMimeType`
     JSON), como no S1;
   - **schema:** o mesmo, mais o schema enviado em `responseJsonSchema`.
3. 50 chamadas por modo, a percorrer as 7 fotos do S1, com intervalo de 4,5 s
   (limite de 15 pedidos/min).
4. Cada resposta é validada com o pacote `jsonschema` (Draft 2020-12): primeiro
   tem de ser JSON completo, depois tem de cumprir o schema.

## Resultados
| | Só prompt | Prompt + schema na API |
|---|---|---|
| Respostas recebidas | 49 (1 × 503) | 50 (1 × 503, compensada com 1 chamada extra) |
| **Respostas inválidas** | **3 (6 %)** | **0** |
| Acerto médio (recall) | 72 % | 64 % |
| Latência mediana | 2,1 s | 2,3 s |
| Fotos classificadas como `poor` | 0 | 0 |

### Descobertas
- **Sem schema, o modelo sai da lista de valores permitidos.** As 3 falhas
  foram todas a unidade `"frasco"`, que não existe no enum. O JSON em si
  estava sempre bem formado; o problema é o conteúdo dos campos.
- **Com schema, o formato é garantido.** A API aceitou o schema completo
  (`enum`, `exclusiveMinimum`, `additionalProperties`, `minLength`) sem erros.
- **O acerto desceu 8 pontos com o schema.** Restringir o formato pode
  prejudicar o conteúdo; parte da diferença também pode ser variação:
  - mesmo com temperatura 0, quase todas as chamadas à mesma foto deram
    respostas diferentes;
  - o acerto da mesma foto variou bastante (ex.: foto 01 entre 25 % e 50 % com
    schema; foto 04 entre 67 % e 100 % sem schema).
- **"embalagem" domina as quantidades:** 71 % dos itens com schema (216 de
  304). O modelo não sabe quanto há dentro de um pacote fechado. Para as
  calorias (S4), o utilizador terá de ajustar a quantidade na revisão (caixa
  de escolhas para a unidade).
- **`photoQuality` nunca foi `poor`**, nem para a despensa com pouca luz. O
  campo funciona em termos de formato, mas a sua utilidade **não foi
  validada**: falta testar com fotos más a propósito (tremidas, escuras, de
  longe).
- **Disponibilidade:** 2 em 101 pedidos deram 503 mesmo depois das novas
  tentativas (~1 min de espera cada).

## Limites e condições do plano gratuito
Os mesmos do S1 ([001-gemini-vision.md](001-gemini-vision.md)): 15 pedidos/min,
500 pedidos/dia por projeto. O structured output não tem custo nem limite
extra. Este spike usou ~103 pedidos.

## Conclusão
**Sim, com schema na API.** Com `responseJsonSchema`, 50 de 50 respostas
cumpriram o schema; só com o prompt, 6 % falharam. O preço é um acerto
possivelmente mais baixo, que passa a ser trabalho de prompt medido pelas
avaliações (D21).

Recomendações:
- Enviar sempre o schema na API **e** validar na app (defesa em
  profundidade: nunca confiar cegamente na resposta).
- Investigar a descida de acerto quando se definirem as avaliações (D21),
  com várias corridas por foto para separar variação de efeito real.
- Testar `photoQuality` com fotos más antes de o usar na app.

Decisão resultante: [ADR-010](../decisions.md#adr-010--formato-da-resposta-json-schema-na-api--validação-na-app) (D15).
