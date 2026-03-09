from behave import given, when, then

# --- Lógica de Limpeza e Identificação ---
def identificar_status(valor_texto):
    valor = float(valor_texto.replace('.', '').replace(',', '.'))
    return "Crédito" if valor > 0 else "Débito"

@given('que recebo um valor de crédito de "{valor}"')
def step_recebe_credito(context, valor):
    context.valor_entrada = valor

@given('que recebo um valor de débito de "{valor}"')
def step_recebe_debito(context, valor):
    context.valor_entrada = valor

@when('o sistema processa a transação')
def step_processa_dados(context):
    context.resultado_status = identificar_status(context.valor_entrada)

@then('o status da transação deve ser "{status_esperado}"')
def step_valida_status(context, status_esperado):
    assert context.resultado_status == status_esperado

# --- Lógica de Fluxo de Conciliação (Interface) ---
@given('que existe uma transação pendente de "{tipo}" no valor de "{valor}"')
def step_prep_conciliacao(context, tipo, valor):
    context.transacao = {
        'tipo': tipo,
        'valor': float(valor.replace('.', '').replace(',', '.')),
        'status': 'Pendente'
    }
    context.total_conciliado = 0.0

@when('o usuário clica em conciliar a transação')
def step_clica_conciliar(context):
    context.transacao['status'] = 'Conciliado'
    context.total_conciliado += context.transacao['valor']

@then('o status de conciliação deve ser "{status_esperado}"')
def step_valida_conciliacao(context, status_esperado):
    assert context.transacao['status'] == status_esperado

@then('o valor deve ser somado ao total conciliado')
def step_valida_soma(context):
    assert context.total_conciliado > 0