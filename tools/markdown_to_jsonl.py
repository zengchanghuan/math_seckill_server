#!/usr/bin/env python3
"""
专升本数学题库 → 训练数据 JSONL 自动化流水线

将 Markdown 格式的专升本数学真题转换为：
1. 题目结构 JSONL（包含完整元数据）
2. SFT 训练用 JSONL（instruction/input/output 格式）

使用方法:
    python markdown_to_jsonl.py --input_md <markdown_file> --output_jsonl <output.jsonl> --output_sft_jsonl <sft.jsonl> [--answer_file <answer_file>]
"""

import re
import json
import argparse
from pathlib import Path
from typing import List, Dict, Optional, Tuple


def extract_year_from_filename(filename: str) -> Optional[int]:
    """
    从文件名提取年份
    
    支持格式：
    - "2023年广东专升本..."
    - "gd-zsb-2023-..."
    - "2023_..."
    
    如果文件名中没有年份，返回 None
    """
    # 尝试匹配4位数字年份
    match = re.search(r'(\d{4})', filename)
    if match:
        year = int(match.group(1))
        # 确保年份在合理范围内（2000-2100）
        if 2000 <= year <= 2100:
            return year
    return None


def extract_year_from_content(content: str) -> Optional[int]:
    """
    从内容中提取年份（备用方法）
    
    查找模式如："2023年"、"2023年度"等
    """
    patterns = [
        r'(\d{4})\s*年',
        r'(\d{4})\s*年度',
    ]
    for pattern in patterns:
        match = re.search(pattern, content[:1000])  # 只检查前1000个字符
        if match:
            year = int(match.group(1))
            if 2000 <= year <= 2100:
                return year
    return None


def detect_question_type(text: str) -> str:
    """
    检测题目类型
    
    判断逻辑：
    1. 选择题：包含 A. B. C. D. 等选项标记
    2. 填空题：包含下划线占位符，且无选项
    3. 解答题：其他情况，或明确标记"解答题"/"计算题"
    4. 未知：无法判断
    
    注意：这个判断逻辑可能需要根据实际题目格式微调
    """
    text_lower = text.lower()
    
    # 检查是否有选项标记（A. B. C. D. 等）
    has_options = bool(re.search(r'\b[A-D]\.\s+', text))
    
    # 检查是否有下划线占位符（填空题特征）
    has_blank = bool(re.search(r'_+|\u00A0+', text))
    
    # 检查是否有明确的题型标记
    if '选择题' in text or '单选题' in text or '多选题' in text:
        return 'choice'
    if '填空题' in text:
        return 'fill'
    if '解答题' in text or '计算题' in text or '综合题' in text:
        return 'solve'
    
    # 根据内容特征判断
    if has_options:
        return 'choice'
    elif has_blank and not has_options:
        return 'fill'
    elif '解：' in text or '解答：' in text or '解题过程' in text:
        return 'solve'
    else:
        return 'unknown'


def extract_options(text: str) -> List[str]:
    """
    提取选择题选项
    
    支持格式：
    - A. 选项内容（单独一行）
    - A. 选项 B. 选项（同一行）
    - A. 选项（多行选项）
    
    返回格式：["A. 选项1", "B. 选项2", ...]
    
    注意：如果选项格式特殊，可能需要调整正则表达式
    """
    options = []
    
    # 方法1：匹配单独一行的选项（A. 开头，到下一选项或段落结束）
    pattern1 = r'^\s*([A-D])\.\s+([^\n]+(?:\n(?!\s*[A-D]\.)[^\n]+)*)'
    matches = re.finditer(pattern1, text, re.MULTILINE)
    for match in matches:
        letter = match.group(1)
        content = match.group(2).strip()
        # 移除末尾可能的多余字符
        content = re.sub(r'\s*[（(].*$', '', content)
        options.append(f"{letter}. {content}")
    
    # 如果方法1没找到足够的选项，尝试方法2：同一行的多个选项
    if len(options) < 2:
        options = []
        pattern2 = r'([A-D])\.\s+([^A-D\n]+?)(?=\s+[A-D]\.|$)'
        matches = re.finditer(pattern2, text)
        for match in matches:
            letter = match.group(1)
            content = match.group(2).strip()
            content = re.sub(r'\s*[（(].*$', '', content)
            options.append(f"{letter}. {content}")
    
    # 去重并排序（按 A, B, C, D 顺序）
    seen = set()
    unique_options = []
    for opt in options:
        if opt[0] not in seen:
            seen.add(opt[0])
            unique_options.append(opt)
    
    return sorted(unique_options, key=lambda x: x[0])


