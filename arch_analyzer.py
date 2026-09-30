#!/usr/bin/env python3
"""
Анализатор структуры проекта
"""

import os
import sys
from typing import Dict, List, Optional
import time

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.prompt import Prompt
    from rich.table import Table
    from rich.text import Text
    from rich.tree import Tree
except ImportError:
    print("Не найдена библиотека rich. Установите: pip install rich")
    sys.exit(1)

console = Console()

# Иконка и цвет по расширению файла
ICONS = {
    '.py': ('🐍', 'yellow'),
    '.js': ('📜', 'bright_yellow'), '.ts': ('📜', 'bright_blue'),
    '.jsx': ('⚛', 'cyan'), '.tsx': ('⚛', 'cyan'),
    '.html': ('🌐', 'bright_red'), '.css': ('🎨', 'magenta'), '.scss': ('🎨', 'magenta'),
    '.md': ('📝', 'bright_white'), '.txt': ('📝', 'white'),
    '.json': ('⚙', 'green'), '.yaml': ('⚙', 'green'), '.yml': ('⚙', 'green'),
    '.toml': ('⚙', 'green'), '.ini': ('⚙', 'green'), '.env': ('⚙', 'green'),
    '.png': ('🖼', 'bright_magenta'), '.jpg': ('🖼', 'bright_magenta'),
    '.jpeg': ('🖼', 'bright_magenta'), '.gif': ('🖼', 'bright_magenta'),
    '.svg': ('🖼', 'bright_magenta'), '.ico': ('🖼', 'bright_magenta'),
    '.zip': ('📦', 'red'), '.rar': ('📦', 'red'), '.7z': ('📦', 'red'), '.tar': ('📦', 'red'), '.gz': ('📦', 'red'),
    '.exe': ('⚡', 'bright_green'), '.bat': ('⚡', 'bright_green'), '.ps1': ('⚡', 'bright_green'), '.sh': ('⚡', 'bright_green'),
}
DEFAULT_ICON = ('📄', 'white')


def fmt_size(size: int) -> str:
    """Переводит байты в читаемый вид"""
    if size >= 1024 ** 3:
        return f"{size / 1024 ** 3:.2f} GB"
    if size >= 1024 ** 2:
        return f"{size / 1024 ** 2:.2f} MB"
    if size >= 1024:
        return f"{size / 1024:.1f} KB"
    return f"{size} Б"


