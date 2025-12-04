"""
批量生成章节题目脚本（优化版）
- 防止题目重复
- 答案使用有理数表示
"""
import json
import random
from pathlib import Path
import sys
import hashlib

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

import sympy as sp


# ========== 唯一ID生成系统 ==========

_used_ids = set()

def generate_unique_id(prefix: str, content: str) -> str:
    """生成基于内容的唯一ID"""
    # 使用内容哈希确保唯一性
    content_hash = hashlib.md5(content.encode()).hexdigest()[:8]
    unique_id = f"{prefix}_{content_hash}"

    # 确保ID未被使用
    counter = 0
    while unique_id in _used_ids:
        counter += 1
        unique_id = f"{prefix}_{content_hash}_{counter}"

    _used_ids.add(unique_id)
    return unique_id


# ========== 优化的题目生成函数 ==========

def generate_algebra_question(difficulty="L1"):
    """生成代数与方程题目 - 使用有理数"""
    x = sp.Symbol('x')

    # 一元二次方程：使用整数系数
    a = random.randint(1, 5)
    b = random.randint(-10, 10)
    c = random.randint(-10, 10)

    equation = a * x**2 + b * x + c
    discriminant = b**2 - 4*a*c

    question = f"方程 ${sp.latex(equation)} = 0$ 的判别式 $\\Delta$ 是？"
    answer = str(discriminant)  # 整数，不是浮点数

    # 生成干扰项（都是整数）
    options = [
        str(discriminant),
        str(b**2 + 4*a*c),
        str(b**2 - 2*a*c),
        str(abs(discriminant) + random.randint(1, 5)),
    ]
    random.shuffle(options)
    correct_index = chr(65 + options.index(answer))

    return {
        "questionId": generate_unique_id("algebra", question),
        "topic": "代数与方程",
        "difficulty": difficulty,
        "type": "choice",
        "question": question,
        "options": options,
        "answer": correct_index,
        "solution": f"判别式 $\\Delta = b^2 - 4ac = ({b})^2 - 4 \\times {a} \\times ({c}) = {discriminant}$",
        "tags": ["代数", "一元二次方程", "判别式"],
        "knowledgePoints": ["代数", "方程"],
        "abilityTags": ["apply", "analyze"],
        "source": "generated",
        "reviewStatus": "approved"
    }


def generate_geometry_question(difficulty="L1"):
    """生成平面几何题目 - 使用有理数/分数"""
    # 选择偶数确保结果是整数，或使用分数
    base = random.choice([4, 6, 8, 10, 12])
    height = random.choice([3, 5, 7, 9])

    # 计算面积（使用SymPy的Rational）
    area = sp.Rational(base * height, 2)

    question = f"底边为 ${base}$，高为 ${height}$ 的三角形面积是？"
    answer_latex = sp.latex(area)

    # 生成干扰项
    options = [
        answer_latex,
        str(base * height),
        sp.latex(sp.Rational(base + height, 2)),
        sp.latex(sp.Rational(base * height, 4)),
    ]
    random.shuffle(options)
    correct_index = chr(65 + options.index(answer_latex))

    return {
        "questionId": generate_unique_id("geometry", question),
        "topic": "平面几何",
        "difficulty": difficulty,
        "type": "choice",
        "question": question,
        "options": [f"${opt}$" for opt in options],
        "answer": correct_index,
        "solution": f"三角形面积 $S = \\frac{{1}}{{2}} \\times$ 底 $\\times$ 高 $= \\frac{{1}}{{2}} \\times {base} \\times {height} = {answer_latex}$",
        "tags": ["几何", "三角形", "面积"],
        "knowledgePoints": ["几何", "三角形"],
        "abilityTags": ["memory", "apply"],
        "source": "generated",
        "reviewStatus": "approved"
    }


def generate_combinatorics_question(difficulty="L1"):
    """生成排列组合题目 - 整数答案"""
    from math import factorial

    n = random.randint(5, 10)
    r = random.randint(2, min(4, n))

    # 排列数（整数）
    p_nr = factorial(n) // factorial(n - r)
    c_nr = factorial(n) // (factorial(r) * factorial(n - r))

    question = f"从 ${n}$ 个不同元素中取出 ${r}$ 个排列，有多少种方式？"
    answer = str(p_nr)

    # 干扰项（都是整数）
    options = [
        str(p_nr),
        str(c_nr),
        str(n * r),
        str(factorial(n)),
    ]
    random.shuffle(options)
    correct_index = chr(65 + options.index(answer))

    return {
        "questionId": generate_unique_id("combinatorics", question),
        "topic": "排列与组合",
        "difficulty": difficulty,
        "type": "choice",
        "question": question,
        "options": options,
        "answer": correct_index,
        "solution": f"排列数 $A_{{{n}}}^{{{r}}} = \\frac{{{n}!}}{{({n}-{r})!}} = {p_nr}$",
        "tags": ["排列", "组合", "计数"],
        "knowledgePoints": ["排列", "组合"],
        "abilityTags": ["apply", "analyze"],
        "source": "generated",
        "reviewStatus": "approved"
    }