def extract_answer_and_solution(text: str) -> Tuple[str, str]:
    """
    从文本中提取答案和解析
    
    支持格式：
    - 【答案】答案内容
    - 【解析】解析内容
    - 【解答】解答内容
    
    返回：(answer, solution)
    
    注意：答案和解析的标记格式可能需要根据实际文件微调
    """
    answer = ""
    solution = ""
    
    # 提取答案
    answer_patterns = [
        r'【答案】[：:]\s*(.+?)(?=【|$)',
        r'【答案】\s*(.+?)(?=【|$)',
        r'答案[：:]\s*(.+?)(?=【|$)',
    ]
    for pattern in answer_patterns:
        match = re.search(pattern, text, re.DOTALL)
        if match:
            answer = match.group(1).strip()
            # 清理答案文本（移除多余空白和换行）
            answer = re.sub(r'\s+', ' ', answer)
            break
    
    # 提取解析
    solution_patterns = [
        r'【解析】[：:]\s*(.+?)(?=【|$)',
        r'【解答】[：:]\s*(.+?)(?=【|$)',
        r'【解析】\s*(.+?)(?=【|$)',
        r'【解答】\s*(.+?)(?=【|$)',
        r'解析[：:]\s*(.+?)(?=【|$)',
    ]
    for pattern in solution_patterns:
        match = re.search(pattern, text, re.DOTALL)
        if match:
            solution = match.group(1).strip()
            break
    
    return answer, solution


def clean_markdown_to_text(md_text: str) -> str:
    """
    将 Markdown 转换为纯文本（保留换行）
    
    移除：
    - **加粗标记**
    - 其他 Markdown 标记
    
    保留：
    - 换行符
    - LaTeX 公式（$...$ 格式）
    """
    text = md_text
    
    # 移除加粗标记（但保留内容）
    text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
    
    # 移除其他常见 Markdown 标记（但保留内容）
    text = re.sub(r'#{1,6}\s+', '', text)  # 标题标记
    text = re.sub(r'```[\s\S]*?```', '', text)  # 代码块
    text = re.sub(r'`([^`]+)`', r'\1', text)  # 行内代码
    
    # 保留 LaTeX 公式（$...$ 和 $$...$$）
    # 这里不做处理，保留原样
    
    return text.strip()


