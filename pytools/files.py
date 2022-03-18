"""
文件搜索，批量处理等。
"""
import os
import re
import filecmp
from .convert import *


def search_files(filedir, filetype='.ipynb'):
    """按文件扩展名在指定文件夹中搜索文件
    
    filedir: 要搜索的文件夹路径
    filetype: 要搜索的文件的扩展名，可以是扩展名元组，默认搜索 .ipynb,
        并排除缓存文件

    返回文件的绝对路径列表
    """
    filelist = []
    for root, _, files in os.walk(filedir):
        if '.ipynb_checkpoints' in root:
            continue
        for i in files:
            if i.endswith(filetype):
                filelist.append(os.path.join(root, i))
    return filelist


def file_dedup(filedir, filetype=('.jpg', '.png')):
    """指定文件夹中大量文件去重
    
    filedir: 指定文件夹路径
    filetype: 要去重的文件的扩展名
    """
    files = search_files(filedir, filetype)
    # 按文件大小排序，使重复文件排到一起方便去重
    sort_files = sorted(files, key=os.path.getsize)
    for n in range(len(sort_files)):
        # 每次往后搜索 50 个
        for f in sort_files[n + 1:n + 51]:
            # 搜到重复文件，把它删除
            if filecmp.cmp(sort_files[n], f):
                os.remove(f)
                # 从排序列表中删除，减少搜索次数
                sort_files.remove(f)


def generate_directory(filedir, filetype='.ipynb', filename='README.md'):
    """搜索指定文件夹中的文件，按顺序在该文件夹中生成目录文件
    
    filedir: 指定文件夹路径
    filetype: 要用来生成目录的文件的扩展名
    filename: 存放目录的文件的文件名

    文件内容中的第一个 "#+ xxx" 中的 xxx 作为目录，否则直接文件名做目录
    """
    files = search_files(filedir, filetype)
    directory = []
    for f in files:
        with open(f, encoding='utf-8') as r:
            match = re.search(r'#+\s+(.+?)\\?n?"?,?\n', r.read())
            if match is not None:
                title = match.group(1)
            else:
                title = os.path.split(f)[-1]

        link = f.split(filedir)[-1].replace('\\', '/').strip('/')
        directory.append(f'- [{title}]({link})\n')

    with open(os.path.join(filedir, filename), 'w', encoding='utf-8') as w:
        w.writelines(directory)


def ipynbs2mds(input_dir, out_dir=None):
    """指定文件夹中的 ipynb 全部转换为 md
    
    input_dir: 指定的文件夹路径
    out_dir: 转换文件储存目录，如果提供，所有转换文件都放到该目录下，
        默认每个转换文件和源文件在同目录中
    """
    files = search_files(input_dir, '.ipynb')
    for f in files:
        ipynb2md(f, out_dir)


def mds2ipynbs(input_dir, out_dir=None):
    """指定文件夹中的 md 全部转换为 ipynb
    
    input_dir: 指定的文件夹路径
    out_dir: 转换文件储存目录，如果提供，所有转换文件都放到该目录下，
        默认每个转换文件和源文件在同目录中
    """
    files = search_files(input_dir, '.md')
    for f in files:
        md2ipynb(f, out_dir)