import json
import time

# Variavel global: so SOBREVIVE entre chamadas se a AWS reaproveitar o mesmo
# ambiente de execucao. Em um cold start ela volta a 0. E o que o experimento
# do campo "invocacaoNesteAmbiente" demonstra.
invocacoes_neste_ambiente = 0


# ---------------------------------------------------------------------------
# Regra de negocio do Rota Vital: compatibilidade sanguinea ABO/Rh (hemacias).
# Mesma regra que nasceu de testes na Parte 1 (TDD).
# ---------------------------------------------------------------------------
TIPOS_VALIDOS = {"A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"}


def _grupo_abo(tipo):
    return tipo.rstrip("+-")


def _is_positivo(tipo):
    return tipo.endswith("+")


def compativel(doador, receptor):
    abo_doador = _grupo_abo(doador)
    abo_receptor = _grupo_abo(receptor)
    abo_ok = {
        "O": True,                                    # doador universal (ABO)
        "A": abo_receptor in ("A", "AB"),
        "B": abo_receptor in ("B", "AB"),
        "AB": abo_receptor == "AB",                   # AB so doa para AB
    }[abo_doador]
    # Rh: doador Rh+ nao pode doar para receptor Rh-.
    rh_ok = not (_is_positivo(doador) and not _is_positivo(receptor))
    return abo_ok and rh_ok


# ---------------------------------------------------------------------------
# Handler da funcao Lambda.
# ---------------------------------------------------------------------------
def lambda_handler(event, context):
    global invocacoes_neste_ambiente
    invocacoes_neste_ambiente += 1

    # A Function URL / API Gateway entregam o payload dentro de "body".
    # O botao Test do console entrega o objeto JSON direto como event.
    if isinstance(event, dict) and "body" in event:
        pedido = json.loads(event.get("body") or "{}")
    else:
        pedido = event or {}

    # Experimento do limite de tempo (Passo 5): dorme 5s e estoura o Timeout de 3s.
    if pedido.get("demorar"):
        time.sleep(5)

    doador = pedido.get("doador")
    receptor = pedido.get("receptor")
    if doador not in TIPOS_VALIDOS or receptor not in TIPOS_VALIDOS:
        return {
            "statusCode": 400,
            "body": json.dumps(
                {"erro": "informe 'doador' e 'receptor' validos, ex.: O-, AB+"}
            ),
        }

    ok = compativel(doador, receptor)
    resposta = {
        "requisicaoId": pedido.get("requisicaoId"),
        "doador": doador,
        "receptor": receptor,
        "compativel": ok,
        "motivo": "compativel" if ok else "incompativel no sistema ABO/Rh",
        "invocacaoNesteAmbiente": invocacoes_neste_ambiente,
    }
    return {"statusCode": 200, "body": json.dumps(resposta)}
