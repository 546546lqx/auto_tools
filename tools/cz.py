#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import cv2
import os
import argparse
from pathlib import Path

def extract_frames_by_frame_interval(video_path, output_dir, frame_interval=30, 
                                      quality=95, resize_width=None, resize_height=None,
                                      prefix="frame"):
    """
    按帧间隔抽帧
    :param video_path: 视频文件路径
    :param output_dir: 输出图片目录
    :param frame_interval: 每隔多少帧抽一帧（例如 30 表示每 30 帧抽 1 张）
    :param quality: JPEG 压缩质量 (0~100)
    :param resize_width: 缩放宽度（None 表示不缩放）
    :param resize_height: 缩放高度（None 表示不缩放）
    :param prefix: 输出图片文件名前缀
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"错误：无法打开视频文件 {video_path}")
        return False

    # 获取视频基本信息
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = total_frames / fps if fps > 0 else 0
    
    print(f"视频信息：{total_frames} 帧, {fps:.2f} fps, 时长 {duration:.2f} 秒")
    print(f"抽帧模式：每 {frame_interval} 帧抽取 1 张")
    
    os.makedirs(output_dir, exist_ok=True)
    
    frame_count = 0
    saved_count = 0
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # 每隔 frame_interval 帧保存一张
        if frame_count % frame_interval == 0:
            # 调整尺寸
            if resize_width is not None and resize_height is not None:
                frame = cv2.resize(frame, (resize_width, resize_height), interpolation=cv2.INTER_AREA)
            
            # 生成输出文件名（可添加时间戳或序号）
            filename = f"{prefix}_{saved_count+1:06d}.jpg"
            save_path = os.path.join(output_dir, filename)
            
            # 保存图片
            cv2.imwrite(save_path, frame, [cv2.IMWRITE_JPEG_QUALITY, quality])
            saved_count += 1
            print(f"已保存：{filename} (原始帧号 {frame_count})")
        
        frame_count += 1
        
        # 进度提示
        if frame_count % 1000 == 0:
            print(f"处理进度：{frame_count}/{total_frames} 帧 ({100*frame_count/total_frames:.1f}%)")
    
    cap.release()
    print(f"抽帧完成！共保存 {saved_count} 张图片到目录：{output_dir}")
    return True

def extract_frames_by_time_interval(video_path, output_dir, time_interval=1.0,
                                    quality=95, resize_width=None, resize_height=None,
                                    prefix="frame"):
    """
    按时间间隔抽帧
    :param video_path: 视频文件路径
    :param output_dir: 输出图片目录
    :param time_interval: 每隔多少秒抽一帧（例如 0.5 表示每半秒抽一张）
    :param quality: JPEG 压缩质量 (0~100)
    :param resize_width: 缩放宽度
    :param resize_height: 缩放高度
    :param prefix: 文件名前缀
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"错误：无法打开视频文件 {video_path}")
        return False
    
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = total_frames / fps if fps > 0 else 0
    
    print(f"视频信息：{total_frames} 帧, {fps:.2f} fps, 时长 {duration:.2f} 秒")
    print(f"抽帧模式：每 {time_interval} 秒抽取 1 张 (约 {int(fps * time_interval)} 帧)")
    
    os.makedirs(output_dir, exist_ok=True)
    
    # 计算需要的帧间隔（取整）
    frame_interval = max(1, int(round(fps * time_interval)))
    
    frame_count = 0
    saved_count = 0
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # 基于时间间隔的采样
        if frame_count % frame_interval == 0:
            if resize_width is not None and resize_height is not None:
                frame = cv2.resize(frame, (resize_width, resize_height), interpolation=cv2.INTER_AREA)
            
            timestamp = frame_count / fps if fps > 0 else 0
            filename = f"{prefix}_{saved_count+1:06d}.jpg"
            save_path = os.path.join(output_dir, filename)
            cv2.imwrite(save_path, frame, [cv2.IMWRITE_JPEG_QUALITY, quality])
            saved_count += 1
            print(f"已保存：{filename} (时间 {timestamp:.2f}s, 帧号 {frame_count})")
        
        frame_count += 1
        
        if frame_count % 1000 == 0:
            print(f"处理进度：{frame_count}/{total_frames} 帧 ({100*frame_count/total_frames:.1f}%)")
    
    cap.release()
    print(f"抽帧完成！共保存 {saved_count} 张图片到目录：{output_dir}")
    return True

def main():
    parser = argparse.ArgumentParser(description="MP4 视频抽帧工具（抽帧后自动删除原始视频）")
    parser.add_argument("video", help="输入视频文件路径 (.mp4)")
    parser.add_argument("--output_dir", "-o", default="./frames", help="输出图片目录 (默认 ./frames)")
    parser.add_argument("--mode", "-m", choices=["frame", "time"], default="frame", 
                        help="抽帧模式：frame=按帧间隔，time=按时间间隔 (默认 frame)")
    parser.add_argument("--interval", "-i", type=float, default=30,
                        help="间隔值：帧模式下为帧数间隔（如 30），时间模式下为秒间隔（如 0.5）")
    parser.add_argument("--quality", "-q", type=int, default=95,
                        help="JPEG 压缩质量 1~100 (默认 95)")
    parser.add_argument("--width", type=int, default=None,
                        help="输出图片宽度（像素），不指定则保持原尺寸")
    parser.add_argument("--height", type=int, default=None,
                        help="输出图片高度（像素），不指定则保持原尺寸")
    parser.add_argument("--prefix", "-p", default="frame",
                        help="输出文件名前缀 (默认 'frame')")
    
    args = parser.parse_args()
    
    # 检查视频文件是否存在
    if not os.path.exists(args.video):
        print(f"错误：视频文件不存在 {args.video}")
        return
    
    # 确保宽高同时指定或同时为 None
    if (args.width is None) != (args.height is None):
        print("错误：--width 和 --height 必须同时指定或同时省略")
        return
    
    # 记录原始视频路径
    video_path = args.video
    
    # 调用对应的抽帧函数
    success = False
    if args.mode == "frame":
        success = extract_frames_by_frame_interval(
            video_path=video_path,
            output_dir=args.output_dir,
            frame_interval=int(args.interval),
            quality=args.quality,
            resize_width=args.width,
            resize_height=args.height,
            prefix=args.prefix
        )
    else:  # time mode
        success = extract_frames_by_time_interval(
            video_path=video_path,
            output_dir=args.output_dir,
            time_interval=args.interval,
            quality=args.quality,
            resize_width=args.width,
            resize_height=args.height,
            prefix=args.prefix
        )
    
    # 抽帧成功后自动删除原始视频
    if success and os.path.exists(video_path):
        try:
            os.remove(video_path)
            print(f"已自动删除原始视频文件：{video_path}")
        except Exception as e:
            print(f"警告：删除视频文件失败 - {e}")

if __name__ == "__main__":
    main()