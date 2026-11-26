# Evidências — Serverless (AWS Lambda)

Capturar os prints abaixo (o enunciado exige evidência de cada item):

- [ ] Função criada no console do Lambda (Python 3.12) — `01-funcao-criada.png`
- [ ] Aba **Test** com o evento `pedido.json` retornando 200 + a guia/compatibilidade — `02-test-evento.png`
- [ ] **Duas invocações** com os tempos (Duration) anotados — `03-duas-invocacoes.png`
- [ ] **Function URL** criada — `04-function-url.png`
- [ ] Chamada por **curl** na Function URL (rodar 3x, mostrando `invocacaoNesteAmbiente` crescendo) — `05-curl-http.png`
- [ ] `demorar=true` estourando o **Timeout de 3s** (erro) — `06-timeout-erro.png`
- [ ] Após subir o Timeout para 10s, a mesma chamada funcionando — `07-timeout-ok.png`
- [ ] Log do **CloudWatch** mostrando **Init Duration** (cold start) e **Duration** — `08-cloudwatch-init.png`

Vídeo (até 3 min, gravação de tela): invocação com evento + chamada por HTTP + erro de tempo limite.
