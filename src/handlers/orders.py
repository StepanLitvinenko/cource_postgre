from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from prompt_toolkit import prompt
from prompt_toolkit.shortcuts import choice
from prompt_toolkit.completion import WordCompleter

from psycopg.rows import class_row
from rich.panel import Panel
from rich.table import Table

from commands import command, CATEGORY_ORDERS
from console import console, render_error
from db import get_conn
from validators import NonEmptyValidator, YesNoValidator, QuantityValidator


@dataclass
class Order:
    id: int
    status: str
    total_amount: Decimal
    created_at: datetime
    updated_at: datetime
    warehouse_id: int


@dataclass
class OrderWithDetails(Order):
    warehouse_city: str
    warehouse_address: str


@dataclass
class OrderItem:
    id: int
    order_id: int
    product_id: int
    quantity: int
    price: Decimal
    created_at: datetime
    updated_at: datetime
    product_name: Optional[str] = None
    product_sku: Optional[str] = None


def _recalculate_order_total(order_id: int) -> None:
    """Пересчитывает сумму заказа и обновляет её в БД"""
    conn = get_conn()

    with conn.cursor() as cur:
        # Считаем сумму всех позиций
        cur.execute("""
            SELECT COALESCE(SUM(quantity * price), 0)
            FROM sales.order_items
            WHERE order_id = %s
        """, (order_id,))
        total = cur.fetchone()[0]

        # Обновляем заказ
        cur.execute(
            "UPDATE sales.orders SET total_amount = %s WHERE id = %s",
            (total, order_id)
        )
        conn.commit()

def _render_order(order: OrderWithDetails) -> None:
    table = Table(show_header=False, box=None, padding=(0, 2))

    table.add_column("Поле", style="bold cyan", width=15)
    table.add_column("Значение", style="white")

    table.add_row("ID", str(order.id))
    table.add_row("Статус", order.status)
    table.add_row("Сумма", f"{order.total_amount:.2f}")
    table.add_row("Создан", order.created_at.strftime("%Y-%m-%d %H:%M:%S"))
    table.add_row("Склад", f"{order.warehouse_city}, {order.warehouse_address}")

    panel = Panel(table, expand=False, title=f"[bold green]Заказ #{order.id}[/bold green]", border_style="green")
    console.print(panel)


def _render_order_items(order_id: int) -> None:
    conn = get_conn()

    # джойним чтобы получить вместо id товара его название
    with conn.cursor(row_factory=class_row(OrderItem)) as cur:
        cur.execute("""
            SELECT 
                sales.order_items.id,
                sales.order_items.order_id,
                sales.order_items.product_id,
                sales.order_items.quantity,
                sales.order_items.price,
                sales.order_items.created_at,
                sales.order_items.updated_at,
                catalog.products.name AS product_name,
                catalog.products.sku AS product_sku
            FROM sales.order_items
            JOIN catalog.products ON sales.order_items.product_id = catalog.products.id
            WHERE sales.order_items.order_id = %s
            ORDER BY sales.order_items.id
        """, (order_id,))
        items: List[OrderItem] = cur.fetchall()

    if not items:
        console.print("[yellow]В заказе нет НИЧЕГО[/yellow]")
        return

    table = Table(title=f"Позиции заказа #{order_id}", show_header=True, header_style="bold cyan")
    table.add_column("ID", style="dim", width=6, justify="right")
    table.add_column("SKU", style="green", min_width=15)
    table.add_column("Товар", style="yellow", min_width=25)
    table.add_column("Кол-во", style="magenta", justify="right")
    table.add_column("Цена", style="cyan", justify="right")
    table.add_column("Сумма", style="green", justify="right")

    for item in items:
        total = item.quantity * item.price
        table.add_row(
            str(item.id),
            item.product_sku or "",
            item.product_name or f"Товар #{item.product_id}",
            str(item.quantity),
            f"{item.price:.2f}",
            f"{total:.2f}"
        )

    console.print(table)


