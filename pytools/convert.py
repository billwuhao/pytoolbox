"""
文件格式转换。
"""
import os
import shutil
import re
import json


def ipynb2md(filepath, outdir=None):
    """将一个 ipynb 文件转换为同名的 md 文件
    
    filepath: 源文件路径
    outdir: 输出文件存放目录，默认和源文件同目录
    """
    cmd = f'jupyter nbconvert --to markdown {filepath}'
    os.system(cmd)

    path = os.path.splitext(filepath)[0] + '.md'
    with open(path, encoding='utf-8') as r:
        data = r.read()
    with open(path, 'w', encoding='utf-8') as w:
        w.write(re.sub('\n{3,}', '\n\n', data))

    if outdir is not None:
        shutil.move(path, outdir)


def __split_md(filepath):
    """将一个 md 文件内容拆分，将每对 ``` 包围的 code 拆成一段
    
    filepath: md 文件路径

    返回拆分后的列表
    """
    with open(filepath, encoding='utf-8') as f:
        # ``` 标记的行内代码改为 ` 标记
        data = re.sub(r"```(.+?)```", r"`\1`", f.read())

    matches = re.finditer(r"^ *```", data, re.M)
    indices = [match.span()[0] for match in matches]

    indices.append(len(data))
    if indices[0] != 0:
        indices.insert(0, 0)

    groups = [data[indices[i]:indices[i + 1]] for i in range(len(indices) - 1)]
    cells = []
    for i in range(len(groups)):
        if not re.findall(r"(^ *```)", groups[i]):
            cells.append(re.sub(r'(^ *\n\n?)|( *\n$)', '', groups[i]))
        else:
            cells.append(re.sub(r'( *\n$)', '', groups[i]))
            # ``` 成对出现，移除第二个
            groups[i + 1] = re.sub(r"(^ *```)", '', groups[i + 1])

    return cells


def md2ipynb(filepath, outdir=None):
    """将一个 md 文件转换为同名的 ipynb 文件
    
    filepath: 源文件路径
    outdir: 输出文件存放目录，默认和源文件同目录
    """
    data = {"cells": [], "metadata": {}, "nbformat": 4, "nbformat_minor": 2}
    for i in __split_md(filepath):
        source = i.splitlines(True)
        cell = {"cell_type": "markdown", "metadata": {}, "source": source}
        if re.findall(r"(^ *```)", i):
            cell['cell_type'] = 'code'
            cell['source'] = source[1:]

        data['cells'].append(cell)

    path = os.path.splitext(filepath)[0] + '.ipynb'
    with open(path, 'w', encoding='utf-8') as w:
        json.dump(data, w, indent=4, ensure_ascii=False)

    if outdir is not None:
        shutil.move(path, outdir)