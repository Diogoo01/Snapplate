# Spike 007 — CI Android no GitHub Actions

- **Issue:** #3
- **Estado:** Concluído
- **Data de início / fim:** 2026-11-24 / 2026-11-24
- **Limite de tempo:** 2 h (dentro do limite)

## Pergunta
Quanto tempo demora (e quanto custa) um CI Android no GitHub Actions?

## Critério de sucesso
- [x] Pipeline com build + testes unitários + lint num projeto Android "hello world"
- [x] Duração < 10 min com cache do Gradle → **1 min 18 s**
- [x] Limites do plano gratuito para repositórios públicos confirmados

## Abordagem
1. Projeto *Empty Activity* (Compose) criado no Android Studio em `spike-ci/`
   (AGP 9.4.1, Gradle 9.6.0, Kotlin 2.2.10, compileSdk 37, toolchain do daemon JDK 25).
2. Workflow com `actions/checkout@v7`, `actions/setup-java@v6` (Temurin 25),
   `gradle/actions/setup-gradle@v6` e três passos: `assembleDebug`,
   `testDebugUnitTest`, `lintDebug`.
3. Quatro execuções em `ubuntu-latest` para comparar com e sem cache.

## Resultados

| Execução | Cache | Total | Build | Testes | Lint |
|---|---|---|---|---|---|
| 1 (push) | Nenhuma | 3 min 08 s | 2 min 26 s | 6 s | 25 s |
| 2 (manual) | Nenhuma (só leitura, ver abaixo) | 3 min 36 s | 2 min 45 s | 7 s | 28 s |
| 3 (push) | Nenhuma; grava 606 MB | 3 min 05 s | — | — | — |
| 4 (manual) | **Restaurada (606 MB, 6 s)** | **1 min 18 s** | 34 s | 3 s | 18 s |

A cache reduz o tempo em cerca de **60 %**.

### Descobertas
- **A cache só é gravada a partir da `main`.** Por omissão, o `setup-gradle`
  fica em modo só de leitura nas outras branches. Isto é intencional: os PRs
  reutilizam a cache da `main` sem a "poluírem". No spike foi preciso
  `cache-read-only: false` para medir o efeito.
  Consequência para o projeto real: **o CI tem de correr também em push na
  `main`** para a cache se manter atualizada.
- **JDK 25:** o Android Studio gerou `gradle/gradle-daemon-jvm.properties`
  com `toolchainVersion=25`. O CI tem de usar a mesma versão (ou o Gradle
  descarrega-a sozinho, mais lento).
- **`gradlew` sem permissão de execução** quando criado no Windows: foi
  preciso `git update-index --chmod=+x gradlew`.
- **Três invocações do Gradle** repetem a fase de configuração; numa só
  (`./gradlew assembleDebug testDebugUnitTest lintDebug`) o tempo deve descer
  um pouco (não medido).

## Limites e condições do plano gratuito
Fonte: [GitHub Docs — GitHub Actions billing](https://docs.github.com/en/billing/concepts/product-billing/github-actions)
(consultada a 2026-11-24).
- **Repositórios públicos:** runners standard (ex.: `ubuntu-latest`) são
  **gratuitos** e não contam para a quota incluída.
- **Cache:** 10 GB por repositório. Este projeto usa ~0,6 GB.
- **Artefactos (privados):** 500 MB no plano Free. Os relatórios do spike
  ficam 7 dias.
- Para comparação, em repositórios privados o plano Free inclui o equivalente a
  US$ 12/mês (cerca de 2000 min em Linux), o que dava para ~600 execuções
  com cache.

## Conclusão
**Sim, compensa.** Um CI Android com build, testes e lint demora ~1 min 20 s
com cache e é gratuito num repositório público. O workflow de referência está
abaixo. O código do spike (`spike-ci/` e `spike-ci.yml`) **não entra na
`main`**: o CI definitivo é criado na Fase 2, com o projeto real, segundo a
decisão D19.

### Workflow de referência usado no spike
```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    timeout-minutes: 30
    steps:
      - uses: actions/checkout@v7
      - uses: actions/setup-java@v6
        with:
          distribution: temurin
          java-version: "25"
      - uses: gradle/actions/setup-gradle@v6
      - run: ./gradlew assembleDebug
      - run: ./gradlew testDebugUnitTest
      - run: ./gradlew lintDebug
      - uses: actions/upload-artifact@v7
        if: always()
        with:
          name: reports
          path: app/build/reports/
          retention-days: 7
```

Decisão resultante: [ADR-008](../decisions.md#adr-008--ci-um-único-job-gradle-no-github-actions) (um único job Gradle).
