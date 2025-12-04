"""
智能题目识别器
使用正则表达式识别题目结构，支持：
- 一、单项选择题
- 二、填空题
- 三、解答题
等格式
"""
import re
import json
from typing import List, Dict
from pathlib import Path


class SmartSplitter:
    def __init__(self):
        """初始化智能识别器"""
        # 大题类型关键词
        self.section_keywords = {
            'choice': ['单项选择题', '单选题', '选择题'],
            'multiple': ['多项选择题', '多选题'],
            'fill': ['填空题'],
            'solution': ['解答题', '计算题', '证明题']
        }

        # 题号模式（更宽松）
        self.question_patterns = [
            r'^\s*(\d+)[.、．]\s*',                    # 1. 或 1、
            r'^\s*\((\d+)\)\s*',                      # (1)
            r'^\s*【(\d+)】\s*',                      # 【1】
            r'[^0-9](\d+)[.、]\s*[^\d]',              # 前后有非数字
        ]

        # 选项模式
        self.option_patterns = [
            r'^([A-D])[.、．]\s*(.+)',                # A. 或 A、
            r'^\(([A-D])\)\s*(.+)',                   # (A)
            r'^【([A-D])】\s*(.+)',                   # 【A】
        ]

    def find_sections(self, text: str) -> List[Dict]:
        """
        查找各大题的位置

        Returns:
            [{"type": "choice", "start": 100, "keyword": "单项选择题"}, ...]
        """
        sections = []
        lines = text.split('\n')

        for i, line in enumerate(lines):
            for q_type, keywords in self.section_keywords.items():
                for keyword in keywords:
                    if keyword in line:
                        sections.append({
                            'type': q_type,
                            'start_line': i,
                            'keyword': keyword,
                            'start_text': line
                        })
                        break

        return sections

    def extract_questions_from_section(self, text: str, section_type: str) -> List[Dict]:
        """
        从某个大题中提取所有小题

        Args:
            text: 该大题的文本
            section_type: 题目类型（choice/fill/solution）

        Returns:
            题目列表
        """
        questions = []
        lines = text.split('\n')

        current_question = None
        current_options = []
        question_number = 1

        for line_idx, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue

            # 检测题号
            found_number = None
            for pattern in self.question_patterns:
                match = re.search(pattern, line)
                if match:
                    found_number = match.group(1)
                    break

            if found_number:
                # 保存上一题
                if current_question:
                    current_question['options'] = current_options
                    current_question['ocrRawText'] = current_question.get('ocrRawText', '') + '\n' + '\n'.join(current_options)
                    questions.append(current_question)

                # 开始新题
                current_question = {
                    'questionNumber': int(found_number),
                    'rawText': '',
                    'ocrRawText': line,
                    'type': section_type,
                    'options': [],
                    'answer': '',
                    'difficulty': 'L1',
                    'knowledgePoints': [],
                    'solution': '',
                    'topic': ''
                }
                current_options = []
                question_number = int(found_number) + 1
                continue

            # 检测选项（仅选择题）
            if section_type in ['choice', 'multiple'] and current_question:
                option_match = None
                for pattern in self.option_patterns:
                    match = re.match(pattern, line)
                    if match:
                        option_match = match
                        break

                if option_match:
                    letter = option_match.group(1)
                    content = option_match.group(2).strip()
                    current_question['options'].append({
                        'letter': letter,
                        'content': content
                    })
                    current_options.append(f"{letter}. {content}")
                    continue

            # 普通文本（追加到当前题）
            if current_question:
                if current_question['ocrRawText']:
                    current_question['ocrRawText'] += '\n' + line
                else:
                    current_question['ocrRawText'] = line

        # 保存最后一题
        if current_question:
            current_question['options'] = current_options
            questions.append(current_question)

        return questions

    def process_ocr_result(self, ocr_file: str) -> Dict:
        """
        处理OCR结果，智能识别题目

        Args:
            ocr_file: OCR结果JSON文件路径

        Returns:
            {
                "sections": [...],
                "questions": [...],
                "total": 10
            }
        """
        # 读取OCR结果
        with open(ocr_file, 'r', encoding='utf-8') as f:
            ocr_data = json.load(f)

        full_text = ocr_data.get('ocrResult', {}).get('fullText', '')

        # 1. 查找各大题
        sections = self.find_sections(full_text)

        if not sections:
            print('⚠️  未找到大题标记（一、单项选择题等）')
            # 尝试作为整体处理
            sections = [{'type': 'choice', 'start_line': 0, 'keyword': '全部'}]

        # 2. 提取每个大题的内容
        lines = full_text.split('\n')
        all_questions = []

        for i, section in enumerate(sections):
            start = section['start_line']
            # 结束位置：下一个大题的开始，或文本末尾
            end = sections[i + 1]['start_line'] if i + 1 < len(sections) else len(lines)

            section_text = '\n'.join(lines[start:end])
            section_questions = self.extract_questions_from_section(
                section_text,
                section['type']
            )

            all_questions.extend(section_questions)

            print(f"✓ {section['keyword']}: 识别到 {len(section_questions)} 道题")

        return {
            'sections': sections,
            'questions': all_questions,
            'total': len(all_questions)
        }


def main():
    """命令行使用"""
    import sys

    if len(sys.argv) < 2:
        print("用法: python smart_splitter.py <ocr_result.json>")
        return

    ocr_file = sys.argv[1]

    # 创建识别器
    splitter = SmartSplitter()

    # 处理
    result = splitter.process_ocr_result(ocr_file)

    print(f"\n✅ 智能识别完成！")
    print(f"   总题目数: {result['total']}")
    print(f"   大题数: {len(result['sections'])}")

    # 保存结果
    output_path = Path(ocr_file).parent / "smart_questions.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"   保存到: {output_path}")

    # 显示前3题
    if result['questions']:
        print(f"\n📝 前3道题预览：")
        for q in result['questions'][:3]:
            print(f"\n题目 {q['questionNumber']}:")
            print(f"  OCR原文: {q['ocrRawText'][:80]}...")
            print(f"  类型: {q['type']}")
            print(f"  选项数: {len(q.get('options', []))}")


if __name__ == "__main__":
    main()

