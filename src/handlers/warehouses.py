from dataclasses import dataclass

from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter
from rich.panel import Panel
from rich.table import Table

from console import console, render_error
from db import get_conn
from validators import ChoiceValidator, NonEmptyValidator, YesNoValidator
from commands import command, CATEGORY_WAREHOUSES
from auth import ROLE_CATALOG_MANAGER, ROLE_SALES_MANAGER


def get_cities() -> list[str]:
    """Возвращает список городов из БД."""
    conn = get_conn()
    with conn.cursor() as cur:
        cur.execute("SELECT name FROM catalog.cities ORDER BY name")
        rows = cur.fetchall()
        return [row[0] for row in rows]


def get_city_completer() -> WordCompleter:
    """Создает комплитер для городов."""
    return WordCompleter(get_cities(), ignore_case=True, sentence=True)


def get_city_validator() -> ChoiceValidator:
    """Создает валидатор для городов."""
    return ChoiceValidator(get_cities(), message="Город должен быть из списка. Используйте Tab для автодополнения.")


@dataclass
class Warehouse:
    id: int
    city_id: int
    city_name: str
    address: str
    is_central: bool
    label: str | None


def _render_warehouse(warehouse: Warehouse) -> None:
    table = Table(show_header=False, box=None, padding=(0, 2))

    table.add_column("Поле", style="bold cyan", width=15)
    table.add_column("Значение", style="white")

    table.add_row("ID", str(warehouse.id))
    table.add_row("Город", warehouse.city_name)
    table.add_row("Адрес", warehouse.address)
    table.add_row("Центральный?", str(warehouse.is_central))
    table.add_row("Метка", warehouse.label or "")

    panel = Panel(
        table,
        expand=False,
        title=f"[bold green]Склад #{warehouse.id}[/bold green]",
        border_style="green",
    )

    console.print(panel)


@command("list warehouses", "список всех складов", CATEGORY_WAREHOUSES, [ROLE_CATALOG_MANAGER, ROLE_SALES_MANAGER])
def list_warehouses() -> None:
    conn = get_conn()
    table = Table(title="Склады", show_header=True, header_style="bold cyan")

    table.add_column("ID", style="dim", width=6, justify="right")
    table.add_column("Город", style="green", min_width=20)
    table.add_column("Адрес", style="yellow", min_width=30)
    table.add_column("Центральный?", style="magenta", min_width=15)
    table.add_column("Метка", style="magenta", min_width=15)

    with conn.cursor() as cur:
        cur.execute("""
            SELECT 
                w.id,
                w.city_id,
                c.name AS city_name,
                w.address,
                w.is_central,
                w.label
            FROM catalog.warehouses w
            JOIN catalog.cities c ON w.city_id = c.id
            ORDER BY w.id
        """)
        rows = cur.fetchall()

    for row in rows:
        table.add_row(
            str(row[0]),
            row[2],
            row[3],
            str(row[4]),
            row[5] or "",
        )

    console.print(table)


@command("show warehouse", "информация о складе", CATEGORY_WAREHOUSES, [ROLE_CATALOG_MANAGER, ROLE_SALES_MANAGER])
def show_warehouse(_id: str) -> None:
    conn = get_conn()
    with conn.cursor() as cur:
        cur.execute("""
            SELECT 
                w.id,
                w.city_id,
                c.name AS city_name,
                w.address,
                w.is_central,
                w.label
            FROM catalog.warehouses w
            JOIN catalog.cities c ON w.city_id = c.id
            WHERE w.id = %s
        """, (_id,))
        row = cur.fetchone()

    if row is None:
        render_error(f"Склад с ID {_id} не найден")
        return

    warehouse = Warehouse(
        id=row[0],
        city_id=row[1],
        city_name=row[2],
        address=row[3],
        is_central=row[4],
        label=row[5]
    )
    _render_warehouse(warehouse)


