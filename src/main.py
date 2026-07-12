import logging
import argparse

from prompt_toolkit import PromptSession

from console import console, render_error
from db import connect, DB_USER
from setup import setup_logger
from auth import login, auth_user

# pylint: disable-next=unused-import
import handlers
from commands import get_completer, find_command, get_args

setup_logger(psycopg_log_level=logging.INFO)


def main() -> None:
    # Парсим CLI аргументы
    parser = argparse.ArgumentParser(description="Inventory Management System")
    parser.add_argument("-u", "--username", help="Username for authentication")
    parser.add_argument("-p", "--password", help="Password for authentication")
    cli_args = parser.parse_args()

    # Подключение к БД
    connect()
    logging.info("App Started")

    # Аутентификация
    login(username=cli_args.username, password=cli_args.password)

    # Вывод заголовка через rich
    user = auth_user()
    console.print("\n[bold cyan]═══════════════════════════════════════[/bold cyan]")
    console.print("[bold cyan]   Inventory Management System[/bold cyan]")
    console.print("[bold cyan]═══════════════════════════════════════[/bold cyan]")
    console.print(f"[dim]Подключено к БД: inventorydb (user: {DB_USER})[/dim]")
    console.print(f"[dim]Пользователь: {user.username} (роль: {user.role})[/dim]\n")

    # Создаём сессию prompt_toolkit с автодополнением команд
    completer = get_completer()
    session: PromptSession[str] = PromptSession(completer=completer)

    # Формируем промпт с именем пользователя
    prompt_text = f"{user.username} ({user.role})> "

    # Основной цикл
    while True:
        try:
            _input = session.prompt(prompt_text).strip()

            if not _input:
                continue

            # Выход - обрабатываем отдельно
            if _input == "exit":
                break

            cmd = find_command(_input)
            if cmd:
                args = get_args(_input, cmd) if cmd.args else {}
                cmd.handler(**args)
            else:
                console.print(f"[red]Неизвестная команда: {_input}[/red]")
                console.print("[dim]Введите 'help' для списка команд[/dim]\n")

        except KeyboardInterrupt:
            break
        except Exception as e:
            logging.exception(e)
            render_error(f"Ошибка: {e}")

    console.print("\n[cyan]До свидания![/cyan]\n")


if __name__ == "__main__":
    main()
