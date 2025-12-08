"""
数据迁移脚本：将现有题目升级到v2格式
添加元信息字段、质量统计字段、审核状态等
"""
import json
import os
from datetime import datetime
from typing import Dict, List


def migrate_question(old_question: Dict) -> Dict:
    """迁移单个题目"""

    # 基础字段
    new_question = {
        "questionId": old_question.get("questionId"),
        "topic": old_question.get("topic"),
        "difficulty": old_question.get("difficulty"),
        "type": old_question.get("type", "choice"),

        # 内容
        "question": old_question.get("question"),
        "answer": old_question.get("answer"),
        "solution": old_question.get("solution"),
        "options": old_question.get("options"),

        # 答案类型
        "answerType": old_question.get("answerType"),
        "answerExpr": old_question.get("answerExpr"),

        # 分类标签
        "knowledgePoints": infer_knowledge_points(old_question),
        "abilityTags": infer_ability_tags(old_question),
        "tags": old_question.get("tags", []),

        # 章节信息
        "chapter": old_question.get("chapter"),
        "section": old_question.get("section"),

        # 来源信息
        "source": "generated",
        "isRealExam": False,
        "templateId": None,

        # 质量统计（初始化为0）
        "totalAttempts": 0,
        "correctCount": 0,
        "correctRate": None,
        "discriminationIndex": None,
        "avgTimeSeconds": None,
        "optionDistribution": None,

        # 审核状态（已有题目自动标记为pending）
        "reviewStatus": "pending",
        "reviewerId": None,
        "reviewComment": None,

        # 时间戳
        "createdAt": old_question.get("createdAt", datetime.now().isoformat()),
        "updatedAt": None
    }

    return new_question


def infer_knowledge_points(question: Dict) -> List[str]:
    """
    根据题目内容推断知识点
    这是一个简单的启发式方法，后续需要人工审核
    """
    topic = question.get("topic", "")
    tags = question.get("tags", [])
    question_text = question.get("question", "").lower()

    knowledge_points = []

    # 基于topic推断
    if "三角" in topic:
        knowledge_points.append("三角函数")
    elif "代数" in topic or "方程" in topic:
        knowledge_points.append("代数方程")
    elif "导数" in topic:
        knowledge_points.append("导数")
    elif "极限" in topic:
        knowledge_points.append("极限")
    elif "积分" in topic:
        knowledge_points.append("积分")
    elif "几何" in topic:
        knowledge_points.append("平面几何")
    elif "复数" in topic:
        knowledge_points.append("复数")

    # 基于tags推断
    for tag in tags:
        if tag not in knowledge_points:
            knowledge_points.append(tag)

    # 基于题干关键词推断
    keywords = {
        "定义域": "定义域",
        "值域": "值域",
        "单调": "单调性",
        "极值": "极值",
        "最值": "最值",
        "导数": "导数",
        "切线": "切线",
        "判别式": "判别式",
    }

    for keyword, kp in keywords.items():
        if keyword in question_text and kp not in knowledge_points:
            knowledge_points.append(kp)

    return knowledge_points if knowledge_points else [topic]


def infer_ability_tags(question: Dict) -> List[str]:
    """
    根据题目难度和类型推断能力要求
    """
    difficulty = question.get("difficulty", "L1")
    qtype = question.get("type", "choice")
    question_text = question.get("question", "").lower()

    ability_tags = []

    # 基于难度推断
    if difficulty == "L1":
        # 基础题通常是记忆和理解
        ability_tags = ["memory", "understand"]
    elif difficulty == "L2":
        # 中档题通常是应用和分析
        ability_tags = ["apply", "analyze"]
    elif difficulty == "L3":
        # 压轴题通常是综合和建模
        ability_tags = ["synthesize", "model"]

    # 基于题型推断
    if qtype == "choice":
        # 选择题侧重理解
        if "understand" not in ability_tags:
            ability_tags.append("understand")
    elif qtype in ["fill", "solution"]:
        # 填空和解答题侧重应用
        if "apply" not in ability_tags:
            ability_tags.append("apply")

    # 基于题干关键词推断
    if "证明" in question_text:
        if "analyze" not in ability_tags:
            ability_tags.append("analyze")

    if "应用" in question_text or "实际问题" in question_text:
        if "model" not in ability_tags:
            ability_tags.append("model")

    return ability_tags


def migrate_questions_file(input_file: str, output_file: str = None):
    """
    迁移整个题库文件

    Args:
        input_file: 输入文件路径
        output_file: 输出文件路径（默认为原文件）
    """
    if output_file is None:
        # 备份原文件
        backup_file = input_file.replace(".json", "_backup.json")
        print(f"备份原文件到: {backup_file}")

        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()
        with open(backup_file, 'w', encoding='utf-8') as f:
            f.write(content)

        output_file = input_file

    # 读取原题库
    print(f"读取题库: {input_file}")
    with open(input_file, 'r', encoding='utf-8') as f:
        old_questions = json.load(f)

    print(f"原题库共有 {len(old_questions)} 道题")

    # 迁移每道题
    new_questions = []
    for i, old_q in enumerate(old_questions):
        try:
            new_q = migrate_question(old_q)
            new_questions.append(new_q)

            if (i + 1) % 100 == 0:
                print(f"已迁移 {i + 1}/{len(old_questions)} 道题")
        except Exception as e:
            print(f"迁移第 {i + 1} 道题时出错: {e}")
            print(f"题目ID: {old_q.get('questionId')}")

    # 保存新题库
    print(f"保存新题库到: {output_file}")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(new_questions, f, ensure_ascii=False, indent=2)

    print(f"迁移完成！新题库共有 {len(new_questions)} 道题")

    # 统计信息
    print("\n=== 迁移统计 ===")
    print(f"难度分布:")
    difficulty_stats = {}
    for q in new_questions:
        diff = q.get("difficulty", "unknown")
        difficulty_stats[diff] = difficulty_stats.get(diff, 0) + 1
    for diff, count in sorted(difficulty_stats.items()):
        print(f"  {diff}: {count}")

    print(f"\n题型分布:")
    type_stats = {}
    for q in new_questions:
        qtype = q.get("type", "unknown")
        type_stats[qtype] = type_stats.get(qtype, 0) + 1
    for qtype, count in sorted(type_stats.items()):
        print(f"  {qtype}: {count}")

    print(f"\n审核状态:")
    review_stats = {}
    for q in new_questions:
        status = q.get("reviewStatus", "unknown")
        review_stats[status] = review_stats.get(status, 0) + 1
    for status, count in sorted(review_stats.items()):
        print(f"  {status}: {count}")


def main():
    """主函数"""
    import sys

    # 默认路径
    default_input = "../data/questions.json"

    input_file = sys.argv[1] if len(sys.argv) > 1 else default_input

    if not os.path.exists(input_file):
        print(f"错误：文件不存在 {input_file}")
        print(f"用法: python migrate_to_v2.py [输入文件路径]")
        return

    migrate_questions_file(input_file)


if __name__ == "__main__":
    main()