@command("list orders", "список всех заказов", CATEGORY_ORDERS)
def list_orders() -> None:
    conn = get_conn()
    table = Table(title="Заказы", show_header=True, header_style="bold cyan")

    table.add_column("ID", style="dim", width=6, justify="right")
    table.add_column("Статус", style="green", min_width=12)
    table.add_column("Сумма", style="magenta", justify="right")
    table.add_column("Создан", style="yellow", min_width=20)
    table.add_column("Склад", style="blue", min_width=20)

    with conn.cursor(row_factory=class_row(OrderWithDetails)) as cur:
        cur.execute("""
            SELECT 
                sales.orders.id,
                sales.orders.status,
                sales.orders.total_amount,
                sales.orders.created_at,
                sales.orders.updated_at,
                sales.orders.warehouse_id,
                catalog.warehouses.city AS warehouse_city,
                catalog.warehouses.address AS warehouse_address
            FROM sales.orders
            JOIN catalog.warehouses ON sales.orders.warehouse_id = catalog.warehouses.id
            ORDER BY sales.orders.id DESC
        """)
        orders = cur.fetchall()

    for order in orders:
        table.add_row(
            str(order.id),
            order.status,
            f"{order.total_amount:.2f}",
            order.created_at.strftime("%Y-%m-%d %H:%M"),
            order.warehouse_city
        )

    console.print(table)


@command("show order", "информация о заказе", CATEGORY_ORDERS)
def show_order(_id: str) -> None:
    conn = get_conn()

    with conn.cursor(row_factory=class_row(OrderWithDetails)) as cur:
        cur.execute("""
            SELECT 
                sales.orders.id,
                sales.orders.status,
                sales.orders.total_amount,
                sales.orders.created_at,
                sales.orders.updated_at,
                sales.orders.warehouse_id,
                catalog.warehouses.city AS warehouse_city,
                catalog.warehouses.address AS warehouse_address
            FROM sales.orders
            JOIN catalog.warehouses ON sales.orders.warehouse_id = catalog.warehouses.id
            WHERE sales.orders.id = %s
        """, (_id,))
        order = cur.fetchone()

    if order is None:
        render_error(f"Заказ  {_id} не найден")
        return

    _render_order(order)
    _render_order_items(int(_id))


@command("add order", "создать новый заказ", CATEGORY_ORDERS)
def add_order() -> None:
    conn = get_conn()

    with conn.cursor() as cur:
        cur.execute("SELECT catalog.warehouses.id, catalog.warehouses.city FROM catalog.warehouses ORDER BY catalog.warehouses.city")
        warehouses = cur.fetchall()

    if not warehouses:
        render_error("Нет ни одного склада. Сначала создайте склад.")
        return

    options = [(str(warehouse_id), f"{warehouse_id}: {city}") for warehouse_id, city in warehouses]
    selected_warehouse_id = choice(
        message="Выберите склад для заказа:",
        options=options,
        default=options[0][0]
    )

    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO sales.orders (warehouse_id, status) VALUES (%s, 'unpublished') RETURNING id",
            (selected_warehouse_id,)
        )
        order_id = cur.fetchone()[0]
        conn.commit()

    console.print(f"[green]Создан заказ #{order_id}[/green]")

    add_more = YesNoValidator.is_yes(
        prompt("Добавить товар в заказ? (y/n): ", validator=YesNoValidator()).strip()
    )

    while add_more:
        _add_order_item(order_id)
        add_more = YesNoValidator.is_yes(
            prompt("Добавить еще товар? (y/n): ", validator=YesNoValidator()).strip()
        )

    show_order(str(order_id))


def _add_order_item(order_id: int) -> None:
    conn = get_conn()

    with conn.cursor() as cur:
        cur.execute("""
            SELECT 
                catalog.products.id,
                catalog.products.sku,
                catalog.products.name,
                catalog.products.price
            FROM catalog.products
            WHERE catalog.products.id NOT IN (
                SELECT sales.order_items.product_id 
                FROM sales.order_items 
                WHERE sales.order_items.order_id = %s
            )
            ORDER BY catalog.products.name
        """, (order_id,))
        products = cur.fetchall()

    if not products:
        render_error("Все доступные товары уже добавлены в заказ")
        return

    product_map = {str(p[0]): p for p in products}

    product_choices = [f"{p[0]}: {p[1]} - {p[2]}" for p in products]

    completer = WordCompleter(product_choices, ignore_case=True, sentence=True)

    console.print("[bold]Доступные товары:[/bold]")

    display_limit = min(10, len(products))

    for product in products[:display_limit]:
        console.print(f"  [cyan]{product[0]}[/cyan]: {product[1]} - {product[2]} ({product[3]:.2f})")
    if len(products) > display_limit:
        console.print(
            f"[dim] всего {len(products) - display_limit} товаров. [/dim]")

    while True:
        try:
            user_input = prompt(
                "Введите ID товара или начните вводить название/SKU : ",
                validator=NonEmptyValidator(),
                completer=completer
            ).strip()

            # Пытаемся извлечь ID из ввода (поддерживаем как "123", так и "123: SKU - Name")
            parts = user_input.split(':')
            if parts:
                candidate_id = parts[0].strip()
                if candidate_id in product_map:
                    product = product_map[candidate_id]
                    product_id = product[0]
                    break
            render_error("Товар не найден.")
        except Exception:
            render_error("error.")

    quantity = int(prompt("Количество: ", validator=QuantityValidator()).strip())

    with conn.cursor() as cur:
        cur.execute("SELECT catalog.products.price FROM catalog.products WHERE catalog.products.id = %s", (product_id,))
        price = cur.fetchone()[0]

    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO sales.order_items (order_id, product_id, quantity, price, updated_at) VALUES (%s, %s, %s, "
            "%s, CURRENT_TIMESTAMP)",
            (order_id, product_id, quantity, price)
        )
        conn.commit()

    _recalculate_order_total(order_id)
    console.print(f"[green]Товар добавлен в заказ #{order_id}[/green]")

