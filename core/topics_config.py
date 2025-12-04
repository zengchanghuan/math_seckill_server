"""
主题和章节配置
用于定义各个主题下的章节结构
"""

# 主题和章节的配置字典
TOPICS_CHAPTERS = {
    "高中衔接大学数学基础": [
        "三角函数",
        "代数与方程",
        "平面几何",
        "立体几何",
        "解析几何",
        "数列",
        "概率与统计",
        "函数与极限",
        "导数与微分",
        "积分"
    ],
    "导数基础": [
        "导数的定义",
        "导数的计算",
        "导数的应用"
    ]
}

# 默认主题
DEFAULT_TOPIC = "高中衔接大学数学基础"


def get_chapters_by_topic(topic: str) -> list[str]:
    """
    根据主题获取章节列表

    Args:
        topic: 主题名称

    Returns:
        章节列表，如果主题不存在返回空列表
    """
    return TOPICS_CHAPTERS.get(topic, [])


def get_all_topics() -> list[str]:
    """
    获取所有可用的主题列表

    Returns:
        主题名称列表
    """
    return list(TOPICS_CHAPTERS.keys())


def is_valid_topic_chapter(topic: str, chapter: str) -> bool:
    """
    验证主题和章节的组合是否有效

    Args:
        topic: 主题名称
        chapter: 章节名称

    Returns:
        如果组合有效返回 True，否则返回 False
    """
    chapters = get_chapters_by_topic(topic)
    return chapter in chapters


