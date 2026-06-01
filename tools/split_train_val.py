import os
import random
import shutil
from pathlib import Path

def split_yolo_dataset(data_root, train_ratio=0.8, random_seed=42):
    """
    将 YOLO 格式的数据集划分为训练集和验证集。

    Args:
        data_root (str): 数据集根目录，应包含 images/ 和 labels/ 两个子文件夹。
        train_ratio (float): 训练集比例，默认 0.8。
        random_seed (int): 随机种子，确保结果可重复。
    """
    random.seed(random_seed)

    # 定义原始路径
    images_dir = Path(data_root) / "images"
    labels_dir = Path(data_root) / "labels"

    if not images_dir.exists() or not labels_dir.exists():
        raise FileNotFoundError("未找到 images 或 labels 文件夹，请检查数据集根目录结构。")

    # 获取所有图片文件（支持常见图片扩展名）
    image_extensions = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff", ".webp"}
    all_images = [f for f in images_dir.iterdir() if f.suffix.lower() in image_extensions]

    if not all_images:
        raise ValueError("images 文件夹中没有找到任何图片文件。")

    # 检查每个图片对应的标签文件是否存在
    valid_pairs = []
    for img_path in all_images:
        label_path = labels_dir / (img_path.stem + ".txt")
        if label_path.exists():
            valid_pairs.append(img_path)
        else:
            print(f"警告：图片 {img_path.name} 没有对应的标签文件，已跳过。")

    if not valid_pairs:
        raise ValueError("没有找到任何有效的图片-标签对。")

    # 随机打乱并划分
    random.shuffle(valid_pairs)
    split_idx = int(len(valid_pairs) * train_ratio)
    train_images = valid_pairs[:split_idx]
    val_images = valid_pairs[split_idx:]

    # 创建目标文件夹结构
    for split in ["train", "val"]:
        (images_dir / split).mkdir(parents=True, exist_ok=True)
        (labels_dir / split).mkdir(parents=True, exist_ok=True)

    # 移动文件
    def move_files(file_list, split):
        for img_path in file_list:
            # 移动图片
            dest_img = images_dir / split / img_path.name
            shutil.move(str(img_path), str(dest_img))

            # 移动对应的标签
            src_label = labels_dir / (img_path.stem + ".txt")
            dest_label = labels_dir / split / (img_path.stem + ".txt")
            shutil.move(str(src_label), str(dest_label))

    move_files(train_images, "train")
    move_files(val_images, "val")

    # 输出统计信息
    print(f"划分完成！总有效样本数：{len(valid_pairs)}")
    print(f"训练集：{len(train_images)} 张图片，比例 {len(train_images)/len(valid_pairs):.2%}")
    print(f"验证集：{len(val_images)} 张图片，比例 {len(val_images)/len(valid_pairs):.2%}")
    print(f"数据集已整理至：{data_root}/images/{{train,val}} 和 {data_root}/labels/{{train,val}}")

if __name__ == "__main__":
    # ==================== 请在此处填写您的参数 ====================
    data_root = r"C:\\Users\\Administrator\\Desktop\\img_test"   # 数据集根目录（包含 images/ 和 labels/）
    train_ratio = 0.8                                         # 训练集比例 (0~1)
    seed = 42                                                 # 随机种子
    # =============================================================

    if not (0 < train_ratio < 1):
        raise ValueError("train_ratio 必须在 0 到 1 之间。")

    split_yolo_dataset(data_root, train_ratio, seed)