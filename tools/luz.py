#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import cv2
import time
import sys
import os
import signal
import argparse
from datetime import datetime
from threading import Event

# 全局停止事件
stop_event = Event()

def signal_handler(sig, frame):
    print("\n收到中断信号，正在停止录制...")
    stop_event.set()

def get_output_filename(output_dir, prefix, ext="mp4"):
    """生成带时间戳的输出文件名"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{prefix}_{timestamp}.{ext}"
    return os.path.join(output_dir, filename)

def record_rtsp(rtsp_url, output_dir, segment_minutes=5, total_duration=None, prefix="recording"):
    """
    录制 RTSP 流并分段保存
    :param rtsp_url: RTSP 地址 (支持 rtsp://user:pass@ip:port/...)
    :param output_dir: 输出目录
    :param segment_minutes: 每段视频的时长（分钟）
    :param total_duration: 总录制时长（分钟），None 表示持续录制直到手动停止
    :param prefix: 输出文件名前缀
    """
    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)

    # 打开 RTSP 流
    cap = cv2.VideoCapture(rtsp_url, cv2.CAP_FFMPEG)
    if not cap.isOpened():
        print(f"错误：无法打开 RTSP 流，请检查地址：{rtsp_url}")
        return

    # 获取视频参数
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # 如果无法获取 FPS，使用默认 25
    if fps <= 0:
        fps = 25.0
        print("警告：无法获取帧率，使用默认 25 fps")

    print(f"视频参数：{width}x{height}, {fps:.2f} fps")
    print(f"分段时长：{segment_minutes} 分钟，输出目录：{output_dir}")
    print("开始录制... (按 Ctrl+C 停止)")

    # 分段参数
    segment_frames = int(fps * segment_minutes * 60)
    frame_count = 0
    segment_index = 0
    out = None
    last_reconnect_time = time.time()
    reconnect_delay = 5  # 重连等待秒数

    # 总录制帧数限制（如果设置了 total_duration）
    total_frames_limit = int(fps * total_duration * 60) if total_duration else None

    # 主循环
    while not stop_event.is_set():
        ret, frame = cap.read()

        if not ret:
            print("读取帧失败，可能 RTSP 连接断开，尝试重连...")
            cap.release()
            time.sleep(reconnect_delay)
            cap = cv2.VideoCapture(rtsp_url, cv2.CAP_FFMPEG)
            if not cap.isOpened():
                print("重连失败，继续等待...")
                continue
            else:
                print("重连成功，继续录制")
                # 重连后重新获取视频参数（可能变化）
                fps = cap.get(cv2.CAP_PROP_FPS)
                width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                if fps <= 0:
                    fps = 25.0
                segment_frames = int(fps * segment_minutes * 60)
                # 重置帧计数器，开始新段
                frame_count = 0
                if out:
                    out.release()
                continue

        # 每一帧到达，写入
        frame_count += 1

        # 是否需要新建分段文件
        if out is None or frame_count > segment_frames:
            if out:
                out.release()
                print(f"分段完成：{current_filename}")
            # 生成新的输出文件
            current_filename = get_output_filename(output_dir, prefix)
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(current_filename, fourcc, fps, (width, height))
            if not out.isOpened():
                print(f"错误：无法创建视频文件 {current_filename}")
                break
            print(f"新建分段：{current_filename}")
            frame_count = 1
            segment_index += 1

        # 写入帧
        out.write(frame)

        # 检查总时长限制
        if total_frames_limit and frame_count + (segment_index-1)*segment_frames >= total_frames_limit:
            print(f"已达到总录制时长 {total_duration} 分钟，停止录制")
            break

    # 释放资源
    if out:
        out.release()
    cap.release()
    print("录制结束")

def parse_arguments():
    parser = argparse.ArgumentParser(description="RTSP 录制工具")
    parser.add_argument("rtsp_url", help="RTSP 流地址，例：rtsp://user:pass@192.168.1.100:554/stream")
    parser.add_argument("--output_dir", "-o", default="./recordings", help="输出目录 (默认 ./recordings)")
    parser.add_argument("--segment_minutes", "-s", type=int, default=5, help="每段视频时长（分钟），默认 5")
    parser.add_argument("--total_duration", "-t", type=int, default=None, help="总录制时长（分钟），默认持续录制")
    parser.add_argument("--prefix", "-p", default="rtsp_rec", help="文件名前缀")
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_arguments()

    # 注册信号处理（Ctrl+C）
    signal.signal(signal.SIGINT, signal_handler)

    # 启动录制
    record_rtsp(
        rtsp_url=args.rtsp_url,
        output_dir=args.output_dir,
        segment_minutes=args.segment_minutes,
        total_duration=args.total_duration,
        prefix=args.prefix
    )