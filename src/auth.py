import argparse
from typing import Final, Sequence

from prompt_toolkit import prompt

from console import console
from users import User, find_user_by_login_and_pass

ROLE_CATALOG_MANAGER: Final[str] = "catalog_manager"
ROLE_SALES_MANAGER: Final[str] = "sales_manager"

ALL_ROLES: Final[Sequence[str]] = (
    ROLE_SALES_MANAGER,
    ROLE_CATALOG_MANAGER,
)

_USER: User | None = None


def login(username: str | None = None, password: str | None = None) -> None:
    """Аутентификация пользователя. Сначала пытается через CLI, затем интерактивно."""
    global _USER

    if username and password:
        user = find_user_by_login_and_pass(username, password)
        if user:
            if user.role not in ALL_ROLES:
                raise ValueError(f"Invalid user role: {user.role}")
            console.print(
                f"\n[green]✓ Вошел: {user.username} ({user.role})[/green]\n"
            )
            _USER = user
            return

        console.print("\n[red]✗ не получилось войти из CLI[/red]")

    console.print("\n[bold cyan]═══════════════════════════════════════[/bold cyan]")
    console.print("[bold cyan]   Вход в систему[/bold cyan]")
    console.print("[bold cyan]═══════════════════════════════════════[/bold cyan]\n")

    while True:
        username_input = prompt("Имя пользователя: ").strip()
        password_input = prompt("Пароль: ", is_password=True).strip()

        user = find_user_by_login_and_pass(username_input, password_input)

        if user:
            if user.role not in ALL_ROLES:
                raise ValueError(f"Invalid user role: {user.role}")
            console.print(
                f"\n[green]Djitk {user.username} ({user.role})[/green]\n"
            )
            _USER = user
            return

        console.print("\n[red]✗ Неверное имя пользователя или пароль[/red]\n")


def auth_user() -> User:
    """Возвращает аутентифицированного пользователя."""
    if _USER is None:
        raise RuntimeError("Not authenticated")
    return _USER


def get_current_user_role() -> str:
    """Возвращает роль текущего пользователя."""
    return auth_user().role
