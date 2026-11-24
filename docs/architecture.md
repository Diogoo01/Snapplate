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
| Integração LLM | Identificar ingredientes e gerar receitas | Por decidir (D11, D13, D15) — spikes S1–S3 |
| Backend / proteção da chave | Evitar chave da API exposta na app | Por decidir (D12) — spike S5 |
| Dados nutricionais | Calcular calorias por dose | Por decidir (D14) — spike S4 |

## Diagramas
A criar em [diagrams/](diagrams/) depois dos spikes S1 e S5.
