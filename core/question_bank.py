"""
题库管理模块
负责题目的CRUD、质量统计、查询等操作
"""
import json
import os
from typing import List, Optional, Dict
from datetime import datetime
from schemas import QuestionMetadata, QualityStats, Difficulty, ProblemType


class QuestionBank:
    """题库管理器"""

    def __init__(self, data_file: str = "data/questions.json"):
        self.data_file = data_file
        self.questions: Dict[str, QuestionMetadata] = {}
        self.load()

    def load(self):
        """从文件加载题库"""
        if not os.path.exists(self.data_file):
            os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
            self.save()
            return

        with open(self.data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            for item in data:
                question = QuestionMetadata(**item)
                self.questions[question.questionId] = question

    def save(self):
        """保存题库到文件"""
        data = [q.model_dump(mode='json') for q in self.questions.values()]
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def get(self, question_id: str) -> Optional[QuestionMetadata]:
        """获取单个题目"""
        return self.questions.get(question_id)

    def add(self, question: QuestionMetadata) -> QuestionMetadata:
        """添加题目"""
        if question.questionId in self.questions:
            raise ValueError(f"题目ID {question.questionId} 已存在")

        self.questions[question.questionId] = question
        self.save()
        return question

    def update(self, question: QuestionMetadata) -> QuestionMetadata:
        """更新题目"""
        if question.questionId not in self.questions:
            raise ValueError(f"题目ID {question.questionId} 不存在")

        question.updatedAt = datetime.now()
        self.questions[question.questionId] = question
        self.save()
        return question

    def delete(self, question_id: str) -> bool:
        """删除题目"""
        if question_id in self.questions:
            del self.questions[question_id]
            self.save()
            return True
        return False

    def query(
        self,
        topic: Optional[str] = None,
        difficulty: Optional[Difficulty] = None,
        question_type: Optional[ProblemType] = None,
        knowledge_points: Optional[List[str]] = None,
        chapter: Optional[str] = None,
        section: Optional[str] = None,
        is_real_exam: Optional[bool] = None,
        review_status: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[QuestionMetadata]:
        """查询题目"""
        results = list(self.questions.values())

        # 筛选条件
        if topic:
            results = [q for q in results if q.topic == topic]

        if difficulty:
            results = [q for q in results if q.difficulty == difficulty]

        if question_type:
            results = [q for q in results if q.type == question_type]

        if knowledge_points:
            results = [
                q for q in results
                if any(kp in q.knowledgePoints for kp in knowledge_points)
            ]

        if chapter:
            results = [q for q in results if q.chapter == chapter]

        if section:
            results = [q for q in results if q.section == section]

        if is_real_exam is not None:
            results = [q for q in results if q.isRealExam == is_real_exam]

        if review_status:
            results = [q for q in results if q.reviewStatus == review_status]

        # 限制数量
        if limit:
            results = results[:limit]

        return results

    def update_quality_stats(self, question_id: str, stats: QualityStats):
        """更新题目质量统计"""
        question = self.get(question_id)
        if not question:
            raise ValueError(f"题目ID {question_id} 不存在")

        question.totalAttempts = stats.totalAttempts
        question.correctCount = stats.correctCount
        question.correctRate = stats.correctRate
        question.avgTimeSeconds = stats.avgTimeSeconds
        question.discriminationIndex = stats.discriminationIndex
        question.optionDistribution = stats.optionDistribution

        self.update(question)

    def get_statistics(self) -> Dict:
        """获取题库统计信息"""
        total = len(self.questions)

        # 按难度统计
        difficulty_stats = {
            "L1": 0,
            "L2": 0,
            "L3": 0
        }

        # 按题型统计
        type_stats = {
            "choice": 0,
            "fill": 0,
            "solution": 0
        }

        # 按审核状态统计
        review_stats = {
            "pending": 0,
            "approved": 0,
            "rejected": 0,
            "revision": 0
        }

        # 按来源统计
        source_stats = {
            "real_exam": 0,
            "generated": 0,
            "manual": 0
        }

        for q in self.questions.values():
            difficulty_stats[q.difficulty.value] += 1
            type_stats[q.type.value] += 1
            review_stats[q.reviewStatus.value] += 1

            if q.isRealExam:
                source_stats["real_exam"] += 1
            elif q.source == "manual":
                source_stats["manual"] += 1
            else:
                source_stats["generated"] += 1

        return {
            "total": total,
            "difficultyStats": difficulty_stats,
            "typeStats": type_stats,
            "reviewStats": review_stats,
            "sourceStats": source_stats
        }


# 全局单例
question_bank = QuestionBank()







