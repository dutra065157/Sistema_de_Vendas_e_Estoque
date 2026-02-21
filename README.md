# Graça Presentes 🎁

Sistema de Ponto de Venda (PDV) e Gestão de Estoque desenvolvido em Python utilizando o framework Flet. O sistema foi projetado para gerenciar vendas, controlar estoque e fornecer relatórios visuais para uma loja de presentes.

## 🚀 Funcionalidades

### 📊 Dashboard e Relatórios

- **Resumo de Vendas:** Total vendido, quantidade de vendas e ticket médio.
- **Gráficos Interativos:**
  - Distribuição por forma de pagamento (Pizza).
  - Evolução de vendas por período (Linha).
  - Produtos mais vendidos (Barras).
  - Visualização de estoque crítico.
- **Relatório Diário:** Consulta detalhada de vendas por data específica.

### 📦 Gestão de Estoque

- **Cadastro de Produtos:** Inclusão de nome, preço, quantidade, categoria, descrição e imagem.
- **Edição e Exclusão:** Gerenciamento completo do ciclo de vida do produto.
- **Busca:** Pesquisa rápida de produtos com visualização de imagem.

### 🛒 Frente de Caixa (PDV)

- **Carrinho de Compras:** Adição dinâmica de itens e cálculo de subtotal.
- **Checkout:**
  - Cálculo automático de troco (para pagamentos em dinheiro).
  - Suporte a Cartão (Débito/Crédito com parcelas) e PIX.
- **Comprovantes:**
  - Geração de texto para impressão.
  - **QR Code** para compartilhamento rápido.
  - Integração direta para envio via **WhatsApp**.

## 🛠️ Tecnologias Utilizadas

