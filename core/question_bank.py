"""
题目库管理：生成题目并持久化到题库
"""

import json
from pathlib import Path
from typing import List, Dict
from datetime import datetime

from models import Question
from core.problem_generator import (
    generate_trig_choice_l1,
    generate_trig_fill_l1,
    generate_algebra_choice_l1,
    generate_algebra_fill_l1,
)
from core.geometry_generator import generate_geometry_problem


class QuestionBank:
    """
    题目库管理器
    
    负责：
    1. 生成题目并分配唯一ID
    2. 持久化到本地JSON文件（模拟数据库）
    3. 根据条件查询题目
    """
    
    def __init__(self, db_path: str = "data/questions.json"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(exist_ok=True)
        self.questions: Dict[str, Question] = {}
        self._load_questions()
    
    def _load_questions(self):
        """从文件加载题库"""
        if self.db_path.exists():
            with open(self.db_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.questions = {
                    q['questionId']: Question(**q) for q in data
                }
            print(f"✅ 加载题库：{len(self.questions)} 道题目")
        else:
            self.questions = {}
            print("📝 题库为空，将创建新题库")
    
    def _save_questions(self):
        """保存题库到文件"""
        data = [q.model_dump() for q in self.questions.values()]
        with open(self.db_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"💾 题库已保存：{len(self.questions)} 道题目")
    
    def _generate_question_id(self, topic: str, difficulty: str, type_: str) -> str:
        """
        生成题目ID
        格式：{topic_abbr}_{difficulty}_{type_abbr}_{序号}
        如：trig_L1_c_001
        """
        topic_abbr_map = {
            "三角函数": "trig",
            "代数与方程": "alg",
            "平面几何": "geo",
            "反三角函数": "atrig",
            "排列与组合": "comb",
            "复数": "comp",
            "参数方程与极坐标方程": "para",
        }
        type_abbr_map = {
            "choice": "c",
            "fill": "f",
            "solution": "s",
        }
        
        topic_abbr = topic_abbr_map.get(topic, "misc")
        type_abbr = type_abbr_map.get(type_, "c")
        
        # 查找当前最大序号
        prefix = f"{topic_abbr}_{difficulty}_{type_abbr}_"
        existing_ids = [qid for qid in self.questions.keys() if qid.startswith(prefix)]
        
        if existing_ids:
            max_num = max([int(qid.split('_')[-1]) for qid in existing_ids])
            next_num = max_num + 1
        else:
            next_num = 1
        
        return f"{prefix}{next_num:03d}"
    
    def add_question(self, question_data: Dict) -> Question:
        """
        添加题目到题库（如果不存在）
        
        Args:
            question_data: 题目生成器返回的字典
            
        Returns:
            Question对象
        """
        # 生成唯一ID
        question_id = self._generate_question_id(
            question_data['topic'],
            question_data['difficulty'],
            question_data['type']
        )
        
        # 创建Question对象
        question = Question(
            questionId=question_id,
            topic=question_data['topic'],
            difficulty=question_data['difficulty'],
            type=question_data['type'],
            chapter=question_data.get('chapter'),
            section=question_data.get('section'),
            question=question_data['question'],
            answer=question_data['answer'],
            solution=question_data['solution'],
            options=question_data.get('options', []),
            tags=question_data.get('tags', []),
            answerType=question_data.get('answerType'),
            answerExpr=question_data.get('answerExpr'),
            createdAt=datetime.now().isoformat()
        )
        
        # 添加到题库
        self.questions[question_id] = question
        self._save_questions()
        
        return question
    
    def get_or_create_questions(
        self,
        topic: str,
        difficulty: str,
        type_: str | None,
        chapter: str | None,
        section: str | None,
        count: int = 1
    ) -> List[Question]:
        """
        获取或生成题目
        
        先从题库中查找符合条件的题目，不足则生成新题并加入题库
        
        Args:
            topic: 主题
            difficulty: 难度
            type_: 题型（可选）
            chapter: 章节
            section: 节
            count: 需要的题目数量
            
        Returns:
            题目列表
        """
        # 查询现有题目
        existing = self.query_questions(
            topic=topic,
            difficulty=difficulty,
            type_=type_,
            chapter=chapter,
            section=section
        )
        
        result = []
        
        # 如果现有题目足够，随机选择
        if len(existing) >= count:
            import random
            result = random.sample(existing, count)
        else:
            # 使用所有现有题目
            result.extend(existing)
            
            # 生成不足的题目
            needed = count - len(existing)
            for _ in range(needed):
                question_data = self._generate_single_question(
                    topic, difficulty, type_, chapter, section
                )
                question = self.add_question(question_data)
                result.append(question)
        
        return result
    
    def _generate_single_question(
        self,
        topic: str,
        difficulty: str,
        type_: str | None,
        chapter: str | None,
        section: str | None
    ) -> Dict:
        """
        生成单道题目（调用相应的生成器）
        """
        from core.problem_config import get_problem_type_for_difficulty
        
        if type_ is None:
            type_ = get_problem_type_for_difficulty(difficulty)
        
        # 根据主题和题型调用生成器
        if topic == "三角函数" or (chapter and "三角函数" in chapter):
            if type_ == "choice":
                return generate_trig_choice_l1()
            elif type_ == "fill":
                return generate_trig_fill_l1()
            else:
                return generate_trig_choice_l1()
        
        elif topic == "代数与方程" or (chapter and "代数" in chapter):
            if type_ == "choice":
                return generate_algebra_choice_l1()
            elif type_ == "fill":
                return generate_algebra_fill_l1()
            else:
                return generate_algebra_choice_l1()
        
        elif topic == "平面几何" or (chapter and "几何" in chapter):
            return generate_geometry_problem(difficulty)
        
        else:
            # 默认
            return generate_trig_choice_l1()
    
    def query_questions(
        self,
        topic: str | None = None,
        difficulty: str | None = None,
        type_: str | None = None,
        chapter: str | None = None,
        section: str | None = None,
    ) -> List[Question]:
        """
        查询题库中符合条件的题目
        """
        results = []
        
        for question in self.questions.values():
            # 匹配条件
            if topic and question.topic != topic:
                continue
            if difficulty and question.difficulty != difficulty:
                continue
            if type_ and question.type != type_:
                continue
            if chapter and question.chapter != chapter:
                continue
            if section and question.section != section:
                continue
            
            results.append(question)
        
        return results
    
    def get_question_by_id(self, question_id: str) -> Question | None:
        """根据ID获取题目"""
        return self.questions.get(question_id)


# 全局单例
_question_bank = None

def get_question_bank() -> QuestionBank:
    """获取题库单例"""
    global _question_bank
    if _question_bank is None:
        _question_bank = QuestionBank()
    return _question_bank

