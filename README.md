# Atividade Individual 1 — Serverless (Rota Vital)

**Função serverless que valida a compatibilidade sanguínea (ABO/Rh) de uma requisição do Rota Vital.**
Recebe `doador` e `receptor` e devolve se a transfusão é segura — a mesma regra que nasceu de testes na Parte 1 (TDD), agora como função serverless.

- **Caminho:** A - AWS SAM CLI **local** (roda na máquina, sem conta/cartão).
- **Runtime:** Python 3.12.
- **Função:** `compatibilidade/app.py` · **Handler:** `app.lambda_handler`.

## Pré-requisitos
- Docker Desktop rodando.
- AWS SAM CLI (`sam --version`).
- Python 3.12.
- No Windows, rodar os comandos no **Git Bash** ou **WSL** (por causa das barras `\` nos comandos).

## Como rodar

**1. Build**
```bash
sam build
```

**2. Invocar com um evento (Passo 3)** - rodar DUAS vezes e anotar o tempo:
```bash
sam local invoke -e events/pedido.json
sam local invoke -e events/pedido.json
```

**3. Acionar por HTTP (Passo 4)**
```bash
sam local start-api
# em outro terminal, 3 vezes:
curl -X POST http://127.0.0.1:3000/compatibilidade -H "Content-Type: application/json" \
  -d '{"requisicaoId":"R-002","doador":"O-","receptor":"AB+"}'
```
Observe o campo `invocacaoNesteAmbiente`. Pare o servidor (Ctrl+C), suba de novo com reaproveitamento e repita:
```bash
sam local start-api --warm-containers LAZY
```
Anote a diferença no `invocacaoNesteAmbiente`.

**4. Bater no limite de tempo (Passo 5)**
```bash
sam local invoke -e events/pedido-demorar.json
```
A função dorme 5s, mas o `Timeout` do `template.yaml` é 3s → erro de timeout. Depois **mude `Timeout: 3` para `Timeout: 10`** no `template.yaml`, rode `sam build` e repita: agora funciona.

## O que a função faz

| Entrada (JSON) | Saída |
|---|---|
| `{ "doador": "O-", "receptor": "AB+" }` | `{"compativel": true, ...}` |
| `{ "doador": "A+", "receptor": "O+" }` | `{"compativel": false, "motivo": "incompativel no sistema ABO/Rh"}` |
| `{ "doador": "X9", ... }` | `400` → `{"erro": "..."}` |
| `{ ..., "demorar": true }` | dorme 5s (experimento de timeout) |

## Perguntas (respostas)

**1. Por que a primeira invocação demorou mais que a segunda? O que acontece na fase de Init?**
Na primeira chamada há um *cold start*: o SAM sobe um container novo, inicia o runtime Python e carrega o código antes de rodar o handler — essa preparação é a fase de **Init**. Na segunda, o ambiente já está pronto e é reaproveitado, então pula o Init e responde mais rápido.

**2. O que `invocacaoNesteAmbiente` mostrou com e sem `--warm-containers`? O que isso diz sobre variável global?**
**Sem** `--warm-containers`, cada chamada cria um container novo e descartável, então o contador fica **sempre 1**. **Com** `--warm-containers LAZY`, o container é reaproveitado e o contador **cresce** (1, 2, 3...). Conclusão: **não dá para confiar em variável global para guardar estado** entre invocações — o ambiente pode ser recriado a qualquer momento. Estado tem que ir para fora (banco, cache, fila).

**3. O que aconteceu com `demorar = true`? Qual o tempo máximo no Lambda, e o que fazer com trabalho mais longo?**
A função dormiu 5s e foi **interrompida pelo Timeout de 3s** (erro). Na AWS, o tempo máximo de uma execução do Lambda é **15 minutos**. Para trabalho mais longo: quebrar o processo com **Step Functions**, processar **assíncrono por fila** (SQS), ou mover para um serviço sempre ligado (container).

**4. Custo de 1 milhão de execuções com 128 MB e 100 ms (preços us-east-1 da aula).**
- **Requisições:** 1.000.000 × US$ 0,20 / 1.000.000 = **US$ 0,20**.
- **Computação:** 128/1024 = 0,125 GB; por execução 0,125 × 0,1 s = 0,0125 GB-s; total 0,0125 × 1.000.000 = **12.500 GB-s**; × US$ 0,0000166667 = **US$ 0,2083**.
- **Total ≈ US$ 0,41/mês** (bruto). Com a faixa sempre gratuita (1M requisições + 400k GB-s), este volume fica **dentro do grátis** → custo efetivo ~US$ 0,00.

**5. Em que parte do Rota Vital uma função assim faria sentido, e em qual não faria?**
A validação de compatibilidade é **pura e sem estado**, logo é amigável a serverless, faria sentido como função **acionada por evento** (emitir a guia de transporte quando uma requisição é atendida, ou processar leituras de telemetria em rajada). Onde **não** faria sentido: no **caminho crítico do Atendimento em tempo real**, uma decisão à vida do paciente não deveria pagar o custo de um *cold start*, e o acesso ao banco em alto volume sofre com o limite de conexões típico de serverless. Nesse caminho, mantém-se um serviço sempre ligado. Em resumo: serverless para o eventual, stateless e tolerante a latência; serviço contínuo para o caminho crítico e com muitas conexões de banco.

## Uso de IA
- **Ferramenta:** Claude (assistente de IA).
- **Finalidade:** rascunhar o código da função (regra ABO/Rh reaproveitada da Parte 1), o `template.yaml`, os eventos de teste, o README e a conta de custo.
- **Validação:** executei a função localmente conferindo os casos (O-→AB+ compatível; A+→O+ e O+→O- incompatíveis; inválido → 400); os experimentos de cold start, estado com/sem `--warm-containers` e timeout foram rodados por mim com o SAM e registrados em `evidencias/`. A conta de custo foi refeita à mão.
