# -*- coding: utf-8 -*-
# @Time : 2022/3/31 9:54
# @Author : Melon
# @Site : 
# @File : look_video.py
# @Software: PyCharm
import base64
import json
import logging
import random
import time
from urllib.parse import quote

from Crypto.Cipher import AES
from Crypto.Hash import MD5
from Crypto.Util.Padding import pad

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36',
}

BASE_URL = 'https://zjy2.icve.com.cn/prod-api'

# 获取学习课程列表
GET_LEARNNING_COURSE_LIST = BASE_URL + '/spoc/courseInfoStudent/myCourseList'

# 获取一级目录
GET_PROCESS_LIST = BASE_URL + '/spoc/courseDesign/study/record'

# 刷课记录时长
STU_PROCESS_CELL_LOG = BASE_URL + '/spoc/studyRecord/update'

# PPT类型获取总页数
GET_URL_PNGS = BASE_URL + '/spoc/oss/getUrlPngs'

# 视频获取时长
GET_VIDEO_TIME = 'https://upload.icve.com.cn/{}/status'


# 1.获取所有课程
def get_learnning_course_list(session):
    data = {
        'pageNum': 1,
        'pageSize': 1000
    }
    result = session.get(url=GET_LEARNNING_COURSE_LIST, headers=headers, params=data)
    return result.json()


# 2.得到一级目录
def get_process_list(session, course_id, course_info_id, open_class_id, parent_id, level):
    data = {
        'courseId': course_id,
        'courseInfoId': course_info_id,
        'parentId': parent_id,
        "level": level,
        "classId": open_class_id
    }

    result = session.get(url=GET_PROCESS_LIST, params=data, headers=headers)
    return result.json()


# 6.开始刷课--------->
def stu_process_cell_log(session, course_info_id, class_id, study_time, source_id, total_num):
    data = {
        "courseInfoId": course_info_id,
        "classId": class_id,
        "studyTime": study_time,
        "sourceId": source_id,
        "totalNum": total_num,
        "actualNum": total_num,
        "lastNum": total_num,
    }

    def encrypt_data(_data):
        access_token = session.access_token
        key = MD5.new(access_token.encode()).hexdigest()[:16]
        data_bytes = json.dumps(_data, separators=(',', ':')).encode('utf-8')
        padded_data = pad(data_bytes, AES.block_size)
        cipher = AES.new(key.encode('utf-8'), AES.MODE_ECB)
        encrypted_data = cipher.encrypt(padded_data)
        return base64.b64encode(encrypted_data).decode()

    param = {"param": quote(encrypt_data(data))}
    result = session.post(url=STU_PROCESS_CELL_LOG, json=param, headers=headers)
    try:
        return result.json()['msg']
    except Exception as e:
        logging.error(result.text, e)


# 获取总页数
def get_url_pngs(session, file_url):
    data = {'fileUrl': file_url, }
    result = session.get(url=GET_URL_PNGS, params=data, headers=headers)
    return len(result.json()['data'])


# 获取总时长
def get_video_time(session, file_url):
    result = session.get(url=GET_VIDEO_TIME.format(file_url), headers=headers)
    return result.json()


