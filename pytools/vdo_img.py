"""
视频，图片处理。
"""
from moviepy.editor import VideoFileClip
import os
import shutil
import imageio
from PIL import Image, ImageSequence
from pygifsicle import gifsicle


def vdo_to_gif(filepath, t_start=(0, 0, 0), t_end=None, res=0.5, outpath=None):
    """将视频中某个片段转换为 gif
    
    filepath: 视频文件路径，视频可以是 MP4，avi 等
    t_start: 开始时间 (时，分，秒)，默认从头开始
    t_end: 结束时间，格式同开始时间，默认到结尾
    res: 缩放比例
    outpath: 转换后 gif 文件输出路径，默认视频文件路径，且同名

    返回 gif 文件的路径
    """
    clip = VideoFileClip(filepath)
    if outpath is None:
        outpath = os.path.splitext(filepath)[0] + '.gif'
    clip.subclip(t_start, t_end).resize(res).write_gif(outpath)

    return outpath


def zip_image(imgpath, outfile=None, kb=200):
    """等比例压缩图片（非动图）到指定大小以下

    imgpath: 源文件路径
    outfile: 压缩文件保存路径，默认覆盖源文件
    kb: 压缩目标大小（kb）
    """
    if outfile is None:
        outfile = imgpath

    size = os.path.getsize(imgpath) / 1024
    if size < kb:
        print(f'{imgpath}大小已小于{kb}kb，无需压缩')
        shutil.copy(imgpath, outfile)
        return

    quality = 90
    n = 1
    while size >= kb:
        im = Image.open(imgpath)
        x, y = im.size
        out = im.resize((int(x * 0.95), int(y * 0.95)), Image.ANTIALIAS)
        out.save(outfile, quality=quality)
        imgpath = outfile
        if quality - 5 < 30:
            if size >= kb:
                quality = 80
            else:
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

    n = 0.99
    while size >= kb:
        gifsicle(gif,
                 destination=destination,
                 optimize=True,
                 options=["--lossy=90", "--scale",
                          str(n)])
        if not cover:
            gif = destination
        size = os.path.getsize(gif) / 1024
        n -= 0.01

    return destination

def zip_gif_by_size(gif, rp=500, cover=False):
    """压缩动图(gif)到指定尺寸(rp)以下
    
    gif: gif 格式动图本地路径
    rp: 指定压缩尺寸, 默认 500(宽或高)
    cover: 是否覆盖原图, 默认不覆盖，文件名多了 "-zip" 且和原文件在相同文件夹中

    返回压缩生成的 gif 的路径，覆盖就返回 None
    """

    img_list = []

    # 读取原gif动图
    img = Image.open(gif)

    # 对原动图进行压缩，并存入img_list 
    for i in ImageSequence.Iterator(img):
        i = i.convert('RGB')
        if max(i.size[0], i.size[1]) > rp:
            i.thumbnail((rp, rp))
        else:
            return gif
        img_list.append(i)

    # 计算帧的频率
    durt = (img.info)['duration'] / 1000

    destination = None
    if not cover:
        destination = f"{os.path.splitext(gif)[0]}-zip.gif"
    else:
        destination = gif

    # 读取img_list合成新的gif
    imageio.mimsave(destination, img_list, duration=durt )
    return destination
