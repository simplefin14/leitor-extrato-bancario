# language: pt
Funcionalidade: Processamento e Conciliação de Extrato

  # --- Regras de Transformação de Dados ---
  Cenário: Identificar um crédito corretamente
    Dado que recebo um valor de crédito de "1.500,00"
    Quando o sistema processa a transação
    Então o status da transação deve ser "Crédito"

  Cenário: Identificar um débito corretamente
    Dado que recebo um valor de débito de "50,00"
    Quando o sistema processa a transação
    Então o status da transação deve ser "Débito"

  # --- Regras de Negócio da Interface ---
  Cenário: Mover transação para conciliados
    Dado que existe uma transação pendente de "Crédito" no valor de "1.500,00"
    Quando o usuário clica em conciliar a transação
    Então o status de conciliação deve ser "Conciliado"
    E o valor deve ser somado ao total conciliado