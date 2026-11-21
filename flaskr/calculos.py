
from flask import Blueprint, render_template, request


bp = Blueprint("calculos", __name__)


def calcular_irpf(salario):
    # Tabela mensal do IRPF de 2026
    base = max(0, salario - 607.20)

    if base <= 2428.80:
        imposto = 0
    elif base <= 2826.65:
        imposto = base * 0.075 - 182.16
    elif base <= 3751.05:
        imposto = base * 0.15 - 394.16
    elif base <= 4664.68:
        imposto = base * 0.225 - 675.49
    else:
        imposto = base * 0.275 - 908.73

    # Redução adicional válida em 2026
    if salario <= 5000:
        reducao = 312.89
    elif salario <= 7350:
        reducao = 978.62 - (0.133145 * salario)
    else:
        reducao = 0

    imposto = max(0, imposto - reducao)

    return round(imposto, 2)


def calcular_decimo_terceiro(salario, meses):
    return round((salario / 12) * meses, 2)



@bp.route("/painel", methods=("GET", "POST"))
def painel():
    irpf = None
    decimo_terceiro = None
    erro = None

    if request.method == "POST":
        try:
            tipo = request.form.get("tipo")
            salario = float(
                request.form.get("salario", "0").replace(",", ".")
            )

            if salario <= 0:
                raise ValueError("Informe um salário válido.")

            if tipo == "irpf":
                irpf = calcular_irpf(salario)

            elif tipo == "decimo":
                meses = int(request.form.get("meses", "0"))

                if meses < 0 or meses > 12:
                    raise ValueError("Os meses devem estar entre 0 e 12.")

                decimo_terceiro = calcular_decimo_terceiro(
                    salario, meses
                )

            else:
                raise ValueError("Tipo de cálculo inválido.")

        except ValueError as e:
            erro = str(e) or "Preencha os campos corretamente."

    return render_template(
        "calculos/index.html",
        irpf=irpf,
        decimo_terceiro=decimo_terceiro,
        erro=erro
    )