def parse_markdown_to_questions(md_text: str, filename: str) -> List[Dict]:
    """
    解析 Markdown 文本，提取所有题目
    
    返回题目列表，每个题目是一个字典，包含所有字段
    
    题号识别模式（按优先级）：
    1. 第\d+题 / 第\s*\d+\s*题
    2. \d+\.\s*（数字+点+空格）
    3. \(\d+\)（括号数字）
    4. \d+、（数字+顿号）
    5. \*\*\d+\.\*\*（加粗格式）
    
    注意：题号正则表达式可能需要根据实际 Markdown 格式微调
    """
    questions = []
    
    # 提取年份
    year = extract_year_from_filename(filename)
    if not year:
        year = extract_year_from_content(md_text)
    
    # 题号识别模式（按优先级尝试）
    question_number_patterns = [
        r'第\s*(\d+)\s*题',  # "第1题" 或 "第 1 题"
        r'(\d+)\.\s+',  # "1. " 或 "1."
        r'\((\d+)\)',  # "(1)"
        r'(\d+)、',  # "1、"
        r'\*\*(\d+)\.\*\*',  # "**1.**"
        r'(\d+)\.\s*\[',  # "1. ["
    ]
    
    # 尝试使用第一个匹配的模式进行切分
    question_blocks = []
    used_pattern = None
    
    for pattern in question_number_patterns:
        # 使用题号作为分割点
        parts = re.split(pattern, md_text)
        if len(parts) > 1:
            question_blocks = parts
            used_pattern = pattern
            break
    
    if not question_blocks:
        # 如果所有模式都失败，尝试更宽松的匹配
        # 查找所有可能的题号位置
        matches = list(re.finditer(r'(\d+)\.\s+', md_text))
        if matches:
            question_blocks = []
            last_pos = 0
            for i, match in enumerate(matches):
                if i > 0:
                    question_blocks.append(md_text[last_pos:match.start()])
                question_blocks.append(match.group(1))  # 题号
                last_pos = match.start()
            question_blocks.append(md_text[last_pos:])
            used_pattern = r'(\d+)\.\s+'
    
    if not question_blocks:
        print(f"⚠️  警告：无法识别题号格式，尝试按段落切分")
        # 最后的后备方案：按双换行切分
        question_blocks = re.split(r'\n\n+', md_text)
        used_pattern = 'paragraph'
    
    # 处理切分后的块
    current_question_num = 0
    i = 0
    
    while i < len(question_blocks):
        # 跳过空块
        if not question_blocks[i].strip():
            i += 1
            continue
        
        # 尝试提取题号
        question_num = None
        question_text_start = i
        
        if used_pattern and used_pattern != 'paragraph':
            # 如果当前块是题号
            if i < len(question_blocks) and question_blocks[i].isdigit():
                try:
                    question_num = int(question_blocks[i])
                    question_text_start = i + 1
                except ValueError:
                    pass
        
        # 如果没找到题号，尝试从文本中提取
        if question_num is None:
            for pattern in question_number_patterns:
                match = re.search(pattern, question_blocks[i])
                if match:
                    try:
                        question_num = int(match.group(1))
                        break
                    except (ValueError, IndexError):
                        pass
        
        # 如果还是没找到，使用递增编号
        if question_num is None:
            current_question_num += 1
            question_num = current_question_num
        else:
            current_question_num = question_num
        
        # 提取题目文本（从当前块到下一个题号或文件结束）
        question_text_parts = []
        if question_text_start < len(question_blocks):
            question_text_parts.append(question_blocks[question_text_start])
        
        # 查找下一个题号的位置
        next_question_start = len(question_blocks)
        for j in range(question_text_start + 1, len(question_blocks)):
            # 检查是否是题号
            is_question_num = False
            if used_pattern and used_pattern != 'paragraph':
                if j < len(question_blocks) and question_blocks[j].isdigit():
                    try:
                        next_num = int(question_blocks[j])
                        if next_num > question_num:
                            is_question_num = True
                    except ValueError:
                        pass
            
            # 或者检查是否包含题号模式
            if not is_question_num:
                for pattern in question_number_patterns:
                    if re.search(pattern, question_blocks[j]):
                        is_question_num = True
                        break
            
            if is_question_num:
                next_question_start = j
                break
            else:
                question_text_parts.append(question_blocks[j])
        
        # 合并题目文本
        question_text_full = '\n'.join(question_text_parts).strip()
        
        # 移除答案和解析部分（如果存在，会在后面单独提取）
        # 先提取答案和解析
        answer, solution = extract_answer_and_solution(question_text_full)
        
        # 从题目文本中移除答案和解析标记
        question_text_clean = question_text_full
        question_text_clean = re.sub(r'【答案】[：:]?\s*.*?(?=【|$)', '', question_text_clean, flags=re.DOTALL)
        question_text_clean = re.sub(r'【解析】[：:]?\s*.*?(?=【|$)', '', question_text_clean, flags=re.DOTALL)
        question_text_clean = re.sub(r'【解答】[：:]?\s*.*?(?=【|$)', '', question_text_clean, flags=re.DOTALL)
        question_text_clean = question_text_clean.strip()
        
        # 检测题型
        question_type = detect_question_type(question_text_clean)
        
        # 提取选项（仅选择题）
        options = []
        if question_type == 'choice':
            options = extract_options(question_text_clean)
        
        # 生成 question_id
        filename_base = Path(filename).stem
        # 清理文件名，只保留字母、数字、连字符
        filename_base = re.sub(r'[^\w-]', '-', filename_base)
        filename_base = re.sub(r'-+', '-', filename_base).strip('-')
        question_id = f"{filename_base}-q{question_num}"
        
        # 构建题目字典
        question_dict = {
            'question_id': question_id,
            'year': year,
            'province': '广东',
            'exam': '专升本 高等数学',
            'type': question_type,
            'chapter': None,  # 预留字段
            'knowledge_points': [],  # 预留字段
            'question_text': clean_markdown_to_text(question_text_clean),
            'question_markdown': question_text_clean,
            'options': options if question_type == 'choice' else [],
            'answer': answer,
            'solution': solution,
        }
        
        questions.append(question_dict)
        
        # 移动到下一个题目
        i = next_question_start
    
    return questions


