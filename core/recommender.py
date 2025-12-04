"""
个性化推荐模块
基于学生能力画像推荐题目
"""
import random
from typing import List
from schemas import QuestionMetadata, StudentProfile, Difficulty, ProblemType


class ProblemRecommender:
    """题目推荐器"""

    def __init__(self, question_bank_ref, answer_tracker_ref):
        self.question_bank = question_bank_ref
        self.answer_tracker = answer_tracker_ref

    def recommend_for_weak_points(
        self,
        student_id: str,
        count: int = 20
    ) -> tuple[List[QuestionMetadata], str]:
        """
        为学生推荐题目（薄弱知识点模式）

        策略：
        - 70%：薄弱知识点的L1+L2题
        - 20%：已掌握知识点的L2+L3题（巩固）
        - 10%：随机新题（拓展）
        """
        # 获取学生画像
        profile = self.answer_tracker.calculate_student_profile(
            student_id,
            self.question_bank
        )

        problems = []
        reason_parts = []

        # 获取已做过的题目ID
        done_records = self.answer_tracker.get_student_records(student_id)
        done_question_ids = set(r.questionId for r in done_records)

        # 70%：薄弱知识点
        weak_count = int(count * 0.7)
        if profile.weakPoints:
            reason_parts.append(f"薄弱知识点：{', '.join(profile.weakPoints[:3])}")

            for kp in profile.weakPoints:
                # 每个薄弱点取若干道题
                per_kp_count = weak_count // len(profile.weakPoints)

                # 先取L1题（基础）
                l1_questions = self.question_bank.query(
                    knowledge_points=[kp],
                    difficulty=Difficulty.L1,
                    review_status="approved"
                )
                l1_questions = [q for q in l1_questions if q.questionId not in done_question_ids]

                # 再取L2题（提升）
                l2_questions = self.question_bank.query(
                    knowledge_points=[kp],
                    difficulty=Difficulty.L2,
                    review_status="approved"
                )
                l2_questions = [q for q in l2_questions if q.questionId not in done_question_ids]

                # 混合L1和L2（2:1比例）
                candidates = (
                    random.sample(l1_questions, min(len(l1_questions), per_kp_count * 2 // 3)) +
                    random.sample(l2_questions, min(len(l2_questions), per_kp_count // 3))
                )

                problems.extend(candidates[:per_kp_count])

        # 20%：已掌握知识点（巩固）
        consolidate_count = int(count * 0.2)
        strong_points = [
            kp for kp, rate in profile.knowledgeMastery.items()
            if rate >= 0.75 and kp not in profile.weakPoints
        ]

        if strong_points:
            random_strong = random.choice(strong_points)
            reason_parts.append(f"巩固强项：{random_strong}")

            l2_l3_questions = (
                self.question_bank.query(
                    knowledge_points=[random_strong],
                    difficulty=Difficulty.L2,
                    review_status="approved"
                ) +
                self.question_bank.query(
                    knowledge_points=[random_strong],
                    difficulty=Difficulty.L3,
                    review_status="approved"
                )
            )
            l2_l3_questions = [q for q in l2_l3_questions if q.questionId not in done_question_ids]
            problems.extend(random.sample(l2_l3_questions, min(len(l2_l3_questions), consolidate_count)))

        # 10%：随机新题（拓展）
        new_count = count - len(problems)
        if new_count > 0:
            all_approved = self.question_bank.query(review_status="approved")
            unseen = [q for q in all_approved if q.questionId not in done_question_ids]

            if unseen:
                problems.extend(random.sample(unseen, min(len(unseen), new_count)))
                reason_parts.append("拓展新题")

        # 截断到指定数量
        problems = problems[:count]

        # 生成推荐理由
        if not reason_parts:
            reason = "基于您的学习记录，为您推荐以下题目"
        else:
            reason = f"基于您的学习数据：{' | '.join(reason_parts)}"

        return problems, reason

    def recommend_comprehensive(
        self,
        student_id: str,
        count: int = 20
    ) -> tuple[List[QuestionMetadata], str]:
        """
        综合训练模式：按考试蓝图分布推荐

        策略：
        - L1: 50%
        - L2: 35%
        - L3: 15%
        """
        profile = self.answer_tracker.calculate_student_profile(
            student_id,
            self.question_bank
        )

        done_records = self.answer_tracker.get_student_records(student_id)
        done_question_ids = set(r.questionId for r in done_records)

        problems = []

        # L1: 50%
        l1_count = int(count * 0.5)
        l1_questions = self.question_bank.query(
            difficulty=Difficulty.L1,
            review_status="approved"
        )
        l1_questions = [q for q in l1_questions if q.questionId not in done_question_ids]
        problems.extend(random.sample(l1_questions, min(len(l1_questions), l1_count)))

        # L2: 35%
        l2_count = int(count * 0.35)
        l2_questions = self.question_bank.query(
            difficulty=Difficulty.L2,
            review_status="approved"
        )
        l2_questions = [q for q in l2_questions if q.questionId not in done_question_ids]
        problems.extend(random.sample(l2_questions, min(len(l2_questions), l2_count)))

        # L3: 15%
        l3_count = count - len(problems)
        l3_questions = self.question_bank.query(
            difficulty=Difficulty.L3,
            review_status="approved"
        )
        l3_questions = [q for q in l3_questions if q.questionId not in done_question_ids]
        problems.extend(random.sample(l3_questions, min(len(l3_questions), l3_count)))

        # 打乱顺序
        random.shuffle(problems)

        reason = "综合训练模式：按考试难度分布推荐（L1:50%, L2:35%, L3:15%）"
        return problems, reason

    def recommend_exam_prep(
        self,
        student_id: str,
        count: int = 20
    ) -> tuple[List[QuestionMetadata], str]:
        """
        考前冲刺模式：针对性突破

        策略：
        - 80%：薄弱知识点的中等难度题（L2）
        - 20%：高频错题重练
        """
        profile = self.answer_tracker.calculate_student_profile(
            student_id,
            self.question_bank
        )

        done_records = self.answer_tracker.get_student_records(student_id)

        problems = []

        # 80%：薄弱知识点的L2题
        weak_count = int(count * 0.8)
        if profile.weakPoints:
            for kp in profile.weakPoints:
                per_kp_count = weak_count // len(profile.weakPoints)

                l2_questions = self.question_bank.query(
                    knowledge_points=[kp],
                    difficulty=Difficulty.L2,
                    review_status="approved"
                )
                problems.extend(random.sample(l2_questions, min(len(l2_questions), per_kp_count)))

        # 20%：错题重练
        error_count = count - len(problems)
        error_records = [r for r in done_records if not r.isCorrect]

        if error_records:
            # 获取错题（去重）
            error_question_ids = list(set(r.questionId for r in error_records))
            random.shuffle(error_question_ids)

            for qid in error_question_ids[:error_count]:
                question = self.question_bank.get(qid)
                if question:
                    problems.append(question)

        problems = problems[:count]

        reason = f"考前冲刺：针对薄弱知识点（{', '.join(profile.weakPoints[:3])}）+ 高频错题"
        return problems, reason

    def recommend(
        self,
        student_id: str,
        mode: str = "weak_points",
        count: int = 20
    ) -> tuple[List[QuestionMetadata], str]:
        """
        统一推荐接口

        Args:
            student_id: 学生ID
            mode: 推荐模式
                - "weak_points": 薄弱知识点模式
                - "comprehensive": 综合训练模式
                - "exam_prep": 考前冲刺模式
            count: 推荐题目数量

        Returns:
            (题目列表, 推荐理由)
        """
        if mode == "weak_points":
            return self.recommend_for_weak_points(student_id, count)
        elif mode == "comprehensive":
            return self.recommend_comprehensive(student_id, count)
        elif mode == "exam_prep":
            return self.recommend_exam_prep(student_id, count)
        else:
            # 默认使用薄弱知识点模式
            return self.recommend_for_weak_points(student_id, count)


