#!/usr/bin/env python3
"""
Markdown 真题文件转 JSON 工具
将 Markdown 格式的真题文件转换为 JSON 格式，并导入到 questions.json
"""

import json
import re
import sys
import uuid
from pathlib import Path
from typing import List, Dict, Optional, Tuple

# 数据文件路径
DATA_DIR = Path(__file__).parent.parent / "data"
QUESTIONS_FILE = DATA_DIR / "questions.json"

def extract_year_from_filename(filename: str) -> Optional[int]:
    """从文件名提取年份"""
    match = re.search(r'(\d{4})', filename)
    if match:
        return int(match.group(1))
    return None

def parse_choice_question(text: str, question_num: int) -> Optional[Dict]:
    """解析选择题"""
    # 匹配题号和题目内容（支持两种格式：**1. ** 或 1.）
    # 先尝试匹配题号在开头
    match = re.match(r'(?:\*\*)?(\d+)\.\s*(.+?)(?:\*\*)?', text, re.DOTALL)
    if not match:
        # 如果开头没有题号，尝试在整个文本中查找
        match = re.search(r'(?:\*\*)?(\d+)\.\s*(.+?)(?:\*\*)?', text, re.DOTALL)
        if not match:
            return None

    question_text = match.group(2).strip()

    # 提取选项（支持多种格式）
    options = []
    # 格式1: A. 选项内容（单独一行，可能有多个空格）
    option_pattern1 = r'^\s*([A-D])\.\s+([^\n]+)'
    # 格式2: A. 选项 B. 选项（同一行，用空格分隔）
    option_pattern2 = r'([A-D])\.\s+([^A-D\n]+?)(?=\s+[A-D]\.|$)'
    # 格式3: A. 选项（在同一行，用多个空格分隔）
    option_pattern3 = r'([A-D])\.\s+([^\s]+(?:\s+[^\s]+)*?)(?=\s+[A-D]\.|$)'

    for match in re.finditer(option_pattern1, text, re.MULTILINE):
        opt_text = match.group(2).strip()
        # 如果选项文本包含其他选项字母，需要进一步分割
        if re.search(r'\b[B-D]\.', opt_text):
            # 包含其他选项，需要分割
            parts = re.split(r'\s+([B-D])\.\s+', opt_text)
            if len(parts) > 1:
                options.append(f"{match.group(1)}. {parts[0].strip()}")
                for j in range(1, len(parts), 2):
                    if j + 1 < len(parts):
                        options.append(f"{parts[j]}. {parts[j+1].strip()}")
            else:
                options.append(f"{match.group(1)}. {opt_text}")
        else:
            options.append(f"{match.group(1)}. {opt_text}")

    # 如果格式1没找到，尝试格式2
    if len(options) < 2:
        options = []
        for match in re.finditer(option_pattern2, text):
            options.append(f"{match.group(1)}. {match.group(2).strip()}")

    # 如果还是不够，尝试格式3（更宽松的匹配）
    if len(options) < 2:
        options = []
        # 直接查找所有 A. B. C. D. 模式
        all_options = re.findall(r'([A-D])\.\s+([^\n]+?)(?=\s+[A-D]\.|$|\n\n)', text)
        for letter, content in all_options:
            content = content.strip()
            # 移除末尾的括号等
            content = re.sub(r'\s*[（(].*$', '', content)
            options.append(f"{letter}. {content}")

    if len(options) < 2:
        return None

    return {
        'type': 'choice',
        'questionNumber': question_num,
        'question': question_text,
        'options': options,
        'answer': '',  # 需要从解析文件中获取
        'solution': '',
    }

def parse_fill_question(text: str, question_num: int) -> Optional[Dict]:
    """解析填空题"""
    # 匹配题号和题目内容（支持两种格式）
    match = re.match(r'(?:\*\*)?(\d+)\.\s*(.+?)(?:\*\*)?', text, re.DOTALL)
    if not match:
        return None

    question_text = match.group(2).strip()
    # 替换下划线为空白
    question_text = re.sub(r'_+|\u00A0+|\s+', '______', question_text)

    return {
        'type': 'fill',
        'questionNumber': question_num,
        'question': question_text,
        'answer': '',  # 需要从解析文件中获取
        'solution': '',
    }

