from db import get_conn
from prompt_toolkit.shortcuts import choice
from console import console, render_error



def select_category():
    conn = get_conn()

    categories = conn.execute(
        "SELECT id, category_type FROM catalog.product_categories ORDER BY id"
    ).fetchall()

    if not categories:
        render_error("Нет ни одной категории. Сначала создайте категорию.")
        return


    options = [(str(cat_id), f"{cat_id}: {cat_name}") for cat_id, cat_name in categories]


    selected_id_str = choice(
        message="Выберите категорию:",
        options=options,
        default=options[0][0] if options else None
    )


    category_id = int(selected_id_str)
    category_name = next(name for cat_id, name in categories if str(cat_id) == selected_id_str)
    return category_id, category_name