def study_record(session, info, class_id):
    sleep_randint = random.randint(5, 10)
    time.sleep(sleep_randint)
    name = info['name']
    file_type = info['fileType']
    course_id = info['id']
    course_info_id = info['courseInfoId']
    file_url = json.loads(info['fileUrl'])['url']
    if file_type == "img":
        resp_result = stu_process_cell_log(session, course_info_id, class_id, random.randint(12, 22), course_id, 1)
        sleep_randint = random.randint(5, 10)
        logging.info('\t\t\t\t\t\t学习课件中... 课程: %s 延时: %s 结果: %s', name, sleep_randint, resp_result)
        time.sleep(sleep_randint)
    elif file_type == "ppt" or file_type == "doc":
        total_num = get_url_pngs(session, file_url)
        resp_result = stu_process_cell_log(session, course_info_id, class_id, random.randint(12, 22), course_id,
                                           total_num)
        sleep_randint = random.randint(5, 10)
        logging.info('\t\t\t\t\t\t学习课件中... 课程: %s 延时: %s 结果: %s', name, sleep_randint, resp_result)
        time.sleep(sleep_randint)
    elif file_type == "video":
        video_time = get_video_time(session, file_url)['args']['duration']
        total_seconds = int(sum(float(x) * 60 ** i for i, x in enumerate(reversed(video_time.split(':')))))
        study_time = total_seconds + random.randint(12, 22)
        resp_result = stu_process_cell_log(session, course_info_id, class_id, study_time, course_id, total_seconds)
        sleep_randint = random.randint(5, 10)
        logging.info('\t\t\t\t\t\t学习课件中... 课程: %s 延时: %s 结果: %s', name, sleep_randint, resp_result)
        time.sleep(sleep_randint)


def start(session, jump_content):
    separator = "*" * 40
    logger.info(separator)
    logger.info(f"运行信息")
    logger.info(separator)
    logger.info(f"* 跳过课程: {jump_content if jump_content is not None else ''}")
    logger.info(separator)
    logger.info("开始执行")
    logger.info(separator)
    course = get_learnning_course_list(session)

    jump_list = []
    if jump_content is not None and '#' in jump_content:
        jump_list = jump_content.split('#')[1:]

    logging.info("--------------------------------【加载课程】---------------------------")
    for i in course['rows']:
        logging.info("【%s%%】《%s》- %s %s", i['studySpeed'], i['courseName'], i['presidingTeacher'], i['termName'])
    logging.info("--------------------------------【加载完成】---------------------------")
    time.sleep(random.uniform(1, 1.5))
    for i in course['rows']:
        logging.info("进入课程：【%s】", i['courseName'])
        if any(s in i['courseName'] for s in jump_list):
            logger.info("\t匹配到过滤条件: %s - 跳过", i['courseName'])
            continue
        time.sleep(random.uniform(1, 1.5))
        # 一级目录
        moduleList1 = get_process_list(session, i['courseId'], i['courseInfoId'], i['classId'], 0, 1)

        for j in moduleList1:
            time.sleep(random.uniform(0.5, 1))
            if j['speed'] == 100:
                logging.info("\t%s 课程已刷进度 100", j['name'])
                continue
            logging.info("\t%s", j['name'])
            # 二级目录
            moduleList2 = get_process_list(session, i['courseId'],i['courseInfoId'], i['classId'], j['id'], 2)
            for k in moduleList2:
                # time.sleep(random.uniform(0.5, 1))
                logging.info("\t\t%s", k['name'])
                # 三级目录
                moduleList3 = get_process_list(session, i['courseId'],i['courseInfoId'], i['classId'], k['id'], 3)
                for m in moduleList3:
                    # time.sleep(random.uniform(0.5, 1))
                    if m['speed'] == 100:
                        logging.info("\t\t\t%s 课程已刷进度 100", m['name'])
                        continue
                    logging.info("\t\t\t\t%s", m['name'])
                    # 如果只有三级目录
                    if not m.get('children') or not len(m.get('children', [])):
                        # 如果课程完成-不刷课
                        if m['speed'] == 100:
                            logging.info("\t\t\t\t\t%s 课程已刷进度 100%", m['name'])
                            continue
                        # 将信息拿去刷课
                        try:
                            study_record(session, m, i['classId'])
                        except Exception as e:
                            logging.error("错误跳过: %s", e)
                            # 四级目录(最终)
                    else:
                        for n in m.get('children', []):
                            # time.sleep(random.uniform(1, 1.5))
                            # 如果课程完成-不刷课
                            if n['speed'] == 100:
                                logging.info("\t\t\t\t\t%s 课程已刷进度 100", n['name'])
                                continue
                            # 将信息拿去刷课

                            try:
                                study_record(session, n, i['classId'])
                            except Exception as e:
                                logging.error("错误跳过: %s", e)
