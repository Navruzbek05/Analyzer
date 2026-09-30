"""Быстрая проверка: python test_arch_analyzer.py"""
import os
import tempfile

from arch_analyzer import ProjectAnalyzer, fmt_size

assert fmt_size(0) == "0 Б"
assert fmt_size(1500) == "1.5 KB"
assert fmt_size(5 * 1024 ** 2) == "5.00 MB"

with tempfile.TemporaryDirectory() as tmp:
    os.mkdir(os.path.join(tmp, 'a'))
    with open(os.path.join(tmp, 'a', 'b.txt'), 'w') as f:
        f.write('x' * 100)
    with open(os.path.join(tmp, 'c.txt'), 'w') as f:
        f.write('y' * 50)

    result = ProjectAnalyzer().analyze_project(tmp)
    folder_a = result['tree_structure'][0]
    assert folder_a['name'] == 'a' and folder_a['size'] == 100
    assert result['stats'] == {'total_files': 2, 'total_dirs': 1, 'total_size': 150}

print("OK")
