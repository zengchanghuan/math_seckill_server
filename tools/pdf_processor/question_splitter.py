"""
题目智能切分器
根据OCR结果和布局信息，将页面切分为独立的题目
"""
import re
from typing import List, Dict, Optional, Tuple
from pathlib import Path
import json


class QuestionSplitter:
    def __init__(self):
        """初始化题目切分器"""
        # 题号模式
        self.question_patterns = [
            r'^\s*(\d+)\.\s*',           # 1. 2. 3.
            r'^\s*\((\d+)\)\s*',         # (1) (2) (3)
            r'^\s*【(\d+)】\s*',         # 【1】【2】
            r'^\s*第(\d+)题\s*',         # 第1题
        ]

        # 选项模式
        self.option_patterns = [
            r'^([A-D])\.\s*(.+)',        # A. B. C. D.
            r'^([A-D])、\s*(.+)',        # A、B、C、D、
            r'^\(([A-D])\)\s*(.+)',      # (A) (B) (C) (D)
        ]

    def detect_question_number(self, text: str) -> Optional[int]:
        """
        检测文本是否为题号

        Args:
            text: 文本

        Returns:
            题号（如果检测到）或None
        """
        for pattern in self.question_patterns:
            match = re.match(pattern, text)
            if match:
                try:
                    return int(match.group(1))
                except:
                    pass
        return None

    def detect_option(self, text: str) -> Optional[Tuple[str, str]]:
        """
        检测文本是否为选项

        Args:
            text: 文本

        Returns:
            (选项字母, 选项内容) 或 None
        """
        for pattern in self.option_patterns:
            match = re.match(pattern, text.strip())
            if match:
                return (match.group(1), match.group(2).strip())
        return None

    def split_by_lines(self, ocr_result: Dict) -> List[Dict]:
        """
        根据OCR结果按行切分题目

        Args:
            ocr_result: OCR识别结果

        Returns:
            题目列表
        """
        full_text = ocr_result.get('fullText', '')
        lines = full_text.split('\n')

        questions = []
        current_question = None
        current_options = []

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # 检测题号
            q_num = self.detect_question_number(line)
            if q_num is not None:
                # 保存上一题
                if current_question:
                    current_question['options'] = current_options
                    questions.append(current_question)

                # 开始新题
                current_question = {
                    'questionNumber': q_num,
                    'rawText': line,
                    'options': [],
                    'hasFormula': self._has_math_symbols(line)
                }
                current_options = []
                continue

            # 检测选项
            option_match = self.detect_option(line)
            if option_match and current_question:
                letter, content = option_match
                current_options.append({
                    'letter': letter,
                    'content': content,
                    'hasFormula': self._has_math_symbols(content)
                })
                continue

            # 普通文本（追加到当前题目）
            if current_question:
                current_question['rawText'] += ' ' + line

        # 保存最后一题
        if current_question:
            current_question['options'] = current_options
            questions.append(current_question)

        return questions

    def _has_math_symbols(self, text: str) -> bool:
        """
        简单检测是否包含数学符号

        Args:
            text: 文本

        Returns:
            是否包含数学符号
        """
        math_keywords = [
            'sin', 'cos', 'tan', 'log', 'ln', 'lim',
            '∫', '∑', '√', '≈', '≤', '≥', '≠',
            '∞', 'π', '°', '²', '³',
            '∈', '⊂', '∪', '∩',
            'α', 'β', 'γ', 'θ'
        ]

        text_lower = text.lower()
        return any(keyword in text_lower for keyword in math_keywords)

    def enhance_with_coordinates(self, questions: List[Dict], ocr_result: Dict) -> List[Dict]:
        """
        为切分的题目添加坐标信息

        Args:
            questions: 题目列表
            ocr_result: OCR结果（含坐标）

        Returns:
            增强后的题目列表
        """
        words = ocr_result.get('words', [])

        for question in questions:
            # 找到题目文本在words中的位置
            # 简化版：取第一个词的坐标作为题目起始位置
            q_text_start = str(question['questionNumber'])

            matching_words = [w for w in words if q_text_start in w['text']]
            if matching_words:
                first_word = matching_words[0]
                question['bounds'] = {
                    'x': first_word['left'],
                    'y': first_word['top'],
                    'w': 500,  # 默认宽度
                    'h': 200   # 默认高度
                }

        return questions

    def process_page(self, ocr_result: Dict) -> Dict:
        """
        处理单页的OCR结果，切分为题目

        Args:
            ocr_result: OCR识别结果

        Returns:
            处理结果
        """
        # 按行切分
        questions = self.split_by_lines(ocr_result)

        # 添加坐标信息
        questions = self.enhance_with_coordinates(questions, ocr_result)

        return {
            'questionCount': len(questions),
            'questions': questions
        }


def main():
    """示例用法"""
    import sys

    if len(sys.argv) < 2:
        print("用法: python question_splitter.py <ocr_result.json>")
        return

    # 读取OCR结果
    with open(sys.argv[1], 'r', encoding='utf-8') as f:
        ocr_result = json.load(f)

    # 创建切分器
    splitter = QuestionSplitter()

    # 切分题目
    result = splitter.process_page(ocr_result['ocrResult'])

    print(f"\n✅ 识别到 {result['questionCount']} 道题目\n")

    for q in result['questions']:
        print(f"题目 {q['questionNumber']}:")
        print(f"  内容: {q['rawText'][:80]}...")
        print(f"  选项数: {len(q['options'])}")
        if q.get('bounds'):
            print(f"  位置: ({q['bounds']['x']}, {q['bounds']['y']})")
        print()

    # 保存结果
    output_path = Path(sys.argv[1]).with_name('questions_split.json')
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"✅ 结果已保存到: {output_path}")


if __name__ == "__main__":
    main()