@command("add order_item", "добавить товар в заказ", CATEGORY_ORDERS)
def add_order_item(order_id: str) -> None:
    conn = get_conn()

    with conn.cursor() as cur:
        cur.execute("SELECT sales.orders.status FROM sales.orders WHERE sales.orders.id = %s", (order_id,))
        result = cur.fetchone()

    if not result:
        render_error(f"Заказ с ID {order_id} не найден")
        return

    if result[0] != 'unpublished':
        render_error(f"Нельзя редактировать заказ со статусом '{result[0]}'")
        return

    _add_order_item(int(order_id))
    show_order(order_id)


@command("edit order_item", "редактировать позицию заказа", CATEGORY_ORDERS)
def edit_order_item(order_id: str) -> None:
    conn = get_conn()

    with conn.cursor() as cur:
        cur.execute("SELECT sales.orders.status FROM sales.orders WHERE sales.orders.id = %s", (order_id,))
        result = cur.fetchone()

    if not result:
        render_error(f"Заказ с ID {order_id} не найден")
        return

    if result[0] != 'unpublished':
        render_error(f"Нельзя редактировать заказ со статусом '{result[0]}'")
        return

    with conn.cursor(row_factory=class_row(OrderItem)) as cur:
        cur.execute("""
            SELECT 
                sales.order_items.id,
                sales.order_items.order_id,
                sales.order_items.product_id,
                sales.order_items.quantity,
                sales.order_items.price,
                sales.order_items.created_at,
                sales.order_items.updated_at,
                catalog.products.name AS product_name,
                catalog.products.sku AS product_sku
            FROM sales.order_items
            JOIN catalog.products ON sales.order_items.product_id = catalog.products.id
            WHERE sales.order_items.order_id = %s
            ORDER BY sales.order_items.id
        """, (order_id,))
        items = cur.fetchall()

    if not items:
        render_error("В заказе нет позиций для редактирования")
        return

    options = [(str(item.id), f"#{item.id}: {item.product_sku} - {item.product_name} (x{item.quantity})") for item in items]
    selected_id = choice(message="Выберите позицию для редактирования:", options=options, default=options[0][0])

    selected_item = next(item for item in items if str(item.id) == selected_id)

    new_quantity = int(
        prompt(f"Новое количество (текущее: {selected_item.quantity}): ", default=str(selected_item.quantity),
               validator=QuantityValidator()).strip())

    with conn.cursor() as cur:
        cur.execute("UPDATE sales.order_items SET quantity = %s WHERE sales.order_items.id = %s", (new_quantity, selected_id))
        conn.commit()

    _recalculate_order_total(int(order_id))
    console.print(f"[green]Позиция #{selected_id} обновлена[/green]")
    show_order(order_id)


