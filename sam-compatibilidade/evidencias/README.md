# Evidências — Serverless (SAM CLI local)

Capturar os prints:

- [ ] `sam build` concluído — `01-sam-build.png`
- [ ] `sam local invoke` com o evento, rodado **2 vezes**, tempos anotados — `02-invoke-2x.png`
- [ ] `sam local start-api` no ar + `curl` 3x (sem --warm-containers): `invocacaoNesteAmbiente` sempre 1 — `03-curl-sem-warm.png`
- [ ] `sam local start-api --warm-containers LAZY` + `curl` 3x: contador cresce (1,2,3) — `04-curl-com-warm.png`
- [ ] `demorar:true` estourando o Timeout de 3s (erro) — `05-timeout-erro.png`
- [ ] Após Timeout=10 no template.yaml + `sam build`, a mesma chamada funcionando — `06-timeout-ok.png`

Vídeo (até 3 min): invocação com evento + chamada por HTTP (curl) + erro de tempo limite.
