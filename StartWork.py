# -*- coding: utf-8 -*-
# @Time : 2022/3/31 9:30
# @Author : Melon
# @Site : 
# @Note : 
# @File : StartWork.py
# @Software: PyCharm
import logging

import ZJYMain.init_zjy as mooc_init
import ZJYMain.look_video as mook_video
from update import check_for_updates

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

APP_VERSION = 'dev' if 'TAG_NAME' in '${TAG_NAME}' else '${TAG_NAME}'

border = '*' * 80
logger.info(border)
logger.info(f'应用程序启动，版本: {APP_VERSION}')
logger.info('开源支持: https://github.com/11273/zjy-work-answer')
logger.info(border)

check_for_updates(APP_VERSION)

# ****************************************** 配置 ******************************************
# 账号
username = input('请输入账号: ')  # 账号
password = input('请输入密码: ')  # 密码
# ****************************************** 结束 ******************************************

if __name__ == '__main__':
    try:
        session = mooc_init.login(username, password)
        mook_video.start(session)
    except Exception as e:
        logging.exception('运行异常', e)
        input("程序结束，如遇错误请重新运行，多次重复错误请提交Github...")
