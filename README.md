📊 Leitor de Extrato & Conciliação Bancária Interativa
Este projeto nasceu da necessidade de transformar extratos bancários brutos (CSV) em uma interface de conciliação fluida, visual e eficiente. Desenvolvido com Python e Streamlit, o app permite que o usuário gerencie transações financeiras através de cards interativos.

🚀 Funcionalidades Atuais
Upload Dinâmico: Leitura de arquivos CSV com tratamento automático de encoding (ISO-8859-1/UTF-8).

Limpeza de Dados Pro: Conversão automática de valores monetários no padrão brasileiro (ex: 1.500,00) para formato computacional.

Interface Kanban: Divisão de transações entre "Pendentes" e "Conciliados" com movimentação em um clique.

Soma em Tempo Real: Cálculo instantâneo do saldo dos itens conciliados através de gerenciamento de estado (Session State).

Visual Premium: Cards grandes com indicadores visuais de Crédito (Verde) e Débito (Vermelho).

🛠️ Tecnologias Utilizadas
Python 3.10+

Pandas: Manipulação e limpeza de dados.

Streamlit: Framework para a interface web responsiva.

Git/GitHub: Versionamento e controle de histórico.

📈 Evolução do Projeto (Iterações)

V1: Script básico de leitura e tratamento de erro de encoding.
Implementação de testes BDD e Gherkin para validar a categorização de transações.
Interface Streamlit simples para visualização das transações em tabela.

V2: Refatoração completa para UX baseada em Cards e fluxo de trabalho Pendente/Conciliado e interface Streamlit com tabela de dados e métricas.

📦 Como executar
Clone o repositório:
git clone https://github.com/SEU_USUARIO/NOME_DO_REPOSITORIO.git

Instale as dependências:
pip install -r requirements.txt

Execute o app:
streamlit run código/app.py