class ProjectAnalyzer:
    def __init__(self):
        self.exclude_dirs = [
            '.git', '__pycache__', '.venv', 'venv',
            'node_modules', '.idea', '.vscode', 'build',
            'dist', '.pytest_cache', '.coverage', '.mypy_cache'
        ]

        self.exclude_files = [
            '.gitignore', '.gitattributes', '.DS_Store',
            'Thumbs.db', 'desktop.ini'
        ]

    def get_path(self) -> Optional[str]:
        """Получаем путь от пользователя"""
        console.print(
            "[dim]Пример:[/] C:\\Users\\Name\\Projects\\myapp   "
            "[dim]или[/] [cyan].[/] [dim](текущая папка),[/] [cyan]..[/] [dim](папка выше),[/] [cyan]exit[/] [dim](выход)[/]"
        )

        while True:
            try:
                path_input = Prompt.ask("\n[bold cyan]Путь к проекту[/]").strip()

                if not path_input:
                    console.print("[red]Путь не может быть пустым![/]")
                    continue

                if path_input.lower() in ['exit', 'quit', 'выход']:
                    return None

                # Убираем кавычки
                path_input = path_input.strip('"\'')

                # Заменяем слеши для Windows
                path_input = path_input.replace('/', '\\')

                # Обработка текущей директории
                if path_input == '.':
                    path_input = os.getcwd()
                elif path_input == '..':
                    path_input = os.path.dirname(os.getcwd())

                # Обработка тильды
                if path_input.startswith('~'):
                    path_input = os.path.expanduser(path_input)

                # Расширение переменных окружения
                if '%' in path_input:
                    path_input = os.path.expandvars(path_input)

                # Проверяем существование пути
                if not os.path.exists(path_input):
                    console.print(f"[red]Путь не существует:[/] {path_input}")
                    console.print("[dim]Проверьте правильность пути и попробуйте снова[/]")
                    continue

                return os.path.abspath(path_input)

            except (KeyboardInterrupt, EOFError):
                return None
            except Exception as e:
                console.print(f"[red]Ошибка ввода:[/] {e}")
                continue

    def analyze_project(self, path: str) -> Dict:
        """Анализирует проект по указанному пути"""
        result = {
            'path': path,
            'name': os.path.basename(path),
            'is_file': os.path.isfile(path),
            'is_dir': os.path.isdir(path),
            'exists': True,
            'tree_structure': [],
            'stats': {
                'total_files': 0,
                'total_dirs': 0,
                'total_size': 0,
            },
            'scan_time': 0,
            'error': None
        }

        start_time = time.time()

        try:
            if result['is_file']:
                # Анализ одного файла
                self._analyze_single_file(path, result)
            elif result['is_dir']:
                # Полное сканирование с деревом
                result['tree_structure'] = self._build_tree_structure(path, path)
                # Собираем статистику из дерева
                self._collect_stats_from_tree(result)

        except PermissionError as e:
            result['error'] = f"Нет доступа: {e}"
        except Exception as e:
            result['error'] = f"Ошибка анализа: {e}"

        result['scan_time'] = time.time() - start_time
        return result

    def _analyze_single_file(self, file_path: str, result: Dict):
        """Анализирует один файл"""
        try:
            size = os.path.getsize(file_path)
            result['stats']['total_files'] = 1
            result['stats']['total_size'] = size

            result['tree_structure'].append({
                'name': os.path.basename(file_path),
                'type': 'file',
                'size': size,
                'path': '',
                'children': []
            })
        except Exception as e:
            result['error'] = f"Ошибка анализа файла: {e}"

    def _build_tree_structure(self, root_path: str, current_path: str, depth: int = 0, max_depth: int = 10) -> List[Dict]:
        """Рекурсивно строит структуру дерева"""
        if depth > max_depth:
            return []

        items = []

        try:
            with os.scandir(current_path) as entries:
                # Сортируем: сначала папки, потом файлы, все по алфавиту
                dirs = []
                files = []

                for entry in entries:
                    # Пропускаем скрытые файлы и исключенные папки
                    if (entry.name.startswith('.') or
                        entry.name in self.exclude_dirs or
                        entry.name in self.exclude_files):
                        continue

                    if entry.is_dir():
                        dirs.append(entry)
                    else:
                        files.append(entry)

                # Сортируем
                dirs.sort(key=lambda x: x.name.lower())
                files.sort(key=lambda x: x.name.lower())

                # Обрабатываем папки
                for entry in dirs:
                    try:
                        rel_path = os.path.relpath(entry.path, root_path)
                        children = self._build_tree_structure(root_path, entry.path, depth + 1, max_depth)

                        items.append({
                            'name': entry.name,
                            'type': 'dir',
                            'path': rel_path,
                            'size': sum(child['size'] for child in children),
                            'children': children
                        })
                    except (PermissionError, OSError):
                        # Нет доступа к папке
                        items.append({
                            'name': entry.name,
                            'type': 'dir',
                            'path': '',
                            'size': 0,
                            'children': [],
                            'error': 'Нет доступа'
                        })
                        continue

                # Обрабатываем файлы
                for entry in files:
                    try:
                        rel_path = os.path.relpath(entry.path, root_path)
                        size = entry.stat().st_size

                        items.append({
                            'name': entry.name,
                            'type': 'file',
                            'path': rel_path,
                            'size': size,
                            'children': []
                        })
                    except (PermissionError, OSError):
                        # Нет доступа к файлу
                        items.append({
                            'name': entry.name,
                            'type': 'file',
                            'path': '',
                            'size': 0,
                            'children': [],
                            'error': 'Нет доступа'
                        })
                        continue

        except (PermissionError, OSError):
            # Нет доступа к текущей папке
            pass

        return items

    def _collect_stats_from_tree(self, result: Dict):
        """Собирает статистику из дерева структуры"""
        def process_items(items: List[Dict]):
            for item in items:
                if item['type'] == 'file':
                    result['stats']['total_files'] += 1
                    result['stats']['total_size'] += item['size']
                elif item['type'] == 'dir':
                    result['stats']['total_dirs'] += 1
                    # Рекурсивно обрабатываем детей
                    process_items(item['children'])

        process_items(result['tree_structure'])

    def print_results(self, result: Dict):
        """Выводит результаты анализа"""
        if result['error']:
            console.print(f"[bold red]Ошибка:[/] {result['error']}")
            return

        stats = result['stats']
        info = Table.grid(padding=(0, 2))
        info.add_column(style="dim")
        info.add_column()
        info.add_row("Путь", result['path'])
        info.add_row("Тип", 'Файл' if result['is_file'] else 'Папка')
        if result['is_dir']:
            info.add_row("Папок", f"[bold]{stats['total_dirs']}[/]")
            info.add_row("Файлов", f"[bold]{stats['total_files']}[/]")
        info.add_row("Размер", f"[bold green]{fmt_size(stats['total_size'])}[/]")
        info.add_row("Время", f"{result['scan_time']:.2f} сек")

        console.print()
        console.print(Panel(info, title=f"[bold]{result['name']}[/]", border_style="cyan", expand=False))

        root = Tree(f"📦 [bold]{result['name']}[/]", guide_style="bright_black")
        self._to_rich_tree(result['tree_structure'], root)
        console.print(root)

    def _to_rich_tree(self, items: List[Dict], parent: Tree):
        """Рекурсивно добавляет элементы в rich-дерево"""
        for item in items:
            label = Text()
            if item['type'] == 'dir':
                label.append(f"📂 {item['name']}/", style="bold blue")
            else:
                icon, style = ICONS.get(os.path.splitext(item['name'])[1].lower(), DEFAULT_ICON)
                label.append(f"{icon} {item['name']}", style=style)

            if item.get('error'):
                label.append("  [Нет доступа]", style="red")
            else:
                label.append(f"  {fmt_size(item['size'])}", style="dim")

            branch = parent.add(label)
            self._to_rich_tree(item['children'], branch)

    def run(self):
        """Основной цикл программы"""
        console.print(Panel(
            "[bold]АНАЛИЗАТОР СТРУКТУРЫ ПРОЕКТОВ[/]\n[dim]Показывает полную структуру проекта[/]",
            border_style="cyan", expand=False
        ))

        while True:
            try:
                # Получаем путь от пользователя
                path = self.get_path()

                if path is None:
                    console.print("\n[dim]Выход из программы[/]")
                    break

                # Анализируем проект
                with console.status(f"[cyan]Сканирую[/] {path}…"):
                    result = self.analyze_project(path)

                # Выводим результаты
                self.print_results(result)

                # Спрашиваем, хочет ли пользователь проанализировать еще
                console.print()
                choice = Prompt.ask("Проанализировать другой проект? [cyan](y/n)[/]", default="n", show_default=False)
                if choice.lower().strip() not in ['y', 'yes', 'да', 'д']:
                    console.print("\n[bold cyan]Спасибо за использование программы![/]")
                    break

                console.rule(style="bright_black")

            except (KeyboardInterrupt, EOFError):
                console.print("\n\n[dim]Выход из программы[/]")
                break
            except Exception as e:
                console.print(f"\n[red]Неожиданная ошибка:[/] {e}")
                console.print("[dim]Попробуйте еще раз...[/]")
                continue

def main():
    """Точка входа в программу"""
    analyzer = ProjectAnalyzer()

    # Запускаем анализатор
    try:
        analyzer.run()
    except Exception as e:
        console.print(f"\n[bold red]Критическая ошибка:[/] {e}")
        input("Нажмите Enter для выхода...")

if __name__ == "__main__":
    main()