def parse_solution_question(text: str, question_num: int) -> Optional[Dict]:
    """解析解答题（计算题、综合题）"""
    # 匹配题号和题目内容（支持两种格式）
    match = re.match(r'(?:\*\*)?(\d+)\.\s*(.+?)(?:\*\*)?', text, re.DOTALL)
    if not match:
        return None

    question_text = match.group(2).strip()

    return {
        'type': 'solution',
        'questionNumber': question_num,
        'question': question_text,
        'answer': '',  # 需要从解析文件中获取
        'solution': '',
    }

def parse_markdown_file(md_file: Path) -> Tuple[List[Dict], Optional[int]]:
    """解析 Markdown 文件，返回题目列表和年份"""
    with open(md_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # 提取年份
    year = extract_year_from_filename(md_file.name)

    # 按章节分割（支持 ## 和 ### 两种格式）
    sections = re.split(r'##+\s*[一二三四五六七八九十]+、', content)

    questions = []
    current_question_num = 0

    for section in sections:
        if not section.strip():
            continue

        # 判断题目类型
        if '单项选择题' in section or '选择题' in section:
            question_type = 'choice'
            parse_func = parse_choice_question
        elif '填空题' in section:
            question_type = 'fill'
            parse_func = parse_fill_question
        elif '计算题' in section or '综合题' in section or '解答题' in section:
            question_type = 'solution'
            parse_func = parse_solution_question
        else:
            continue

        # 分割题目（支持多种格式）
        # 格式1: **题号.** （加粗格式）
        # 格式2: 题号. （普通格式，不在**中）
        # 格式3: 题号. [（带括号）

        # 先尝试格式1（**题号.**）
        question_blocks = re.split(r'\*\*(\d+)\.', section)
        if len(question_blocks) < 3:
            # 尝试格式2和3：题号. 或 题号. [
            question_blocks = re.split(r'(?<!\*)\b(\d+)\.\s+(?:\[|（)?', section)

        # 如果还是没找到，尝试更宽松的匹配（包括**中的题号）
        if len(question_blocks) < 3:
            question_blocks = re.split(r'(\d+)\.\s+', section)

        for i in range(1, len(question_blocks), 2):
            if i + 1 >= len(question_blocks):
                break

            try:
                question_num = int(question_blocks[i])
                question_text = question_blocks[i+1]

                # 找到下一题的起始位置（避免包含下一题的内容）
                # 查找下一个题号（比当前题号大1）
                next_num = question_num + 1
                next_pattern = rf'(?:\*\*)?{next_num}\.\s*(?:\[|（)?'
                next_question_match = re.search(next_pattern, question_text)
                if next_question_match:
                    question_text = question_text[:next_question_match.start()]

                # 找到章节结束标记
                section_end = re.search(r'---|###', question_text)
                if section_end:
                    question_text = question_text[:section_end.start()]

                # 构建完整的题目文本（包含题号）
                full_text = f"{question_num}. {question_text}"

                parsed = parse_func(full_text, question_num)
                if parsed:
                    questions.append(parsed)
                    current_question_num = question_num
            except (ValueError, IndexError) as e:
                # 跳过解析失败的题目
                continue

    return questions, year

def parse_answer_file(answer_file: Path) -> Dict[int, Dict[str, str]]:
    """解析答案文件，返回题号到答案和解析的映射"""
    with open(answer_file, 'r', encoding='utf-8') as f:
        content = f.read()

    answers = {}

    # 匹配答案和解析
    pattern = r'\*\*(\d+)\.\s*(.+?)\*\*\s*\*\s*\*\*【答案】\*\*\s*(.+?)(?:\*\s*\*\*【解析】\*\*\s*(.+?))?(?=\*\*|\Z)'

    for match in re.finditer(pattern, content, re.DOTALL):
        question_num = int(match.group(1))
        answer = match.group(3).strip()
        solution = match.group(4).strip() if match.group(4) else ''

        answers[question_num] = {
            'answer': answer,
            'solution': solution
        }

    return answers

def convert_to_question_format(parsed_q: Dict, answer_info: Optional[Dict], paper_id: str, year: int) -> Dict:
    """转换为标准题目格式"""
    question_id = f"{paper_id}_q{parsed_q['questionNumber']}"

    question = {
        'questionId': question_id,
        'topic': '高等数学',
        'difficulty': 'L1',  # 默认难度，可以后续调整
        'type': parsed_q['type'],
        'question': parsed_q['question'],
        'answer': answer_info['answer'] if answer_info else '',
        'solution': answer_info['solution'] if answer_info else '',
        'shortSolution': answer_info['solution'][:200] if answer_info and answer_info['solution'] else '',
        'tags': ['真题', '专升本', '广东'],
        'knowledgePoints': ['高等数学'],
        'abilityTags': ['apply'],
        'source': 'real_exam',
        'isRealExam': True,
        'paperId': paper_id,
        'year': year,
        'reviewStatus': 'approved',
    }

    if parsed_q['type'] == 'choice' and 'options' in parsed_q:
        question['options'] = parsed_q['options']

    return question

def import_from_markdown(md_file: str, answer_file: Optional[str] = None, paper_id: Optional[str] = None):
    """从 Markdown 文件导入真题"""
    md_path = Path(md_file)
    if not md_path.exists():
        print(f"❌ 文件不存在: {md_file}")
        return

    # 解析题目
    print(f"📖 解析文件: {md_file}")
    questions, year = parse_markdown_file(md_path)

    if not questions:
        print("❌ 未找到题目")
        return

    print(f"✓ 找到 {len(questions)} 道题目")

    # 解析答案（如果有）
    answers = {}
    if answer_file:
        answer_path = Path(answer_file)
        if answer_path.exists():
            print(f"📖 解析答案文件: {answer_file}")
            answers = parse_answer_file(answer_path)
            print(f"✓ 找到 {len(answers)} 道题的答案")

    # 生成 paper_id
    if not paper_id:
        if year:
            paper_id = f"paper_{year}_1"
        else:
            paper_id = f"paper_unknown_{uuid.uuid4().hex[:8]}"

    # 转换为标准格式
    converted_questions = []
    for q in questions:
        q_num = q['questionNumber']
        answer_info = answers.get(q_num)
        converted = convert_to_question_format(q, answer_info, paper_id, year or 2023)
        converted_questions.append(converted)

    # 导入到 questions.json
    if QUESTIONS_FILE.exists():
        with open(QUESTIONS_FILE, 'r', encoding='utf-8') as f:
            existing_questions = json.load(f)
    else:
        existing_questions = []

    existing_ids = {q.get('questionId') for q in existing_questions}

    added_count = 0
    updated_count = 0

    for q in converted_questions:
        qid = q['questionId']
        if qid in existing_ids:
            # 更新现有题目
            for i, eq in enumerate(existing_questions):
                if eq.get('questionId') == qid:
                    existing_questions[i].update(q)
                    updated_count += 1
                    print(f"✓ 更新题目: {qid}")
                    break
        else:
            # 添加新题目
            existing_questions.append(q)
            added_count += 1
            print(f"✓ 添加题目: {qid}")

    # 保存
    with open(QUESTIONS_FILE, 'w', encoding='utf-8') as f:
        json.dump(existing_questions, f, ensure_ascii=False, indent=2)

    print(f"\n✅ 导入完成!")
    print(f"  - 新增: {added_count} 道题目")
    print(f"  - 更新: {updated_count} 道题目")
    print(f"  - 试卷ID: {paper_id}")
    print(f"  - 年份: {year or '未知'}")

def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("""
Markdown 真题转 JSON 工具

用法:
  python markdown_to_json.py <markdown_file> [--answer-file <answer_file>] [--paper-id <paper_id>]

参数:
  markdown_file      Markdown 格式的真题文件路径
  --answer-file      可选，包含答案和解析的 Markdown 文件
  --paper-id         可选，试卷ID（如 paper_2023_1），如果不提供会自动生成

示例:
  # 只导入题目（无答案）
  python markdown_to_json.py "../math_seckill/2021 年广东省普通高等学校专升本考试 高等数学试题.md"

  # 导入题目和答案
  python markdown_to_json.py "../math_seckill/2021 年广东省普通高等学校专升本考试 高等数学试题.md" \\
    --answer-file "../math_seckill/2021 年广东省普通高等学校专升本考试 高等数学试题及解析.md"

  # 指定试卷ID
  python markdown_to_json.py "../math_seckill/广东省2023年普通高等学校专升本招生考试高等数学试卷.md" \\
    --paper-id paper_2023_1
        """)
        return

    md_file = sys.argv[1]
    answer_file = None
    paper_id = None

    # 解析参数
    i = 2
    while i < len(sys.argv):
        if sys.argv[i] == '--answer-file' and i + 1 < len(sys.argv):
            answer_file = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == '--paper-id' and i + 1 < len(sys.argv):
            paper_id = sys.argv[i + 1]
            i += 2
        else:
            i += 1

    import_from_markdown(md_file, answer_file, paper_id)

if __name__ == '__main__':
    main()

