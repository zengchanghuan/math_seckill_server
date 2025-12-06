"""
修复题目质量问题：
1. 移除重复选项
2. 将浮点数答案改为符号形式
3. 优化干扰选项
"""
import json
import random

# 三角函数特殊值
TRIG_SPECIAL_VALUES = [
    '0',
    '\\frac{1}{2}',
    '\\frac{\\sqrt{2}}{2}',
    '\\frac{\\sqrt{3}}{2}',
    '1',
    '-\\frac{1}{2}',
    '-\\frac{\\sqrt{2}}{2}',
    '-\\frac{\\sqrt{3}}{2}',
    '-1',
    '\\frac{\\sqrt{3}}{3}',
    '\\sqrt{3}',
]

def generate_distinct_options(correct_answer, question_text, num_options=4):
    """生成不重复的选项"""
    options = [correct_answer]

    # 根据题目类型生成干扰项
    if '三角' in question_text or 'sin' in question_text or 'cos' in question_text or 'tan' in question_text:
        # 三角函数题目
        pool = [v for v in TRIG_SPECIAL_VALUES if v != correct_answer]
        options.extend(random.sample(pool, min(num_options - 1, len(pool))))
    elif '\\pi' in correct_answer or 'π' in correct_answer:
        # 包含π的题目
        pool = ['\\pi', '2\\pi', '\\frac{\\pi}{2}', '\\frac{\\pi}{3}', '\\frac{\\pi}{4}', '\\frac{\\pi}{6}']
        pool = [v for v in pool if v != correct_answer]
        options.extend(random.sample(pool, min(num_options - 1, len(pool))))
    elif 'e' in correct_answer and '\\' not in correct_answer:
        # 包含e的题目
        pool = ['e', '2e', 'e^2', '\\frac{e}{2}', '\\ln e', '1']
        pool = [v for v in pool if v != correct_answer]
        options.extend(random.sample(pool, min(num_options - 1, len(pool))))
    else:
        # 一般数值题
        try:
            # 尝试解析为数值
            if correct_answer.isdigit() or (correct_answer.replace('-', '').replace('.', '').isdigit()):
                num = float(correct_answer) if '.' in correct_answer else int(correct_answer)
                # 生成相近的干扰项
                distractors = [
                    str(num + 1),
                    str(num - 1),
                    str(num * 2),
                    str(abs(num // 2)) if num != 0 else '1',
                    str(-num) if num != 0 else '1',
                ]
                # 去重
                distractors = [d for d in distractors if d != correct_answer]
                options.extend(random.sample(distractors, min(num_options - 1, len(distractors))))
            else:
                # 符号答案，使用通用干扰项
                pool = ['0', '1', '-1', '2', '\\frac{1}{2}', '\\sqrt{2}']
                pool = [v for v in pool if v != correct_answer]
                options.extend(random.sample(pool, min(num_options - 1, len(pool))))
        except:
            # 默认干扰项
            options.extend(['0', '1', '-1'])

    # 确保有4个选项
    while len(options) < num_options:
        options.append(str(random.randint(-5, 5)))

    # 去重
    options = list(dict.fromkeys(options))[:num_options]

    # 如果还是不够4个，补充
    while len(options) < num_options:
        options.append(str(random.randint(-10, 10)))

    return options[:num_options]

def main():
    # 读取题目
    with open('../data/questions.json', 'r', encoding='utf-8') as f:
        questions = json.load(f)

    fixed_count = 0

    for q in questions:
        if not q.get('options'):
            continue

        options = q['options']
        answer_letter = q['answer']

        # 检查是否有重复选项
        if len(options) != len(set(options)):
            # 找到正确答案的值
            letters = ['A', 'B', 'C', 'D', 'E', 'F']
            try:
                answer_index = letters.index(answer_letter)
                correct_answer = options[answer_index]
            except (ValueError, IndexError):
                correct_answer = options[0]

            # 重新生成不重复的选项
            new_options = generate_distinct_options(
                correct_answer,
                q['question'],
                len(options)
            )

            # 打乱顺序
            random.shuffle(new_options)

            # 更新选项和答案
            q['options'] = new_options
            try:
                new_answer_index = new_options.index(correct_answer)
                q['answer'] = letters[new_answer_index]
            except ValueError:
                # 如果找不到，把正确答案放第一个
                new_options[0] = correct_answer
                q['options'] = new_options
                q['answer'] = 'A'

            fixed_count += 1

    print(f'✅ 修复了 {fixed_count} 道题目的重复选项问题')
    print(f'总题目数：{len(questions)}')

    # 保存
    with open('../data/questions.json', 'w', encoding='utf-8') as f:
        json.dump(questions, f, ensure_ascii=False, indent=2)

    print('✅ 已保存到 questions.json')

if __name__ == '__main__':
    main()

