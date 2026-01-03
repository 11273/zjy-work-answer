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
    if file_size_bytes <= 0:
        return 30  # 最少30秒
    
    # 使用64kbps码率计算（最低码率，得到最长时长）
    # 64 kbps = 8 KB/s
    size_kb = file_size_bytes / 1024
    bitrate_kb_s = 8  # KB/s
    
    duration_seconds = size_kb / bitrate_kb_s
    
    # 增加20%的缓冲时间，确保时长充足
    duration_seconds = duration_seconds * 1.2
    
    # 限制范围：最少30秒，最多3600秒（1小时）
    duration_seconds = max(30, min(duration_seconds, 3600))
    
    return int(duration_seconds)


def time_to_seconds(time_str):
    """
    将时间字符串转换为秒数
    
    支持格式：
    - "MM:SS" 
    - "HH:MM:SS"
    
    参数：
        time_str: 时间字符串
    
    返回：
        秒数
    """
    if not time_str:
        return 0
    
    parts = time_str.split(':')
    if len(parts) == 2:  # MM:SS
        minutes, seconds = int(parts[0]), int(parts[1])
        return minutes * 60 + seconds
    elif len(parts) == 3:  # HH:MM:SS
        hours, minutes, seconds = int(parts[0]), int(parts[1]), int(parts[2])
        return hours * 3600 + minutes * 60 + seconds
    else:
        return 0


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
    解析音频信息，提取文件大小和URL
    
    参数：
        audio_info: 音频信息字典
    
    返回：
        dict: 包含file_size和file_url的字典
    """
    try:
        file_url_data = json.loads(audio_info['fileUrl'])
        return {
            'file_size': file_url_data.get('size', 1093170),
            'file_url': file_url_data.get('url', ''),
            'md5': file_url_data.get('md5', '')
        }
    except Exception as e:
        logger.error(f"解析音频信息失败: {e}")
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
