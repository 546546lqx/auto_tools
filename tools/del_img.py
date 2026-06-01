import os
from pathlib import Path
    
# ========== 配置区域 ==========
IMAGES_DIR = Path("C:\\Users\\Administrator\\Desktop\\img_test\\images")   # 图片文件夹
LABELS_DIR = Path("C:\\Users\\Administrator\\Desktop\\img_test\\labels")   # 标注文件夹
DRY_RUN = False                  # True=仅预览不删除，False=真正删除
IMG_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.bmp', '.tif', '.tiff'}  # 支持的图片格式
# ==============================

def main():
    images_dir = IMAGES_DIR
    labels_dir = LABELS_DIR

    if not images_dir.exists():
        print(f"错误：图片文件夹不存在 -> {images_dir}")
        return
    if not labels_dir.exists():
        print(f"错误：标注文件夹不存在 -> {labels_dir}")
        return

    deleted_images = 0
    deleted_labels = 0

    # ---------- 1. 删除没有对应 txt 的图片 ----------
    print("【步骤1】检查多余图片（无对应标注文件）...")
    for img_path in images_dir.rglob('*'):
        if img_path.is_file() and img_path.suffix.lower() in IMG_EXTENSIONS:
            rel_path = img_path.relative_to(images_dir)
            label_path = labels_dir / rel_path.with_suffix('.txt')
            if not label_path.exists():
                if DRY_RUN:
                    print(f"[预览] 待删除多余图片: {img_path}")
                else:
                    try:
                        os.remove(img_path)
                        print(f"[删除] 多余图片: {img_path}")
                    except Exception as e:
                        print(f"[失败] {img_path} -> {e}")
                deleted_images += 1

    # ---------- 2. 删除没有对应图片的 txt ----------
    print("\n【步骤2】检查多余标注文件（无对应图片）...")
    for label_path in labels_dir.rglob('*.txt'):
        if label_path.is_file():
            rel_path = label_path.relative_to(labels_dir)
            # 尝试替换后缀为常见的图片扩展名
            img_found = False
            for ext in IMG_EXTENSIONS:
                img_path = images_dir / rel_path.with_suffix(ext)
                if img_path.exists():
                    img_found = True
                    break
            if not img_found:
                if DRY_RUN:
                    print(f"[预览] 待删除多余标注: {label_path}")
                else:
                    try:
                        os.remove(label_path)
                        print(f"[删除] 多余标注: {label_path}")
                    except Exception as e:
                        print(f"[失败] {label_path} -> {e}")
                deleted_labels += 1

    print(f"\n完成。{'预览' if DRY_RUN else '实际删除'}统计:")
    print(f"  - 删除无标注的图片: {deleted_images} 张")
    print(f"  - 删除无图片的标注: {deleted_labels} 个")

if __name__ == "__main__":
    main()