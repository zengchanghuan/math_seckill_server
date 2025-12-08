"""
作答记录跟踪模块
记录学生答题数据，用于质量统计和能力画像分析
"""
import json
import os
from typing import List, Dict
from datetime import datetime
from collections import defaultdict
from schemas import AnswerRecord, StudentProfile, QualityStats


class AnswerTracker:
    """作答记录追踪器"""

    def __init__(self, data_file: str = "data/answer_records.json"):
        self.data_file = data_file
        self.records: List[AnswerRecord] = []
        self.load()

    def load(self):
        """从文件加载记录"""
        if not os.path.exists(self.data_file):
            os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
            self.save()
            return

        with open(self.data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            self.records = [AnswerRecord(**item) for item in data]

    def save(self):
        """保存记录到文件"""
        data = [r.model_dump(mode='json') for r in self.records]
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def add_record(self, record: AnswerRecord):
        """添加作答记录"""
        self.records.append(record)
        self.save()

    def get_student_records(self, student_id: str) -> List[AnswerRecord]:
        """获取某学生的所有记录"""
        return [r for r in self.records if r.studentId == student_id]

    def get_question_records(self, question_id: str) -> List[AnswerRecord]:
        """获取某题目的所有记录"""
        return [r for r in self.records if r.questionId == question_id]

    def calculate_question_stats(self, question_id: str) -> QualityStats:
        """计算题目质量统计"""
        records = self.get_question_records(question_id)

        if not records:
            return QualityStats(
                questionId=question_id,
                totalAttempts=0,
                correctCount=0,
                correctRate=0.0,
                avgTimeSeconds=0.0
            )

        total = len(records)
        correct = sum(1 for r in records if r.isCorrect)
        correct_rate = correct / total if total > 0 else 0.0
        avg_time = sum(r.timeSpent for r in records) / total if total > 0 else 0.0

        # 计算区分度（需要学生总分数据）
        discrimination = self._calculate_discrimination(question_id, records)

        # 计算选项分布（如果有用户答案）
        option_dist = self._calculate_option_distribution(records)

        return QualityStats(
            questionId=question_id,
            totalAttempts=total,
            correctCount=correct,
            correctRate=correct_rate,
            avgTimeSeconds=avg_time,
            discriminationIndex=discrimination,
            optionDistribution=option_dist
        )

    def _calculate_discrimination(
        self,
        question_id: str,
        records: List[AnswerRecord]
    ) -> float:
        """
        计算区分度
        区分度 = 高分组正确率 - 低分组正确率
        """
        # 按学生分组，计算每个学生的总正确率
        student_scores = defaultdict(lambda: {"correct": 0, "total": 0})

        for record in self.records:
            sid = record.studentId
            student_scores[sid]["total"] += 1
            if record.isCorrect:
                student_scores[sid]["correct"] += 1

        # 计算每个学生的正确率
        student_rates = {}
        for sid, stats in student_scores.items():
            if stats["total"] > 0:
                student_rates[sid] = stats["correct"] / stats["total"]

        if len(student_rates) < 10:  # 样本太少，不计算区分度
            return None

        # 排序，取前27%和后27%
        sorted_students = sorted(student_rates.items(), key=lambda x: x[1], reverse=True)
        n = len(sorted_students)
        top_27 = int(n * 0.27)

        top_group = [sid for sid, _ in sorted_students[:top_27]]
        low_group = [sid for sid, _ in sorted_students[-top_27:]]

        # 计算这道题在两组的正确率
        top_records = [r for r in records if r.studentId in top_group]
        low_records = [r for r in records if r.studentId in low_group]

        top_correct_rate = (
            sum(1 for r in top_records if r.isCorrect) / len(top_records)
            if top_records else 0
        )
        low_correct_rate = (
            sum(1 for r in low_records if r.isCorrect) / len(low_records)
            if low_records else 0
        )

        return top_correct_rate - low_correct_rate

    def _calculate_option_distribution(
        self,
        records: List[AnswerRecord]
    ) -> Dict[str, float]:
        """计算选项分布（仅用于选择题）"""
        if not records:
            return {}

        option_counts = defaultdict(int)
        total = len(records)

        for record in records:
            # 假设userAnswer是选项字母，如"A", "B", "C", "D"
            option_counts[record.userAnswer] += 1

        # 转换为比例
        option_dist = {
            option: count / total
            for option, count in option_counts.items()
        }

        return option_dist

    def calculate_student_profile(
        self,
        student_id: str,
        question_bank_ref=None  # 引用QuestionBank以获取题目元信息
    ) -> StudentProfile:
        """计算学生能力画像"""
        records = self.get_student_records(student_id)

        if not records:
            return StudentProfile(
                studentId=student_id,
                updatedAt=datetime.now()
            )

        total = len(records)
        correct = sum(1 for r in records if r.isCorrect)
        avg_time = sum(r.timeSpent for r in records) / total if total > 0 else None

        # 如果有题库引用，计算更详细的画像
        knowledge_mastery = {}
        type_accuracy = {}
        difficulty_accuracy = {}
        weak_points = []

        if question_bank_ref:
            # 按知识点统计
            kp_stats = defaultdict(lambda: {"correct": 0, "total": 0})
            type_stats = defaultdict(lambda: {"correct": 0, "total": 0})
            diff_stats = defaultdict(lambda: {"correct": 0, "total": 0})

            for record in records:
                question = question_bank_ref.get(record.questionId)
                if not question:
                    continue

                # 知识点统计
                for kp in question.knowledgePoints:
                    kp_stats[kp]["total"] += 1
                    if record.isCorrect:
                        kp_stats[kp]["correct"] += 1

                # 题型统计
                qtype = question.type.value
                type_stats[qtype]["total"] += 1
                if record.isCorrect:
                    type_stats[qtype]["correct"] += 1

                # 难度统计
                diff = question.difficulty.value
                diff_stats[diff]["total"] += 1
                if record.isCorrect:
                    diff_stats[diff]["correct"] += 1

            # 计算掌握度
            knowledge_mastery = {
                kp: stats["correct"] / stats["total"]
                for kp, stats in kp_stats.items()
                if stats["total"] > 0
            }

            type_accuracy = {
                qtype: stats["correct"] / stats["total"]
                for qtype, stats in type_stats.items()
                if stats["total"] > 0
            }

            difficulty_accuracy = {
                diff: stats["correct"] / stats["total"]
                for diff, stats in diff_stats.items()
                if stats["total"] > 0
            }

            # 找出薄弱知识点（正确率<0.6）
            weak_points = [
                kp for kp, rate in knowledge_mastery.items()
                if rate < 0.6
            ]

        # 简单预测分数（基于L1/L2/L3的权重）
        predicted_score = None
        if difficulty_accuracy:
            # 假设考试分布：L1占50%，L2占35%，L3占15%
            l1_rate = difficulty_accuracy.get("L1", 0.5)
            l2_rate = difficulty_accuracy.get("L2", 0.5)
            l3_rate = difficulty_accuracy.get("L3", 0.5)
            predicted_score = (l1_rate * 50 + l2_rate * 35 + l3_rate * 15)

        return StudentProfile(
            studentId=student_id,
            knowledgeMastery=knowledge_mastery,
            questionTypeAccuracy=type_accuracy,
            difficultyAccuracy=difficulty_accuracy,
            totalProblems=total,
            correctCount=correct,
            avgTimePerProblem=avg_time,
            weakPoints=weak_points,
            predictedScore=predicted_score,
            updatedAt=datetime.now()
        )


# 全局单例
answer_tracker = AnswerTracker()







