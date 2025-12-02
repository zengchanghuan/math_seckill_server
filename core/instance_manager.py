"""
用户训练实例管理器
"""

import json
import random
from pathlib import Path
from typing import List, Dict
from datetime import datetime

from models import UserPaperInstance, PaperSection, Question, CreateInstanceRequest
from core.question_bank import get_question_bank


class InstanceManager:
    """
    用户训练实例管理器
    
    负责：
    1. 根据配置创建训练实例（选题）
    2. 存储实例到本地JSON（模拟数据库）
    3. 查询用户的实例
    """
    
    def __init__(self, db_path: str = "data/instances.json"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(exist_ok=True)
        self.instances: Dict[str, UserPaperInstance] = {}
        self._load_instances()
    
    def _load_instances(self):
        """加载实例数据"""
        if self.db_path.exists():
            with open(self.db_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.instances = {
                    inst['instanceId']: UserPaperInstance(**inst) for inst in data
                }
            print(f"✅ 加载训练实例：{len(self.instances)} 个")
        else:
            self.instances = {}
            print("📝 实例库为空")
    
    def _save_instances(self):
        """保存实例数据"""
        data = [inst.model_dump() for inst in self.instances.values()]
        with open(self.db_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"💾 实例已保存：{len(self.instances)} 个")
    
    def create_instance(self, request: CreateInstanceRequest) -> tuple[UserPaperInstance, List[Question]]:
        """
        创建新的训练实例
        
        Args:
            request: 创建请求
            
        Returns:
            (实例对象, 题目列表)
        """
        question_bank = get_question_bank()
        
        # 生成实例ID
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        user_prefix = request.userId or "guest"
        instance_id = f"{user_prefix}_{timestamp}"
        
        # 根据配置选题
        # 这里简化处理：按题型分配
        # L1: 60%选择 + 30%填空 + 10%解答
        # L2: 30%选择 + 40%填空 + 30%解答
        # L3: 10%选择 + 30%填空 + 60%解答
        
        choice_count = 0
        fill_count = 0
        solution_count = 0
        
        if request.difficulty == "L1":
            choice_count = int(request.questionCount * 0.6)
            fill_count = int(request.questionCount * 0.3)
            solution_count = request.questionCount - choice_count - fill_count
        elif request.difficulty == "L2":
            choice_count = int(request.questionCount * 0.3)
            fill_count = int(request.questionCount * 0.4)
            solution_count = request.questionCount - choice_count - fill_count
        else:  # L3
            choice_count = int(request.questionCount * 0.1)
            fill_count = int(request.questionCount * 0.3)
            solution_count = request.questionCount - choice_count - fill_count
        
        # 从题库获取或生成题目
        choice_questions = question_bank.get_or_create_questions(
            topic=request.topic,
            difficulty=request.difficulty,
            type_="choice",
            chapter=request.chapter,
            section=request.section,
            count=choice_count
        )
        
        fill_questions = question_bank.get_or_create_questions(
            topic=request.topic,
            difficulty=request.difficulty,
            type_="fill",
            chapter=request.section,
            section=request.section,
            count=fill_count
        )
        
        solution_questions = question_bank.get_or_create_questions(
            topic=request.topic,
            difficulty=request.difficulty,
            type_="solution",
            chapter=request.chapter,
            section=request.section,
            count=solution_count
        )
        
        # 组装sections
        sections = []
        
        if choice_questions or fill_questions:
            # 选择填空合并为一个section
            mixed_ids = [q.questionId for q in choice_questions] + [q.questionId for q in fill_questions]
            random.shuffle(mixed_ids)
            sections.append(PaperSection(
                sectionName="选择填空题",
                questionIds=mixed_ids
            ))
        
        if solution_questions:
            sections.append(PaperSection(
                sectionName="解答题",
                questionIds=[q.questionId for q in solution_questions]
            ))
        
        # 创建实例
        instance = UserPaperInstance(
            instanceId=instance_id,
            userId=request.userId,
            topic=request.topic,
            difficulty=request.difficulty,
            chapter=request.chapter,
            section=request.section,
            sections=sections,
            totalQuestions=request.questionCount,
            createdAt=datetime.now().isoformat()
        )
        
        # 保存实例
        self.instances[instance_id] = instance
        self._save_instances()
        
        # 收集所有题目
        all_questions = choice_questions + fill_questions + solution_questions
        
        return instance, all_questions
    
    def get_instance(self, instance_id: str) -> UserPaperInstance | None:
        """获取实例"""
        return self.instances.get(instance_id)
    
    def get_user_instances(self, user_id: str) -> List[UserPaperInstance]:
        """获取用户的所有实例"""
        return [
            inst for inst in self.instances.values()
            if inst.userId == user_id
        ]


# 全局单例
_instance_manager = None

def get_instance_manager() -> InstanceManager:
    """获取实例管理器单例"""
    global _instance_manager
    if _instance_manager is None:
        _instance_manager = InstanceManager()
    return _instance_manager

