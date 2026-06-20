from dataclasses import dataclass
from decimal import Decimal
from typing import List

from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter
from psycopg.rows import class_row
from rich.panel import Panel
from rich.table import Table

from console import console, render_error
from db import get_conn
from validators import ChoiceValidator, NonEmptyValidator, YesNoValidator
from commands import command, CATEGORY_CATEGORIES


@dataclass
class ProductCategory:
    id: int
    category_type: str


def _render_category(category: ProductCategory):  # pylint: disable=unused-argument
    table = Table(show_header=False, box=None, padding=(0, 2))

    table.add_column("Поле", style="bold cyan", width=15)
    table.add_column("Значение", style="white")

    table.add_row("ID", str(category.id))
    table.add_row("Категория", category.category_type)

    panel = Panel(
        table,
        expand=False,
        border_style="green",
    )

    console.print(panel)


def get_list_categories() -> List[str]:
    conn = get_conn()
    table = Table(title="Категории", show_header=True, header_style="bold cyan")
    ret: List[str] = []

    with conn.cursor(row_factory=class_row(ProductCategory)) as cur:
        cur.execute("SELECT * FROM catalog.product_categories")
        categories: list[ProductCategory] = cur.fetchall()

    for category in categories:
        ret.append(category.category_type)

    return ret


@command("list categories", "список всех категорий", CATEGORY_CATEGORIES)
def list_categories() -> None:
    conn = get_conn()
    table = Table(title="Категории", show_header=True, header_style="bold cyan")

    table.add_column("ID", style="dim", width=6, justify="right")
    table.add_column("Category", style="green", min_width=20)

    with conn.cursor(row_factory=class_row(ProductCategory)) as cur:
        cur.execute("SELECT * FROM catalog.product_categories")
        categories: list[ProductCategory] = cur.fetchall()

    for category in categories:
        table.add_row(
            str(category.id),
            category.category_type
        )
    console.print(table)


@command("show category", "информация о категории", CATEGORY_CATEGORIES)
def show_category(_id: str) -> None:
    conn = get_conn()
    with conn.cursor(row_factory=class_row(ProductCategory)) as cur:
        cur.execute("SELECT * FROM catalog.product_categories WHERE id = %s", (_id,))
        category: ProductCategory | None = cur.fetchone()

    if category is None:
        render_error(f"Категория с ID {_id} не найдена")
        return

    _render_category(category)


@command("add category", "добавить категорию товаров (интерактивно)", CATEGORY_CATEGORIES)
def add_category() -> None:
    conn = get_conn()
    category = prompt("Категория: ", validator=NonEmptyValidator()).strip()
    conn.execute(
        "INSERT INTO catalog.product_categories (category_type) VALUES (%s)",
        [category]
    )

    console.print(f"[green]Добавлена категория  {category}  [/green]")


@command("edit category", "редактировать товар", CATEGORY_CATEGORIES)
def edit_category(_id: str) -> None:
    conn = get_conn()
    with conn.cursor(row_factory=class_row(ProductCategory)) as cur:
        cur.execute("SELECT * FROM catalog.product_categories WHERE id = %s", (_id,))
        categoryProduct: ProductCategory | None = cur.fetchone()

    if categoryProduct is None:
        render_error(f"Категория с ID {_id} не найдена")
        return

    category = prompt(
        "Категрия: ",
        default=categoryProduct.category_type
    ).strip()

    conn.execute(
        """UPDATE catalog.product_categories SET category_type = %s
        WHERE id = %s""",
        (category, _id),
    )

    console.print(f"[green]Изменилась категория, было: {categoryProduct.category_type}, стало {category}  [/green]")


@command("delete category", "удалить категорию", CATEGORY_CATEGORIES)
def delete_category(_id: str) -> None:
    conn = get_conn()
    with conn.cursor(row_factory=class_row(ProductCategory)) as cur:
        cur.execute("SELECT * FROM catalog.product_categories WHERE id = %s", (_id,))
        categoryProduct: ProductCategory | None = cur.fetchone()

    if categoryProduct is None:
        render_error(f"Категория с ID {_id} не найдена")
        return

    _render_category(categoryProduct)

    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM catalog.products WHERE category_id = %s", (_id,))
        count = cur.fetchone()[0]

    warning = ""
    if count > 0:
        warning = f" В категории {count} товаров, они будут удалены!"

    answer = prompt(
        f"Вы уверены, что хотите удалить категорию?{warning} (y/n, д/н): ",
        validator=YesNoValidator()
    )

    if YesNoValidator.is_yes(answer):
        with conn.cursor() as cur:

            cur.execute("DELETE FROM catalog.products WHERE category_id = %s", (_id,))

            cur.execute("DELETE FROM catalog.product_categories WHERE id = %s", (_id,))

            conn.commit()

        console.print(
            f"[green]Удалена категория {categoryProduct.category_type} и все товары в ней[/green]"
        )