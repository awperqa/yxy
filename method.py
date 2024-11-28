import random
import re

from constant import (LOGIN_URL,UserAgent,CHEATCHECK_URL,CHECK_URL,LOGINAPI_URL,
                      COURSE_URL,Authorization,TEXTBOOK_URL,TEXTBOOK_INFORMATION_URL,
                      STU_URL,CLASS_URL,STUDYRECORD_URL,CHAPTER_URL,HEARTBEAT_URL,STUDY_TIME_URL,ANSWER_URL,RECORD_URL,AES_KEY,WATCH_VIDEO_URL,USER_URL)
import requests
import logging
import entry
from Crypto.Cipher import DES
from Crypto.Util.Padding import pad
import base64
import json
from Crypto.Util.Padding import unpad
from entry import StartEndTime, Question, Video, QuestionStudyRecordDTO, StudyRecord, PageStudyRecordDTO
from deal_error import CustomError
import time

session = requests.Session()
session.headers.update({"User-Agent": UserAgent})

def cheatCheck(loginName):
    data = {"loginName":loginName}
    response = session.get(CHEATCHECK_URL, params=data)
    print(response.text)
def check(loginName, password):
    data = {"loginName":loginName,"password":password}
    response = session.get(CHECK_URL, params=data)
    print(response.text)
def loginApi(loginName):
    data = {"loginName":loginName}
    response = session.get(LOGINAPI_URL, params=data)
    print(response.text)
def seconds_to_hhmmss(seconds):
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours:02}:{minutes:02}:{seconds:02}"
def des_encrypt(data, key):
    """
    使用 DES 加密数据
    :param data: 要加密的数据（字符串）
    :param key: DES 密钥（8 字节字符串）
    :return: 加密后的 Base64 字符串
    """
    data = re.sub(r"\s+", "", data)
    # 确保密钥长度为 8 字节
    if len(key) != 8:
        raise ValueError("DES 密钥长度必须为 8 字节")

    # 初始化 DES 加密器（ECB 模式）
    cipher = DES.new(key.encode('utf-8'), DES.MODE_ECB)

    # 数据需要先进行 PKCS7 填充
    padded_data = pad(data.encode('utf-8'), DES.block_size)

    # 加密
    encrypted_bytes = cipher.encrypt(padded_data)

    # 转为 Base64 字符串
    encrypted_base64 = base64.b64encode(encrypted_bytes).decode('utf-8')

    return encrypted_base64
def des_decrypt(encrypted_data, key):
    """
    使用 DES 解密数据
    :param encrypted_data: 加密后的 Base64 字符串
    :param key: DES 密钥（8 字节字符串）
    :return: 解密后的原始字符串
    """
    # 确保密钥长度为 8 字节
    if len(key) != 8:
        raise ValueError("DES 密钥长度必须为 8 字节")

    # 初始化 DES 解密器（ECB 模式）
    cipher = DES.new(key.encode('utf-8'), DES.MODE_ECB)

    # 将 Base64 解码为加密字节
    encrypted_bytes = base64.b64decode(encrypted_data)

    # 解密并移除填充
    decrypted_bytes = unpad(cipher.decrypt(encrypted_bytes), DES.block_size)

    # 返回解密后的字符串
    return decrypted_bytes.decode('utf-8')

def init_record(itemid, init_time, userName):
    pageStudyRecordDTOList = []
    record = StudyRecord(
        itemid=itemid,
        autoSave=0,
        withoutOld=None,
        complete=1,
        studyStartTime=init_time,
        userName=userName,
        score=100,
        pageStudyRecordDTOList=pageStudyRecordDTOList
    )
    return record
def get_pageStudyRecordDTO(type, pageid, studyTime, type_list, **kwargs):
    if type == 0:
        pageStudyRecordDTO = PageStudyRecordDTO(
            pageid=pageid,
            complete=1,
            studyTime=studyTime,
            score=100,
            answerTime=1,
            submitTimes=0,
            questions=[],
            videos=type_list if type_list else [],
            speaks=[]
        )
        return pageStudyRecordDTO
    if type == 1:
        questionStudyRecordDTO = QuestionStudyRecordDTO(
            pageid=pageid,
            complete=1,
            studyTime=studyTime,
            score=100,
            answerTime=1,
            submitTimes=0,
            coursepageId=kwargs["coursepageId"],
            questions=type_list,
            videos=[],
            speaks=[]
        )
        return questionStudyRecordDTO

