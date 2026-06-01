import os

# 定义类别映射：原ID -> 新ID
id_mapping = {
    1: 0,
    2: 1,

}

def transform_label_file(file_path):
    """读取YOLO格式txt文件，转换首列ID，写回原文件"""
    new_lines = []
    with open(file_path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue  # 跳过空行
            parts = line.split()
            if len(parts) < 5:
                # 格式错误，保留原行或跳过（这里跳过并打印警告）
                print(f"警告：{file_path} 中的行格式不正确，已跳过: {line}")
                continue
            try:
                old_id = int(parts[0])
                new_id = id_mapping.get(old_id, old_id)  # 未映射则保留原值
                parts[0] = str(new_id)
                new_lines.append(' '.join(parts))
            except ValueError:
                print(f"警告：{file_path} 中的类别ID不是整数，已跳过: {line}")
                continue

    # 写回文件
    with open(file_path, 'w') as f:
        f.write('\n'.join(new_lines))
        if new_lines:
            f.write('\n')  # 最后换行（可选）

def main():
    labels_dir = "C:\\Users\\Administrator\\Desktop\\Violence-Image-Dataset-master\\Violence-Image-Dataset-master\\rgb\\labels"  # 文件夹路径，可根据需要修改
    if not os.path.isdir(labels_dir):
        print(f"错误：找不到 {labels_dir} 文件夹，请确认路径")
        return

    txt_files = [f for f in os.listdir(labels_dir) if f.endswith('.txt')]
    if not txt_files:
        print(f"{labels_dir} 中没有 .txt 文件")
        return

    for filename in txt_files:
        file_path = os.path.join(labels_dir, filename)
        transform_label_file(file_path)
        print(f"已处理：{filename}")

    print("所有文件转换完成！")

if __name__ == "__main__":
    main()