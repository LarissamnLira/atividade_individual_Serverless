# Evidências — Serverless (SAM CLI local)

Função serverless que valida a compatibilidade ABO/Rh de uma requisição do Rota Vital, executada localmente com o AWS SAM CLI.

## E1 — Build

- [x] `sam build` concluído com sucesso.
![Build Succeeded](img/01-sam-build.png)

## E2 — Invocação com evento

- [x] `sam local invoke` retornando `200` com `"compativel": true` e o campo `invocacaoNesteAmbiente`. A primeira invocação é mais lenta (cold start / construção da imagem); a seguinte reaproveita o ambiente.
![Invocação 1](img/02-invoke-2x_1.png)
![Invocação 2](img/02-invoke-2x_2.png)

## E3 — Gatilho HTTP sem reaproveitamento

- [x] `sam local start-api` + `curl` 3x **sem** `--warm-containers`: o campo `invocacaoNesteAmbiente` fica **sempre 1** — cada chamada roda num container novo e descartável.
![curl sem warm 1](img/03-curl-sem-warm_1.png)
![curl sem warm 2](img/03-curl-sem-warm_2.png)

## E4 — Gatilho HTTP com reaproveitamento

- [x] `sam local start-api --warm-containers LAZY` + `curl` 3x: o `invocacaoNesteAmbiente` cresce **1 → 2 → 3** — o container é reaproveitado e a variável global sobrevive. Prova que não se pode confiar em estado numa variável global.
![curl com warm 1](img/04-curl-com-warm_1.png)
![curl com warm 2](img/04-curl-com-warm_2.png)

## E5 — Limite de tempo (timeout)

- [x] Com `Timeout: 3` no `template.yaml`, o evento `pedido-demorar.json` (dorme 5s) é cortado: **"timed out after 3 seconds"**.
![Timeout de 3s](img/05-timeout-erro.png)

## E6 — Timeout ajustado

- [x] Após mudar o `Timeout` para `10` e refazer o `sam build`, a mesma chamada roda os 5s e retorna `200` (Duration ~5222 ms).
![Timeout 10s funcionando](img/06-timeout-ok.png)

---

**Vídeo (até 3 min):** invocação com evento + chamada por HTTP (curl) + erro de tempo limite.
![Vídeo](video/video_atvd_serveless.mp4)