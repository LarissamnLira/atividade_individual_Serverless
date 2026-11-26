# Atividade Individual 1 — Serverless

**Função HTTP serverless que valida a compatibilidade sanguínea (ABO/Rh) de uma requisição do Rota Vital.**
Recebe `doador` e `receptor` e devolve se a transfusão é segura. É a mesma regra de negócio que nasceu de testes na Parte 1 (TDD), agora exposta como função.

- **Provedor:** AWS Lambda na nuvem.
- **Runtime:** Python 3.12.
- **Arquivo:** `lambda_function.py` · **Handler:** `lambda_function.lambda_handler`.

## O que a função faz

| Entrada (JSON) | Saída |
|---|---|
| `{ "doador": "O-", "receptor": "AB+" }` | `200` → `{"compativel": true, ...}` |
| `{ "doador": "A+", "receptor": "O+" }` | `200` → `{"compativel": false, "motivo": "incompativel no sistema ABO/Rh"}` |
| `{ "doador": "X9", ... }` | `400` → `{"erro": "..."}` |
| `{ ..., "demorar": true }` | dorme 5s (para o experimento de timeout) |

A resposta inclui `invocacaoNesteAmbiente`, um contador em **variável global** usado para observar o reaproveitamento do ambiente de execução.

## Como rodar (AWS Lambda — Caminho B)

> Antes: crie um **alerta de orçamento** (AWS Budgets) de poucos dólares. Ao terminar, **apague a Function URL e a função**. A faixa sempre gratuita do Lambda (1M requisições + 400k GB-s/mês) cobre este teste.

1. **Criar a função** — console do Lambda → *Create function* → *Author from scratch* → runtime **Python 3.12**. Cole o conteúdo de `lambda_function.py` no editor e *Deploy*.
2. **Timeout inicial** — *Configuration → General configuration → Edit* → **Timeout = 3s** (para o experimento do Passo 5).
3. **Testar com evento** — aba *Test* → cole o conteúdo de `events/pedido.json` → *Test*. Deve retornar `201/200` com o resultado. **Rode duas vezes** e anote a *Duration* de cada uma.
4. **Gatilho HTTP (Function URL)** — *Configuration → Function URL → Create* → Auth type **NONE** (só durante o teste). Depois, no terminal:
   ```bash
   curl -X POST "<FUNCTION_URL>" -H "Content-Type: application/json" \
     -d '{"requisicaoId":"R-002","doador":"O-","receptor":"AB+"}'
   ```
   Rode **3 vezes** e observe o campo `invocacaoNesteAmbiente`.
5. **Bater no limite de tempo** — chame com `events/pedido-demorar.json` (`"demorar": true`). A função dorme 5s e **estoura o Timeout de 3s** → registre o erro. Depois aumente o **Timeout para 10s**, *Deploy* e repita: agora funciona.
6. **Cold start** — em *Monitor → View CloudWatch logs*, abra um log e veja o **Init Duration** (fase de inicialização) e a **Duration**.
7. **Limpeza** — apague a Function URL e a função.

## Perguntas (respostas)

**1. Por que a primeira invocação demorou mais que a segunda? O que acontece na fase de Init?**
Na primeira chamada ocorre um *cold start*: a AWS provisiona um ambiente de execução novo, baixa o código, inicia o runtime Python e só então roda o handler — isso é a fase de **Init** (aparece como *Init Duration* no CloudWatch). Na segunda chamada, o ambiente já está "quente" e é reaproveitado, pulando o Init; por isso é mais rápida.

**2. O que o campo `invocacaoNesteAmbiente` mostrou com e sem reaproveitamento? O que isso diz sobre guardar estado numa variável global?**
Em chamadas seguidas e rápidas, o ambiente é reaproveitado e o contador **cresce** (1, 2, 3...), porque a variável global sobrevive. Quando ocorre um *cold start* (ambiente novo — após ociosidade, novo deploy, ou escalonamento em paralelo), o contador **volta a 1**. Conclusão: **não se pode confiar em variável global para guardar estado** entre invocações; o estado tem que ir para fora (banco, cache, fila). *(No Caminho A local, o equivalente é rodar `sam local start-api` com e sem `--warm-containers LAZY`.)*

**3. O que aconteceu com `demorar = true`? Qual é o tempo máximo de uma execução no Lambda, e o que fazer com um trabalho mais longo?**
A função dormiu 5s e foi **encerrada pelo Timeout de 3s** (erro `Task timed out`). O tempo máximo de uma execução no Lambda é **15 minutos**. Para trabalho mais longo, não se usa uma única função síncrona: quebra-se o processo (ex.: **Step Functions** para orquestrar etapas), processa-se de forma **assíncrona por fila** (SQS) ou move-se a carga para um serviço sempre ligado (container).

**4. Custo de 1 milhão de execuções com 128 MB e 100 ms (preços us-east-1 da aula).**
- **Requisições:** 1.000.000 × US$ 0,20 / 1.000.000 = **US$ 0,20**.
- **Computação:** memória = 128/1024 = 0,125 GB; por execução = 0,125 × 0,1 s = 0,0125 GB-s; total = 0,0125 × 1.000.000 = **12.500 GB-s**; custo = 12.500 × US$ 0,0000166667 = **US$ 0,2083**.
- **Total ≈ US$ 0,41/mês.** Descontando a faixa sempre gratuita (1M requisições + 400k GB-s), este volume fica **dentro do grátis**, custo efetivo ~US$ 0,00. O valor acima é o custo "cheio", sem o free tier.

**5. Em que parte do Rota Vital uma função assim faria sentido, e em qual não faria?**
A validação de compatibilidade é **pura e sem estado**, então tecnicamente é amigável a serverless — e faria sentido como função **acionada por evento** (ex.: emitir a guia de transporte quando uma requisição é atendida, ou processar leituras de telemetria em rajada). Onde **não** faria sentido: no **caminho crítico do Atendimento em tempo real** — uma decisão à vida do paciente não deveria pagar o custo de um *cold start*, e o acesso ao banco em alto volume sofre com o limite de conexões e com *connection storms* típicos de serverless. Para esse caminho, mantém-se um serviço sempre ligado. Resumo: serverless para o que é eventual, stateless e tolerante a latência; serviço contínuo para o caminho crítico e com muitas conexões de banco.

## Uso de IA (PO-CESAR-021 — permitido com declaração)

- **Ferramenta:** Claude (assistente de IA).
- **Finalidade:** rascunhar o código da função (regra ABO/Rh reaproveitada da Parte 1), os eventos de teste, a estrutura do README e a conta de custo.
- **Validação:** executei a função localmente conferindo os casos (O-→AB+ compatível; A+→O+ e O+→O- incompatíveis; tipo inválido → 400); os experimentos de cold start, estado global e timeout foram rodados por mim na AWS e registrados em `evidencias/`. A conta de custo foi refeita à mão.