- **Linguagem:** Python 3.x
- **Interface Gráfica (GUI):** [Flet](https://flet.dev/) (Baseado em Flutter)
- **Banco de Dados:** SQLite3
- **Manipulação de Dados:** Pandas
- **Utilitários:** QRCode, Base64, Webbrowser

## ⚙️ Instalação e Execução

### Pré-requisitos

Certifique-se de ter o Python instalado em sua máquina.

1. **Clone o repositório:**

   ```bash
   git clone https://github.com/seu-usuario/graca-presentes.git
   cd pacoteflet
   ```

2. **Crie um ambiente virtual (Opcional, mas recomendado):**

   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Instale as dependências:**

   ```bash
   pip install flet pandas qrcode pillow
   ```

4. **Execute a aplicação:**
   ```bash
   python app.py
   ```

## 📦 Criando o Executável (.exe)

O projeto já inclui um arquivo de especificação (`spec.py`) para o PyInstaller. Para gerar um executável standalone para Windows:

1. Instale o PyInstaller:

   ```bash
   pip install pyinstaller
   ```

2. Execute o build usando o arquivo de especificação:

   ```bash
   pyinstaller spec.py
   ```

3. O executável será gerado na pasta `dist/Graça_Presentes`.

## 📂 Estrutura do Projeto

- `app.py`: Arquivo principal contendo a lógica da interface, navegação e eventos.
- `database.py`: Camada de persistência (SQLite), queries e logs de erro.
- `relatorio.py`: Componentes visuais dos gráficos e lógica de dashboards.
- `spec.py`: Configuração de build para o PyInstaller.

=======

> > > > > > > 72367cf482d8edcbe790f7113f26b8eb7f7dd0d8

## 🛍️ GRAÇA PRESENTES - Sistema de Vendas e Estoque

**🚀 _Sistema integrado com back-end e frontend mobile (Flet)_**

<p align="center">
   <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white">
   <img src="https://img.shields.io/badge/Flet-0078D4?style=for-the-badge&logo=flutter&logoColor=white">
   <img src="https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white">
   <img src="https://img.shields.io/badge/Desktop-APP-4ECDC4?style=for-the-badge">
   <img src="https://img.shields.io/badge/Windows-0078D6?style=for-the-badge&logo=windows&logoColor=white">

# <<<<<<< HEAD

> > > > > > > 72367cf482d8edcbe790f7113f26b8eb7f7dd0d8

</p>

🌟 SOBRE O PROJETO
O GRAÇA PRESENTES é um sistema desktop desenvolvido em Python com interface estilo mobile para gerenciamento completo de uma loja de presentes. O sistema oferece controle de vendas, estoque, cadastro de produtos e relatórios detalhados em uma interface otimizada para uso em computadores.

### 🎯 CARACTERÍSTICAS PRINCIPAIS

<<<<<<< HEAD
🖥️ APLICATIVO DESKTOP

    💰 SISTEMA COMPLETO DE VENDAS

    📊 CONTROLE DE ESTOQUE EM TEMPO REAL

    📈 DASHBOARD COM ANALYTICS

    🏷️ CADASTRO DE PRODUTOS COM IMAGENS

=======
🖥️ APLICATIVO DESKTOP

    💰 SISTEMA COMPLETO DE VENDAS

    📊 CONTROLE DE ESTOQUE EM TEMPO REAL

    📈 DASHBOARD COM ANALYTICS

    🏷️ CADASTRO DE PRODUTOS COM IMAGENS


> > > > > > > 72367cf482d8edcbe790f7113f26b8eb7f7dd0d8

    📋 RELATÓRIOS DETALHADOS

### 🛠️ TECNOLOGIAS UTILIZADAS

     Python	Linguagem principal

<<<<<<< HEAD

     Flet Framework para interface

     Pandas	Análise e processamento de dados

     PyInstaller Empacotamento para desktop

=======

     Flet Framework para interface

     Pandas	Análise e processamento de dados

     PyInstaller Empacotamento para desktop

> > > > > > > 72367cf482d8edcbe790f7113f26b8eb7f7dd0d8

### 🎯TELAS DO SISTEMA

![Tela do App](assets/Captura%20de%20tela%202025-10-19%20003701.png)

<<<<<<< HEAD
🛒 Sistema de Vendas
Carrinho de Compras com seleção de produtos, Cálculo automático de valores e totais, Sistema de troco para pagamento em dinheiro,
Finalização de compra com atualização automática do estoque

💰 FINALIZAÇÃO DE VENDA

![Tela do App](assets/Captura%20de%20tela%202025-10-19%20003842.png)

# 📝 CADASTRO DE PRODUTOS

🛒 Sistema de Vendas
Carrinho de Compras com seleção de produtos, Cálculo automático de valores e totais, Sistema de troco para pagamento em dinheiro,
Finalização de compra com atualização automática do estoque

💰 FINALIZAÇÃO DE VENDA

![Tela do App](assets/Captura%20de%20tela%202025-10-19%20003842.png)

📝 CADASTRO DE PRODUTOS

> > > > > > > 72367cf482d8edcbe790f7113f26b8eb7f7dd0d8

![Tela do App](assets/Captura%20de%20tela%202025-10-19%20004036.png)

Cadastro completo de produtos (código, nome, preço, estoque, categoria), Busca e seleção de produtos
Exibição de imagens dos produtos, Listagem de produtos cadastrados

<<<<<<< HEAD
📈 RELATÓRIOS

![Tela do App](assets/Captura%20de%20tela%202025-10-19%20004215.png)

📊 RELATÓRIOS

![Tela do App](assets/Captura%20de%20tela%202025-10-19%20004301.png)

📈 RELATÓRIOS POR DATA

![Tela do App](assets/Captura%20de%20tela%202025-10-19%20004504.png)

# 📈 RELATÓRIOS

📈 RELATÓRIOS

![Tela do App](assets/Captura%20de%20tela%202025-10-19%20004215.png)

📊 RELATÓRIOS

![Tela do App](assets/Captura%20de%20tela%202025-10-19%20004301.png)

📈 RELATÓRIOS POR DATA

![Tela do App](assets/Captura%20de%20tela%202025-10-19%20004504.png)

📈 RELATÓRIOS

> > > > > > > 72367cf482d8edcbe790f7113f26b8eb7f7dd0d8

![Tela do App](assets/Captura%20de%20tela%202025-10-19%20004602.png)

<p align="center">
<<<<<<< HEAD
=======


> > > > > > > 72367cf482d8edcbe790f7113f26b8eb7f7dd0d8

  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white">
  <img src="https://img.shields.io/badge/Flet-0178FF?style=for-the-badge&logo=flet&logoColor=white">
  <img src="https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white">
  
</p>

<<<<<<< HEAD

### 💾Funcionalidades Técnicas

_Banco de Dados_

- Armazenamento em arquivos CSV
- Sincronização em tempo real
- Backup automático de dados

  # _Interface_

### 💾Funcionalidades Técnicas

_Banco de Dados_

- Armazenamento em arquivos CSV
- Sincronização em tempo real
- Backup automático de dados

  _Interface_

  > > > > > > > 72367cf482d8edcbe790f7113f26b8eb7f7dd0d8

- Design responsivo para mobile
- Navegação intuitiva entre telas
- Feedback visual imediato

<<<<<<< HEAD
_Business Logic_
=======
_Business Logic_

> > > > > > > 72367cf482d8edcbe790f7113f26b8eb7f7dd0d8

- Atualização automática do estoque
- Cálculo preciso de valores e trocos
- Validação de dados de entrada
  <<<<<<< HEAD
  =======

> > > > > > > 72367cf482d8edcbe790f7113f26b8eb7f7dd0d8
