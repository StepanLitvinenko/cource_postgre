from dataclasses import dataclass

from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter
from psycopg.rows import class_row
from rich.panel import Panel
from rich.table import Table

from console import console, render_error
from db import get_conn
from validators import ChoiceValidator, NonEmptyValidator, YesNoValidator
from commands import command, CATEGORY_WAREHOUSES

cities = [
    "Москва",
    "Санкт-Петербург",
    "Новосибирск",
    "Екатеринбург",
    "Казань",
    "Нижний Новгород",
    "Челябинск",
    "Самара",
    "Омск",
    "Ростов-на-Дону",
    "Уфа",
    "Красноярск",
    "Воронеж",
    "Пермь",
    "Волгоград",
]

city_completer = WordCompleter(cities, ignore_case=True, sentence=True)
city_validator = ChoiceValidator(
    cities, message="Город должен быть из списка. Используйте Tab для автодополнения."
)


@dataclass
class Warehouse:
    id: int
    city: str
    address: str
    is_central: bool
    label: str | None


def _render_warehouse(warehouse: Warehouse) -> None:
    table = Table(show_header=False, box=None, padding=(0, 2))

    table.add_column("Поле", style="bold cyan", width=15)
    table.add_column("Значение", style="white")

    table.add_row("ID", str(warehouse.id))
    table.add_row("Город", warehouse.city)
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


@command("list warehouses", "список всех складов", CATEGORY_WAREHOUSES)
def list_warehouses() -> None:
    conn = get_conn()
    table = Table(title="Склады", show_header=True, header_style="bold cyan")

    table.add_column("ID", style="dim", width=6, justify="right")
    table.add_column("Город", style="green", min_width=20)
    table.add_column("Адрес", style="yellow", min_width=30)
    table.add_column("Центральный?", style="magenta", min_width=15)
    table.add_column("Метка", style="magenta", min_width=15)

    with conn.cursor(row_factory=class_row(Warehouse)) as cur:
        cur.execute("SELECT * FROM catalog.warehouses")
        warehouses: list[Warehouse] = cur.fetchall()

    for warehouse in warehouses:
        table.add_row(
            str(warehouse.id),
            warehouse.city,
            warehouse.address,
            str(warehouse.is_central),
            warehouse.label or "",
        )
    console.print(table)


@command("show warehouse", "информация о складе", CATEGORY_WAREHOUSES)
def show_warehouse(_id: str) -> None:
    conn = get_conn()
    with conn.cursor(row_factory=class_row(Warehouse)) as cur:
        cur.execute("SELECT * FROM catalog.warehouses WHERE id = %s", (_id,))
        warehouse: Warehouse | None = cur.fetchone()

    if warehouse is None:
        render_error(f"Склад с ID {_id} не найден")
        return

    _render_warehouse(warehouse)


@command("add warehouse", "добавить склад (интерактивно)", CATEGORY_WAREHOUSES)
def add_warehouse() -> None:
    conn = get_conn()
    city = prompt("Город: ", validator=city_validator, completer=city_completer).strip()
    address = prompt("Адрес: ", validator=NonEmptyValidator()).strip()
    label = prompt("Метка (необязательно): ").strip() or None
    is_central = YesNoValidator.is_yes(
        prompt("Сделать центральным? (y/n): ", validator=YesNoValidator()).strip()
    )

    with conn.cursor() as cur:
        if is_central:
            cur.execute("UPDATE catalog.warehouses SET is_central = false")

        cur.execute(
            "INSERT INTO catalog.warehouses (city, address, label, is_central) VALUES (%s, %s, %s, %s)",
            (city, address, label, is_central),
        )
        conn.commit()

    console.print(f"[green]Склад в городе {city} добавлен[/green]")
    if is_central:
        console.print("[green]Склад сделан центральным[/green]")


