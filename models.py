"""
数据模型定义：题目层 + 用户实例层
"""

from pydantic import BaseModel
from typing import List, Dict
from datetime import datetime


class Question(BaseModel):
    """
    题目层：每道题唯一存在
    """
    questionId: str  # 唯一ID，格式如 "trig_1_001"
    topic: str
    difficulty: str  # L1/L2/L3
    type: str  # choice/fill/solution
    chapter: str | None = None
    section: str | None = None
    question: str
    answer: str
    solution: str
    options: List[str] = []
    tags: List[str] = []
    answerType: str | None = None
    answerExpr: str | None = None
    createdAt: str | None = None


class PaperSection(BaseModel):
    """
    试卷的一个部分（如：选择填空部分、解答题部分）
    """
    sectionName: str  # 如 "选择填空题"、"解答题"
    questionIds: List[str]  # 该部分包含的题目ID列表


class UserPaperInstance(BaseModel):
    """
    用户实例层：用户某次训练的实例
    """
    instanceId: str  # 实例ID，格式如 "user123_20231202_001"
    userId: str | None = None  # 用户ID（可选，本地存储时可能为空）
    topic: str  # 主题，如 "三角函数"
    difficulty: str  # L1/L2/L3
    chapter: str | None = None
    section: str | None = None
    sections: List[PaperSection]  # 分段题目列表
    totalQuestions: int  # 总题数
    createdAt: str  # 创建时间
    completedAt: str | None = None  # 完成时间
    
    # 用户作答记录（可选，也可以单独存储）
    userAnswers: Dict[str, str] = {}  # {questionId: userAnswer}
    answerStatus: Dict[str, bool] = {}  # {questionId: isCorrect}


class CreateInstanceRequest(BaseModel):
    """
    创建用户训练实例的请求
    """
    userId: str | None = None
    topic: str
    difficulty: str = "L1"
    chapter: str | None = None
    section: str | None = None
    questionCount: int = 20  # 本次训练的题目数量


class CreateInstanceResponse(BaseModel):
    """
    创建实例的响应
    """
    instance: UserPaperInstance
    questions: List[Question]  # 实例包含的所有题目详情

