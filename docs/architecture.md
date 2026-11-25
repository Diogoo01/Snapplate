# Arquitetura

> Documento vivo. Só descreve o que já foi **decidido** (ver
> [decisions.md](decisions.md)). O que está por decidir aparece marcado.

## Fluxo principal (conceptual)

```
Foto ──► Identificação de ingredientes (LLM) ──► Revisão pelo utilizador
                                                        │
                                                        ▼
            Calorias por dose ◄── Receitas ◄── Ingredientes confirmados
```

## Componentes
| Componente | Responsabilidade | Estado |
|---|---|---|
| App Android | UI, captura de foto, revisão, apresentação de receitas | Stack por decidir (D4–D10) |
| Integração LLM | Identificar ingredientes e gerar receitas | Identificação: Gemini 3.5 Flash-Lite ([ADR-009](decisions.md#adr-009--modelo-de-visão-gemini-35-flash-lite-via-gemini-api)); receitas e formato por decidir (D13, D15) |
| Backend / proteção da chave | Evitar chave da API exposta na app | Por decidir (D12) — spike S5 |
| Dados nutricionais | Calcular calorias por dose | Por decidir (D14) — spike S4 |

## Diagramas
A criar em [diagrams/](diagrams/) depois dos spikes S1 e S5.