def select_new_central_warehouse(exclude_id: int) -> int | None:
    conn = get_conn()

    with conn.cursor(row_factory=class_row(Warehouse)) as cur:
        cur.execute(
            "SELECT * FROM catalog.warehouses WHERE id != %s ORDER BY id",
            (exclude_id,)
        )
        other_warehouses = cur.fetchall()

    if not other_warehouses:
        render_error("Всегда дольжен быть ОДИН центральный склад")
        return None


    console.print("\n[bold]Список кандидатов на звание центральногоо:[/bold]")
    for wh in other_warehouses:
        central_marker = " [bold cyan](текущий цнтральный)[/bold cyan]" if wh.is_central else ""
        console.print(f"  [cyan]{wh.id}[/cyan]: {wh.city}, {wh.address}{central_marker}")

    while True:
        try:
            new_id = int(
                prompt("Введите ID нового центрального склада: ", validator=NonEmptyValidator()).strip()
            )
            if any(wh.id == new_id for wh in other_warehouses):
                return new_id
            else:
                render_error(f"Склад с ID {new_id} не найден. Попробуйте снова.")
        except ValueError:
            render_error("ID должен быть числом.")

@command("edit warehouse", "редактировать склад", CATEGORY_WAREHOUSES)
def edit_warehouse(_id: str) -> None:
    conn = get_conn()

    with conn.cursor(row_factory=class_row(Warehouse)) as cur:
        cur.execute("SELECT * FROM catalog.warehouses WHERE id = %s", (_id,))
        warehouse: Warehouse | None = cur.fetchone()

    if warehouse is None:
        render_error(f"Склад с ID {_id} не найден")
        return

    _render_warehouse(warehouse)

    city = prompt(
        "Город: ",
        default=warehouse.city,
        validator=city_validator,
        completer=city_completer,
    ).strip()
    address = prompt(
        "Адрес: ", default=warehouse.address, validator=NonEmptyValidator()
    ).strip()
    label = (
            prompt("Метка (необязательно): ", default=warehouse.label or "").strip() or None
    )

    make_central = YesNoValidator.is_yes(
        prompt("Сделать этот склад центральным? (y/n): ", validator=YesNoValidator()).strip()
    )

    new_central_id = None
    if make_central:

        if not warehouse.is_central:

            with conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) FROM catalog.warehouses WHERE id != %s", (_id,))
                count = cur.fetchone()[0]
                if count == 0:
                    render_error("Нет других складов. Невозможно сделать этот склад центральным, т.к. он единственный.")
                    return

            new_central_id = int(_id)
        else:
            console.print("[yellow]Склад уже является центральным. Статус не изменен.[/yellow]")
    else:
        if warehouse.is_central:
            console.print("[yellow] Вы убираете центральный статус у текущего склада \n  Необходимо выбрать другой склад, который станет центральным[/yellow]")


            new_central_id = select_new_central_warehouse(int(_id))

            if new_central_id is None:
                return
    with conn.cursor() as cur:
        if new_central_id is not None:
            cur.execute("UPDATE catalog.warehouses SET is_central = false")
            cur.execute(
                "UPDATE catalog.warehouses SET is_central = true WHERE id = %s",
                (new_central_id,)
            )

        cur.execute(
            """UPDATE catalog.warehouses 
               SET city = %s, address = %s, label = %s 
               WHERE id = %s""",
            (city, address, label, _id)
        )
        conn.commit()

    console.print(f"[green]Склад в городе {city} обновлен[/green]")
    if new_central_id is not None:
        if new_central_id == int(_id):
            console.print("[green]Склад теперь центральный[/green]")
        else:
            with conn.cursor(row_factory=class_row(Warehouse)) as cur:
                cur.execute("SELECT * FROM catalog.warehouses WHERE id = %s", (new_central_id,))
                new_central = cur.fetchone()
            if new_central:
                console.print(f"[green]Новый центральный склад: {new_central.city} (ID: {new_central.id})[/green]")

@command("delete warehouse", "удалить склад", CATEGORY_WAREHOUSES)
def delete_warehouse(_id: str) -> None:
    conn = get_conn()
    with conn.cursor(row_factory=class_row(Warehouse)) as cur:
        cur.execute("SELECT * FROM catalog.warehouses WHERE id = %s", (_id,))
        warehouse: Warehouse | None = cur.fetchone()

    if warehouse is None:
        render_error(f"Склад с ID {_id} не найден")
        return

    _render_warehouse(warehouse)

    answer = prompt("Вы уверены? (y/n, д/н): ", validator=YesNoValidator())

    if YesNoValidator.is_yes(answer):
        conn.execute("DELETE FROM catalog.warehouses WHERE id = %s", (_id,))
        if warehouse.label:
            console.print(
                f"[green]Склад в городе {warehouse.city} ({warehouse.label}) удален [/green]"
            )
        else:
            console.print(f"[green]Склад в городе {warehouse.city} удален [/green]")
