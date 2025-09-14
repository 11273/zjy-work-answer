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
from update import check_for_updates

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

APP_VERSION = "dev" if "TAG_NAME" in "${TAG_NAME}" else "${TAG_NAME}"

border = "*" * 80
logger.info(border)
logger.info(f"应用程序启动，版本: {APP_VERSION}")
logger.info("开源支持: https://github.com/11273/zjy-work-answer")
logger.info(border)

check_for_updates(APP_VERSION)

# ****************************************** 配置 ******************************************
time.sleep(1)

jump = int(input("是否有需要跳过的课程 1.是 or 2.否: ") or 2)
jump_content = None
if jump == 1:
    print(
        "\t请输入跳过课程名(模糊匹配), 例如\n\t\t输入多个文本随机井号后面的: #设计#思想道德#技术\n\t\t输入单个将固定跳过一个课程: #思想"
    )
    jump_content = input("请输入需要跳过的课程关键字(#电商): ") or ""
# ****************************************** 结束 ******************************************

if __name__ == "__main__":
    try:
        # 使用交互式登录
        session = mooc_init.login_interactive()

        if session:
            mook_video.start(session, jump_content=jump_content)
        else:
            logger.error("❌ 登录失败，程序退出")
            input("程序结束，如遇错误请重新运行，多次重复错误请提交Github...")
    except Exception as e:
        logging.exception("运行异常", e)
        input("程序结束，如遇错误请重新运行，多次重复错误请提交Github...")
