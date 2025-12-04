from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime
from enum import Enum


# ========== 枚举类型 ==========

class ProblemType(str, Enum):
    """题型"""
    CHOICE = "choice"
    FILL = "fill"
    SOLUTION = "solution"


class Difficulty(str, Enum):
    """难度"""
    L1 = "L1"  # 基础题：会做就得分，占50%
    L2 = "L2"  # 中档题：区分度题目，占35%
    L3 = "L3"  # 压轴题：拔高题目，占15%


class AnswerType(str, Enum):
    """答案类型"""
    INTEGER = "integer"       # 整数
    FLOAT = "float"           # 浮点数
    EXPR = "expr"            # 表达式
    TEXT = "text"            # 文本


class AbilityTag(str, Enum):
    """能力要求标签"""
    MEMORY = "memory"         # 记忆：公式、定义
    UNDERSTAND = "understand" # 理解：概念辨析
    APPLY = "apply"          # 应用：套公式解题
    ANALYZE = "analyze"      # 分析：多步推导
    SYNTHESIZE = "synthesize" # 综合：多知识点融合
    MODEL = "model"          # 建模：实际问题数学化


class ReviewStatus(str, Enum):
    """审核状态"""
    PENDING = "pending"       # 待审核
    APPROVED = "approved"     # 已通过
    REJECTED = "rejected"     # 已拒绝
    REVISION = "revision"     # 需修改


# ========== 基础模型 ==========

class ProblemRequest(BaseModel):
    """题目请求"""
    topic: str = "导数基础"
    difficulty: str = "基础"


class ProblemResponse(BaseModel):
    """题目响应（保持向后兼容）"""
    id: str
    topic: str
    difficulty: str
    question: str
    answer: str
    solution: str
    options: List[str]
    tags: List[str] = []


# ========== 扩展的题目模型 ==========

class QuestionMetadata(BaseModel):
    """题目元信息"""
    questionId: str
    topic: str
    difficulty: Difficulty
    type: ProblemType

    # 内容
    question: str
    answer: str
    solution: str
    options: Optional[List[str]] = None

    # 答案相关
    answerType: Optional[AnswerType] = None
    answerExpr: Optional[str] = None  # SymPy表达式字符串

    # 分类标签
    knowledgePoints: List[str] = []   # 知识点标签：["导数", "单调性"]
    abilityTags: List[AbilityTag] = [] # 能力要求：["apply", "analyze"]
    tags: List[str] = []              # 通用标签

    # 章节信息
    chapter: Optional[str] = None
    section: Optional[str] = None

    # 来源信息
    source: str = "generated"         # "real_exam_2023" / "generated" / "manual"
    isRealExam: bool = False
    templateId: Optional[str] = None  # 题型模板ID

    # 质量统计（由系统自动更新）
    totalAttempts: int = 0            # 总作答次数
    correctCount: int = 0             # 正确次数
    correctRate: Optional[float] = None        # 正确率
    discriminationIndex: Optional[float] = None # 区分度
    avgTimeSeconds: Optional[float] = None     # 平均耗时
    optionDistribution: Optional[Dict[str, float]] = None # 选项分布

    # 审核状态
    reviewStatus: ReviewStatus = ReviewStatus.PENDING
    reviewerId: Optional[str] = None
    reviewComment: Optional[str] = None

    # 时间戳
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None


# ========== 作答记录 ==========

class AnswerRecord(BaseModel):
    """学生作答记录"""
    recordId: str
    studentId: str
    questionId: str
    userAnswer: str
    isCorrect: bool
    timeSpent: int  # 秒
    answeredAt: datetime


class AnswerSubmission(BaseModel):
    """提交答案请求"""
    studentId: str
    questionId: str
    userAnswer: str
    timeSpent: int  # 秒


# ========== 学生能力画像 ==========

class StudentProfile(BaseModel):
    """学生能力画像"""
    studentId: str

    # 知识点掌握度 {"导数": 0.75, "极限": 0.60}
    knowledgeMastery: Dict[str, float] = {}

    # 题型正确率 {"choice": 0.80, "fill": 0.65}
    questionTypeAccuracy: Dict[str, float] = {}

    # 难度正确率 {"L1": 0.90, "L2": 0.60, "L3": 0.30}
    difficultyAccuracy: Dict[str, float] = {}

    # 做题统计
    totalProblems: int = 0
    correctCount: int = 0
    avgTimePerProblem: Optional[float] = None

    # 薄弱知识点
    weakPoints: List[str] = []

    # 预测分数（基于当前数据）
    predictedScore: Optional[float] = None

    updatedAt: datetime


# ========== 质量统计 ==========

class QualityStats(BaseModel):
    """题目质量统计"""
    questionId: str
    totalAttempts: int
    correctCount: int
    correctRate: float
    avgTimeSeconds: float
    topGroupCorrectRate: Optional[float] = None  # 高分组正确率
    lowGroupCorrectRate: Optional[float] = None  # 低分组正确率
    discriminationIndex: Optional[float] = None  # 区分度
    optionDistribution: Optional[Dict[str, float]] = None


class QualityStatsUpdate(BaseModel):
    """更新质量统计请求"""
    questionId: str
    stats: QualityStats


# ========== 个性化推荐 ==========

class RecommendationRequest(BaseModel):
    """推荐题目请求"""
    studentId: str
    mode: str = "weak_points"  # "weak_points" / "comprehensive" / "exam_prep"
    count: int = 20


class RecommendationResponse(BaseModel):
    """推荐题目响应"""
    questions: List[QuestionMetadata]
    recommendationReason: str


# ========== 审核相关 ==========

class ReviewRequest(BaseModel):
    """审核请求"""
    questionId: str
    reviewerId: str
    status: ReviewStatus
    comment: Optional[str] = None



