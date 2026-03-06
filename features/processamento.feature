# language: pt
Funcionalidade: Processar extrato bancário

  Cenário: Identificar um crédito corretamente
    Dado que recebo um valor de crédito de "1.500,00"
    Quando o sistema processa a transação
    Então o status da transação deve ser "Crédito"

  Cenário: Identificar um débito corretamente
    Dado que recebo um valor de débito de "50,00"
    Quando o sistema processa a transação
    Então o status da transação deve ser "Débito"