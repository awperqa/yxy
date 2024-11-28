from method import *

loginName = ""
password = ""
kecheng = "形势"


ocId = ""
textbook_id = ""
status = ""

# 登录 查询课程列表
login(loginName,password)
course_list = get_course()
print(course_list)
# 获取课件id
for i in course_list:
        if kecheng in i["name"]:
            ocId = i["id"]
            print(f"ocId: {ocId}")
            textbook = get_textbook(ocId)[0]
            textbook_id = textbook["courseId"]
            status = textbook["status"]
            print(f"课件状态:{'正常' if status==1 else '停止'}")
            print(f"课件id:{textbook_id}")
        if status==-1:
            raise CustomError("课件已截止...............")

class_id = get_class(ocId)

# 获取课件信息
textbook_information = get_textbook_information(ocId, textbook_id)
print(f"总章节信息{textbook_information}")
directory = get_stu(textbook_id, class_id)

for p in directory:
    print(f"当前章节:{p['nodetitle']}")
    nodeid = p["nodeid"]
    # 获取当前小章节具体内容:
    chapter_info = chapter(nodeid)
    print(f"当前小章节内容:{chapter_info}")
    items = p["items"]
    total_time = 0

    info = ""  # 学习记录
    for i in items:
        info = get_study_info(i['itemid'], 4)
        study_time = 0 if info is None else int(info["studyTime"])
        name = None if info is None else info["activity_title"]
        print(f"{name} : {study_time}")
        total_time += study_time
    print(f"开始时间: {seconds_to_hhmmss(total_time)}")

    for i in items:
        itemid = i["itemid"]
        for i in chapter_info:
            item_id2 = i["itemid"]
            if itemid == item_id2 and (info is None or info["score"] != 100 ) :
                # 初始化学习
                wholepageDTOList = i["wholepageDTOList"]
                init_time = studyrecord_init(itemid)
                init_data = init_record(itemid, init_time, get_user_name()).to_dict()
                for j in wholepageDTOList:
                    relationid = j["relationid"]
                    # 课程页面内容
                    question_list = []
                    video_list = []
                    coursepageDTOList = j["coursepageDTOList"]
                    for course_page in coursepageDTOList:
                        pageStudyRecordDTO = ""
                        if "videoLength" in course_page and course_page["videoLength"] > 0:
                            # 当前为视频
                            video_id = course_page["resourceid"]
                            watch_video(nodeid, class_id, textbook_id, video_id)
                            video_lenth = course_page["videoLength"]
                            study_time = float(video_lenth) + random.randint(0, 10)
                            video = Video(videoid=video_id, current=0.0, status=1, recordTime=0, time=video_lenth)
                            video_list.append(video)
                            pageStudyRecordDTO = get_pageStudyRecordDTO(0, relationid, study_time, video_list).to_dict()
                        elif "questionDTOList" in course_page and len(course_page["questionDTOList"]) > 0:
                            # 当前为答题
                            questionDTOList = course_page["questionDTOList"]
                            coursepageId = course_page["coursepageDTOid"]
                            parentid = course_page["parentid"]
                            study_time = random.randint(100, 500)
                            for question in questionDTOList:
                                if "questionid" in question:
                                    question_id = question["questionid"]
                                    score = question["score"]
                                    answerList = get_answer(question_id, parentid)
                                    question_i = Question(questionid=question_id, answerList=answerList, score=score)
                                    question_list.append(question_i)
                            pageStudyRecordDTO = get_pageStudyRecordDTO(1, relationid, study_time, question_list,
                                                                        coursepageId=coursepageId).to_dict()
                        else:
                            study_time = random.randint(100, 500)
                            pageStudyRecordDTO = get_pageStudyRecordDTO(0, relationid, study_time, []).to_dict()

                    init_data["pageStudyRecordDTOList"].append(pageStudyRecordDTO)

                print(init_data)
                record(json.dumps(init_data, ensure_ascii=False))

    total_time = 0
    for i in items:
        info = get_study_info(i['itemid'], 4)
        study_time = int(info["studyTime"])
        name = info["activity_title"]
        print(f"{name} : {study_time}")
        total_time += study_time
    print(f"结束时间: {seconds_to_hhmmss(total_time)}")


