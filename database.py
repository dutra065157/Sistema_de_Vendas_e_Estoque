import os
import sqlite3
from datetime import datetime
import sys
import logging

# ==============================================================
# CONFIGURAÇÃO DE LOGGING PARA CAPTURAR ERROS
# ==============================================================


def setup_logging():
    """Configura sistema de logging para debug"""
    try:
        if getattr(sys, 'frozen', False):
            log_dir = os.path.dirname(sys.executable)
        else:
            log_dir = os.path.dirname(os.path.abspath(__file__))

        log_file = os.path.join(log_dir, 'erros.log')

        logging.basicConfig(
            filename=log_file,
            level=logging.DEBUG,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        logging.info("=== INICIANDO APLICATIVO ===")
    except Exception as e:
        print(f"Erro no logging: {e}")


# Configurar logging imediatamente
setup_logging()

# ==============================================================
# CONFIGURAÇÃO DO BANCO DE DADOS (CORRIGIDA)
# ==============================================================


def get_db_path():
    """Obtém o caminho do banco de dados com tratamento de erro"""
    try:
        logging.info("Obtendo caminho do banco de dados...")

        # Verifica se está executando como executável PyInstaller
        if getattr(sys, 'frozen', False):
            # Se é executável, usa o diretório do executável
            base_dir = os.path.dirname(sys.executable)
            logging.info(f"Modo executável - Diretório: {base_dir}")
        else:
            # Se é script Python, usa o diretório do script
            base_dir = os.path.dirname(os.path.abspath(__file__))
            logging.info(f"Modo desenvolvimento - Diretório: {base_dir}")

        # Cria a pasta database se não existir
        database_dir = os.path.join(base_dir, "database")
        os.makedirs(database_dir, exist_ok=True)
        logging.info(f"Pasta database: {database_dir}")

        db_path = os.path.join(database_dir, "graca_presentes.db")
        logging.info(f"Caminho final do banco: {db_path}")

        # Testa se consegue escrever no diretório
        test_file = os.path.join(database_dir, "test_write.tmp")
        with open(test_file, 'w') as f:
            f.write("test")
        os.remove(test_file)
        logging.info("Permissão de escrita OK")

        return db_path

    except Exception as e:
        logging.error(f"ERRO em get_db_path: {e}")

        # Fallback: usar diretório temporário
        import tempfile
        temp_db = os.path.join(tempfile.gettempdir(), "graca_presentes.db")
        logging.info(f"Usando fallback: {temp_db}")

        return temp_db


DB_PATH = get_db_path()

# ==============================================================
# FUNÇÕES DO BANCO DE DADOS (COM TRATAMENTO DE ERRO)
# ==============================================================


def criar_banco():
    """Cria as tabelas do banco de dados se não existirem"""
    try:
        logging.info("Criando/verificando banco de dados...")

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Tabela de produtos
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS produtos (
            codigo TEXT PRIMARY KEY,
            nome TEXT NOT NULL,
            preco REAL NOT NULL,
            quantidade INTEGER NOT NULL,
            categoria TEXT NOT NULL,
            descricao TEXT,
            data_cadastro TEXT NOT NULL,
            image_path TEXT
        )
        ''')

        # Tabela de vendas
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS vendas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data_venda TEXT NOT NULL,
            total REAL NOT NULL,
            forma_pagamento TEXT NOT NULL,
            valor_recebido REAL,
            troco REAL
        )
        ''')

        # Tabela de itens vendidos
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS itens_vendidos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            venda_id INTEGER NOT NULL,
            produto_codigo TEXT NOT NULL,
            nome TEXT NOT NULL,
            preco_unitario REAL NOT NULL,
            quantidade INTEGER NOT NULL,
            subtotal REAL NOT NULL,
            FOREIGN KEY (venda_id) REFERENCES vendas(id),
            FOREIGN KEY (produto_codigo) REFERENCES produtos(codigo)
        )
        ''')

        # Tabela de dados do cartão (NOVA)
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS dados_cartao (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            venda_id INTEGER NOT NULL,
            nome_cliente TEXT,
            tipo_cartao TEXT,
            parcelas INTEGER,
            FOREIGN KEY (venda_id) REFERENCES vendas(id)
        )
        ''')

        conn.commit()
        conn.close()
        logging.info("Banco de dados criado/verificado com sucesso")

    except Exception as e:
        logging.error(f"ERRO ao criar banco: {e}")
        raise  # Re-lança a exceção para ser tratada no app principal


