#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import argparse
import re

def natural_sort_key(s):
    """自然排序：让数字按数值大小排序，而不是字符串字典序"""
    return [int(c) if c.isdigit() else c for c in re.split(r'(\d+)', s)]

def rename_pairs(images_dir, labels_dir, prefix="frame_by", start=1, digit=6, dry_run=False):
    """
    将 images_dir 中的 .png 和 labels_dir 中的 .txt 配对重命名

    :param images_dir: 存放 PNG 图片的文件夹路径
    :param labels_dir: 存放 TXT 标注文件的文件夹路径
    :param prefix:    新文件名前缀，默认 "frame_by"
    :param start:     起始编号，默认 1
    :param digit:     编号数字位数（补零），默认 6
    :param dry_run:   是否只打印预览而不实际重命名，默认 False
    """
    # 获取所有 PNG 文件（仅文件名，不含扩展名）
    png_files = [f for f in os.listdir(images_dir) if f.lower().endswith('.png')]
    if not png_files:
        print("错误：images 目录中没有找到 PNG 文件")
        return

    # 获取所有 TXT 文件
    txt_files = [f for f in os.listdir(labels_dir) if f.lower().endswith('.txt')]
    if not txt_files:
        print("错误：labels 目录中没有找到 TXT 文件")
        return

    # 数量必须一致
    if len(png_files) != len(txt_files):
        print(f"错误：图片数量 ({len(png_files)}) 与标注文件数量 ({len(txt_files)}) 不一致，无法确保对应关系。")
        return

    # 排序：使用自然排序使文件名中的数字正确排序（例如 2.png 排在 10.png 之前）
    png_files.sort(key=natural_sort_key)
    txt_files.sort(key=natural_sort_key)

    # 建立配对列表（按排序后的顺序一一对应）
    pairs = list(zip(png_files, txt_files))

    print(f"找到 {len(pairs)} 对文件，准备重命名...")
    if dry_run:
        print("【预览模式】不会实际重命名文件\n")

    for idx, (png_name, txt_name) in enumerate(pairs, start=start):
        # 构造新文件名
        number = str(idx).zfill(digit)
        new_png = f"{prefix}_{number}.png"
        new_txt = f"{prefix}_{number}.txt"

        old_png_path = os.path.join(images_dir, png_name)
        new_png_path = os.path.join(images_dir, new_png)
        old_txt_path = os.path.join(labels_dir, txt_name)
        new_txt_path = os.path.join(labels_dir, new_txt)

        # 检查目标文件是否已存在（防止覆盖）
        if os.path.exists(new_png_path) or os.path.exists(new_txt_path):
            print(f"警告：目标文件已存在，跳过 {png_name} ↔ {txt_name}")
            continue

        if dry_run:
            print(f"[预览] {png_name} -> {new_png}")
            print(f"[预览] {txt_name} -> {new_txt}")
        else:
            os.rename(old_png_path, new_png_path)
            os.rename(old_txt_path, new_txt_path)
            print(f"已重命名：{png_name} -> {new_png}, {txt_name} -> {new_txt}")

    if not dry_run:
        print("\n重命名完成！")
    else:
        print("\n预览结束，未执行实际重命名。")

def main():
    parser = argparse.ArgumentParser(description="批量重命名图片和标注文件，保持配对关系")
    parser.add_argument("--images_dir", "-i", default="./images", help="存放 PNG 图片的文件夹 (默认 ./images)")
    parser.add_argument("--labels_dir", "-l", default="./labels", help="存放 TXT 标注的文件夹 (默认 ./labels)")
    parser.add_argument("--prefix", "-p", default="frame_by", help="新文件名前缀 (默认 frame_by)")
    parser.add_argument("--start", "-s", type=int, default=1, help="起始编号 (默认 1)")
    parser.add_argument("--digit", "-d", type=int, default=6, help="编号数字位数 (默认 6，即 frame_by_000001)")
    parser.add_argument("--dry_run", "-n", action="store_true", help="预览模式，不实际重命名")

    args = parser.parse_args()

    # 检查文件夹是否存在
    if not os.path.isdir(args.images_dir):
        print(f"错误：images 目录不存在: {args.images_dir}")
        return
    if not os.path.isdir(args.labels_dir):
        print(f"错误：labels 目录不存在: {args.labels_dir}")
        return

    rename_pairs(args.images_dir, args.labels_dir, args.prefix, args.start, args.digit, args.dry_run)

if __name__ == "__main__":
    main()