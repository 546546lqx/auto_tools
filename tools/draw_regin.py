import cv2
import numpy as np

# 请替换为你的 RTSP 流地址
RTSP_URL = "rtsp://192.168.1.181:8554/C036/ac01"

# 全局变量
points = []          # 存储鼠标点击的点（原始图像坐标）
drawing = False      # 未使用，保留兼容

# 显示尺寸（固定宽度，高度等比计算）
DISPLAY_WIDTH = 800
disp_width = DISPLAY_WIDTH
disp_height = None   # 后续根据原始图像比例计算
scale_x = 1.0        # 显示图像宽度 / 原始图像宽度
scale_y = 1.0        # 显示图像高度 / 原始图像高度
orig_width = None
orig_height = None

def orig_to_disp(x_orig, y_orig):
    """将原始图像坐标转换为显示图像坐标"""
    return int(x_orig * scale_x), int(y_orig * scale_y)

def disp_to_orig(x_disp, y_disp):
    """将显示图像坐标转换为原始图像坐标"""
    return int(x_disp / scale_x), int(y_disp / scale_y)

def mouse_callback(event, x_disp, y_disp, flags, param):
    """鼠标回调函数：左键添加顶点（存储原始坐标），右键重置"""
    global points

    if event == cv2.EVENT_LBUTTONDOWN:
        # 将显示坐标转换为原始坐标并存储
        x_orig, y_orig = disp_to_orig(x_disp, y_disp)
        points.append((x_orig, y_orig))
        update_display()

    elif event == cv2.EVENT_RBUTTONDOWN:
        # 右键重置所有点
        points = []
        update_display()

def update_display():
    """更新显示图像，绘制多边形（投影到显示尺寸上）"""
    # 缩放显示图像
    img_disp = cv2.resize(img_original, (disp_width, disp_height))

    if len(points) > 0:
        # 将所有原始坐标转换为显示坐标
        disp_points = [orig_to_disp(x, y) for (x, y) in points]

        # 绘制顶点（小圆点）
        for pt in disp_points:
            cv2.circle(img_disp, pt, 5, (0, 0, 255), -1)

        # 绘制多边形轮廓（至少两个点）
        if len(points) >= 2:
            pts_array = np.array(disp_points, dtype=np.int32).reshape((-1, 1, 2))
            cv2.polylines(img_disp, [pts_array], isClosed=False, color=(0, 255, 0), thickness=2)

        # 最后一个点与第一个点连线示意闭合（至少三个点）
        if len(points) >= 3:
            first_pt = disp_points[0]
            last_pt = disp_points[-1]
            cv2.line(img_disp, last_pt, first_pt, (255, 0, 0), 2)

    cv2.imshow("Draw Polygon - Left: add point, Right: reset, Enter: finish, Esc: quit", img_disp)

# 1. 读取 RTSP 流的第一帧
cap = cv2.VideoCapture(RTSP_URL)
if not cap.isOpened():
    print("无法打开 RTSP 流，请检查地址或网络")
    exit()

print("正在获取第一帧...")
ret, img_original = cap.read()
cap.release()

if not ret:
    print("获取第一帧失败")
    exit()

# 2. 获取原始图像尺寸
orig_height, orig_width = img_original.shape[:2]
print(f"原始图像尺寸: {orig_width} x {orig_height}")

# 3. 计算显示尺寸（等比缩放，固定宽度）
disp_height = int(DISPLAY_WIDTH * orig_height / orig_width)
scale_x = DISPLAY_WIDTH / orig_width
scale_y = disp_height / orig_height
print(f"显示窗口尺寸: {disp_width} x {disp_height}")

# 4. 创建窗口并设置鼠标回调
cv2.namedWindow("Draw Polygon - Left: add point, Right: reset, Enter: finish, Esc: quit")
cv2.setMouseCallback("Draw Polygon - Left: add point, Right: reset, Enter: finish, Esc: quit", mouse_callback)
update_display()

# 5. 等待用户交互
while True:
    key = cv2.waitKey(1) & 0xFF
    if key == 13:  # Enter 键完成
        if len(points) < 3:
            print("至少需要 3 个点才能构成多边形，请继续添加。")
            continue
        break
    elif key == 27:  # Esc 键退出
        cv2.destroyAllWindows()
        exit()

cv2.destroyAllWindows()

# 6. 将原始像素坐标归一化到 [0, 1] 区间，保留两位小数
norm_points = [[round(x / orig_width, 2), round(y / orig_height, 2)] for (x, y) in points]

# 7. 输出结果
result = [norm_points]
print("\n绘制完成的归一化坐标（保留两位小数）：")
print(result)

# 8. 保存到文件
with open("polygon_coords.txt", "w") as f:
    f.write(str(result))