import os
from collections import defaultdict

# ====================== 请修改这里为你的标签文件夹路径 ======================
LABELS_FOLDER = "C:\\Users\\Administrator\\Desktop\\img_test\\labels"
# =========================================================================

# 统计字典
class_count = defaultdict(int)
total_boxes = 0
empty_files = []

# 遍历所有 txt 文件
for txt_file in os.listdir(LABELS_FOLDER):
    if not txt_file.endswith(".txt"):
        continue

    txt_path = os.path.join(LABELS_FOLDER, txt_file)

    # 读取文件
    with open(txt_path, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]

    # 空文件记录
    if not lines:
        empty_files.append(txt_file)
        continue

    # 统计每一行的类别（每行第一个数字就是类别ID）
    for line in lines:
        cls_id = line.split()[0]
        class_count[cls_id] += 1
        total_boxes += 1

# ====================== 输出结果 ======================
print("=" * 50)
print("📊 YOLO 标签类别统计结果")
print("=" * 50)
print(f"📁 标签文件夹: {LABELS_FOLDER}")
print(f"🔹 总标注框数量: {total_boxes}")
print(f"🔹 空标签文件数量: {len(empty_files)}")
print("-" * 50)
print("📦 每个类别出现次数：")
for cls_id, count in sorted(class_count.items(), key=lambda x: int(x[0])):
    print(f"  类别 {cls_id} : {count} 次")
print("=" * 50)