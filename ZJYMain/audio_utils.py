# -*- coding: utf-8 -*-
# @Time : 2026/1/3
# @Author : Assistant
# @Site : 
# @File : audio_utils.py
# @Software: PyCharm
"""
音频处理工具模块
提供音频时长推断和相关工具函数
"""

import json
import logging
import random

logger = logging.getLogger(__name__)


def infer_audio_duration(file_size_bytes):
    """
    根据音频文件大小推断时长（秒）

    规则：
    - 使用64kbps低码率计算，确保时长充足
    - 增加20%缓冲时间
    - 限制在30秒到3600秒之间

    参数：
        file_size_bytes: 文件大小，单位字节

    返回：
        估算的时长（秒）
    """
    return _infer_duration_by_size(
        file_size_bytes,
        bitrate_kb_s=8,  # 64 kbps = 8 KB/s
        buffer_ratio=1.2,
        min_seconds=30,
        max_seconds=3600,
    )


def infer_video_duration(file_size_bytes):
    """
    根据视频文件大小推断时长（秒）

    规则：
    - 按 1Mbps（即 128KB/s）估算
    - 增加10%缓冲时间
    - 限制在30秒到7200秒（2小时）之间

    当官方时长接口（upload.icve.com.cn/xxx/status）不可用时作为降级方案。

    参数：
        file_size_bytes: 文件大小，单位字节

    返回：
        估算的时长（秒）
    """
    return _infer_duration_by_size(
        file_size_bytes,
        bitrate_kb_s=128,  # 1 Mbps = 128 KB/s
        buffer_ratio=1.1,
        min_seconds=30,
        max_seconds=7200,
    )


def _infer_duration_by_size(file_size_bytes, bitrate_kb_s, buffer_ratio, min_seconds, max_seconds):
    """根据文件大小与码率估算时长（通用实现）"""
    try:
        file_size_bytes = float(file_size_bytes)
    except (TypeError, ValueError):
        return min_seconds

    if file_size_bytes <= 0:
        return min_seconds

    duration_seconds = file_size_bytes / 1024 / bitrate_kb_s * buffer_ratio
    duration_seconds = max(min_seconds, min(duration_seconds, max_seconds))
    return int(duration_seconds)


def time_to_seconds(time_str):
    """
    将时间字符串转换为秒数

    支持格式：
    - "SS" / "SS.mmm"
    - "MM:SS"
    - "HH:MM:SS"

    参数：
        time_str: 时间字符串

    返回：
        秒数（转换失败返回 0）
    """
    if not time_str:
        return 0

    try:
        parts = [float(p) for p in str(time_str).strip().split(':')]
    except (TypeError, ValueError):
        return 0

    if len(parts) > 3:
        return 0

    return int(sum(value * 60 ** i for i, value in enumerate(reversed(parts))))


def seconds_to_time_str(seconds):
    """
    将秒数转换为MM:SS格式的时间字符串
    
    参数：
        seconds: 秒数
    
    返回：
        MM:SS格式字符串
    """
    minutes = seconds // 60
    seconds = seconds % 60
    return f"{minutes}:{seconds:02d}"


def parse_audio_file_info(audio_info):
    """
    解析音频/视频信息，提取文件大小和URL

    参数：
        audio_info: 音频/视频信息字典

    返回：
        dict: 包含file_size和file_url的字典
    """
    try:
        file_url_data = json.loads(audio_info['fileUrl'])
        return {
            'file_size': file_url_data.get('size') or 1093170,
            'file_url': file_url_data.get('url', ''),
            'md5': file_url_data.get('md5', '')
        }
    except Exception as e:
        logger.error(f"解析媒体文件信息失败: {e}")
        return {
            'file_size': 1093170,  # 默认值
            'file_url': '',
            'md5': ''
        }


def calculate_audio_study_params(audio_info):
    """
    计算音频学习参数

    参数：
        audio_info: 音频信息字典

    返回：
        dict: 包含学习所需的各项参数
    """
    # 解析文件信息
    file_info = parse_audio_file_info(audio_info)
    file_size = file_info['file_size']

    # 推断时长
    duration_seconds = infer_audio_duration(file_size)

    # 计算学习时间（增加随机缓冲）
    study_time = duration_seconds + random.randint(12, 22)

    # 转换为时间字符串
    audio_time = seconds_to_time_str(duration_seconds)

    return {
        'duration_seconds': duration_seconds,
        'study_time': study_time,
        'audio_time': audio_time,
        'file_size': file_size,
        'file_url': file_info['file_url']
    }


def calculate_video_study_params(video_info):
    """
    计算视频学习参数（按文件大小估算时长，作为官方接口的降级方案）

    参数：
        video_info: 视频信息字典

    返回：
        dict: 包含学习所需的各项参数
    """
    file_info = parse_audio_file_info(video_info)
    file_size = file_info['file_size']

    duration_seconds = infer_video_duration(file_size)
    study_time = duration_seconds + random.randint(12, 22)

    return {
        'duration_seconds': duration_seconds,
        'study_time': study_time,
        'video_time': seconds_to_time_str(duration_seconds),
        'file_size': file_size,
        'file_url': file_info['file_url']
    }
