import json
from dataclasses import dataclass, field, asdict
from typing import List, Optional


@dataclass
class StartEndTime:
    startTime: int
    endTime: int
@dataclass
class Question:
    questionid: int
    answerList: List[str]
    score: int
@dataclass
class Video:
    videoid: int
    current: float
    status: int
    recordTime: float
    time: float
    startEndTimeList: List[StartEndTime] = field(default_factory=list)

# 作业课件对象
@dataclass
class QuestionStudyRecordDTO:
    pageid: int
    complete: int
    studyTime: int
    score: int
    answerTime: int
    submitTimes: int
    coursepageId: int
    questions: List[Question] = field(default_factory=list)
    videos: List = field(default_factory=list)
    speaks: List = field(default_factory=list)

    def to_json(self):
        # 使用 asdict 将 dataclass 转换为字典，然后使用 json.dumps 转换为 JSON 字符串
        return json.dumps(asdict(self), ensure_ascii=False)

    def to_dict(self):
        # 使用 asdict 将 dataclass 转换为字典
        return asdict(self)

@dataclass
class PageStudyRecordDTO:
    pageid: int
    complete: int
    studyTime: int
    score: int
    answerTime: int
    submitTimes: int
    questions: List[Question] = field(default_factory=list)
    videos: List[Video] = field(default_factory=list)
    speaks: List = field(default_factory=list)

    def to_json(self):
        # 使用 asdict 将 dataclass 转换为字典，然后使用 json.dumps 转换为 JSON 字符串
        return json.dumps(asdict(self), ensure_ascii=False)

    def to_dict(self):
        # 使用 asdict 将 dataclass 转换为字典
        return asdict(self)

@dataclass
class StudyRecord:
    itemid: int
    autoSave: int
    withoutOld: Optional[None]  # Optional because it can be null in the JSON
    complete: int
    studyStartTime: int
    userName: str
    score: int
    pageStudyRecordDTOList: List[object]

    def to_json(self):
        # 使用 asdict 将 dataclass 转换为字典，然后使用 json.dumps 转换为 JSON 字符串
        return json.dumps(asdict(self), ensure_ascii=False)

    def to_dict(self):
        # 使用 asdict 将 dataclass 转换为字典
        return asdict(self)