#!/usr/bin/env python3
"""
Анализатор структуры проекта - простой вариант
"""

import os
import sys
from typing import Dict, List, Optional
import time

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
        print("\n" + "="*60)
        print("АНАЛИЗАТОР СТРУКТУРЫ ПРОЕКТА")
        print("="*60)
        print("\nВведите путь к проекту:")
        print("Пример: C:\\Users\\Name\\Projects\\myapp")
        print("Или: . (текущая папка), .. (папка выше), exit (выход)")
        print("-"*60)
        
        while True:
            try:
                path_input = input("\nВведите путь: ").strip()
                
                if not path_input:
                    print("Путь не может быть пустым!")
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
                    print(f"Путь не существует: {path_input}")
                    print("Проверьте правильность пути и попробуйте снова")
                    continue
                
                return os.path.abspath(path_input)
                
            except KeyboardInterrupt:
                return None
            except Exception as e:
                print(f"Ошибка ввода: {e}")
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
                            'size': 0,
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
        print("\n" + "="*60)
        print("РЕЗУЛЬТАТЫ АНАЛИЗА")
        print("="*60)
        
        if result['error']:
            print(f"Ошибка: {result['error']}")
            return
        
        print(f"Проект: {result['name']}")
        print(f"Путь: {result['path']}")
        print(f"Тип: {'Файл' if result['is_file'] else 'Папка'}")
        
        if result['scan_time'] > 0:
            print(f"Время анализа: {result['scan_time']:.2f} сек")
        
        if result['is_dir']:
            stats = result['stats']
            print(f"\nСТАТИСТИКА:")
            print(f"  Папок: {stats['total_dirs']}")
            print(f"  Файлов: {stats['total_files']}")
            
            # Размер
            total_size = stats['total_size']
            if total_size > 1024 * 1024 * 1024:  # GB
                print(f"  Общий размер: {total_size / (1024*1024*1024):.2f} GB")
            elif total_size > 1024 * 1024:  # MB
                print(f"  Общий размер: {total_size / (1024*1024):.2f} MB")
            elif total_size > 1024:  # KB
                print(f"  Общий размер: {total_size / 1024:.2f} KB")
            else:
                print(f"  Общий размер: {total_size} байт")
        
        # Выводим полное дерево структуры
        print(f"\nСТРУКТУРА ПРОЕКТА:")
        print("-" * 60)
        
        if result['is_file']:
            # Для одного файла
            item = result['tree_structure'][0]
            print(f"{item['name']}")
        else:
            # Для папки - выводим дерево
            self._print_tree(result['tree_structure'])
    
    def _print_tree(self, items: List[Dict], prefix: str = ""):
        """Рекурсивно выводит дерево структуры"""
        for i, item in enumerate(items):
            is_last = (i == len(items) - 1)
            
            # Определяем префиксы для дерева
            if prefix == "":
                # Корневой уровень
                connector = "└── " if is_last else "├── "
            else:
                connector = "    " if prefix.endswith("    ") else "│   "
            
            if item['type'] == 'dir':
                # Папка
                line = f"{prefix}{connector}{item['name']}/"
                
                if item.get('error'):
                    line += f" [Нет доступа]"
                
                print(line)
                
                # Рекурсивно выводим содержимое папки
                if item['children']:
                    new_prefix = prefix + ("    " if is_last else "│   ")
                    self._print_tree(item['children'], new_prefix)
                    
            else:
                # Файл
                line = f"{prefix}{connector}{item['name']}"
                
                if item.get('error'):
                    line += f" [Нет доступа]"
                
                print(line)

    def run(self):
        """Основной цикл программы"""
        print("\n" + "="*60)
        print("АНАЛИЗАТОР СТРУКТУРЫ ПРОЕКТОВ")
        print("="*60)
        print("Показывает полную структуру проекта")
        print("="*60)
        
        while True:
            try:
                # Получаем путь от пользователя
                path = self.get_path()
                
                if path is None:
                    print("\nВыход из программы")
                    break
                
                # Анализируем проект
                print(f"\nАнализирую: {path}")
                result = self.analyze_project(path)
                
                # Выводим результаты
                self.print_results(result)
                
                # Спрашиваем, хочет ли пользователь проанализировать еще
                print("\n" + "="*60)
                choice = input("\nПроанализировать другой проект? (y/n): ").lower().strip()
                
                if choice not in ['y', 'yes', 'да', 'д']:
                    print("\nСпасибо за использование программы!")
                    break
                    
                print("\n" + "="*60)
                
            except KeyboardInterrupt:
                print("\n\nВыход из программы")
                break
            except Exception as e:
                print(f"\nНеожиданная ошибка: {e}")
                print("Попробуйте еще раз...")
                continue

def main():
    """Точка входа в программу"""
    # Проверяем версию Python
    if sys.version_info < (3, 6):
        print("Требуется Python 3.6 или выше")
        return
    
    analyzer = ProjectAnalyzer()
    
    # Запускаем анализатор
    try:
        analyzer.run()
    except Exception as e:
        print(f"\nКритическая ошибка: {e}")
        input("Нажмите Enter для выхода...")

if __name__ == "__main__":
    main()