# 登录
def login(loginName, password):
    data = {
        'loginName': loginName,
        'password': password
    }
    response = session.post(LOGIN_URL, data=data, allow_redirects=False)
    print(response.text)
    print(response.status_code)
    if response.cookies is not None:
        session.headers.update({
            "User-Agent": UserAgent,
            "Authorization": response.cookies.get('AUTHORIZATION'),
            "Content-Type": "application/json"
        })
        for i in response.cookies:
            print(i.name, i.value)
    if response.status_code == 302:
        print("登录成功")
        time.sleep(1)
    else:
        print("登录失败")
        raise CustomError("账号密码错误")

# 课程
def get_course():
    data = {
        'keyword': "",
        'publishStatus': 1,
        'type': 1,
        'pn': 1,
        'ps': 15,
        'lang': "zh"
    }
    response = session.get(COURSE_URL, params=data, timeout=60)
    response.raise_for_status()  # 检查 HTTP 响应状态码，如果不是 2xx 会抛出异常
    json_data = response.json()
    if "courseList" in json_data and isinstance(json_data["courseList"], list):
        logging.info("课程列表获取成功！")
        return json_data["courseList"]
        time.sleep(1)
    else:
        logging.error("响应中未包含课程列表或格式错误")
        raise CustomError("获取课程列表失败")


# 课件id
def get_textbook(ocId):
    url = TEXTBOOK_URL + "/" + str(ocId) + "/" + "list"
    data = {"lang":"zh"}
    response = session.get(url, params=data)
    response.raise_for_status()  # 检查 HTTP 响应状态码，如果不是 2xx 会抛出异常
    json_data = response.json()
    if len(json_data) != 0:
        logging.info("课件获取成功！")
        time.sleep(1)
        return json_data
    else:
        logging.error("响应中未包含课件或格式错误")
        raise CustomError("无课件")


# 课件章节信息
def get_textbook_information(ocId, textbookId):
    data = {
        'currentPlatformType': 1,
        'ocId': ocId,
        'textbookId': textbookId,
        'lang': 'zh'
    }
    response = session.get(TEXTBOOK_INFORMATION_URL, params=data, timeout=60)
    response.raise_for_status()  # 检查 HTTP 响应状态码，如果不是 2xx 会抛出异常
    json_data = response.json()
    if "list" in json_data and isinstance(json_data["list"], list):
        logging.info("课件信息获取成功！")
        time.sleep(1)
        return json_data["list"]
    else:
        logging.error("响应中未包含课件信息或格式错误")
        raise CustomError("课件信息获取失败")

# 获取班级
def get_class(ocId):
    url = CLASS_URL + "/" + str(ocId)
    data = {"lang":"zh"}
    response = session.get(url, params=data, timeout=60)
    response.raise_for_status()  # 检查 HTTP 响应状态码，如果不是 2xx 会抛出异常
    json_data = response.json()
    if "classId" in json_data :
        logging.info("班级id获取成功！")
        time.sleep(1)
        return json_data["classId"]
    else:
        logging.error("响应中未包含班级id或格式错误")
        raise CustomError("获取班级id失败")

# 课件章节详情内容
def get_stu(textbook_id, classId):
    url = STU_URL + "/" + str(textbook_id) + "/" + "directory"
    data = {"classId": classId}
    response = session.get(url, params=data, timeout=60)
    response.raise_for_status()  # 检查 HTTP 响应状态码，如果不是 2xx 会抛出异常
    json_data = response.json()
    if "chapters" in json_data and isinstance(json_data["chapters"], list):
        logging.info("学习信息获取成功！")
        time.sleep(1)
        return json_data["chapters"]
    else:
        logging.error("响应中未包含学习信息或格式错误")
        raise CustomError("课件章节获取失败")

# 初始化学习记录
def studyrecord_init(itemid):
    url = STUDYRECORD_URL + "/" + str(itemid)
    response = session.get(url, timeout=60)
    response.raise_for_status()  # 检查 HTTP 响应状态码，如果不是 2xx 会抛出异常
    json_data = response.json()
    if json_data is not None:
        logging.info("学习记录初始化成功！")
        time.sleep(1)
        return json_data
    else:
        logging.error("响应中未包含学习记录初始化或格式错误")
        raise CustomError("学习初始化失败")