def parse_answer_file(answer_file_path: str) -> Dict[int, Tuple[str, str]]:
    """
    解析单独的答案文件
    
    返回字典：{题号: (答案, 解析)}
    
    注意：答案文件的格式可能需要根据实际情况调整
    """
    answer_dict = {}
    
    try:
        with open(answer_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 尝试匹配题号和对应的答案/解析
        # 模式：题号 + 答案 + 解析
        pattern = r'(?:第\s*)?(\d+)(?:题|\.)\s*(?:【答案】[：:]?\s*(.+?))?(?:【解析】[：:]?\s*(.+?))?(?=第\s*\d+|$)'
        
        matches = re.finditer(pattern, content, re.DOTALL)
        for match in matches:
            question_num = int(match.group(1))
            answer = match.group(2).strip() if match.group(2) else ""
            solution = match.group(3).strip() if match.group(3) else ""
            answer_dict[question_num] = (answer, solution)
    except Exception as e:
        print(f"⚠️  警告：解析答案文件失败: {e}")
    
    return answer_dict


def convert_question_to_sft_record(question_dict: Dict) -> Optional[Dict]:
    """
    将题目字典转换为 SFT 训练格式
    
    格式：
    {
        "instruction": "...",
        "input": "...",
        "output": "..."
    }
    
    如果题目没有答案，返回 None（不包含在 SFT JSONL 中）
    """
    # 如果没有答案，跳过
    if not question_dict.get('answer'):
        return None
    
    # 构建 instruction
    instruction = "请给出本题的答案并写出详细解题步骤。"
    
    # 构建 input
    input_parts = []
    input_parts.append(f"【题型】{question_dict['type']}")
    input_parts.append(f"【考试】{question_dict['province']} {question_dict['exam']}")
    if question_dict.get('year'):
        input_parts.append(f"【年份】{question_dict['year']}年")
    input_parts.append("")
    input_parts.append("题目：")
    input_parts.append(question_dict['question_markdown'])
    
    # 如果是选择题，添加选项
    if question_dict['type'] == 'choice' and question_dict.get('options'):
        input_parts.append("")
        input_parts.append("选项：")
        for opt in question_dict['options']:
            input_parts.append(opt)
    
    input_text = '\n'.join(input_parts)
    
    # 构建 output
    output_parts = []
    output_parts.append(f"答案：{question_dict['answer']}")
    output_parts.append("")
    
    if question_dict.get('solution'):
        output_parts.append("详细解题步骤：")
        output_parts.append(question_dict['solution'])
    else:
        output_parts.append("暂无详细解析")
    
    output_text = '\n'.join(output_parts)
    
    return {
        'instruction': instruction,
        'input': input_text,
        'output': output_text,
    }


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='将专升本数学真题 Markdown 文件转换为 JSONL 格式',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 基本用法（题目和答案在同一文件）
  python markdown_to_jsonl.py \\
    --input_md "2023年广东专升本高等数学试题.md" \\
    --output_jsonl "questions.jsonl" \\
    --output_sft_jsonl "sft_train.jsonl"
  
  # 使用单独的答案文件
  python markdown_to_jsonl.py \\
    --input_md "2023年广东专升本高等数学试题.md" \\
    --answer_file "2023年广东专升本高等数学试题答案.md" \\
    --output_jsonl "questions.jsonl" \\
    --output_sft_jsonl "sft_train.jsonl"
        """
    )
    
    parser.add_argument(
        '--input_md',
        type=str,
        required=True,
        help='输入 Markdown 文件路径'
    )
    parser.add_argument(
        '--output_jsonl',
        type=str,
        required=True,
        help='输出题目结构 JSONL 文件路径'
    )
    parser.add_argument(
        '--output_sft_jsonl',
        type=str,
        required=True,
        help='输出 SFT 训练用 JSONL 文件路径'
    )
    parser.add_argument(
        '--answer_file',
        type=str,
        default=None,
        help='可选：单独的答案文件路径'
    )
    
    args = parser.parse_args()
    
    # 检查输入文件
    input_path = Path(args.input_md)
    if not input_path.exists():
        print(f"❌ 错误：输入文件不存在: {args.input_md}")
        return
    
    # 读取 Markdown 文件
    print(f"📖 读取文件: {args.input_md}")
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            md_content = f.read()
    except Exception as e:
        print(f"❌ 错误：读取文件失败: {e}")
        return
    
    # 解析题目
    print("🔍 解析题目...")
    questions = parse_markdown_to_questions(md_content, input_path.name)
    
    if not questions:
        print("❌ 错误：未找到任何题目")
        return
    
    print(f"✓ 找到 {len(questions)} 道题目")
    
    # 如果有单独的答案文件，解析并合并
    if args.answer_file:
        answer_path = Path(args.answer_file)
        if answer_path.exists():
            print(f"📖 读取答案文件: {args.answer_file}")
            answer_dict = parse_answer_file(str(answer_path))
            
            # 合并答案到题目中
            for q in questions:
                # 从 question_id 中提取题号
                match = re.search(r'-q(\d+)$', q['question_id'])
                if match:
                    question_num = int(match.group(1))
                    if question_num in answer_dict:
                        answer, solution = answer_dict[question_num]
                        if answer and not q['answer']:
                            q['answer'] = answer
                        if solution and not q['solution']:
                            q['solution'] = solution
            print(f"✓ 合并了 {len(answer_dict)} 道题的答案")
        else:
            print(f"⚠️  警告：答案文件不存在: {args.answer_file}")
    
    # 输出题目结构 JSONL
    print(f"💾 写入题目结构 JSONL: {args.output_jsonl}")
    output_path = Path(args.output_jsonl)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        for q in questions:
            # 确保所有值都可以 JSON 序列化
            q_clean = {}
            for k, v in q.items():
                if v is None:
                    q_clean[k] = None
                elif isinstance(v, (str, int, float, bool, list)):
                    q_clean[k] = v
                else:
                    q_clean[k] = str(v)
            
            f.write(json.dumps(q_clean, ensure_ascii=False) + '\n')
    
    print(f"✓ 已写入 {len(questions)} 道题目")
    
    # 生成并输出 SFT JSONL
    print(f"💾 写入 SFT 训练用 JSONL: {args.output_sft_jsonl}")
    sft_path = Path(args.output_sft_jsonl)
    sft_path.parent.mkdir(parents=True, exist_ok=True)
    
    sft_records = []
    for q in questions:
        sft_record = convert_question_to_sft_record(q)
        if sft_record:
            sft_records.append(sft_record)
    
    with open(sft_path, 'w', encoding='utf-8') as f:
        for record in sft_records:
            f.write(json.dumps(record, ensure_ascii=False) + '\n')
    
    print(f"✓ 已写入 {len(sft_records)} 条 SFT 训练记录")
    print(f"  （跳过了 {len(questions) - len(sft_records)} 道没有答案的题目）")
    
    print("\n✅ 转换完成！")


if __name__ == '__main__':
    main()
