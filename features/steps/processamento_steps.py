from behave import given, when, then

def identificar_status(valor_texto):
    # Converte para float tratando a pontuação brasileira
    valor = float(valor_texto.replace('.', '').replace(',', '.'))
    return "Crédito" if valor > 0 else "Débito"

@given('que recebo um valor de crédito de "{valor}"')
def step_given_credito(context, valor):
    context.valor_testado = valor

@given('que recebo um valor de débito de "{valor}"') # Adicionamos este step para o débito
def step_given_debito(context, valor):
    context.valor_testado = valor # Aqui passamos o valor como positivo, mas a lógica de débito no seu CSV pode ser diferente

@when('o sistema processa a transação')
def step_when_processa(context):
    context.resultado = identificar_status(context.valor_testado)

@then('o status da transação deve ser "{status_esperado}"')
def step_then_conferir(context, status_esperado):
    # O assert falha se o resultado for diferente do esperado
    assert context.resultado == status_esperado, f"Erro: esperado {status_esperado}, mas veio {context.resultado}"