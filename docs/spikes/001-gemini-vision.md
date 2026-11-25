# Spike 001 — Identificação de ingredientes por visão (S1 + S2)

- **Issues:** #4 (S1, Gemini) e #8 (S2, alternativas); os dois spikes foram
  feitos em conjunto, com as mesmas fotos e o mesmo script
- **Estado:** Concluído
- **Data de início / fim:** 2026-11-25 / 2026-11-25
- **Limite de tempo:** 4 h (S1) + 3 h (S2), dentro do limite

## Pergunta
Um modelo de visão gratuito identifica corretamente os ingredientes numa foto
real do frigorífico ou da despensa? O Gemini é a melhor opção, ou há uma
alternativa gratuita igual ou melhor?

## Critério de sucesso
- [ ] ≥ 80 % dos ingredientes visíveis identificados em 10–15 fotos reais
  → **71 %** no melhor modelo, com **7 fotos**
- [x] Tempo de resposta < 10 s por foto → **~2 s** típico no Gemini flash-lite
  (mas ver "Disponibilidade")
- [x] Limites do plano gratuito e política de uso de dados documentados
- [x] (S2) Pelo menos 1 alternativa testada com as mesmas fotos e o mesmo critério
- [x] (S2) Tabela comparativa: precisão, latência, limites, privacidade

## Abordagem
1. 7 fotos reais em `evals/photos/` (fora do git): armário de massas, despensa
   com pouca luz, prateleira de pacotes, prateleira do frigorífico, porta do
   frigorífico, vista geral do frigorífico e fruteira.
2. Anotação manual dos ingredientes esperados em
   [`spike-s1/expected.json`](../../spike-s1/expected.json), com sinónimos.
   Conteúdo de recipientes opacos fica de fora (não se adivinha).
3. Script descartável [`spike-s1/run.py`](../../spike-s1/run.py) (só biblioteca
   padrão do Python): envia cada foto a cada modelo, pede JSON
   `{"ingredients":[{"name","confidence"}]}` e calcula:
   - **acerto (recall):** % dos ingredientes esperados encontrados;
   - **extras:** itens devolvidos que não correspondem a nenhum esperado
     (revistos à mão: alguns existiam mesmo e foram acrescentados às anotações);
   - **latência** e **estado** (ok, indisponível, JSON inválido).
   Os pedidos com 429/5xx são repetidos até 3 vezes (5 s, 15 s, 30 s).
4. Modelos: Gemini API direta (`gemini-3.5-flash-lite`, `gemini-3.8-flash`) e
   OpenRouter gratuitos com visão (`google/gemma-4-31b-it:free`,
   `nvidia/nemotron-3.5-super-vl:free`). Temperatura 0.
5. Duas versões do prompt (ver [prompts.md](../ai/prompts.md)):
   - **v1:** "identifica os ingredientes visíveis";
   - **v2:** percorrer a foto por zonas, ler os rótulos das embalagens
     fechadas, ignorar o que não se come, não adivinhar recipientes opacos,
     nome genérico em vez de marca.

## Resultados

### Prompt v1 (4 modelos)
| Modelo | Respostas | Acerto médio | Latência típica | Extras |
|---|---|---|---|---|
| gemini-3.5-flash-lite | 7/7 | 64 % | ~2 s | 3 |
| gemini-3.8-flash | 0/7 | — | — | sempre 503 "high demand" |
| gemma-4-31b-it:free | 2/7 | 52 % | ~27 s | 1 (resto 429 do fornecedor) |
| nemotron-3.5-super-vl:free | 7/7 | 63 % | ~27 s | 5 |

### Prompt v2 (os dois modelos fiáveis)
| Modelo | Respostas | Acerto médio | Latência típica | Extras |
|---|---|---|---|---|
| **gemini-3.5-flash-lite** | 7/7 | **71 %** (v1: 64 %) | **~2,5 s** | 8 |
| nemotron-3.5-super-vl:free | 7/7 | 68 % (v1: 63 %) | ~37 s | **21** |

### Acerto por foto (flash-lite)
| Foto | v1 | v2 |
|---|---|---|
| 01 armário de massas | 50 % | 50 % |
| 02 despensa, pouca luz | 63 % | **88 %** |
| 03 prateleira de pacotes | 54 % | 54 % |
| 04 prateleira do frigorífico | 50 % | 67–83 % |
| 05 porta do frigorífico | 80 % | 80 % |
| 06 vista geral do frigorífico | 53 % | 60 % |
| 07 fruteira | 100 % | 100 % |

### Descobertas
- **O prompt conta.** Só a mudança de texto subiu o flash-lite 7 pontos; o
  maior ganho foi na despensa escura, por ler os rótulos.
- **Pedir "procura tudo" pode aumentar as invenções.** O Nemotron passou de 5
  para 21 extras com o v2 (pão, café, batata frita, mel…). O flash-lite
  manteve-se contido.
- **Onde todos falham:** embalagens fechadas sem leitura fácil (lasanha,
  natas de soja, aveia, cuscuz), itens pequenos numa vista geral (carne
  picada, bacon) e sobremesas em embalagens parecidas (mousse vs pudim).
- **Objetos com forma de alimento enganam:** um ambientador em forma de limão
  foi listado como "limão" por todos os modelos. Um medicamento na porta do
  frigorífico nunca foi listado (bom).