@command("add warehouse", "добавить склад (интерактивно)", CATEGORY_WAREHOUSES, [ROLE_CATALOG_MANAGER])
def add_warehouse() -> None:
    conn = get_conn()

    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM catalog.warehouses")
        count = cur.fetchone()[0]
        is_first_warehouse = (count == 0)

    city_name = prompt("Город: ", validator=get_city_validator(), completer=get_city_completer()).strip()
    address = prompt("Адрес: ", validator=NonEmptyValidator()).strip()
    label = prompt("Метка (необязательно): ").strip() or None

    if is_first_warehouse:
        is_central = True
        console.print("[yellow]Первый склад всегда центральный.[/yellow]")
    else:
        is_central = YesNoValidator.is_yes(
            prompt("Сделать этот склад центральным? (y/n): ", validator=YesNoValidator()).strip()
        )

    with conn.cursor() as cur:
        cur.execute("SELECT id FROM catalog.cities WHERE name = %s", (city_name,))
        city_id = cur.fetchone()[0]

        cur.execute(
            "INSERT INTO catalog.warehouses (city_id, address, label, is_central) VALUES (%s, %s, %s, %s)",
            (city_id, address, label, is_central),
        )
        conn.commit()

    console.print(f"[green]Склад в городе {city_name} добавлен[/green]")
    if is_central:
        console.print("[green]Склад сделан центральным[/green]")


@command("edit warehouse", "редактировать склад", CATEGORY_WAREHOUSES, [ROLE_CATALOG_MANAGER])
def edit_warehouse(_id: str) -> None:
    conn = get_conn()

    with conn.cursor() as cur:
        cur.execute("""
            SELECT 
                w.id,
                w.city_id,
                c.name AS city_name,
                w.address,
                w.is_central,
                w.label
            FROM catalog.warehouses w
            JOIN catalog.cities c ON w.city_id = c.id
            WHERE w.id = %s
        """, (_id,))
        row = cur.fetchone()

    if row is None:
        render_error(f"Склад с ID {_id} не найден")
        return

    warehouse = Warehouse(
        id=row[0],
        city_id=row[1],
        city_name=row[2],
        address=row[3],
        is_central=row[4],
        label=row[5]
    )
    _render_warehouse(warehouse)

    city_name = prompt(
        "Город: ",
        default=warehouse.city_name,
        validator=get_city_validator(),
        completer=get_city_completer(),
    ).strip()

    address = prompt(
        "Адрес: ", default=warehouse.address, validator=NonEmptyValidator()
    ).strip()
    label = (
        prompt("Метка (необязательно): ", default=warehouse.label or "").strip() or None
    )

    is_central = warehouse.is_central

    if not warehouse.is_central:
        make_central = YesNoValidator.is_yes(
            prompt("Сделать этот склад центральным? (y/n): ", validator=YesNoValidator()).strip()
        )
        if make_central:
            is_central = True
    else:
        console.print("[dim]Склад уже является центральным. Статус не изменен.[/dim]")

    with conn.cursor() as cur:
        cur.execute("SELECT id FROM catalog.cities WHERE name = %s", (city_name,))
        city_id = cur.fetchone()[0]

        cur.execute(
            """UPDATE catalog.warehouses 
               SET city_id = %s, address = %s, label = %s, is_central = %s
               WHERE id = %s""",
            (city_id, address, label, is_central, _id)
        )
        conn.commit()

    console.print(f"[green]Склад в городе {city_name} обновлен[/green]")
    if is_central and not warehouse.is_central:
        console.print("[green]Склад теперь центральный[/green]")


@command("delete warehouse", "удалить склад", CATEGORY_WAREHOUSES, [ROLE_CATALOG_MANAGER])
def delete_warehouse(_id: str) -> None:
    conn = get_conn()

    with conn.cursor() as cur:
        cur.execute("""
            SELECT 
                w.id,
                w.city_id,
                c.name AS city_name,
                w.address,
                w.is_central,
                w.label
            FROM catalog.warehouses w
            JOIN catalog.cities c ON w.city_id = c.id
            WHERE w.id = %s
        """, (_id,))
        row = cur.fetchone()

    if row is None:
        render_error(f"Склад с ID {_id} не найден")
        return

    warehouse = Warehouse(
        id=row[0],
        city_id=row[1],
        city_name=row[2],
        address=row[3],
        is_central=row[4],
        label=row[5]
    )

    if warehouse.is_central:
        render_error("Нельзя удалить центральный склад.")
        return

    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM sales.orders WHERE warehouse_id = %s", (_id,))
        count = cur.fetchone()[0]
        if count > 0:
            render_error(f"Отказано. На складе висит {count} заказов.")
            return

    _render_warehouse(warehouse)

    answer = prompt("Вы уверены? (y/n, д/н): ", validator=YesNoValidator())

    if YesNoValidator.is_yes(answer):
        conn.execute("DELETE FROM catalog.warehouses WHERE id = %s", (_id,))
        if warehouse.label:
            console.print(
                f"[green]Склад в городе {warehouse.city_name} ({warehouse.label}) удален [/green]"
            )
        else:
            console.print(f"[green]Склад в городе {warehouse.city_name} удален [/green]")