# 学习章节内容   内含视频长度
def chapter(nodeid):
    url = CHAPTER_URL + "/" + str(nodeid)
    response = session.get(url, timeout=60)
    response.raise_for_status()  # 检查 HTTP 响应状态码，如果不是 2xx 会抛出异常
    json_data = response.json()
    if "wholepageItemDTOList" in json_data:
        logging.info("学习详情获取成功！")
        time.sleep(1)
        return json_data["wholepageItemDTOList"]
    else:
        logging.error("响应中未包含学习详情或格式错误")
        raise CustomError("课件详情获取失败")

def record(data):
    params = {"courseType": 4,"platform": "PC"}
    data_json = des_encrypt(data, AES_KEY)
    headers = {
        "authorization": session.cookies.get('AUTHORIZATION'),
        "ua-authorization": session.cookies.get('AUTHORIZATION'),
        "user-agent": UserAgent,
        "Content-Type": "application/json"
    }
    response = session.post(RECORD_URL, params = params, data = data_json, headers=headers, timeout=60)
    response.raise_for_status()  # 检查 HTTP 响应状态码，如果不是 2xx 会抛出异常
    json_data = response.json()
    if json_data == 1:
        logging.info("进度保存成功！")
        time.sleep(1)
        return json_data
    else:
        logging.error("响应中未包含学习详情或格式错误")
        raise CustomError("进度保存失败")


# 学习心跳检测
def heartbeat(itemid, init_time):
    url = HEARTBEAT_URL + "/" + str(itemid) + "/" + str(init_time)
    response = session.get(url, timeout=60)
    response.raise_for_status()  # 检查 HTTP 响应状态码，如果不是 2xx 会抛出异常
    json_data = response.json()
    if json_data["status"] == 0:
        logging.info("学习记录心跳检测成功！")
        time.sleep(1)
        return json_data
    else:
        logging.error("响应中未包含学习记录心跳检测或格式错误")
        raise CustomError("心跳检测失败")


# 获取学习信息
def get_study_info(itemid, courseType):
    url = STUDY_TIME_URL + "/" + str(itemid)
    data = {"courseType":courseType}
    response = session.get(url,params=data, timeout=60)
    response.raise_for_status()  # 检查 HTTP 响应状态码，如果不是 2xx 会抛出异常
    if response.text != "" and response.text is not None:
        json_data = response.json()
        if json_data is not None:
            logging.info("学习信息获取成功！")
            time.sleep(1)
            return json_data
        else:
            logging.error("响应中未包含学习信息或格式错误")
            raise CustomError("学习记录获取失败")
    else:
        return None


# 获取答案
def get_answer(question_id, parentId):
    url = ANSWER_URL + "/" + str(question_id)
    data = {"parentId":parentId}
    response = session.get(url, params= data, timeout=60)
    response.raise_for_status()  # 检查 HTTP 响应状态码，如果不是 2xx 会抛出异常
    json_data = response.json()
    if "correctAnswerList" in json_data:
        logging.info("获取答案成功！")
        time.sleep(1)
        return json_data["correctAnswerList"]
    else:
        logging.error("响应中未包含答案或格式错误")
        raise CustomError("获取答案失败")


# 开始观看视频
def watch_video(chapterId, classId, courseId, videoId):
    data = {
        "chapterId": chapterId,
        "classId": classId,
        "courseId": courseId,
        "videoId": videoId
    }
    response = session.post(WATCH_VIDEO_URL, json= data, timeout=60)
    response.raise_for_status()  # 检查 HTTP 响应状态码，如果不是 2xx 会抛出异常
    logging.info("观看视频成功！")
    time.sleep(1)


# 获取用户姓名
def get_user_name():
    response = session.get(USER_URL, timeout=60)
    response.raise_for_status()  # 检查 HTTP 响应状态码，如果不是 2xx 会抛出异常
    if "name" in response.json():
        logging.info("获取用户姓名成功！")
        time.sleep(1)
        return response.json()["name"]
    else:
        raise CustomError("获取用户姓名失败")