def salvar_produto_db(produto):
    """Salva ou atualiza um produto no banco de dados"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT OR REPLACE INTO produtos
            (codigo, nome, preco, quantidade, categoria,
             descricao, data_cadastro, image_path)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            produto['codigo'],
            produto['nome'],
            produto['preco'],
            produto['quantidade'],
            produto['categoria'],
            produto['descricao'],
            datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            produto.get('image_path', '')
        ))

        conn.commit()
        conn.close()
        logging.info(f"Produto salvo: {produto['codigo']}")

    except Exception as e:
        logging.error(f"ERRO ao salvar produto {produto['codigo']}: {e}")
        raise


def buscar_produtos_db(filtro=None):
    """Busca produtos no banco de dados com filtro opcional"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        if filtro:
            cursor.execute('''
                SELECT * FROM produtos
                WHERE codigo LIKE ? OR nome LIKE ?
                ORDER BY nome
            ''', (f'%{filtro}%', f'%{filtro}%'))
        else:
            cursor.execute('SELECT * FROM produtos ORDER BY nome')

        produtos = cursor.fetchall()
        conn.close()
        logging.info(f"Busca realizada - {len(produtos)} produtos encontrados")
        return produtos

    except Exception as e:
        logging.error(f"ERRO ao buscar produtos: {e}")
        return []  # Retorna lista vazia em caso de erro


def buscar_produto_db(codigo):
    """Busca um produto específico pelo código"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM produtos WHERE codigo = ?', (codigo,))
        produto = cursor.fetchone()
        conn.close()
        return produto

    except Exception as e:
        logging.error(f"ERRO ao buscar produto {codigo}: {e}")
        return None


def excluir_produto_db(codigo):
    """Exclui um produto do banco de dados"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM produtos WHERE codigo = ?', (codigo,))
        conn.commit()
        conn.close()
        logging.info(f"Produto excluído: {codigo}")

    except Exception as e:
        logging.error(f"ERRO ao excluir produto {codigo}: {e}")
        raise


def atualizar_estoque_db(codigo, quantidade):
    """Atualiza o estoque de um produto"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
        UPDATE produtos
        SET quantidade = quantidade + ?
        WHERE codigo = ?
        ''', (quantidade, codigo))
        conn.commit()
        conn.close()
        logging.info(f"Estoque atualizado: {codigo} + {quantidade}")

    except Exception as e:
        logging.error(f"ERRO ao atualizar estoque {codigo}: {e}")
        raise


def registrar_venda_db(venda, itens, dados_cartao=None):
    """Registra uma venda e seus itens no banco de dados"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Insere a venda principal
        cursor.execute('''
        INSERT INTO vendas
        (data_venda, total, forma_pagamento, valor_recebido, troco)
        VALUES (?, ?, ?, ?, ?)
        ''', (
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            venda['total'],
            venda['forma_pagamento'],
            venda.get('valor_recebido'),
            venda.get('troco')
        ))

        venda_id = cursor.lastrowid

        # Insere os dados do cartão se houver
        if dados_cartao:
            cursor.execute('''
            INSERT INTO dados_cartao
            (venda_id, nome_cliente, tipo_cartao, parcelas)
            VALUES (?, ?, ?, ?)
            ''', (
                venda_id,
                dados_cartao.get('nome_cliente'),
                dados_cartao.get('tipo_cartao'),
                dados_cartao.get('parcelas')
            ))

        # Insere os itens vendidos
        for item in itens:
            cursor.execute('''
            INSERT INTO itens_vendidos
            (venda_id, produto_codigo, nome, preco_unitario, quantidade, subtotal)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                venda_id,
                item['codigo'],
                item['nome'],
                item['preco'],
                item['quantidade'],
                item['subtotal']
            ))

        conn.commit()
        conn.close()
        logging.info(f"Venda registrada: ID {venda_id}")
        return venda_id

    except Exception as e:
        logging.error(f"ERRO ao registrar venda: {e}")
        raise

def obter_venda(venda_id):
    """Busca uma venda pelo ID"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM vendas WHERE id = ?", (venda_id,))
        venda = cursor.fetchone()
        conn.close()
        return venda
    except Exception as e:
        logging.error(f"ERRO ao buscar venda {venda_id}: {e}")
        return None

def obter_itens_venda(venda_id):
    """Busca os itens de uma venda pelo ID"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM itens_vendidos WHERE venda_id = ?", (venda_id,))
        itens = cursor.fetchall()
        conn.close()
        return itens
    except Exception as e:
        logging.error(f"ERRO ao buscar itens da venda {venda_id}: {e}")
        return []

# ==============================================================
# FUNÇÃO DE INICIALIZAÇÃO DO BANCO
# ==============================================================


def inicializar_banco():
    """Função para inicializar o banco ao iniciar o app"""
    try:
        logging.info("Inicializando banco de dados...")
        criar_banco()
        logging.info("Banco inicializado com sucesso")
        return True
    except Exception as e:
        logging.error(f"FALHA na inicialização do banco: {e}")
        return False
