import flet as ft
import os
import sys
import platform
import shutil
from datetime import datetime
import asyncio
import traceback
import pandas as pd
from datetime import date
from relatorio import *
from database import *
from relatorio import DashboardGraficos  # Importa a nova classe
import qrcode
from io import BytesIO
import base64
import webbrowser
import urllib.parse


# ==============================================================
# FUNÇÕES AUXILIARES E ESTADO DA APLICAÇÃO
# ==============================================================


class AppState:
    """Classe para gerenciar o estado da aplicação"""

    def __init__(self):
        self.carrinho = []
        self.produto_editando = None
        self.uploaded_image_path = None
        self.dashboard = None  # Será inicializado depois
        self.ultima_venda_id = None


def mostrar_mensagem(page, texto, cor=ft.Colors.GREEN):
    """Exibe uma mensagem temporária na interface"""
    page.snack_bar = ft.SnackBar(
        content=ft.Text(texto, color=cor),
        bgcolor=ft.Colors.GREY_900 if page.theme_mode == ft.ThemeMode.DARK else ft.Colors.WHITE,
        behavior=ft.SnackBarBehavior.FLOATING
    )
    page.snack_bar.open = True
    page.update()


def confirmar_acao(page, mensagem, callback):
    """Exibe um diálogo de confirmação para ações críticas"""
    def fechar_dialogo(e):
        dialogo.open = False
        page.update()

    def confirmar(e):
        callback()
        fechar_dialogo(e)

    dialogo = ft.AlertDialog(
        modal=True,
        title=ft.Text("Confirmação"),
        content=ft.Text(mensagem),
        actions=[
            ft.TextButton("Sim", on_click=confirmar),
            ft.TextButton("Não", on_click=fechar_dialogo),
        ],
        actions_alignment=ft.MainAxisAlignment.END
    )

    page.dialog = dialogo
    dialogo.open = True
    page.update()


# ==============================================================
# FUNÇÕES PRINCIPAIS DA APLICAÇÃO
# ==============================================================