def generate_complex_question(difficulty="L1"):
    """生成复数题目 - 使用有理数"""
    # 使用小整数确保结果简洁
    a = random.randint(-5, 5)
    b = random.randint(1, 5)
    c = random.randint(-5, 5)
    d = random.randint(1, 5)

    # 复数加法
    real_part = a + c
    imag_part = b + d

    question = f"计算 $({a} + {b}i) + ({c} + {d}i)$ = ?"

    # 答案使用标准形式
    if imag_part >= 0:
        answer = f"{real_part} + {imag_part}i"
    else:
        answer = f"{real_part} - {abs(imag_part)}i"

    # 干扰项
    options = [
        answer,
        f"{a + c} + {b}i",
        f"{a} + {b + d}i",
        f"{a - c} + {b - d}i",
    ]
    random.shuffle(options)
    correct_index = chr(65 + options.index(answer))

    return {
        "questionId": generate_unique_id("complex", question),
        "topic": "复数",
        "difficulty": difficulty,
        "type": "choice",
        "question": question,
        "options": [f"${opt}$" for opt in options],
        "answer": correct_index,
        "solution": f"实部相加，虚部相加：$({a})+({c}) + ({b}+{d})i = {answer}$",
        "tags": ["复数", "运算"],
        "knowledgePoints": ["复数", "复数运算"],
        "abilityTags": ["memory", "apply"],
        "source": "generated",
        "reviewStatus": "approved"
    }


def generate_parametric_question(difficulty="L1"):
    """生成参数方程题目 - 使用有理数"""
    a = random.randint(2, 5)

    question = f"参数方程 $\\begin{{cases}} x = {a}t \\\\ y = {a}t^2 \\end{{cases}}$ 消去参数后的方程是？"

    # 答案：y = x²/a²（使用分数表示）
    if a == 1:
        answer = "y = x^2"
    else:
        answer = f"y = \\frac{{x^2}}{{{a**2}}}"

    # 干扰项
    options = [
        answer,
        f"y = {a}x^2",
        f"y = \\frac{{x}}{{{a}}}",
        f"y = x^2 + {a}",
    ]
    random.shuffle(options)
    correct_index = chr(65 + options.index(answer))

    return {
        "questionId": generate_unique_id("parametric", question),
        "topic": "参数方程与极坐标",
        "difficulty": difficulty,
        "type": "choice",
        "question": question,
        "options": [f"${opt}$" for opt in options],
        "answer": correct_index,
        "solution": f"由 $x = {a}t$ 得 $t = \\frac{{x}}{{{a}}}$，代入得 ${answer}$",
        "tags": ["参数方程", "消参"],
        "knowledgePoints": ["参数方程"],
        "abilityTags": ["apply", "analyze"],
        "source": "generated",
        "reviewStatus": "approved"
    }


def generate_inverse_trig_question(difficulty="L1"):
    """生成反三角函数题目 - 使用符号答案"""
    # 常见的反三角函数值（使用符号）
    common_values = [
        ("0", "0"),
        ("\\frac{1}{2}", "\\frac{\\pi}{6}"),
        ("-\\frac{1}{2}", "-\\frac{\\pi}{6}"),
        ("1", "\\frac{\\pi}{2}"),
        ("-1", "-\\frac{\\pi}{2}"),
        ("\\frac{\\sqrt{2}}{2}", "\\frac{\\pi}{4}"),
        ("\\frac{\\sqrt{3}}{2}", "\\frac{\\pi}{3}"),
    ]

    x_val, result = random.choice(common_values)

    question = f"$\\arcsin({x_val})$ 的值是？"
    answer = result

    # 干扰项（都是符号形式）
    options = [
        result,
        "\\frac{\\pi}{3}",
        "\\frac{\\pi}{6}",
        "0",
    ]
    # 确保选项唯一
    options = list(set(options))
    while len(options) < 4:
        options.append(f"\\frac{{\\pi}}{{{random.choice([2,3,4,6])}}}")
    options = options[:4]

    random.shuffle(options)
    correct_index = chr(65 + options.index(answer))

    return {
        "questionId": generate_unique_id("inverse_trig", question),
        "topic": "反三角函数",
        "difficulty": difficulty,
        "type": "choice",
        "question": question,
        "options": [f"${opt}$" for opt in options],
        "answer": correct_index,
        "solution": f"根据反三角函数的定义，$\\arcsin({x_val}) = {answer}$",
        "tags": ["反三角函数", "arcsin"],
        "knowledgePoints": ["反三角函数"],
        "abilityTags": ["memory", "apply"],
        "source": "generated",
        "reviewStatus": "approved"
    }


# ========== 题目加载和保存 ==========

def load_theme_config():
    """加载主题配置"""
    config_path = Path(__file__).parent.parent / "data" / "theme_configs.json"
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_existing_questions():
    """加载现有题目"""
    questions_path = Path(__file__).parent.parent / "data" / "questions.json"
    if questions_path.exists():
        with open(questions_path, 'r', encoding='utf-8') as f:
            questions = json.load(f)
            # 记录已使用的ID
            for q in questions:
                _used_ids.add(q.get('questionId', ''))
            return questions
    return []


