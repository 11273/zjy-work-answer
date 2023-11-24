# -*- coding: utf-8 -*-
# @Time : 2022/3/31 9:30
# @Author : Melon
# @Site : 
# @Note : 
# @File : StartWork.py
# @Software: PyCharm
import logging
import time

import ZJYMain.init_zjy as mooc_init
import ZJYMain.look_video as mook_video

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
# ****************************************** 配置 ******************************************
# 账号
username = ""  # 账号
password = ""  # 密码
# ****************************************** 结束 ******************************************

if __name__ == '__main__':
    for i in range(10):
        try:
            session = mooc_init.login(username, password)
            mook_video.start(session)
            break
        except Exception as e:
            logging.exception('重试次数：%s, e: %s', i, e)
            time.sleep(60 * i)
            continue