@command("delete order_item", "удалить позицию из заказа", CATEGORY_ORDERS)
def delete_order_item(order_id: str) -> None:
    conn = get_conn()

    with conn.cursor() as cur:
        cur.execute("SELECT sales.orders.status FROM sales.orders WHERE sales.orders.id = %s", (order_id,))
        result = cur.fetchone()

    if not result:
        render_error(f"Заказ с ID {order_id} не найден")
        return

    if result[0] != 'unpublished':
        render_error(f"Нельзя редактировать заказ со статусом '{result[0]}'")
        return

    with conn.cursor(row_factory=class_row(OrderItem)) as cur:
        cur.execute("""
            SELECT 
                sales.order_items.id,
                sales.order_items.order_id,
                sales.order_items.product_id,
                sales.order_items.quantity,
                sales.order_items.price,
                sales.order_items.created_at,
                sales.order_items.updated_at,
                catalog.products.name AS product_name,
                catalog.products.sku AS product_sku
            FROM sales.order_items
            JOIN catalog.products ON sales.order_items.product_id = catalog.products.id
            WHERE sales.order_items.order_id = %s
            ORDER BY sales.order_items.id
        """, (order_id,))
        items = cur.fetchall()

    if not items:
        render_error("В заказе нет позиций для удаления")
        return

    options = [(str(item.id), f"#{item.id}: {item.product_sku} - {item.product_name} (x{item.quantity})") for item in items]
    selected_id = choice(message="Выберите позицию для удаления:", options=options, default=options[0][0])

    confirm = YesNoValidator.is_yes(prompt("Вы уверены? (y/n): ", validator=YesNoValidator()).strip())

    if confirm:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM sales.order_items WHERE sales.order_items.id = %s", (selected_id,))
            conn.commit()

        _recalculate_order_total(int(order_id))

        console.print(f"[green]Позиция #{selected_id} удалена[/green]")
        show_order(order_id)


@command("edit order", "редактировать заказ", CATEGORY_ORDERS)
def edit_order(_id: str) -> None:
    conn = get_conn()

    with conn.cursor() as cur:
        cur.execute("SELECT sales.orders.status, sales.orders.warehouse_id FROM sales.orders WHERE sales.orders.id = %s", (_id,))
        result = cur.fetchone()

    if not result:
        render_error(f"Заказ с ID {_id} не найден")
        return

    status, current_warehouse_id = result

    if status != 'unpublished':
        render_error(f"Нельзя редактировать заказ со статусом '{status}'")
        return

    with conn.cursor() as cur:
        cur.execute("SELECT catalog.warehouses.id, catalog.warehouses.city FROM catalog.warehouses ORDER BY catalog.warehouses.city")
        warehouses = cur.fetchall()

    options = [(str(warehouse_id), f"{warehouse_id}: {city}") for warehouse_id, city in warehouses]
    default_option = next((option for option in options if int(option[0]) == current_warehouse_id), options[0])

    selected_warehouse_id = choice(message="Выберите склад:", options=options, default=default_option[0])

    with conn.cursor() as cur:
        cur.execute("UPDATE sales.orders SET warehouse_id = %s WHERE sales.orders.id = %s", (selected_warehouse_id, _id))
        conn.commit()

    console.print(f"[green]Заказ #{_id} обновлен[/green]")
    show_order(_id)


@command("delete order", "удалить заказ", CATEGORY_ORDERS)
def delete_order(_id: str) -> None:
    conn = get_conn()

    with conn.cursor() as cur:
        cur.execute("SELECT sales.orders.status FROM sales.orders WHERE sales.orders.id = %s", (_id,))
        result = cur.fetchone()

    if not result:
        render_error(f"Заказ с ID {_id} не найден")
        return

    if result[0] != 'unpublished':
        render_error(f"Нельзя удалить заказ со статусом '{result[0]}'")
        return

    show_order(_id)

    confirm = YesNoValidator.is_yes(prompt("Вы уверены? (y/n): ", validator=YesNoValidator()).strip())

    if confirm:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM sales.orders WHERE sales.orders.id = %s", (_id,))
            conn.commit()
        console.print(f"[green]Заказ #{_id} удален[/green]")


@command("publish order", "опубликовать заказ", CATEGORY_ORDERS)
def publish_order(_id: str) -> None:
    conn = get_conn()

    with conn.cursor() as cur:
        cur.execute("""
            SELECT 
                sales.orders.status,
                COUNT(sales.order_items.id) AS items_count
            FROM sales.orders
            LEFT JOIN sales.order_items ON sales.orders.id = sales.order_items.order_id
            WHERE sales.orders.id = %s
            GROUP BY sales.orders.status
        """, (_id,))
        result = cur.fetchone()

    if not result:
        render_error(f"Заказ с ID {_id} не найден")
        return

    status, items_count = result

    if status != 'unpublished':
        render_error(f"Заказ уже имеет статус '{status}'. Публикация невозможна.")
        return

    if items_count == 0:
        render_error("Нельзя опубликовать пустой заказ. Добавьте хотя бы одну позицию.")
        return

    with conn.cursor() as cur:
        cur.execute("UPDATE sales.orders SET status = 'new' WHERE sales.orders.id = %s", (_id,))
        conn.commit()

    console.print(f"[green]Заказ #{_id} опубликован (статус: new)[/green]")
    console.print("[yellow]Теперь заказ нельзя редактировать или удалять[/yellow]")
    show_order(_id)