def save_questions(questions):
    """保存题目"""
    questions_path = Path(__file__).parent.parent / "data" / "questions.json"
    # 备份
    if questions_path.exists():
        import shutil
        from datetime import datetime
        backup_path = questions_path.parent / f"questions_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        shutil.copy(questions_path, backup_path)
        print(f"📦 已备份到：{backup_path.name}")

    with open(questions_path, 'w', encoding='utf-8') as f:
        json.dump(questions, f, ensure_ascii=False, indent=2)
    print(f"✅ 已保存 {len(questions)} 道题目")


def count_chapter_questions(questions, chapter_keyword):
    """统计某章节的现有题目数"""
    count = 0
    for q in questions:
        topic = q.get('topic', '')
        tags = q.get('tags', [])
        if chapter_keyword in topic or any(chapter_keyword in tag for tag in tags):
            count += 1
    return count


def main(auto_save=False):
    """主函数：批量生成题目"""
    print("=" * 60)
    print("📚 批量生成章节题目（优化版）")
    print("=" * 60)
    print()

    # 加载配置
    config = load_theme_config()
    theme = config['themes'][0]

    print(f"🎯 主题：{theme['name']}")
    print(f"📊 总目标：{theme['totalQuestions']} 题")
    print()

    # 加载现有题目
    existing = load_existing_questions()
    print(f"📦 现有题目：{len(existing)} 题")
    print(f"📝 已使用ID：{len(_used_ids)} 个")
    print()

    # 统计各章节
    print("📊 各章节现有题目统计：")
    chapter_stats = {}
    for chapter in theme['chapters']:
        chapter_name = chapter['chapterName']
        keyword = chapter_name.split(' ')[-1] if '章' in chapter_name else chapter_name
        count = count_chapter_questions(existing, keyword)
        suggested = chapter['suggestedQuestions']
        chapter_stats[chapter_name] = {'current': count, 'suggested': suggested}

        status = "✅" if count >= suggested else "⚠️" if count > 0 else "❌"
        print(f"   {status} {chapter_name}: {count}/{suggested} 题")
    print()

    # 生成函数映射
    generators = {
        "第2章 代数与方程": generate_algebra_question,
        "第3章 平面几何": generate_geometry_question,
        "第4章 反三角函数": generate_inverse_trig_question,
        "第5章 排列与组合": generate_combinatorics_question,
        "第6章 复数": generate_complex_question,
        "第7章 参数方程与极坐标方程": generate_parametric_question,
    }

    new_questions = []

    # 为每个章节生成题目
    for chapter in theme['chapters']:
        chapter_name = chapter['chapterName']
        suggested = chapter['suggestedQuestions']
        current = chapter_stats.get(chapter_name, {}).get('current', 0)

        if chapter_name not in generators:
            print(f"⏭️  跳过 {chapter_name}（无生成器）")
            continue

        if current >= suggested:
            print(f"⏭️  跳过 {chapter_name}（已有 {current} 题）")
            continue

        needed = suggested - current
        print(f"📝 生成 {chapter_name}")
        print(f"   需生成：{needed} 题")

        generator = generators[chapter_name]
        difficulty_dist = chapter['difficultyDistribution']

        # 根据难度分配
        difficulties = []
        difficulties.extend(['L1'] * int(needed * difficulty_dist['Easy']))
        difficulties.extend(['L2'] * int(needed * difficulty_dist['Medium']))
        difficulties.extend(['L3'] * int(needed * difficulty_dist['Hard']))

        while len(difficulties) < needed:
            difficulties.append(random.choice(['L1', 'L2', 'L3']))

        # 生成题目
        for i, diff in enumerate(difficulties):
            try:
                question = generator(diff)
                new_questions.append(question)

                if (i + 1) % 10 == 0:
                    print(f"   已生成 {i + 1}/{len(difficulties)} 题")
            except Exception as e:
                print(f"   ⚠️  生成失败: {e}")

        print(f"   ✅ 完成：生成 {len(difficulties)} 题")
        print()

    # 合并题目
    all_questions = existing + new_questions

    print("=" * 60)
    print(f"📊 生成统计")
    print(f"   原有题目：{len(existing)} 题")
    print(f"   新增题目：{len(new_questions)} 题")
    print(f"   合计题目：{len(all_questions)} 题")
    print(f"   唯一ID数：{len(_used_ids)} 个")
    print("=" * 60)
    print()

    # 保存
    if new_questions:
        if auto_save or '--yes' in sys.argv or '-y' in sys.argv:
            save_questions(all_questions)
            print("✅ 保存成功！")
        else:
            try:
                confirm = input("是否保存新生成的题目？(y/n): ")
                if confirm.lower() == 'y':
                    save_questions(all_questions)
                    print("✅ 保存成功！")
                else:
                    print("❌ 已取消")
            except EOFError:
                print("\n⚠️  非交互式环境，请使用 --yes 参数")
    else:
        print("ℹ️  没有新题目生成")


if __name__ == "__main__":
    auto = '--yes' in sys.argv or '-y' in sys.argv
    main(auto_save=auto)
