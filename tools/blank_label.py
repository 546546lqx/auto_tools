import os
from pathlib import Path

def generate_empty_labels(images_dir, labels_dir, extensions=None, force=False):
    """
    为 images_dir 中的每张图片在 labels_dir 中生成同名的空 txt 文件

    Args:
        images_dir (str or Path): 图片文件夹路径
        labels_dir (str or Path): 标注文件夹路径
        extensions (set): 支持的图片扩展名集合，默认为常见格式
        force (bool): 是否强制覆盖已存在的 txt 文件，默认 False（跳过）
    """
    if extensions is None:
        extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif', '.webp'}
    
    images_path = Path(images_dir)
    labels_path = Path(labels_dir)
    
    if not images_path.exists():
        print(f"错误：图片文件夹不存在 -> {images_path}")
        return
    
    # 创建 labels 文件夹（如果不存在）
    labels_path.mkdir(parents=True, exist_ok=True)
    
    # 遍历图片文件
    image_files = [f for f in images_path.iterdir() if f.suffix.lower() in extensions]
    if not image_files:
        print(f"警告：在 {images_path} 中没有找到支持的图片文件")
        return
    
    created_count = 0
    skipped_count = 0
    
    for img_file in image_files:
        stem = img_file.stem  # 不含扩展名的文件名
        txt_file = labels_path / f"{stem}.txt"
        
        if txt_file.exists() and not force:
            print(f"跳过已存在：{txt_file}")
            skipped_count += 1
            continue
        
        # 创建空文件（覆盖写入空内容）
        with open(txt_file, 'w') as f:
            pass  # 写入空内容
        print(f"已创建空标签：{txt_file}")
        created_count += 1
    
    print(f"\n完成。创建 {created_count} 个，跳过 {skipped_count} 个。")


if __name__ == "__main__":
    # 修改这里的路径为你自己的文件夹
    IMAGES_DIR = "C:\\Users\\Administrator\\Desktop\\img_test\\images"   # 图片文件夹路径
    LABELS_DIR = "C:\\Users\\Administrator\\Desktop\\img_test\\labels"   # 标签文件夹路径
    
    generate_empty_labels(IMAGES_DIR, LABELS_DIR, force=False)