- **Muitos "extras" eram reais:** arroz, leite, azeite e fiambre existiam e
  não estavam anotados. A revisão manual dos extras é parte do processo de
  avaliação.
- **Variação entre corridas:** mesmo com temperatura 0, a foto 04 deu 83 %
  numa corrida e 67 % noutra. Com 7 fotos, diferenças de poucos pontos podem
  ser acaso.
- **Disponibilidade:**
  - `gemini-3.8-flash` esteve sempre indisponível (503) no plano gratuito.
  - `gemini-3.5-flash-lite` também deu 503 ocasionais: numa corrida falhou 2
    de 7 fotos e algumas fotos demoraram até ~1 min por causa das novas
    tentativas.
  - `gemma-4-31b-it:free` deu quase sempre 429 ("rate-limited upstream").
- **Comparação S2:** a alternativa fiável (Nemotron no OpenRouter) não é
  melhor que o Gemini flash-lite em acerto, é ~15× mais lenta e inventa mais.
  Groq e modelos no dispositivo não foram testados.
- **Jev (TypeSafe AI)** foi excluído: não recebe imagens.

## Limites e condições do plano gratuito
Consultado a 2026-11-25.

### Gemini API (Google AI Studio)
Fontes: [Rate limits](https://aistudio.google.com/docs/rate-limits),
[Termos](https://aistudio.google.com/docs/terms) (em vigor desde 2026-03-23).
- **Limites por projeto, não por chave**; o limite diário reinicia à
  meia-noite (hora do Pacífico). Os valores exatos do plano gratuito por modelo
  só aparecem na consola do AI Studio (página *Rate limit*), não na
  documentação pública. Valores vistos na consola a 2026-11-25:

  | Modelo | RPM | TPM | RPD | Uso no dia do spike |
  |---|---|---|---|---|
  | gemini-3.5-flash-lite | 15 | 250 000 | **500** | 48 pedidos, ~7 300 tokens/min no pico |
  | gemini-3.8-flash | 5 | 250 000 | 20 | 23/20 (limite diário ultrapassado) |

- ⚠️ **Os limites são partilhados por todos os utilizadores da app**, porque
  são por projeto. Com o flash-lite, a app inteira fica limitada a **500 fotos
  por dia** e 15 por minuto. Chega para desenvolvimento e para um grupo pequeno
  de testers; é um ponto a considerar no S5 (proteção da chave) e antes de
  publicar.
- Uma foto gasta poucos tokens face ao limite de 250 000/min: o limite que
  aperta é o número de pedidos, não os tokens.
- **Uso dos dados:** fora do EEE, o plano gratuito pode usar as fotos e
  respostas para melhorar os produtos da Google, com revisão humana. **No EEE,
  Suíça e Reino Unido** aplicam-se os termos de dados do plano pago a todo o
  uso: as fotos **não** são usadas para melhorar os produtos (ficam registadas
  por tempo limitado só para deteção de abuso).
- ⚠️ **Restrição para publicar:** os termos dizem que, para disponibilizar um
  cliente da API a utilizadores no EEE, Suíça ou Reino Unido, só se pode usar
  o plano pago. Para desenvolvimento e aprendizagem não há problema; **antes de
  publicar a app é preciso rever** (plano pago, outro fornecedor ou
  distribuição limitada).

### OpenRouter (modelos `:free`)
Fontes: [Limits](https://openrouter.ai/docs/api-reference/limits),
[FAQ](https://openrouter.ai/docs/faq).
- **20 pedidos/min**; **50 pedidos/dia**, ou **1000/dia** se a conta já
  comprou pelo menos 10 créditos (é o caso da conta usada).
- Os 429 podem vir do fornecedor por trás do modelo (capacidade esgotada),
  como aconteceu com o Gemma.
- O FAQ diz que os modelos gratuitos **geralmente não são adequados para
  produção**.
- Prompts e respostas não são registados por omissão. Fornecedores que treinam
  com os dados só são usados se o interruptor de treino nas definições de
  privacidade estiver ligado (deve ficar **desligado**).
- Chave do spike com limite de gasto de US$ 0.

## Conclusão
**Parcialmente.** O melhor modelo, `gemini-3.5-flash-lite` com o prompt v2,
identifica **~71 %** dos ingredientes em ~2 s, abaixo dos 80 % pedidos. Não há
alternativa gratuita melhor: o Nemotron no OpenRouter tem acerto parecido, mas
é muito mais lento e inventa mais.

A app é viável **porque o passo de revisão do utilizador já faz parte do MVP**
([vision.md](../vision.md)): o modelo dá um ponto de partida e o utilizador
corrige. Isto reforça que esse passo tem de ser rápido e fácil (destacar itens
com pouca confiança, adicionar o que falta).

Recomendações para os próximos passos:
- Usar o prompt v2 como ponto de partida; continuar a melhorá-lo no S3
  (structured output) com o mesmo script de avaliação.
- Tratar 503/429 na app (novas tentativas com espera e mensagem ao utilizador).
- Isolar o fornecedor de LLM atrás de uma interface, para poder trocar de
  modelo sem mexer no resto da app.
- Aumentar o conjunto para 10–15 fotos quando o processo de avaliação for
  formalizado (D21).
- Rever a restrição do EEE antes de publicar.

Decisão resultante: [ADR-009](../decisions.md#adr-009--modelo-de-visão-gemini-35-flash-lite-via-gemini-api)
(D11). D21 (avaliação da LLM) fica por decidir.
