import os
import xml.etree.ElementTree as ET
from pathlib import Path

def convert_voc_to_yolo(xml_path, output_dir=None, class_mapping=None):
    """
    将单个VOC格式XML转换为YOLO格式TXT。
    
    Args:
        xml_path: XML文件路径
        output_dir: 输出目录，默认为XML所在目录
        class_mapping: 类别名到ID的映射字典，若为None则自动构建
    Returns:
        (txt_path, class_id) 或 None
    """
    if output_dir is None:
        output_dir = os.path.dirname(xml_path)
    
    # 解析XML
    tree = ET.parse(xml_path)
    root = tree.getroot()
    
    # 获取图像尺寸
    size_elem = root.find('size')
    if size_elem is None:
        print(f"Warning: {xml_path} no size element, skip")
        return None
    width = int(size_elem.find('width').text)
    height = int(size_elem.find('height').text)
    
    # 找出所有object
    objects = root.findall('object')
    if not objects:
        print(f"Warning: {xml_path} no objects, skip")
        return None
    
    # 准备写入内容
    yolo_lines = []
    for obj in objects:
        name = obj.find('name').text
        # 类别映射
        if class_mapping is None:
            # 简单处理：直接使用name作为class id的字符串，但YOLO需要整数，故报错
            raise ValueError("class_mapping must be provided or built globally")
        class_id = class_mapping.get(name)
        if class_id is None:
            print(f"Warning: unknown class '{name}' in {xml_path}, skip this object")
            continue
        
        bndbox = obj.find('bndbox')
        xmin = float(bndbox.find('xmin').text)
        ymin = float(bndbox.find('ymin').text)
        xmax = float(bndbox.find('xmax').text)
        ymax = float(bndbox.find('ymax').text)
        
        # 计算YOLO格式：中心x,y 和宽高，归一化
        box_w = xmax - xmin
        box_h = ymax - ymin
        x_center = xmin + box_w / 2.0
        y_center = ymin + box_h / 2.0
        x_center_norm = x_center / width
        y_center_norm = y_center / height
        width_norm = box_w / width
        height_norm = box_h / height
        
        # 格式：class x_center y_center width height
        yolo_lines.append(f"{class_id} {x_center_norm:.6f} {y_center_norm:.6f} {width_norm:.6f} {height_norm:.6f}")
    
    if not yolo_lines:
        return None
    
    # 输出txt路径
    base_name = os.path.splitext(os.path.basename(xml_path))[0]
    txt_path = os.path.join(output_dir, base_name + ".txt")
    with open(txt_path, 'w') as f:
        f.write("\n".join(yolo_lines))
    
    return txt_path

def batch_convert(xml_folder, output_folder=None, class_mapping=None):
    """
    批量转换文件夹内所有XML文件。
    
    Args:
        xml_folder: 包含XML文件的文件夹
        output_folder: 输出TXT文件夹，默认与XML同文件夹
        class_mapping: 类别映射字典，若为None则自动从所有XML中构建
    """
    xml_folder = Path(xml_folder)
    if not xml_folder.exists():
        print(f"Folder {xml_folder} not exist")
        return
    
    # 收集所有xml文件
    xml_files = list(xml_folder.glob("*.xml"))
    if not xml_files:
        print(f"No XML files found in {xml_folder}")
        return
    
    # 如果未提供类别映射，则扫描所有XML构建
    if class_mapping is None:
        class_set = set()
        for xml_path in xml_files:
            tree = ET.parse(xml_path)
            root = tree.getroot()
            for obj in root.findall('object'):
                name = obj.find('name').text
                class_set.add(name)
        class_mapping = {name: idx for idx, name in enumerate(sorted(class_set))}
        print(f"Auto-built class mapping: {class_mapping}")
    
    # 确定输出目录
    if output_folder is None:
        output_folder = xml_folder
    else:
        output_folder = Path(output_folder)
        output_folder.mkdir(parents=True, exist_ok=True)
    
    # 转换
    converted = 0
    for xml_path in xml_files:
        result = convert_voc_to_yolo(str(xml_path), str(output_folder), class_mapping)
        if result:
            converted += 1
            print(f"Converted: {xml_path.name} -> {os.path.basename(result)}")
    
    print(f"Done. Converted {converted}/{len(xml_files)} files.")
    
    # 保存类别映射文件（可选）
    mapping_path = output_folder / "classes.txt"
    with open(mapping_path, 'w') as f:
        for name, idx in sorted(class_mapping.items(), key=lambda x: x[1]):
            f.write(f"{name}\n")
    print(f"Class mapping saved to {mapping_path}")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Convert VOC XML annotations to YOLO TXT format.")
    parser.add_argument("xml_folder", help="Folder containing XML files")
    parser.add_argument("--output", "-o", default=None, help="Output folder for TXT files (default: same as xml_folder)")
    parser.add_argument("--classes", "-c", default=None, help="Optional class mapping file (each line: class_name), if not provided, auto-build from XMLs")
    
    args = parser.parse_args()
    
    # 如果提供了类别文件，读取映射
    class_mapping = None
    if args.classes:
        class_mapping = {}
        with open(args.classes, 'r') as f:
            for idx, line in enumerate(f):
                name = line.strip()
                if name:
                    class_mapping[name] = idx
        print(f"Loaded class mapping: {class_mapping}")
    
    batch_convert(args.xml_folder, args.output, class_mapping)