def main(page: ft.Page):
    # Configuração inicial da página
    page.title = "Graça Presentes "

    page.window.maximized = True
    page.padding = 0
    page.theme_mode = ft.ThemeMode.LIGHT
    page.scroll = ft.ScrollMode.AUTO
    page.fonts = {
        "Poppins": "https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&display=swap"
    }
    page.theme = ft.Theme(font_family="Poppins")

    # Inicialização do estado da aplicação
    state = AppState()
    state.dashboard = DashboardGraficos(page)  # Inicializa o dashboard

    # ==============================================================
    # COMPONENTES DE INTERFACE
    # ==============================================================

    # Elementos de imagem
    image_preview = ft.Image(
        width=300,
        height=200,
        fit=ft.ImageFit.CONTAIN,
        border_radius=ft.border_radius.all(10),
        visible=False
    )

    busca_image_preview = ft.Image(
        width=300,
        height=300,
        fit=ft.ImageFit.CONTAIN,
        border_radius=ft.border_radius.all(10),
        visible=False
    )

    # FilePicker para seleção de imagens

    def on_files_selected(e: ft.FilePickerResultEvent):
        if e.files:
            selected_file = e.files[0]
            state.uploaded_image_path = selected_file.path
            image_preview.src = state.uploaded_image_path
            image_preview.visible = True
        else:
            state.uploaded_image_path = None
            image_preview.visible = False
        page.update()

    file_picker = ft.FilePicker(on_result=on_files_selected)
    page.overlay.append(file_picker)

    def pick_files(e):
        file_picker.pick_files(allow_multiple=False)

    # ==============================================================
    # FUNÇÕES DE ATUALIZAÇÃO DE INTERFACE
    # ==============================================================

    def calcular_troco(e):
        """Calcula o troco para pagamentos em dinheiro"""
        try:
            total = sum(item['subtotal'] for item in state.carrinho)
            valor = float(valor_recebido.value)

            if valor >= total:
                troco.value = f"Troco: R$ {valor - total:.2f}"
                troco.visible = True
            else:
                troco.value = "Valor insuficiente!"
                troco.color = ft.Colors.RED
                troco.visible = True
        except ValueError:
            troco.visible = False
        page.update()

    def atualizar_forma_pagamento(e):
        """Mostra/oculta campos de pagamento conforme a forma selecionada"""
        valor_recebido.visible = (forma_pagamento.value == "dinheiro")
        troco.visible = False
        page.update()

    def atualizar_tabela_produtos(filtro=None):
        """Atualiza a tabela de produtos com dados do banco"""
        try:
            produtos = buscar_produtos_db(filtro)

            if not produtos:
                tabela_produtos.rows = [
                    ft.DataRow(
                        cells=[
                            ft.DataCell(ft.Text("Nenhum produto cadastrado", italic=True)),
                            ft.DataCell(ft.Text("")),
                            ft.DataCell(ft.Text("")),
                            ft.DataCell(ft.Text("")),
                            ft.DataCell(ft.Text("")),
                            ft.DataCell(ft.Text("")),
                        ]
                    )
                ]
            else:
                novas_linhas = []
                for idx, p in enumerate(produtos):
                    # Conversão segura dos dados
                    novas_linhas.append(
                        ft.DataRow(
                            cells=[
                                ft.DataCell(ft.Text(str(p[0]), weight=ft.FontWeight.BOLD)),
                                ft.DataCell(ft.Text(str(p[1]))),
                                ft.DataCell(ft.Text(f"R$ {float(p[2]):.2f}", color=ft.Colors.GREEN)),
                                ft.DataCell(ft.Text(str(p[3]), color=ft.Colors.RED if int(p[3]) < 5 else ft.Colors.BLACK)),
                                ft.DataCell(ft.Text(str(p[4]).capitalize(), color=ft.Colors.BLUE_700)),
                                ft.DataCell(
                                    ft.Row([
                                        ft.IconButton(
                                            ft.Icons.REMOVE_RED_EYE,
                                            icon_color=ft.Colors.BLUE_700,
                                            tooltip="Visualizar",
                                            on_click=lambda e, cod=p[0]: mostrar_modal_produto(cod)
                                        ),
                                        ft.IconButton(
                                            icon=ft.Icons.DELETE,
                                            icon_color=ft.Colors.RED_700,
                                            tooltip="Excluir",
                                            on_click=lambda e, cod=p[0]: confirmar_exclusao(cod)
                                        ),
                                    ], spacing=5)
                                ),
                            ],
                            on_select_changed=lambda e, cod=p[0]: selecionar_produto(cod),
                            color=ft.Colors.GREY_100 if idx % 2 == 0 else None
                        )
                    )
                tabela_produtos.rows = novas_linhas

            page.update()
        except Exception as ex:
            print(f"Erro ao atualizar tabela: {ex}")
            traceback.print_exc()

    def atualizar_seletor_produtos():
        """Atualiza o dropdown de seleção de produtos"""
        produtos = buscar_produtos_db()
        seletor_produto.options = [
            ft.dropdown.Option(
                p[0],
                f"{p[1]} (R$ {p[2]:.2f})"
            ) for p in produtos
        ]
        page.update()

    def limpar_formulario(e=None):
        """Limpa o formulário de cadastro de produtos"""
        state.produto_editando = None
        state.uploaded_image_path = None
        codigo_produto.value = ""
        nome_produto.value = ""
        preco_produto.value = ""
        quantidade_produto.value = ""
        categoria_produto.value = ""
        descricao_produto.value = ""
        image_preview.visible = False
        codigo_produto.focus()
        page.update()

    async def cadastrar_produto(e):

        campos_obrigatorios = [codigo_produto,
                               nome_produto, preco_produto, quantidade_produto]

        # Verifica se algum campo está vazio
        campos_vazios = [campo for campo in campos_obrigatorios
                         if not campo.value or str(campo.value).strip() == ""]

        if campos_vazios:  # Se HÁ campos vazios
            ms1 = "Preencha todos os campos obrigatórios!"
            nao_salva.value = ms1
            nao_salva.color = ft.Colors.RED
            nao_salva.visible = True
            nao_salva.update()

            # Destacar os campos vazios
            for campo in campos_obrigatorios:
                if not campo.value or str(campo.value).strip() == "":
                    campo.border_color = ft.Colors.RED  # Borda vermelha
                else:
                    campo.border_color = ft.Colors.GREY_400  # Borda normal
            page.update()

            # Espera 5 segundos e esconde a mensagem E remove bordas vermelhas
            await asyncio.sleep(5)
            nao_salva.visible = False
            # REMOVER BORDAS VERMELHAS após 5 segundos
            for campo in campos_obrigatorios:
                campo.border_color = ft.Colors.GREY_400  # Volta para cor normal
            page.update()
            return

        # Resetar mensagem de erro se existir
        nao_salva.visible = False
        nao_salva.update()

        # Lógica para criar cópia da imagem na pasta do sistema
        caminho_imagem_final = state.uploaded_image_path
        
        if state.uploaded_image_path:
            try:
                # Cria pasta segura dentro do projeto se não existir
                # Verifica se está rodando como .exe (frozen) ou script .py
                if getattr(sys, 'frozen', False):
                    basedir = os.path.dirname(sys.executable)
                else:
                    basedir = os.path.dirname(os.path.abspath(__file__))
                
                pasta_imagens = os.path.join(basedir, "imagens_produtos")
                if not os.path.exists(pasta_imagens):
                    os.makedirs(pasta_imagens)
                
                # Gera nome padronizado para a imagem: img_CODIGO.ext
                extensao = os.path.splitext(state.uploaded_image_path)[1]
                # Sanitiza o código para evitar caracteres inválidos em nomes de arquivo
                cod_arquivo = codigo_produto.value.strip().replace('/', '-').replace('\\', '-')
                novo_nome = f"img_{cod_arquivo}{extensao}"
                destino = os.path.join(pasta_imagens, novo_nome)
                
                # Copia a imagem apenas se a origem for diferente do destino
                if os.path.abspath(state.uploaded_image_path) != os.path.abspath(destino):
                    shutil.copy(state.uploaded_image_path, destino)
                    caminho_imagem_final = destino
                else:
                    # Já está no local correto (ex: editando produto já salvo corretamente)
                    caminho_imagem_final = destino
            except Exception as ex:
                print(f"Erro ao copiar imagem: {ex}")

        try:
            produto = {
                'codigo': codigo_produto.value.strip(),
                'nome': nome_produto.value.strip(),
                'preco': float(preco_produto.value.replace(',', '.')),
                'quantidade': int(quantidade_produto.value),
                'categoria': categoria_produto.value if categoria_produto.value else "outros",
                'descricao': descricao_produto.value.strip() if descricao_produto.value else "",
                'image_path': caminho_imagem_final
            }

            salvar_produto_db(produto)
            limpar_formulario()
            atualizar_tabela_produtos()
            atualizar_seletor_produtos()

            ms2 = "✅ Produto salvo com sucesso!"
            success_salvar_text.value = ms2

            page.update()

            # Limpa mensagem após 5 segundos

            async def clear_success():
                await asyncio.sleep(5)
                success_salvar_text.value = ""
                page.update()
            page.run_task(clear_success)

        except ValueError:
            mostrar_mensagem(
                page, "Preço e quantidade devem ser números válidos!", ft.Colors.RED)

    def selecionar_produto(codigo):
        """Preenche o formulário com dados de um produto existente"""
        produto = buscar_produto_db(codigo)
        if produto:
            codigo_produto.value = produto[0]
            nome_produto.value = produto[1]
            preco_produto.value = str(produto[2])
            quantidade_produto.value = str(produto[3])
            categoria_produto.value = produto[4]
            descricao_produto.value = produto[5]

            if produto[7]:
                state.uploaded_image_path = produto[7]
                image_preview.src = state.uploaded_image_path
                image_preview.visible = True
            else:
                state.uploaded_image_path = None
                image_preview.visible = False

            page.update()

    # ==============================================================
    # MODAL DE DETALHES DO PRODUTO
    # ==============================================================

    modal_codigo = ft.Text(size=22, weight=ft.FontWeight.W_500)
    modal_nome = ft.Text(size=22, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_900)
    modal_preco = ft.Text(size=22, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_700)
    modal_estoque = ft.Text(size=22, weight=ft.FontWeight.W_500)
    modal_categoria = ft.Text(size=22, weight=ft.FontWeight.W_500)
    modal_descricao = ft.Text(size=20, italic=True)
    modal_image = ft.Image(
        width=350,
        height=300,
        fit=ft.ImageFit.CONTAIN,
        border_radius=ft.border_radius.all(5),
        visible=False
    )



    def mostrar_modal_produto(codigo):
        """Exibe modal com detalhes do produto"""
        produto = buscar_produto_db(codigo)
        if produto:
            modal_codigo.value = produto[0]
            modal_nome.value = produto[1]
            modal_preco.value = f"R$ {produto[2]:.2f}"
            modal_estoque.value = str(produto[3])
            modal_categoria.value = produto[4].capitalize()
            modal_descricao.value = produto[5] or "Nenhuma descrição"

            if produto[7]:
                modal_image.src = produto[7]
                modal_image.visible = True
            else:
                modal_image.visible = False

            page.dialog = modal_produto
            modal_produto.open = True
            page.update()

    def fechar_modal(e=None):
        modal_produto.open = False
        page.update()

    def editar_produto_modal(e=None):
        """Preenche formulário com produto do modal"""
        codigo = modal_codigo.value
        fechar_modal(e)
        cadastrar_produto_pagina(e) # Garante que a tela de cadastro/edição seja carregada
        selecionar_produto(codigo)
        codigo_produto.focus()

    def confirmar_exclusao(codigo):
        """Confirma exclusão de produto com modal personalizado"""
        # Busca o produto para obter o nome e exibir no modal
        prod = buscar_produto_db(codigo)
        nome_produto = prod[1] if prod else "este produto"

        # Atualiza o texto do modal global
        txt_modal_exclusao.value = f"Você tem certeza que deseja remover permanentemente '{nome_produto}'?\nEsta ação não pode ser desfeita."
        
        # Define a ação do botão confirmar especificamente para este produto
        def ao_confirmar(e):
            excluir_produto_db(codigo)
            success_delete_text.value = "🗑️ Produto excluído com sucesso!"
            atualizar_tabela_produtos()
            atualizar_seletor_produtos()
            modal_exclusao.open = False
            page.update()

            async def clear_delete_msg():
                await asyncio.sleep(5)
                success_delete_text.value = ""
                page.update()
            page.run_task(clear_delete_msg)

        btn_modal_exclusao.on_click = ao_confirmar
        
        page.dialog = modal_exclusao
        modal_exclusao.open = True
        page.update()

    # ==============================================================
    # FUNÇÕES DE BUSCA
    # ==============================================================

    def buscar_produto(e=None):
        """Realiza busca de produtos no banco de dados"""
        filtro = campo_busca.value.strip()
        produtos = buscar_produtos_db(filtro if filtro else None)

        busca_image_preview.visible = False

        resultados_busca.controls = [
            ft.ListTile(
                leading=ft.Icon(ft.Icons.INVENTORY_2,
                                color=ft.Colors.BLUE_700),
                title=ft.Text(p[1], weight=ft.FontWeight.BOLD),
                subtitle=ft.Text(
                    f"Código: {p[0]} | Preço: R$ {p[2]:.2f} | Estoque: {p[3]}"),
                on_click=lambda e, p=p: selecionar_produto_busca(p),
            ) for p in produtos
        ]

        if not produtos:
            resultados_busca.controls = [
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.SEARCH_OFF),
                    title=ft.Text("Nenhum produto encontrado", italic=True),
                )
            ]

        page.update()

    def selecionar_produto_busca(produto):
        """Mostra imagem do produto na busca"""
        if produto[7]:  # Índice 7 é o caminho da imagem
            busca_image_preview.src = produto[7]
            busca_image_preview.visible = True
        else:
            busca_image_preview.visible = False
        page.update()  # Atualiza a página para exibir a imagem

    # ==============================================================
    # FUNÇÕES DO CARRINHO
    # ==============================================================

    def adicionar_ao_carrinho(e):
        """Adiciona produto ao carrinho de compras"""
        codigo = seletor_produto.value
        if not codigo:
            mostrar_mensagem(page, "Selecione um produto", ft.Colors.RED)
            return

        try:
            quantidade = int(quantidade_compra.value)
            if quantidade <= 0:
                mostrar_mensagem(
                    page, "Quantidade deve ser maior que zero", ft.Colors.RED)
                return
        except ValueError:
            mostrar_mensagem(page, "Quantidade inválida", ft.Colors.RED)
            return

        produto = buscar_produto_db(codigo)
        if not produto:
            mostrar_mensagem(page, "Produto não encontrado", ft.Colors.RED)
            return

        if quantidade > produto[3]:
            mostrar_mensagem(
                page, "Quantidade indisponível em estoque", ft.Colors.RED)
            return

        item_existente = next(
            (i for i in state.carrinho if i['codigo'] == codigo), None)

        if item_existente:
            item_existente['quantidade'] += quantidade
            item_existente['subtotal'] = item_existente['preco'] * \
                item_existente['quantidade']
        else:
            state.carrinho.append({
                'codigo': codigo,
                'nome': produto[1],
                'preco': produto[2],
                'quantidade': quantidade,
                'subtotal': produto[2] * quantidade
            })

        atualizar_estoque_db(codigo, -quantidade)
        atualizar_carrinho()
        atualizar_tabela_produtos()
        mostrar_mensagem(page, "🛒 Produto adicionado ao carrinho!")
        quantidade_compra.value = "1"
        seletor_produto.focus()
        page.update()

    def atualizar_carrinho():
        """Atualiza la exibição do carrinho com tabela e total alinhado"""

        tabela = []

        # Cabeçalho
        tabela.append(
            ft.Row([
                ft.Text("Produto", weight=ft.FontWeight.BOLD,
                        size=20, expand=2),
                ft.Text("Qtde", weight=ft.FontWeight.BOLD, size=20, expand=1),
                ft.Text("Preço un", weight=ft.FontWeight.BOLD,
                        size=20, expand=1),
                ft.Text("Subtotal", weight=ft.FontWeight.BOLD,
                        size=20, expand=1),
                ft.Text("", expand=1)
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        )

        # Linhas com produtos
        for item in state.carrinho:
            tabela.append(
                ft.Row([
                    ft.Text(item['nome'], size=20, expand=2),
                    ft.Text(str(item['quantidade']), size=20, expand=1),
                    ft.Text(f"R$ {item['preco']:.2f}", size=20, expand=1),
                    ft.Text(f"R$ {item['subtotal']:.2f}",
                            size=20, expand=1, color=ft.Colors.GREEN),
                    ft.IconButton(
                        icon=ft.Icons.DELETE,
                        icon_color=ft.Colors.RED_700,
                        tooltip="Remover",
                        on_click=lambda e, cod=item['codigo']: remover_do_carrinho(
                            cod)
                    )
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
            )

        # Calcula o total
        total = sum(item['subtotal'] for item in state.carrinho)

        # Atualiza visual do card e do total alinhado
        itens_carrinho.controls = [
            ft.Card(
                content=ft.Container(
                    content=ft.Column(tabela, spacing=15),
                    padding=10,
                    bgcolor=ft.Colors.GREY_100,
                    border_radius=8

                ),
                elevation=2,
                margin=ft.margin.symmetric(vertical=5)
            ),
            ft.Row(  # total alinhado com a coluna "Subtotal"
                controls=[
                    ft.Container(
                        content=ft.Text(
                            f"Total: R$ {total:.2f}", size=25, weight=ft.FontWeight.BOLD),
                        alignment=ft.alignment.center_right,
                        expand=True
                    )
                ],
                alignment=ft.MainAxisAlignment.END
            )
        ]

        # opcional se tiver visível fora do card
        total_carrinho.value = f"R$ {total:.2f}"
        page.update()

    def remover_do_carrinho(codigo):
        """Remove item do carrinho"""
        item = next((i for i in state.carrinho if i['codigo'] == codigo), None)
        if item:
            atualizar_estoque_db(codigo, item['quantidade'])
            state.carrinho.remove(item)
            atualizar_carrinho()
            atualizar_tabela_produtos()
            success_text_remover.value = "❌ Item removido do carrinho"
            page.update()

            async def clear_success():
                await asyncio.sleep(5)
                success_text_remover.value = ""
                page.update()
            page.run_task(clear_success)

    

    def limpar_carrinho(e):
        """Limpa todos os itens do carrinho"""
        if not state.carrinho:
            mostrar_mensagem(page, "O carrinho já está vazio!", ft.Colors.ORANGE)
            return

        try:
            for item in state.carrinho:
                atualizar_estoque_db(item['codigo'], item['quantidade'])
            state.carrinho.clear()
            atualizar_carrinho()
            atualizar_tabela_produtos()

            success_vendas_text.value = "🔄 Carrinho limpo com sucesso!"
            page.update()

            async def clear_success():
                await asyncio.sleep(5)
                success_vendas_text.value = ""
                page.update()
            page.run_task(clear_success)
        except Exception as ex:
            mostrar_mensagem(page, f"Erro ao limpar carrinho: {ex}", ft.Colors.RED)

    # ==============================================================
    # MODAL DE CHECKOUT
    # ==============================================================

    checkout_itens = ft.Column(scroll=ft.ScrollMode.AUTO)
    checkout_total = ft.Text("R$ 0,00", size=25, weight=ft.FontWeight.BOLD)
    valor_recebido = ft.TextField(
        label="Valor Recebido",
        prefix_text="R$ ",
        visible=False,
        on_change=calcular_troco,
        border_color=ft.Colors.BLUE_700
    )
    troco = ft.Text("Troco: R$ 0,00", visible=False,
                    size=25, weight=ft.FontWeight.BOLD)
    forma_pagamento = ft.Dropdown(
        label="Forma de Pagamento",
        options=[
            ft.dropdown.Option("dinheiro", "Dinheiro"),
            ft.dropdown.Option("cartao", "Cartão"),
            ft.dropdown.Option("pix", "PIX"),
        ],
        value="dinheiro",
        on_change=atualizar_forma_pagamento,
        border_color=ft.Colors.BLUE_700
    )

    # ==============================================================
    # MODAL DADOS CARTÃO (NOVO)
    # ==============================================================

    cartao_nome_cliente = ft.TextField(label="Nome do Cliente", width=400, border_color=ft.Colors.BLUE_700)
    cartao_parcelas = ft.TextField(label="Parcelas", value="1", width=100, disabled=True, keyboard_type=ft.KeyboardType.NUMBER, border_color=ft.Colors.BLUE_700)
    cartao_info_venda = ft.Text("", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_800)

    def on_tipo_cartao_change(e):
        if e.control.value == "debito":
            cartao_parcelas.value = "1"
            cartao_parcelas.disabled = True
        else:
            cartao_parcelas.disabled = False
        page.update()

    cartao_tipo = ft.RadioGroup(
        content=ft.Row([
            ft.Radio(value="debito", label="Débito"),
            ft.Radio(value="credito", label="Crédito")
        ]),
        value="debito",
        on_change=on_tipo_cartao_change
    )

    def fechar_modal_cartao(e=None):
        modal_dados_cartao.open = False
        page.update()

    def confirmar_venda_cartao(e):
        try:
            if not cartao_nome_cliente.value:
                cartao_nome_cliente.error_text = "Nome obrigatório"
                page.update()
                return

            total = sum(item['subtotal'] for item in state.carrinho)
            
            dados_cartao = {
                'nome_cliente': cartao_nome_cliente.value,
                'tipo_cartao': cartao_tipo.value,
                'parcelas': int(cartao_parcelas.value) if cartao_parcelas.value else 1
            }

            venda = {
                'data_venda': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'total': total,
                'forma_pagamento': 'cartao',
                'valor_recebido': total,
                'troco': 0
            }

            venda_id = registrar_venda_db(venda, state.carrinho, dados_cartao)
            state.ultima_venda_id = venda_id
            abrir_modal_comprovante()
            
            # Limpeza e Sucesso
            state.carrinho.clear()
            atualizar_carrinho()
            modal_dados_cartao.open = False
            modal_checkout.open = False
            atualizar_tabela_produtos()
            state.dashboard.atualizar_tudo()

            success_vendas_text.value = f"✅ Venda Cartão 🛒{venda_id} registrada!"
            page.update()

            async def clear_success():
                await asyncio.sleep(5)
                success_vendas_text.value = ""
                page.update()
            page.run_task(clear_success)

        except Exception as ex:
            mostrar_mensagem(page, f"Erro: {str(ex)}", ft.Colors.RED)
            traceback.print_exc()

    modal_dados_cartao = ft.AlertDialog(
        modal=True,
        title=ft.Text("Dados do Cartão", weight="bold", color=ft.Colors.BLUE_800),
        content=ft.Container(
            content=ft.Column([
                cartao_info_venda,
                ft.Divider(),
                cartao_nome_cliente,
                ft.Text("Tipo de Operação:", weight="bold"),
                cartao_tipo,
                cartao_parcelas,
            ], tight=True, spacing=15),
            width=400,
            padding=20
        ),
        actions=[
            ft.TextButton("Confirmar", 
                style=ft.ButtonStyle(bgcolor=ft.Colors.GREEN_700, color=ft.Colors.WHITE),
                on_click=confirmar_venda_cartao),
            ft.TextButton("Cancelar", 
                style=ft.ButtonStyle(color=ft.Colors.RED_700),
                on_click=fechar_modal_cartao)
        ],
        actions_alignment=ft.MainAxisAlignment.SPACE_BETWEEN
    )

    def abrir_checkout(e):
        page.add(modal_checkout)
        """Abre o modal de finalização de compra"""
        if not state.carrinho: 
            mostrar_mensagem(page, "Carrinho vazio", ft.Colors.RED)
            return

        checkout_itens.controls.clear()

        for item in state.carrinho:
            checkout_itens.controls.append(
                ft.Row([
                    ft.Text(f"{item['nome']} x{item['quantidade']}"),
                    ft.Text(f"R$ {item['subtotal']:.2f}",
                            color=ft.Colors.GREEN)
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
            )

        total = sum(item['subtotal'] for item in state.carrinho)
        checkout_total.value = f"R$ {total:.2f}"

        valor_recebido.value = ""
        forma_pagamento.value = "dinheiro"
        valor_recebido.visible = False
        troco.visible = False

        page.dialog = modal_checkout
        modal_checkout.open = True
        page.update()

    def finalizar_compra(e):
        """Finaliza a venda e registra no banco de dados"""
        try:
            forma_pgto = forma_pagamento.value
            total = sum(item['subtotal'] for item in state.carrinho)

            if forma_pgto == "cartao":
                # Prepara e abre modal do cartão
                cartao_nome_cliente.value = ""
                cartao_nome_cliente.error_text = None
                cartao_tipo.value = "debito"
                cartao_parcelas.value = "1"
                cartao_parcelas.disabled = True
                
                data_hora = datetime.now().strftime('%d/%m/%Y %H:%M')
                cartao_info_venda.value = f"Valor: R$ {total:.2f}\nData: {data_hora}"
                
                page.dialog = modal_dados_cartao
                modal_dados_cartao.open = True
                page.update()
                return

            if forma_pgto == "dinheiro":
                try:
                    valor_pago = float(valor_recebido.value)
                    if valor_pago < total:
                        mostrar_mensagem(
                            page, "Valor insuficiente!", ft.Colors.RED)
                        return
                    troco_valor = valor_pago - total
                except ValueError:
                    mostrar_mensagem(
                        page, "Digite um valor válido!", ft.Colors.RED)
                    return
            else:
                troco_valor = 0.0
                valor_pago = total

            venda = {
                'data_venda': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'total': total,
                'forma_pagamento': forma_pgto,
                'valor_recebido': valor_pago if forma_pgto == "dinheiro" else None,
                'troco': troco_valor if forma_pgto == "dinheiro" else None
            }

            venda_id = registrar_venda_db(venda, state.carrinho)
            state.ultima_venda_id = venda_id
            abrir_modal_comprovante()
            state.carrinho.clear()
            atualizar_carrinho()
            modal_checkout.open = False
            atualizar_tabela_produtos()

            # ATUALIZA OS GRÁFICOS APÓS VENDA
            state.dashboard.atualizar_tudo()

            msg = f"✅ Venda 🛒{venda_id} finalizada com sucesso!"
            if forma_pgto == "dinheiro":
                msg += f" Troco: R$ {troco_valor:.2f}"

            success_vendas_text.value = msg
            page.update()

            # Limpa mensagem após 5 segundos
            async def clear_success():
                await asyncio.sleep(5)
                success_vendas_text.value = ""
                page.update()
            page.run_task(clear_success)

        except Exception as ex:
            mostrar_mensagem(
                page, f"Erro ao finalizar venda: {str(ex)}", ft.Colors.RED)
            traceback.print_exc()

    def fechar_modal_checkout(e=None):
        """Fecha o modal de checkout"""
        modal_checkout.open = False
        page.update()

    # ==============================================================
    # NAVEGAÇÃO ENTRE PÁGINAS
    # ==============================================================

    resultado_area = ft.Column(expand=True)

    def carregar_vendas(e):
        resultado_area.controls.clear()
        data_escolhida = e.control.value.strftime("%Y-%m-%d")
        dados = obter_vendas_por_dia(data_escolhida)
        if not dados:
            resultado_area.controls.append(
                ft.Text(f"Nenhuma venda em {data_escolhida}", color="red")
            )
        else:
            tabela = criar_tabela_vendas(dados)
            grafico = criar_grafico_vendas(dados)
            resultado_area.controls.append(
                ft.Text(f"📆 Vendas de {data_escolhida}",
                        size=20, weight="bold", color=TEXT_COLOR)
            )
            resultado_area.controls.append(
                ft.Row([tabela, grafico], expand=True))
        page.update()

    seletor_data = ft.DatePicker(
        on_change=carregar_vendas,
        first_date=date(2025, 1, 1),
        last_date=date.today(),
        value=date.today()
    )
    page.overlay.append(seletor_data)
    botao_data = ft.ElevatedButton(
        "📅 Escolher data", on_click=lambda e: page.open(seletor_data), color=ft.Colors.WHITE, bgcolor=PRIMARY_COLOR
    )

    def cadastrar_produto_pagina(e):
        """Navega para a página de cadastro de produtos"""
        page.clean()
        page.add(header)
        page.add(modal_produto)
        page.add(modal_exclusao)
        page.add(ft.Container(
            content=ft.Column([
                linhacadastros,
                botao_voltar
            ]),
            padding=20
        ))
        page.update()

    def voltar_pagina_inicial(e):
        """Volta para a página inicial"""
        page.clean()
        page.add(header)

        page.add(ft.Container(
            content=ft.Column([
                ft.Column([success_vendas_text, success_text_remover], spacing=0),
                ft.Row([
                    ft.Column([secao_carrinho, form_busca,
                               Botao_pagina_cadastro], expand=2)
                ], expand=True)
            ]),
            padding=ft.padding.only(left=20, right=20, bottom=20, top=0)
        ))

        # Re-adicionar os modais que foram removidos pelo page.clean()
        page.add(modal_checkout)
        page.add(modal_dados_cartao)
        page.add(modal_comprovante)
        page.add(modal_exclusao)

        page.update()

    def mostrar_relatorios(e):
        """Navega para a página de relatórios"""
        page.clean()
        page.add(header)

        # Atualiza os gráficos antes de mostrar
        state.dashboard.atualizar_tudo()

        # ---- LAYOUT ----
        page.add(ft.Container(
            content=ft.Column([
                ft.Text("📊 Dashboard de Vendas", size=30,
                        weight="bold", color=PRIMARY_COLOR),
                state.dashboard.cards,
                ft.Row([state.dashboard.grafico_pizza,
                        state.dashboard.tabela_cartoes], expand=True),
                ft.Divider(),
                ft.Text("📆 Relatório por Data", size=25,
                        weight="bold", color=TEXT_COLOR),
                ft.Row([botao_data]),
                resultado_area,
                ft.Divider(),
                state.dashboard.grafico_linha_pagamento,
                state.dashboard.grafico_barras,
                ft.Divider(),

                state.dashboard.criar_grafico_estoque(),
                botao_voltar
            ]),
            padding=20
        ))
        page.update()

    # ==============================================================
    # DEFINIÇÃO DOS COMPONENTES DE INTERFACE
    # ==============================================================

    # Modal de checkout
    modal_checkout = ft.AlertDialog(
        modal=True,
        title=ft.Text(
            "FINALIZAR COMPRA",
            size=24,
            weight=ft.FontWeight.BOLD,
            text_align=ft.TextAlign.CENTER,
            color=ft.Colors.BLUE_800
        ),
        content=ft.Container(
            content=ft.Column(
                [
                    ft.Text(
                        "ITENS DO CARRINHO",
                        size=15,
                        weight=ft.FontWeight.BOLD,
                        text_align=ft.TextAlign.CENTER,
                        color=ft.Colors.BLUE_700
                    ),
                    ft.Divider(height=2, thickness=2,
                               color=ft.Colors.BLUE_100),
                    checkout_itens,
                    ft.Divider(height=2, thickness=2,
                               color=ft.Colors.BLUE_100),
                    ft.Row(
                        [
                            ft.Text(
                                "TOTAL:",
                                size=20,
                                weight=ft.FontWeight.BOLD,
                                color=ft.Colors.BLUE_700
                            ),
                            checkout_total
                        ],
                        alignment=ft.MainAxisAlignment.CENTER
                    ),
                    ft.Container(forma_pagamento,
                                 padding=ft.padding.symmetric(vertical=10)),
                    ft.Container(valor_recebido,
                                 padding=ft.padding.only(bottom=10)),
                    troco
                ],
                tight=True,
                scroll=ft.ScrollMode.AUTO,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER
            ),
            width=600,
            padding=ft.padding.symmetric(horizontal=30, vertical=20),
        ),
        shape=ft.RoundedRectangleBorder(radius=15),
        actions=[
            ft.TextButton(
                "CONFIRMAR",
                style=ft.ButtonStyle(
                    bgcolor=ft.Colors.GREEN_700,
                    color=ft.Colors.WHITE,
                    padding=ft.padding.symmetric(horizontal=30, vertical=15),
                    shape=ft.RoundedRectangleBorder(radius=10)
                ),
                on_click=finalizar_compra
            ),
            ft.TextButton(
                "CANCELAR",
                style=ft.ButtonStyle(
                    bgcolor=ft.Colors.RED_700,
                    color=ft.Colors.WHITE,
                    padding=ft.padding.symmetric(horizontal=30, vertical=15),
                    shape=ft.RoundedRectangleBorder(radius=10)
                ),
                on_click=fechar_modal_checkout
            )
        ],
        actions_alignment=ft.MainAxisAlignment.SPACE_EVENLY
    )

    # Modal de produto
    modal_produto = ft.AlertDialog(
        modal=True,
        title=ft.Text("INFORMAÇÕES DETALHADAS", size=28, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_800),
        content=ft.Container(
            content=ft.Row([
                # Lado Esquerdo: Imagem
                ft.Container(
                    content=ft.Column([
                        ft.Text("Imagem do Produto", size=18, weight="bold", color=ft.Colors.GREY_700),
                        ft.Divider(),
                        modal_image,
                        ft.Container(
                            content=ft.Icon(ft.Icons.IMAGE_NOT_SUPPORTED, size=100, color=ft.Colors.GREY_300),
                            visible=False, # Lógica para mostrar caso não tenha imagem se desejar
                        )
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=20,
                    bgcolor=ft.Colors.GREY_50,
                    border_radius=10,
                ),
                # Lado Direito: Informações
                ft.Container(
                    content=ft.Column([
                        ft.Row([ft.Text("📦 Nome:", weight=ft.FontWeight.BOLD, size=20, color=ft.Colors.GREY_700), modal_nome]),
                        ft.Row([ft.Text("🔢 Código:", weight=ft.FontWeight.BOLD, size=20, color=ft.Colors.GREY_700), modal_codigo]),
                        ft.Row([ft.Text("💰 Preço:", weight=ft.FontWeight.BOLD, size=20, color=ft.Colors.GREY_700), modal_preco]),
                        ft.Row([ft.Text("📊 Estoque:", weight=ft.FontWeight.BOLD, size=20, color=ft.Colors.GREY_700), modal_estoque]),
                        ft.Row([ft.Text("🏷️ Categoria:", weight=ft.FontWeight.BOLD, size=20, color=ft.Colors.GREY_700), modal_categoria]),
                        ft.Text("📝 Descrição:", weight=ft.FontWeight.BOLD, size=20, color=ft.Colors.GREY_700),
                        ft.Container(content=modal_descricao, padding=ft.padding.only(left=10), width=400),
                    ], spacing=15, scroll=ft.ScrollMode.AUTO),
                    padding=20,
                    expand=True
                )
            ], vertical_alignment=ft.CrossAxisAlignment.START, tight=True),
            width=900,
            height=500,
        ),
        actions=[
            ft.ElevatedButton(
                "✏️ Editar Produto", 
                on_click=editar_produto_modal,
                style=ft.ButtonStyle(bgcolor=ft.Colors.BLUE_700, color=ft.Colors.WHITE, padding=20)
            ),
            ft.ElevatedButton(
                "🗑️ Excluir",
                bgcolor=ft.Colors.RED_700,
                color=ft.Colors.WHITE,
                on_click=lambda e: confirmar_exclusao(modal_codigo.value),
                style=ft.ButtonStyle(padding=20)
            ),
            ft.TextButton(
                "Fechar", 
                on_click=fechar_modal,
                style=ft.ButtonStyle(color=ft.Colors.GREY_700, padding=20)
            )
        ],
        actions_alignment=ft.MainAxisAlignment.END,
        shape=ft.RoundedRectangleBorder(radius=15),
    )

    # Modal de exclusão global (Personalizado)
    txt_modal_exclusao = ft.Text("", size=16)
    btn_modal_exclusao = ft.ElevatedButton("Excluir", bgcolor=ft.Colors.RED_700, color=ft.Colors.WHITE)
    
    modal_exclusao = ft.AlertDialog(
        modal=True,
        title=ft.Row([
            ft.Icon(ft.Icons.WARNING_ROUNDED, color=ft.Colors.RED_700, size=30),
            ft.Text(" Confirmar Exclusão", color=ft.Colors.RED_700, weight=ft.FontWeight.BOLD)
        ], alignment=ft.MainAxisAlignment.START),
        content=ft.Container(
            content=txt_modal_exclusao,
            padding=ft.padding.only(top=10, bottom=10),
            width=400
        ),
        actions=[
            btn_modal_exclusao,
            ft.TextButton("Cancelar", 
                         style=ft.ButtonStyle(color=ft.Colors.GREY_700),
                         on_click=lambda e: fechar_dialogo(modal_exclusao))
        ],
        actions_alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        shape=ft.RoundedRectangleBorder(radius=15)
    )

    # Componentes do formulário de cadastro
    codigo_produto = ft.TextField(
        label="Código do Produto",
        width=300,
        autofocus=True,
        border_color=ft.Colors.BLUE_700,
        prefix_icon=ft.Icons.LABEL


    )
    nome_produto = ft.TextField(
        label="Nome do Produto",
        width=300,
        border_color=ft.Colors.BLUE_700,
        prefix_icon=ft.Icons.LABEL
    )
    preco_produto = ft.TextField(
        label="Preço Unitário (R$)",
        width=300,
        prefix_text="R$ ",
        border_color=ft.Colors.BLUE_700,
        prefix_icon=ft.Icons.ATTACH_MONEY
    )
    quantidade_produto = ft.TextField(
        label="Quantidade em Estoque",
        width=300,
        border_color=ft.Colors.BLUE_700,
        prefix_icon=ft.Icons.INVENTORY
    )
    categoria_produto = ft.Dropdown(
        label="Categoria",
        options=[
            ft.dropdown.Option("cosmeticos", "Cosméticos"),
            ft.dropdown.Option("perfumes", "Perfumes"),
            ft.dropdown.Option("cestas", "Cestas"),
            ft.dropdown.Option("higiene", "Higiene"),
            ft.dropdown.Option("outros", "Outros"),
        ],
        width=300,
        border_color=ft.Colors.BLUE_700
    )
    descricao_produto = ft.TextField(
        label="Descrição",
        multiline=True,
        min_lines=2,
        width=300,
        border_color=ft.Colors.BLUE_700,
    )

    # Seção de busca
    campo_busca = ft.TextField(
        label="Buscar Produto",
        width=300,
        suffix_icon=ft.Icons.SEARCH,
        on_submit=buscar_produto,
        border_color=ft.Colors.BLUE_700
    )

    resultados_busca = ft.Column(
        spacing=5, scroll=ft.ScrollMode.AUTO, height=150)

    # Seção de carrinho
    seletor_produto = ft.Dropdown(
        label="Produto",
        width=300,
        options=[],
        border_color=ft.Colors.BLUE_700,
        leading_icon=ft.Icons.SHOPPING_BAG
    )
    quantidade_compra = ft.TextField(
        label="Quantidade",
        value="1",
        width=300,
        border_color=ft.Colors.BLUE_700
    )
    itens_carrinho = ft.Column(
        spacing=5, scroll=ft.ScrollMode.AUTO, height=150)
    total_carrinho = ft.Text("R$ 0,00", size=40, weight=ft.FontWeight.BOLD)

    # Tabela de produtos
    tabela_produtos = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Código", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Nome", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Preço", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Estoque", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Categoria", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Ações", weight=ft.FontWeight.BOLD)),
        ],
        rows=[],
        width=1100,
        heading_row_color=ft.Colors.BLUE_50,
        column_spacing=20
    )

    # Mensagens
    success_text_remover = ft.Text("", size=20, color=ft.Colors.RED)
    success_vendas_text = ft.Text(value="", size=25, color=ft.Colors.GREEN)
    success_salvar_text = ft.Text(size=20, color=ft.Colors.GREEN)
    nao_salva = ft.Text(size=20, color=ft.Colors.RED_700)

    # ==============================================================
    # MODAL E FUNÇÕES DO COMPROVANTE (NOVO E MELHORADO)
    # ==============================================================

    def gerar_texto_comprovante(venda_id):
        """Gera o conteúdo de texto de um comprovante de venda."""
        venda = obter_venda(venda_id)
        itens = obter_itens_venda(venda_id)

        if not venda:
            return None

        # Formata o texto do comprovante
        texto = f"=== COMPROVANTE DE VENDA ===\n"
        texto += f"Loja: Graça Presentes\n"
        texto += f"WhatsApp: (11) 99999-9999\n" # <--- COLOQUE O NÚMERO DA LOJA AQUI
        texto += f"Data: {venda[1]}\n"
        texto += f"Venda ID: #{venda[0]}\n"
        texto += "-" * 30 + "\n"

        for item in itens:
            # item: id, venda_id, prod_cod, nome, preco, qtd, subtotal
            texto += f"{item[5]}x {item[3]}\n"
            texto += f"   R$ {item[4]:.2f} -> R$ {item[6]:.2f}\n"

        texto += "-" * 30 + "\n"
        texto += f"TOTAL: R$ {venda[2]:.2f}\n"
        texto += f"Forma Pagamento: {venda[3].upper()}\n"

        texto += "\n   Obrigado pela preferência!   \n"
        texto += "==============================\n"
        return texto

    def copiar_comprovante(e):
        """Copia o texto do comprovante para a área de transferência."""
        texto = gerar_texto_comprovante(state.ultima_venda_id)
        if texto:
            page.set_clipboard(texto)
            mostrar_mensagem(page, "✅ Texto do comprovante copiado!")
        else:
            mostrar_mensagem(page, "Erro ao gerar comprovante.", ft.Colors.RED)
        modal_comprovante.open = False
        page.update()

    def imprimir_comprovante_local(e):
        """Salva o comprovante como .txt e abre localmente."""
        texto = gerar_texto_comprovante(state.ultima_venda_id)
        if not texto:
            mostrar_mensagem(page, "Erro ao gerar comprovante.", ft.Colors.RED)
            return

        filename = f"comprovante_{state.ultima_venda_id}.txt"
        try:
            with open(filename, "w", encoding="utf-8") as f:
                f.write(texto)

            if platform.system() == "Windows":
                os.startfile(filename)
            else:
                import subprocess
                opener = "open" if platform.system() == "Darwin" else "xdg-open"
                subprocess.call([opener, filename])
        except Exception as ex:
            mostrar_mensagem(
                page, f"Erro ao abrir comprovante: {ex}", ft.Colors.RED)

        modal_comprovante.open = False
        page.update()

    def mostrar_qr_code(e):
        """Gera e exibe um QR Code com o texto do comprovante."""
        texto = gerar_texto_comprovante(state.ultima_venda_id)
        if not texto:
            mostrar_mensagem(page, "Erro ao gerar comprovante.", ft.Colors.RED)
            return

        qr = qrcode.QRCode(version=None, box_size=10, border=4)
        qr.add_data(texto)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")

        buffer = BytesIO()
        img.save(buffer, format="PNG")
        img_str = base64.b64encode(buffer.getvalue()).decode("utf-8")

        # Atualiza o conteúdo do modal existente para mostrar o QR Code
        modal_comprovante.title = ft.Text("Escaneie o QR Code")
        modal_comprovante.content = ft.Column([
            ft.Image(src_base64=img_str, width=300, height=300, fit=ft.ImageFit.CONTAIN),
            ft.Text("Aponte a câmera para ler o comprovante", text_align=ft.TextAlign.CENTER)
        ], tight=True, horizontal_alignment=ft.CrossAxisAlignment.CENTER, width=300)
        
        modal_comprovante.actions = [
            ft.TextButton("Voltar", on_click=lambda e: abrir_modal_comprovante()),
            ft.TextButton("Fechar", on_click=lambda e: fechar_dialogo(modal_comprovante))
        ]
        modal_comprovante.update()

    def enviar_whatsapp(e):
        """Abre o WhatsApp com o comprovante pronto para ser enviado."""
        texto = gerar_texto_comprovante(state.ultima_venda_id)
        if not texto:
            mostrar_mensagem(page, "Erro ao gerar comprovante.", ft.Colors.RED)
            return

        numero_cliente = whatsapp_numero_field.value.strip()
        if not numero_cliente.isdigit() or len(numero_cliente) < 10:
            whatsapp_numero_field.error_text = "19987790800"
            whatsapp_numero_field.update()
            return

        whatsapp_numero_field.error_text = ""
        whatsapp_numero_field.update()

        texto_url = urllib.parse.quote(texto)
        url = f"https://wa.me/55{numero_cliente}?text={texto_url}"

        webbrowser.open(url)
        modal_comprovante.open = False
        page.update()

    def fechar_dialogo(dialogo):
        dialogo.open = False
        page.update()

    def abrir_modal_comprovante():
        """Abre o modal com as opções de compartilhamento do comprovante."""
        if not state.ultima_venda_id:
            return
        whatsapp_numero_field.value = ""
        whatsapp_numero_field.error_text = ""
        
        # Reconstrói o conteúdo do menu principal do modal
        modal_comprovante.title = ft.Text("Venda Registrada! E agora?", weight="bold")
        modal_comprovante.content = ft.Column([
            ft.Text("Escolha como deseja fornecer o comprovante ao cliente."),
            ft.Divider(),
            ft.ElevatedButton("🖨️ Imprimir / Salvar .txt",
                             icon=ft.Icons.PRINT, on_click=imprimir_comprovante_local, width=300),
            ft.ElevatedButton("📋 Copiar Texto do Comprovante",
                             icon=ft.Icons.COPY, on_click=copiar_comprovante, width=300),
            ft.ElevatedButton("📱 Exibir QR Code na Tela",
                             icon=ft.Icons.QR_CODE_2, on_click=mostrar_qr_code, width=300),
            ft.Divider(),
            ft.Text("Enviar via WhatsApp:", weight="bold"),
            whatsapp_numero_field,
            ft.ElevatedButton("↗️ Enviar via WhatsApp", icon=ft.Icons.SEND,
                             on_click=enviar_whatsapp, width=300, bgcolor=ft.Colors.GREEN_700, color=ft.Colors.WHITE),
        ], tight=True, spacing=10, width=300)
        
        modal_comprovante.actions = [
            ft.TextButton("Fechar", on_click=lambda e: fechar_dialogo(modal_comprovante))
        ]
        
        page.dialog = modal_comprovante
        modal_comprovante.open = True
        page.update()

    whatsapp_numero_field = ft.TextField(
        label="Nº do WhatsApp do Cliente (DDD + Número)", prefix_text="+55")

    modal_comprovante = ft.AlertDialog(
        modal=True,
        # Conteúdo inicial vazio, será preenchido por abrir_modal_comprovante
        title=ft.Text(""),
        content=ft.Container(),
        actions=[],
        actions_alignment=ft.MainAxisAlignment.END
    )

    # ==============================================================
    # LAYOUT PRINCIPAL
    # ==============================================================

    # Cabeçalho

    # Logo
    logo_image = ft.Image(
        src="gata.png",
        height=150,
        fit=ft.ImageFit.CONTAIN
    )

    logo_container = ft.Container(
        content=logo_image,
        padding=ft.padding.only(right=15),
        on_click=voltar_pagina_inicial,
        ink=True,
        border_radius=10
    )
    # Textos
    title_text = ft.Text(
        "GRAÇA PRESENTES",
        size=30,
        weight=ft.FontWeight.W_800,
        color=ft.Colors.WHITE
    )

    description_text = ft.Text(
        "Sistema de gerenciamento de produtos",
        size=16,
        color=ft.Colors.WHITE70
    )

    texts_column = ft.Column(
        [title_text, description_text],
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=3
    )
    # Botões
    relatorios_button = ft.IconButton(
        icon=ft.Icons.INSERT_CHART_OUTLINED_SHARP,
        icon_size=40,
        icon_color=ft.Colors.WHITE,
        tooltip="Relatórios",
        on_click=mostrar_relatorios,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=10),
            padding=15,
            overlay_color="#0F0904FF"  # Branco com 10% de opacidade
        )
    )

    checkout_button = ft.IconButton(
        icon=ft.Icons.SHOPPING_CART_CHECKOUT_OUTLINED,
        icon_size=40,
        icon_color=ft.Colors.WHITE,
        tooltip="Finalizar Compra",
        on_click=abrir_checkout,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=10),
            padding=15,
            overlay_color="#0E7676FF"  # Branco com 10% de opacidade
        )
    )

    buttons_row = ft.Row(
        [relatorios_button, checkout_button],
        spacing=15,
        alignment=ft.MainAxisAlignment.END
    )
    # Área da Logo + Texto
    logo_and_text_row = ft.Row(
        [
            logo_container,
            texts_column
        ],
        alignment=ft.MainAxisAlignment.START,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
        expand=True
    )

    # Cabeçalho
    header = ft.Container(
        content=ft.Row(
            [
                logo_and_text_row,
                buttons_row
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER
        ),
        padding=ft.padding.symmetric(horizontal=30, vertical=5),

        margin=ft.margin.only(bottom=5),
        gradient=ft.LinearGradient(
            begin=ft.alignment.top_left,
            end=ft.alignment.bottom_right,
            colors=["#E30D78", "#0DEA83", "#c8ccdedc"]
        ),
        shadow=ft.BoxShadow(
            spread_radius=1,
            blur_radius=20,
            color="#800d47a1",
            offset=ft.Offset(0, 6)
        ),
        height=110


    )

# Formulário de cadastro
    form_cadastro = ft.Container(
        width=400,
        content=ft.Column(
            [
                ft.Container(
                    content=ft.Text("Cadastro de Produtos",
                                    size=20, weight=ft.FontWeight.BOLD),
                    padding=10
                ),
                ft.Divider(),
                codigo_produto,
                nome_produto,
                preco_produto,
                quantidade_produto,
                categoria_produto,
                descricao_produto,
                ft.Container(
                    content=ft.Column([
                        ft.ElevatedButton(
                            "Escolher Imagem",
                            on_click=pick_files,
                            icon=ft.Icons.IMAGE,
                            style=ft.ButtonStyle(
                                bgcolor=ft.Colors.BLUE_700,
                                color=ft.Colors.WHITE
                            )
                        ),
                        image_preview
                    ], spacing=10),
                    padding=10,
                    alignment=ft.alignment.center
                ),
                ft.Row(
                    [
                        ft.ElevatedButton(
                            "Limpar",
                            icon=ft.Icons.CLEAR,
                            on_click=limpar_formulario,
                            style=ft.ButtonStyle(
                                bgcolor=ft.Colors.GREY_300,
                                color=ft.Colors.BLACK
                            )
                        ),
                        ft.ElevatedButton(
                            "Salvar",
                            icon=ft.Icons.SAVE,
                            on_click=cadastrar_produto,
                            style=ft.ButtonStyle(
                                bgcolor=ft.Colors.BLUE_700,
                                color=ft.Colors.WHITE
                            )
                        )
                    ],
                    spacing=10,
                    alignment=ft.MainAxisAlignment.END
                ), ft.Row([success_salvar_text, nao_salva])
            ],
            scroll=ft.ScrollMode.AUTO
        ),
        padding=10,
        margin=ft.margin.only(right=20),
        border=ft.border.all(1, ft.Colors.GREY_300),
        border_radius=10
    )

    # Busca de produtos
    form_busca = ft.Container(
        content=ft.Column([
            ft.Text("Buscar Produtos", size=20, weight=ft.FontWeight.BOLD),
            ft.Divider(),
            ft.Row([
                campo_busca,
                ft.ElevatedButton(
                    "Buscar",
                    icon=ft.Icons.SEARCH,
                    on_click=buscar_produto,
                    style=ft.ButtonStyle(
                        bgcolor=ft.Colors.BLUE_700,
                        color=ft.Colors.WHITE
                    )
                ),
            ]),
            ft.Row([
                ft.Container(
                    content=resultados_busca,
                    border=ft.border.all(1, ft.Colors.GREY_300),
                    border_radius=5,
                    padding=10,
                    height=300,
                    width=450
                ),
                ft.Container(
                    content=busca_image_preview,
                    alignment=ft.alignment.center,
                    padding=10,
                    expand=True
                )
            ], vertical_alignment=ft.CrossAxisAlignment.START)
        ]),
        padding=10,
        border=ft.border.all(1, ft.Colors.GREY_300),
        border_radius=10
    )

    # Carrinho de compras
    secao_carrinho = ft.Container(
        content=ft.Column(
            [
                ft.Container(
                    content=ft.Text("Carrinho de Compras", size=20,
                                    weight=ft.FontWeight.BOLD),
                    padding=10
                ),
                ft.Divider(),
                ft.Row([
                    seletor_produto,
                    quantidade_compra,
                    ft.ElevatedButton(
                        "Adicionar",
                        icon=ft.Icons.ADD,
                        on_click=adicionar_ao_carrinho,
                        style=ft.ButtonStyle(
                            bgcolor=ft.Colors.GREEN_700,
                            color=ft.Colors.WHITE,
                            padding=10
                        )
                    )
                ], spacing=10),
                ft.Container(
                    content=itens_carrinho,
                    border=ft.border.all(1, ft.Colors.GREY_300),
                    border_radius=5,
                    padding=10,
                    height=250
                ),

                ft.Row(
                    [
                        ft.ElevatedButton(
                            "Limpar",
                            icon=ft.Icons.DELETE,
                            on_click=limpar_carrinho,
                            style=ft.ButtonStyle(
                                bgcolor=ft.Colors.RED_700,
                                color=ft.Colors.WHITE
                            )
                        ),
                        ft.ElevatedButton(
                            "Finalizar",
                            icon=ft.Icons.CHECK_CIRCLE_OUTLINE,
                            on_click=abrir_checkout,
                            style=ft.ButtonStyle(
                                bgcolor=ft.Colors.ORANGE_700,
                                color=ft.Colors.WHITE
                            )
                        )
                    ],
                    spacing=10,
                    alignment=ft.MainAxisAlignment.END
                )
            ]
        ),
        padding=10,
        border=ft.border.all(1, ft.Colors.GREY_300),
        border_radius=10
    )

    # Mensagem de exclusão
    success_delete_text = ft.Text("", size=20, color=ft.Colors.RED, weight=ft.FontWeight.BOLD)

    # Produtos cadastrados
    secao_produtos = ft.Container(
        content=ft.Column(
            [
                ft.Container(
                    content=ft.Text("Produtos Cadastrados", size=20,
                                    weight=ft.FontWeight.BOLD),
                    padding=10
                ),
                success_delete_text,
                ft.Divider(),
                ft.Column(
                    [tabela_produtos],
                    scroll=ft.ScrollMode.AUTO,
                    expand=True
                )
            ],
            expand=True
        ),
        padding=10,
        border=ft.border.all(1, ft.Colors.GREY_300),
        border_radius=10,
        expand=True
    )

    # Botões de navegação
    Botao_pagina_cadastro = ft.ElevatedButton(
        "Cadastrar Produtos",
        icon=ft.Icons.ADD_BOX,
        on_click=cadastrar_produto_pagina,
        style=ft.ButtonStyle(
            bgcolor=ft.Colors.BLUE_700,
            color=ft.Colors.WHITE,
            padding=20
        ),
        height=50,
        width=200
    )

    botao_voltar = ft.ElevatedButton(
        "Voltar Página Inicial",
        icon=ft.Icons.ARROW_BACK,
        on_click=voltar_pagina_inicial,
        style=ft.ButtonStyle(
            bgcolor=ft.Colors.GREY_700,
            color=ft.Colors.WHITE,
            padding=10


        ),
        height=50,
        width=200
    )

    # ==============================================================
    # INICIALIZAÇÃO DA APLICAÇÃO
    # ==============================================================

    # Monta a página inicial
    linhacadastros = ft.Row(controls=[form_cadastro, secao_produtos], alignment=ft.MainAxisAlignment.START,
                            vertical_alignment=ft.CrossAxisAlignment.START, spacing=20)

    page.add(header)
    page.add(ft.Container(
        content=ft.Column([
            ft.Column([success_vendas_text, success_text_remover], spacing=0),
            ft.Row([
                ft.Column([secao_carrinho, form_busca, Botao_pagina_cadastro], expand=2)
            ], expand=True)
        ]),
        padding=ft.padding.only(left=20, right=20, bottom=20, top=0)
    ))

    # Adiciona os modais ao final para garantir que o header fique no topo (índice 0)
    page.add(modal_checkout)
    page.add(modal_dados_cartao)
    page.add(modal_comprovante)
    page.add(modal_produto)
    page.add(modal_exclusao)

    # Inicialização

    atualizar_tabela_produtos()
    atualizar_seletor_produtos()
    page.update()


if __name__ == "__main__":
    criar_banco()

    ft.app(target=main)
