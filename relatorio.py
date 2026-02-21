import flet as ft
import sqlite3
from database import *


def obter_resumo_vendas():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT SUM(total), COUNT(*), AVG(total) FROM vendas")
    total, qtd, ticket = cursor.fetchone()
    conn.close()
    return total or 0, qtd or 0, ticket or 0


def obter_formas_pagamento():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT forma_pagamento, COUNT(*) FROM vendas GROUP BY forma_pagamento")
    dados = cursor.fetchall()
    conn.close()
    return dados


def obter_evolucao_vendas():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT DATE(data_venda), SUM(total)
        FROM vendas
        GROUP BY DATE(data_venda)
        ORDER BY DATE(data_venda)
    """)
    dados = cursor.fetchall()
    conn.close()
    return dados


def obter_evolucao_por_pagamento():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT DATE(data_venda), forma_pagamento, SUM(total)
        FROM vendas
        GROUP BY DATE(data_venda), forma_pagamento
        ORDER BY DATE(data_venda)
    """)
    rows = cursor.fetchall()
    conn.close()

    dados = {}
    formas = set()
    for data, forma, total in rows:
        formas.add(forma)
        if data not in dados:
            dados[data] = {}
        dados[data][forma] = total

    return sorted(dados.items()), sorted(list(formas))


def obter_produtos_mais_vendidos():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT nome, SUM(quantidade)
        FROM itens_vendidos
        GROUP BY produto_codigo, nome
        ORDER BY SUM(quantidade) DESC
    """)
    dados = cursor.fetchall()
    conn.close()
    return dados


def obter_vendas_por_dia(data_alvo):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT iv.nome, SUM(iv.quantidade)
        FROM itens_vendidos iv
        JOIN vendas v ON iv.venda_id = v.id
        WHERE DATE(v.data_venda) = ?
        GROUP BY iv.produto_codigo, iv.nome
        ORDER BY SUM(iv.quantidade) DESC
    """, (data_alvo,))
    resultados = cursor.fetchall()
    conn.close()
    return resultados


