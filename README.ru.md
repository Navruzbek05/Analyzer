# Анализатор структуры проекта

[English](README.md) | **Русский**

[![tests](https://github.com/Navruzbek05/project-tree-analyzer/actions/workflows/test.yml/badge.svg)](https://github.com/Navruzbek05/project-tree-analyzer/actions/workflows/test.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/)

Интерактивная программа, которая показывает структуру папок и файлов проекта в виде цветного дерева с размерами и статистикой.

![Демо](docs/demo.gif)

## 🚀 Возможности

- 📁 **Анализ структуры** — показывает полное дерево папок и файлов проекта
- 📊 **Статистика проекта**:
  - Количество папок и файлов
  - Общий размер проекта (автоматическое преобразование в Б, KB, MB, GB)
  - Время сканирования
- 🌳 **Красивый вывод** — цветное дерево на [rich](https://github.com/Textualize/rich) с иконками по типу файла
- 📏 **Размеры в дереве** — размер каждого файла и суммарный размер каждой папки
- 🛡️ **Умная фильтрация** — исключает ненужные папки (`.git`, `node_modules` и т.д.)
- 🔍 **Анализ отдельных файлов** — поддерживает анализ одного файла

## 📋 Требования

- Python 3.9 или выше
- Библиотека [rich](https://pypi.org/project/rich/)

## 💾 Установка

```bash
git clone https://github.com/Navruzbek05/project-tree-analyzer.git
cd project-tree-analyzer
pip install -r requirements.txt
```

Или скачайте архив со страницы [Releases](https://github.com/Navruzbek05/project-tree-analyzer/releases).

Если rich не установлен, программа сообщит об этом и завершится.

## 🎯 Использование

```bash
python arch_analyzer.py
```

### Примеры ввода пути

При запросе программы введите один из вариантов:

| Вариант | Описание |
|---------|---------|
| `C:\Users\Name\Projects\myapp` | Полный путь к проекту |
| `.` | Текущая папка |
| `..` | Папка выше текущей |
| `~/Documents/project` | Относительно домашней папки |
| `%USERPROFILE%\Desktop` | С переменными окружения |
| `exit` / `quit` / `выход` | Выход из программы |

## 📈 Пример вывода

```
╭──────────────── myapp ─────────────────╮
│ Путь    C:\Users\Name\Projects\myapp   │
│ Тип     Папка                          │
│ Папок   6                              │
│ Файлов  7                              │
│ Размер  2.41 MB                        │
│ Время   0.15 сек                       │
╰────────────────────────────────────────╯
📦 myapp
├── 📂 src/  2.40 MB
│   ├── 📂 components/  40.0 KB
│   │   ├── ⚛ Button.jsx  12.0 KB
│   │   └── ⚛ Form.jsx  28.0 KB
│   ├── 📂 utils/  3.2 KB
│   │   └── 📜 helpers.js  3.2 KB
│   └── 📜 App.js  2.36 MB
├── 📂 tests/  6.1 KB
│   ├── 📂 integration/  0 Б
│   └── 📂 unit/  6.1 KB
│       └── 📜 helpers.test.js  6.1 KB
├── ⚙ package.json  1.2 KB
└── 📝 README.md  4.0 KB
```

В терминале вывод цветной: папки синие, файлы окрашены по типу, размеры приглушены.

## 🔧 Исключаемые папки и файлы

По умолчанию анализатор пропускает все скрытые элементы (имя начинается с `.`) и следующие папки:
- `.git` — репозиторий Git
- `__pycache__` — кеш Python
- `.venv`, `venv` — виртуальные окружения
- `node_modules` — зависимости Node.js
- `.idea` — конфиг IDE JetBrains
- `.vscode` — конфиг VS Code
- `build`, `dist` — скомпилированные файлы
- `.pytest_cache`, `.coverage`, `.mypy_cache` — служебные папки

И файлы:
- `.gitignore`, `.gitattributes`
- `.DS_Store` — система файлов macOS
- `Thumbs.db`, `desktop.ini` — система файлов Windows

## 📝 Структура кода

### Класс `ProjectAnalyzer`

| Метод | Описание |
|-------|---------|
| `get_path()` | Получает и валидирует путь от пользователя |
| `analyze_project(path)` | Анализирует проект и собирает статистику |
| `_build_tree_structure()` | Рекурсивно строит дерево структуры |
| `_collect_stats_from_tree()` | Собирает статистику из дерева |
| `print_results()` | Выводит панель со статистикой и дерево |
| `_to_rich_tree()` | Строит цветное rich-дерево с иконками и размерами |
| `run()` | Основной цикл программы |

Вспомогательная функция `fmt_size(size)` переводит байты в Б / KB / MB / GB.

### Проверка

```bash
python test_arch_analyzer.py
```

## 🎨 Особенности

- ✅ Поддержка Windows, macOS и Linux (проверяется в CI)
- ✅ Обработка ошибок доступа — такие элементы помечаются `[Нет доступа]`
- ✅ Защита от бесконечной рекурсии (максимальная глубина 10 уровней)
- ✅ Интерактивный режим — анализируйте несколько проектов подряд
- ✅ Выход: `Ctrl+C` или `exit`

## 🤝 Участие в разработке

Issues и pull request'ы приветствуются — см. [CONTRIBUTING.md](CONTRIBUTING.md). История изменений — в [CHANGELOG.md](CHANGELOG.md).

## 📄 Лицензия

[MIT](LICENSE) © 2026 Navruzbek — можно свободно использовать, изменять и распространять, в том числе в коммерческих целях.
