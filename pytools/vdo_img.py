"""
视频，图片处理。
"""
from moviepy.editor import VideoFileClip
import os
from PIL import Image
from pygifsicle import gifsicle


def vdo_to_gif(filepath, t_start=(0, 0, 0), t_end=None, outpath=None):
    """将视频中某个片段转换为 gif
    
    filepath: 视频文件路径，视频可以是 MP4，avi 等
    t_start: 开始时间 (时，分，秒)，默认从头开始
    t_end: 结束时间，格式同开始时间，默认到结尾
    outpath: 转换后 gif 文件输出路径，默认视频文件路径，且同名

    返回 gif 文件的路径
    """
    clip = VideoFileClip(filepath)
    if outpath is None:
        outpath = os.path.splitext(filepath)[0] + '.gif'
    clip.subclip(t_start, t_end).write_gif(outpath)

    return outpath


def zip_image(imgpath, outfile=None, kb=200):
    """等比例压缩图片（非动图）到指定大小以下

    imgpath: 源文件路径
    outfile: 压缩文件保存路径，默认覆盖源文件
    kb: 压缩目标大小（kb）
    """
    size = os.path.getsize(imgpath) / 1024
    if size < kb:
        print(f'{imgpath}大小已小于{kb}kb，无需压缩')
        return

    if outfile is None:
        outfile = imgpath

    quality = 90
    while size >= kb:
        im = Image.open(imgpath)
        x, y = im.size
        out = im.resize((int(x * 0.95), int(y * 0.95)), Image.ANTIALIAS)
        out.save(outfile, quality=quality)
        if quality - 5 < 0:
            break
        quality -= 5
        size = os.path.getsize(outfile) / 1024


def zip_gif(gif, kb=200, cover=False):
    """压缩动图(gif)到指定大小(kb)以下
    
    gif: gif 格式动图本地路径
    kb: 指定压缩大小, 默认 200kb
    cover: 是否覆盖原图, 默认不覆盖，文件名多了 "-zip" 且和原文件在相同文件夹中

    该方法需要安装 gifsicle 软件和 pygifsicle 模块

    返回压缩生成的 gif 的路径，覆盖就返回 None
    """

    size = os.path.getsize(gif) / 1024
    if size < kb:
        print(f'{gif}大小已小于{kb}kb，无需压缩')
        return

    destination = None
    if not cover:
        destination = f"{os.path.splitext(gif)[0]}-zip.gif"

    n = 0.9
    while size >= kb:
        gifsicle(gif,
                 destination=destination,
                 optimize=True,
                 options=["--lossy=80", "--scale",
                          str(n)])
        if not cover:
            gif = destination
        size = os.path.getsize(gif) / 1024
        n -= 0.05

    return destination