def obter_dados_estoque():
    """Obtém dados de estoque do banco de dados"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT nome, quantidade FROM produtos ORDER BY quantidade DESC")
    dados = cursor.fetchall()
    conn.close()
    return dados


def obter_detalhes_cartao():
    """Obtém relatório detalhado de vendas no cartão"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT v.id, v.data_venda, v.total, d.nome_cliente, d.tipo_cartao, d.parcelas
        FROM vendas v
        JOIN dados_cartao d ON v.id = d.venda_id
        ORDER BY v.data_venda DESC
    """)
    dados = cursor.fetchall()
    conn.close()
    return dados

# ----------------- COMPONENTES -----------------
PRIMARY_COLOR = ft.Colors.BLUE_600
SECONDARY_COLOR = ft.Colors.BLUE_50
TEXT_COLOR = ft.Colors.GREY_900
HIGHLIGHT_COLOR = ft.Colors.GREEN_600


class DashboardGraficos:
    def __init__(self, page):
        self.page = page
        self.cards = self.criar_cards_resumo()
        self.grafico_pizza = self.criar_grafico_pizza()
        self.grafico_linha_pagamento = self.criar_grafico_linha_pagamento()
        self.grafico_barras = self.criar_grafico_barras()
        self.tabela_cartoes = self.criar_tabela_cartoes()

    def atualizar_tudo(self):
        """Atualiza todos os componentes do dashboard"""
        self.cards = self.criar_cards_resumo()
        self.grafico_pizza = self.criar_grafico_pizza()
        self.grafico_linha_pagamento = self.criar_grafico_linha_pagamento()
        self.grafico_barras = self.criar_grafico_barras()
        self.tabela_cartoes = self.criar_tabela_cartoes()
        self.page.update()

    def criar_cards_resumo(self):
        total, qtd, ticket = obter_resumo_vendas()
        cards = [
            ("💰 Total Vendido", f"R$ {total:,.2f}"),
            ("🛒 Nº de Vendas", str(qtd)),
            ("📊 Ticket Médio", f"R$ {ticket:,.2f}")
        ]

        return ft.Row(
            controls=[
                ft.Container(
                    content=ft.Column(
                        [ft.Text(titulo, size=16, weight="bold", color=TEXT_COLOR),
                         ft.Text(valor, size=20, color=PRIMARY_COLOR, weight="bold")],
                        spacing=5
                    ),
                    padding=20,
                    border_radius=15,
                    bgcolor=SECONDARY_COLOR,
                    expand=True
                ) for titulo, valor in cards
            ],
            expand=True
        )

    def criar_grafico_pizza(self):
        dados = obter_formas_pagamento()
        if not dados:
            return ft.Text("Nenhuma venda registrada")

        return ft.Container(
            content=ft.Column([
                ft.Text("💳 Vendas por Forma de Pagamento",
                        size=20, weight="bold", color=TEXT_COLOR),
                ft.PieChart(
                    sections=[
                        ft.PieChartSection(valor, title=f"{forma} ({valor})")
                        for forma, valor in dados
                    ],
                    sections_space=2,
                    center_space_radius=40,
                    expand=True
                )
            ], spacing=10),
            padding=10,
            border_radius=15,
            bgcolor=SECONDARY_COLOR,
            expand=True
        )

    def criar_grafico_linha_pagamento(self):
        dados, formas = obter_evolucao_por_pagamento()
        if not dados:
            return ft.Text("Nenhuma venda registrada")

        cores = [PRIMARY_COLOR, ft.Colors.RED_600,
                 ft.Colors.ORANGE_600, ft.Colors.PURPLE_600]

        series = []
        for i, forma in enumerate(formas):
            pontos = []
            for idx, (data, valores) in enumerate(dados):
                pontos.append(ft.LineChartDataPoint(
                    idx, valores.get(forma, 0)))
            series.append(ft.LineChartData(
                data_points=pontos,
                stroke_width=3,
                color=cores[i % len(cores)],
                curved=True
            ))

        return ft.Container(
            content=ft.Column([
                ft.Text("📊 Evolução por Forma de Pagamento",
                        size=20, weight="bold", color=TEXT_COLOR),
                ft.LineChart(
                    data_series=series,
                    bottom_axis=ft.ChartAxis(
                        labels=[
                            ft.ChartAxisLabel(
                                value=i, label=ft.Text(data, size=12))
                            for i, (data, _) in enumerate(dados)
                        ]
                    ),
                    expand=True,
                    interactive=True,
                    max_y=max([max(valores.values())
                              for _, valores in dados]) * 1.2 if dados else 100
                )
            ], spacing=10),
            padding=10,
            border_radius=15,
            bgcolor=SECONDARY_COLOR,
            expand=True
        )

    def criar_grafico_barras(self):
        dados = obter_produtos_mais_vendidos()
        if not dados:
            return ft.Container(
                content=ft.Text("Nenhum produto vendido"),
                padding=20,
                border_radius=15,
                bgcolor=SECONDARY_COLOR,
                height=300,
                alignment=ft.alignment.center
            )

        # Ordenar dados por quantidade (decrescente)
        dados_ordenados = sorted(dados, key=lambda x: x[1], reverse=True)

        # Configurações
        max_bar_height = 120
        max_quantidade = max([qtd for _, qtd in dados_ordenados]) * 1.1
        cores = [PRIMARY_COLOR, ft.Colors.GREEN_600, ft.Colors.ORANGE_600,
                 ft.Colors.PURPLE_600, ft.Colors.RED_600, ft.Colors.TEAL_600,
                 ft.Colors.BLUE_400, ft.Colors.AMBER_600]

        # Criar barras verticais organizadas
        barras_verticais = []
        for idx, (produto, quantidade) in enumerate(dados_ordenados):
            bar_height = (quantidade / max_quantidade) * max_bar_height

            barras_verticais.append(
                ft.Container(
                    content=ft.Column(
                        [
                            # Valor no topo (grande e em destaque)
                            ft.Container(
                                content=ft.Text(
                                    f"{quantidade}",
                                    size=16,
                                    weight=ft.FontWeight.BOLD,
                                    color=ft.Colors.BLACK
                                ),
                                height=30,
                                alignment=ft.alignment.center
                            ),

                            # Barra vertical
                            ft.Container(
                                width=25,
                                height=bar_height,
                                bgcolor=cores[idx % len(cores)],
                                border_radius=ft.border_radius.only(
                                    top_left=5,
                                    top_right=5
                                ),
                                alignment=ft.alignment.bottom_center
                            ),

                            # Nome do produto
                            ft.Container(
                                content=ft.Column(
                                    [
                                        ft.Text(
                                            produto[:15] +
                                            ("..." if len(produto) > 15 else ""),
                                            size=11,
                                            weight=ft.FontWeight.BOLD,
                                            color=ft.Colors.GREY_800,
                                            text_align=ft.TextAlign.CENTER
                                        ),
                                        ft.Text(
                                            f"{quantidade} un",
                                            size=10,
                                            color=ft.Colors.GREY_500,
                                            text_align=ft.TextAlign.CENTER
                                        )
                                    ],
                                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                    spacing=2
                                ),
                                width=80,
                                padding=ft.padding.only(top=8),
                                alignment=ft.alignment.top_center
                            )
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=2,
                        alignment=ft.MainAxisAlignment.START
                    ),
                    margin=ft.margin.symmetric(horizontal=5),
                    tooltip=f"{produto}\n{quantidade} unidades vendidas"
                )
            )

        # Calcular total geral
        total_geral = sum([qtd for _, qtd in dados_ordenados])

        return ft.Container(
            content=ft.Column(
                [
                    # Cabeçalho
                    ft.Container(
                        content=ft.Text(
                            "🏆 Produtos Mais Vendidos",
                            size=18,
                            weight=ft.FontWeight.BOLD,
                            color=TEXT_COLOR
                        ),
                        alignment=ft.alignment.center,
                        padding=ft.padding.only(bottom=15)
                    ),

                    # Gráfico de barras verticais
                    ft.Container(
                        content=ft.Row(
                            controls=barras_verticais,
                            spacing=8,
                            alignment=ft.MainAxisAlignment.CENTER,
                            vertical_alignment=ft.CrossAxisAlignment.END
                        ),
                        padding=ft.padding.symmetric(
                            horizontal=10, vertical=15),
                        alignment=ft.alignment.center
                    ),

                    # Linha divisória
                    ft.Divider(height=1, color=ft.Colors.GREY_300),

                    # Resumo total (igual ao "dadu" da imagem)
                    ft.Container(
                        content=ft.Row(
                            [
                                ft.Text(
                                    "Total Geral",
                                    size=14,
                                    weight=ft.FontWeight.BOLD,
                                    color=ft.Colors.BLUE_700
                                ),
                                ft.Container(expand=True),
                                ft.Text(
                                    f"{total_geral} unidades",
                                    size=16,
                                    weight=ft.FontWeight.BOLD,
                                    color=ft.Colors.GREY_800
                                )
                            ],
                            vertical_alignment=ft.CrossAxisAlignment.CENTER
                        ),
                        padding=ft.padding.symmetric(
                            vertical=15, horizontal=20)
                    )
                ],
                spacing=0
            ),
            padding=ft.padding.all(20),
            border_radius=15,
            bgcolor=SECONDARY_COLOR,
            border=ft.border.all(1, ft.Colors.GREY_300)
        )

    def criar_grafico_estoque(self):
        """Cria gráfico de barras horizontais para estoque de produtos"""
        # Obtém os dados do banco
        dados = obter_dados_estoque()

        # Ordena os dados em ordem decrescente por quantidade
        dados_ordenados = sorted(dados, key=lambda x: x[1], reverse=True)

        if not dados_ordenados:
            return ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.INVENTORY_2, size=40,
                            color=ft.Colors.GREY_400),
                    ft.Text("Nenhum produto em estoque",
                            size=16, color=ft.Colors.GREY_600, italic=True)
                ], alignment=ft.MainAxisAlignment.CENTER, spacing=10),
                height=300,
                alignment=ft.alignment.center
            )

        # Cores modernas em gradiente
        cores = [
            ft.Colors.BLUE_700,
            ft.Colors.TEAL_600,
            ft.Colors.INDIGO_600,
            ft.Colors.PURPLE_600,
            ft.Colors.CYAN_600,
            ft.Colors.BLUE_600,
            ft.Colors.TEAL_500
        ]

        max_quantidade = max(
            [quantidade for _, quantidade in dados_ordenados]) * 1.2

        # Calcular largura máxima para escala das barras horizontais
        max_bar_width = 400  # Largura máxima em pixels

        # Criar barras horizontais
        barras_horizontais = []
        for idx, (nome, quantidade) in enumerate(dados_ordenados):
            bar_width = (quantidade / max_quantidade) * max_bar_width

            barras_horizontais.append(
                ft.Row(
                    [
                        # Nome do produto
                        ft.Container(
                            content=ft.Row([
                                ft.Container(
                                    width=10,
                                    height=10,
                                    border_radius=5,
                                    bgcolor=cores[idx % len(cores)],
                                    margin=ft.margin.only(right=10)
                                ),
                                ft.Column([
                                    ft.Text(
                                        nome[:18] +
                                        ("..." if len(nome) > 18 else ""),
                                        size=13,
                                        weight=ft.FontWeight.BOLD,
                                        color=ft.Colors.GREY_800
                                    ),
                                    ft.Text(
                                        f"{quantidade} unidades",
                                        size=11,
                                        color=ft.Colors.GREY_500
                                    )
                                ], spacing=2)
                            ]),
                            width=200
                        ),

                        # Barra horizontal
                        ft.Container(
                            width=bar_width,
                            height=25,
                            bgcolor=cores[idx % len(cores)],
                            border_radius=ft.border_radius.only(
                                top_right=8,
                                bottom_right=8
                            ),
                            tooltip=f"{nome}\nEstoque: {quantidade} unidades",
                            border=ft.border.all(
                                1, ft.Colors.WHITE30)  # Correção aqui
                        ),

                        # Valor numérico
                        ft.Text(
                            f"{quantidade}",
                            size=12,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.GREY_700,
                            width=60,
                            text_align=ft.TextAlign.RIGHT
                        )
                    ],
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=10,
                    height=35
                )
            )

        return ft.Container(
            content=ft.Column([
                # Cabeçalho
                ft.Container(
                    content=ft.Column([
                        ft.Text("📦 ESTOQUE POR PRODUTO",
                                size=20,
                                weight=ft.FontWeight.BOLD,
                                color=ft.Colors.BLUE_800,
                                text_align=ft.TextAlign.CENTER),
                        ft.Text("Quantidade disponível em estoque",
                                size=14,
                                color=ft.Colors.GREY_600,
                                text_align=ft.TextAlign.CENTER)
                    ], spacing=5),
                    padding=ft.padding.only(bottom=20)
                ),

                # Gráfico de barras horizontais
                ft.Container(
                    content=ft.Column(
                        controls=barras_horizontais,
                        spacing=8
                    ),
                    padding=ft.padding.symmetric(horizontal=20)
                ),

                # Resumo e estatísticas
                ft.Container(
                    content=ft.Column([
                        ft.Divider(color=ft.Colors.GREY_200),

                        ft.Row([
                            ft.Text("📋 RESUMO GERAL",
                                    size=14,
                                    weight=ft.FontWeight.BOLD,
                                    color=ft.Colors.BLUE_700),
                            ft.Container(expand=True),
                            ft.Text(f"Total: {sum([q for _, q in dados_ordenados])} unidades",
                                    size=20,
                                    color=ft.Colors.GREY_600)
                        ]),

                        # Cards com os produtos principais
                        ft.Row([
                            ft.Container(
                                content=ft.Column([
                                    ft.Text(f"{idx + 1}º",
                                            size=12,
                                            color=ft.Colors.GREY_500),
                                    ft.Text(nome[:12] + ("..." if len(nome) > 12 else ""),
                                            size=13,
                                            weight=ft.FontWeight.BOLD),
                                    ft.Text(f"{quantidade}",
                                            size=16,
                                            color=cores[idx % len(cores)],
                                            weight=ft.FontWeight.BOLD)
                                ], spacing=3, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                                padding=15,
                                border_radius=10,
                                bgcolor=ft.Colors.GREY_50,
                                width=120,
                                alignment=ft.alignment.center
                            ) for idx, (nome, quantidade) in enumerate(dados_ordenados[:3])
                        ], spacing=10, alignment=ft.MainAxisAlignment.SPACE_AROUND)
                    ], spacing=15),
                    padding=ft.padding.only(top=20)
                )

            ], spacing=0),

            padding=ft.padding.all(25),
            border=ft.border.all(1, ft.Colors.GREY_200),
            border_radius=16,
            bgcolor=ft.Colors.WHITE,
            shadow=ft.BoxShadow(
                spread_radius=0,
                blur_radius=20,
                color=ft.Colors.BLUE_100,
                offset=ft.Offset(0, 4)
            )
        )

    def criar_tabela_cartoes(self):
        """Cria uma tabela detalhada com as vendas de cartão"""
        dados = obter_detalhes_cartao()

        if not dados:
            return ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.CREDIT_CARD_OFF, size=40, color=ft.Colors.GREY_400),
                    ft.Text("Nenhuma venda com cartão registrada", color=ft.Colors.GREY_600)
                ], alignment=ft.MainAxisAlignment.CENTER, spacing=10),
                padding=20,
                border_radius=15,
                bgcolor=SECONDARY_COLOR,
                alignment=ft.alignment.center,
                height=200,
                expand=True
            )

        # Formatação das linhas
        linhas = []
        for id_venda, data, total, nome, tipo, parcelas in dados:
            # Formatar data
            try:
                data_obj = datetime.strptime(data, '%Y-%m-%d %H:%M:%S')
                data_fmt = data_obj.strftime('%d/%m/%Y %H:%M')
            except:
                data_fmt = data

            linhas.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(data_fmt)),
                        ft.DataCell(ft.Text(nome or "Não informado")),
                        ft.DataCell(ft.Text(tipo.upper(), color=ft.Colors.BLUE_700 if tipo == 'credito' else ft.Colors.GREEN_700, weight="bold")),
                        ft.DataCell(ft.Text(f"{parcelas}x")),
                        ft.DataCell(ft.Text(f"R$ {total:.2f}", weight="bold")),
                    ]
                )
            )

        return ft.Container(
            content=ft.Column([
                ft.Text("💳 Detalhamento de Vendas no Cartão", 
                       size=20, weight="bold", color=TEXT_COLOR),
                ft.Column(
                    controls=[ft.DataTable(
                        columns=[
                            ft.DataColumn(ft.Text("Data/Hora", weight="bold")),
                            ft.DataColumn(ft.Text("Cliente", weight="bold")),
                            ft.DataColumn(ft.Text("Tipo", weight="bold")),
                            ft.DataColumn(ft.Text("Parc.", weight="bold")),
                            ft.DataColumn(ft.Text("Valor", weight="bold")),
                        ],
                        rows=linhas,
                        heading_row_color=ft.Colors.BLUE_100,
                    )],
                    scroll=ft.ScrollMode.AUTO, # Permite rolar se a tabela for grande
                    expand=True
                )
            ], spacing=15),
            padding=25,
            border_radius=15,
            bgcolor=SECONDARY_COLOR,
            expand=True,
            height=400
        )

def criar_tabela_vendas(dados):
    return ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Produto", weight="bold", color=TEXT_COLOR)),
            ft.DataColumn(
                ft.Text("Qtd Vendida", weight="bold", color=TEXT_COLOR))
        ],
        rows=[
            ft.DataRow(cells=[ft.DataCell(ft.Text(produto)),
                              ft.DataCell(ft.Text(str(qtd)))])
            for produto, qtd in dados
        ],
        expand=True,
        heading_row_color=PRIMARY_COLOR,
        border=ft.border.all(1, ft.Colors.GREY_300),
        border_radius=10
    )


def criar_grafico_vendas(dados=None):
    cores = [
        PRIMARY_COLOR,
        ft.Colors.GREEN_600,
        ft.Colors.ORANGE_600,
        ft.Colors.PURPLE_600,
    ]

    if not dados:  # se não veio nada, mostra aviso em vez de gráfico
        return ft.Text("Nenhuma venda encontrada", color="red", size=300)

    max_qtd = max([qtd for _, qtd in dados]) * 1.2 if dados else 10

    return ft.BarChart(
        bar_groups=[
            ft.BarChartGroup(
                x=idx,
                bar_rods=[
                    ft.BarChartRod(
                        from_y=0,
                        to_y=qtd,
                        width=40,
                        color=cores[idx % len(cores)],
                        tooltip=f"{produto}: {qtd}",
                        border_radius=5,

                    )
                ],
            )
            for idx, (produto, qtd) in enumerate(dados)
        ],
        bottom_axis=ft.ChartAxis(
            labels=[
                ft.ChartAxisLabel(
                    value=idx,
                    label=ft.Text(produto[:10], size=12),
                )
                for idx, (produto, _) in enumerate(dados)
            ]
        ),
        max_y=max_qtd,
        expand=True,
        interactive=True,
    )
