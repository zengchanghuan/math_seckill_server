#!/usr/bin/env python3
"""
修复题目数据中的数学公式格式问题
"""

import json
import re
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"
QUESTIONS_FILE = DATA_DIR / "questions.json"

def fix_latex_in_question(text: str) -> str:
    """修复题目中的 LaTeX 格式问题"""
    if not text:
        return text

    # 在 $...$ 内部修复
    def fix_math_block(match):
        math_content = match.group(1)
        fixed = math_content
        
        # 通用规则：修复所有 LaTeX 命令后跟多个下划线（2个或更多）的情况
        # 匹配模式：\命令__+字母/数字/{表达式}
        
        # 1. 修复积分符号的下标问题
        # \int______0 或 \int______{0} -> \int_0 或 \int_{0}
        fixed = re.sub(r'\\int_{2,}(\d)(?=\^|\s|$)', r'\\int_{\1}', fixed)
        fixed = re.sub(r'\\int_{2,}(\{[^}]+\})', r'\\int_{\1}', fixed)
        
        # 2. 修复二重积分符号的下标问题
        # \iint______D -> \iint_D
        # \iint______{D} -> \iint_{D}
        fixed = re.sub(r'\\iint_{2,}([A-Za-z])', r'\\iint_{\1}', fixed)
        fixed = re.sub(r'\\iint_{2,}(\{[^}]+\})', r'\\iint_{\1}', fixed)
        
        # 3. 修复其他积分符号（三重积分等）
        fixed = re.sub(r'\\(iiint|oint|oiint)_{2,}([A-Za-z\d])', r'\\\1_{\2}', fixed)
        fixed = re.sub(r'\\(iiint|oint|oiint)_{2,}(\{[^}]+\})', r'\\\1_{\2}', fixed)
        
        # 4. 修复 \left. y \right|______{x=0} -> \left. y \right|_{x=0}
        # 注意：| 在正则中需要转义，但在原始字符串中已经是转义后的
        fixed = re.sub(r'\\right\\|_{2,}(\{[^}]+\})', r'\\right|_{\1}', fixed)
        fixed = re.sub(r'\\right\\|_{2,}([A-Za-z\d=])', r'\\right|_{\1}', fixed)
        
        # 5. 修复求和、乘积等符号的下标问题
        # \sum______, \prod______ 等
        fixed = re.sub(r'\\(sum|prod|bigcup|bigcap|bigvee|bigwedge)_{2,}([A-Za-z\d])', r'\\\1_{\2}', fixed)
        fixed = re.sub(r'\\(sum|prod|bigcup|bigcap|bigvee|bigwedge)_{2,}(\{[^}]+\})', r'\\\1_{\2}', fixed)
        
        # 6. 修复多余的大括号（如 {{{0}}} 变为 {0}）
        fixed = re.sub(r'\{\{+(\d+)\}+\}', r'{\1}', fixed)
        
        return '$' + fixed + '$'

    # 修复所有 $...$ 块
    fixed = re.sub(r'\$([^$]+)\$', fix_math_block, text)

    return fixed

def fix_all_questions():
    """修复所有题目中的格式问题"""
    with open(QUESTIONS_FILE, 'r', encoding='utf-8') as f:
        questions = json.load(f)

    fixed_count = 0
    for q in questions:
        original_question = q.get('question', '')
        fixed_question = fix_latex_in_question(original_question)

        if original_question != fixed_question:
            q['question'] = fixed_question
            fixed_count += 1
            print(f"✓ 修复题目: {q.get('questionId')}")

        # 也修复答案和解析中的公式
        if 'answer' in q:
            original_answer = q.get('answer', '')
            fixed_answer = fix_latex_in_question(original_answer)
            if original_answer != fixed_answer:
                q['answer'] = fixed_answer

        if 'solution' in q:
            original_solution = q.get('solution', '')
            fixed_solution = fix_latex_in_question(original_solution)
            if original_solution != fixed_solution:
                q['solution'] = fixed_solution

        if 'shortSolution' in q:
            original_short = q.get('shortSolution', '')
            fixed_short = fix_latex_in_question(original_short)
            if original_short != fixed_short:
                q['shortSolution'] = fixed_short

    if fixed_count > 0:
        # 备份原文件
        backup_file = QUESTIONS_FILE.with_suffix('.json.backup')
        with open(backup_file, 'w', encoding='utf-8') as f:
            json.dump(questions, f, ensure_ascii=False, indent=2)
        print(f"\n备份已保存到: {backup_file}")

        # 保存修复后的文件
        with open(QUESTIONS_FILE, 'w', encoding='utf-8') as f:
            json.dump(questions, f, ensure_ascii=False, indent=2)

        print(f"\n✅ 修复完成: {fixed_count} 道题目已修复")
    else:
        print("✓ 没有发现需要修复的格式问题")

if __name__ == '__main__':
    fix_all_questions()
