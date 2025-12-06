#!/usr/bin/env python3
"""
真题导入工具
将真题数据导入到 questions.json，并标记为真题（source: 'real_exam', isRealExam: true）
"""

import json
import sys
from pathlib import Path
from typing import List, Dict

# 数据文件路径
DATA_DIR = Path(__file__).parent.parent / "data"
QUESTIONS_FILE = DATA_DIR / "questions.json"

def load_questions() -> List[Dict]:
    """加载现有题目"""
    if not QUESTIONS_FILE.exists():
        return []

    with open(QUESTIONS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_questions(questions: List[Dict]):
    """保存题目"""
    with open(QUESTIONS_FILE, 'w', encoding='utf-8') as f:
        json.dump(questions, f, ensure_ascii=False, indent=2)

def mark_questions_as_real_exam(question_ids: List[str], paper_id: str, year: int):
    """
    将指定题目标记为真题

    Args:
        question_ids: 题目ID列表
        paper_id: 试卷ID（如 'paper_2023_1'）
        year: 年份（如 2023）
    """
    questions = load_questions()

    # 创建题目ID到索引的映射
    question_map = {q.get('questionId'): i for i, q in enumerate(questions)}

    updated_count = 0
    for qid in question_ids:
        if qid in question_map:
            idx = question_map[qid]
            questions[idx]['source'] = 'real_exam'
            questions[idx]['isRealExam'] = True
            questions[idx]['paperId'] = paper_id
            if 'year' not in questions[idx]:
                questions[idx]['year'] = year
            updated_count += 1
            print(f"✓ 已标记题目: {qid} -> {paper_id}")
        else:
            print(f"⚠️  题目未找到: {qid}")

    if updated_count > 0:
        save_questions(questions)
        print(f"\n✅ 成功标记 {updated_count} 道题目为真题")
    else:
        print("\n⚠️  没有题目被更新")

def import_from_json(json_file: str, paper_id: str, year: int):
    """
    从 JSON 文件导入真题

    JSON 文件格式：
    [
        {
            "questionId": "...",
            "question": "...",
            "answer": "...",
            ...
        },
        ...
    ]
    """
    json_path = Path(json_file)
    if not json_path.exists():
        print(f"❌ 文件不存在: {json_file}")
        return

    with open(json_path, 'r', encoding='utf-8') as f:
        new_questions = json.load(f)

    existing_questions = load_questions()
    existing_ids = {q.get('questionId') for q in existing_questions}

    added_count = 0
    for q in new_questions:
        qid = q.get('questionId')
        if not qid:
            print(f"⚠️  跳过无ID的题目")
            continue

        # 标记为真题
        q['source'] = 'real_exam'
        q['isRealExam'] = True
        q['paperId'] = paper_id
        q['year'] = year

        if qid in existing_ids:
            # 更新现有题目
            for i, eq in enumerate(existing_questions):
                if eq.get('questionId') == qid:
                    existing_questions[i].update(q)
                    print(f"✓ 更新题目: {qid}")
                    break
        else:
            # 添加新题目
            existing_questions.append(q)
            added_count += 1
            print(f"✓ 添加题目: {qid}")

    save_questions(existing_questions)
    print(f"\n✅ 导入完成: 新增 {added_count} 道题目，更新 {len(new_questions) - added_count} 道题目")

def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("""
真题导入工具

用法:
  1. 标记现有题目为真题:
     python import_real_exam.py mark --paper-id paper_2023_1 --year 2023 --question-ids q1 q2 q3 ...

  2. 从 JSON 文件导入真题:
     python import_real_exam.py import --json-file path/to/questions.json --paper-id paper_2023_1 --year 2023

  3. 查看帮助:
     python import_real_exam.py --help
        """)
        return

    command = sys.argv[1]

    if command == 'mark':
        # 解析参数
        paper_id = None
        year = None
        question_ids = []

        i = 2
        while i < len(sys.argv):
            if sys.argv[i] == '--paper-id' and i + 1 < len(sys.argv):
                paper_id = sys.argv[i + 1]
                i += 2
            elif sys.argv[i] == '--year' and i + 1 < len(sys.argv):
                year = int(sys.argv[i + 1])
                i += 2
            elif sys.argv[i] == '--question-ids':
                i += 1
                while i < len(sys.argv) and not sys.argv[i].startswith('--'):
                    question_ids.append(sys.argv[i])
                    i += 1
            else:
                i += 1

        if not paper_id or not year or not question_ids:
            print("❌ 缺少必要参数: --paper-id, --year, --question-ids")
            return

        mark_questions_as_real_exam(question_ids, paper_id, year)

    elif command == 'import':
        # 解析参数
        json_file = None
        paper_id = None
        year = None

        i = 2
        while i < len(sys.argv):
            if sys.argv[i] == '--json-file' and i + 1 < len(sys.argv):
                json_file = sys.argv[i + 1]
                i += 2
            elif sys.argv[i] == '--paper-id' and i + 1 < len(sys.argv):
                paper_id = sys.argv[i + 1]
                i += 2
            elif sys.argv[i] == '--year' and i + 1 < len(sys.argv):
                year = int(sys.argv[i + 1])
                i += 2
            else:
                i += 1

        if not json_file or not paper_id or not year:
            print("❌ 缺少必要参数: --json-file, --paper-id, --year")
            return

        import_from_json(json_file, paper_id, year)

    else:
        print(f"❌ 未知命令: {command}")

if __name__ == '__main__':
    main()

