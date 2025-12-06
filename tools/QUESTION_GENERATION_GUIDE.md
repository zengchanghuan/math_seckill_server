# 题目生成使用指南

## 📚 概述

本工具根据 `theme_configs.json` 的配置，自动生成各章节缺少的题目。

---

## 🚀 使用方法

### 基本使用

```bash
cd /Users/zengchanghuan/Desktop/workspace/flutter/math_seckill_server
source venv/bin/activate
python tools/generate_chapter_questions.py
```

### 自动保存（推荐）

```bash
python tools/generate_chapter_questions.py --yes
# 或
python tools/generate_chapter_questions.py -y
```

---

## 🛡️ 安全机制

### 1. 自动备份

- 每次运行前会自动创建备份
- 备份文件：`questions_backup_YYYYMMDD_HHMMSS.json`
- 位置：`data/` 目录

### 2. 防重复生成

- ✅ 自动统计各章节现有题目数
- ✅ 只生成缺少的题目
- ✅ 达到目标的章节自动跳过

示例输出：

```
📊 各章节现有题目统计：
   ⚠️ 第1章 三角函数: 101/110 题
   ✅ 第6章 复数: 60/60 题 ← 自动跳过
   ❌ 第3章 平面几何: 0/30 题 ← 需要生成
```

### 3. 确认机制

- 交互模式：需要手动确认 (y/n)
- 自动模式：使用 `--yes` 参数直接保存

---

## 📊 生成规则

根据 `theme_configs.json` 中的配置：

### 难度分配

- Easy (简单题): 20-50%
- Medium (中等题): 45-60%
- Hard (难题): 5-20%

### 章节权重

按照配置的 `suggestedQuestions` 生成对应数量。

---

## 🔧 支持的章节

当前支持以下章节的自动生成：

### 高中衔接大学数学基础

- ✅ 第2章 代数与方程 (50题)
- ✅ 第3章 平面几何 (30题)
- ✅ 第5章 排列与组合 (100题)
- ✅ 第6章 复数 (60题)
- ✅ 第7章 参数方程与极坐标方程 (70题)

### 待添加生成器

- ⏳ 第1章 三角函数 (需要更复杂的模板)
- ⏳ 第4章 反三角函数 (需要特殊模板)

---

## 📁 文件位置

### 配置文件

```
data/theme_configs.json         # 主题和章节配置
```

### 题目文件

```
data/questions.json             # 当前题库
data/questions_backup_*.json    # 自动备份
```

### 生成脚本

```
tools/generate_chapter_questions.py  # 批量生成脚本
```

---

## ⚠️ 注意事项

### 1. 定期备份

虽然脚本会自动备份，但建议定期手动备份重要数据：

```bash
cp data/questions.json data/questions_manual_backup.json
```

### 2. 题目质量

生成的题目需要人工审核：

- 使用后端的审核系统
- 检查题目的正确性
- 优化题目表述

### 3. 避免完全重新生成

如果需要清空重新生成：

```bash
# 1. 先备份
cp data/questions.json data/questions_full_backup.json

# 2. 清空（慎用！）
echo "[]" > data/questions.json

# 3. 重新生成
python tools/generate_chapter_questions.py --yes
```

---

## 🔄 同步到Flutter

生成后需要同步到Flutter项目：

```bash
# 从后端复制到前端
cp data/questions.json ../math_seckill/assets/data/problems.json

# Flutter应用需要热重启重新加载
# 在Flutter终端按 R 键
```

---

## 📞 故障排除

### 问题1：生成失败

```
⚠️ 生成失败: ...
```

**解决**：检查 SymPy 是否安装

### 问题2：题目重复

脚本已有防重复机制，但如果仍出现：

- 检查 questionId 是否唯一
- 使用随机数确保ID不重复

### 问题3：统计不准确

如果章节统计显示0题但实际有题目：

- 检查题目的 `topic` 和 `tags` 字段
- 确保包含章节关键词

---

## 🎯 最佳实践

1. **每次只生成缺少的题目** - 脚本自动处理
2. **定期查看备份文件** - 确保数据安全
3. **审核新生成的题目** - 使用后端审核系统
4. **同步到Flutter** - 生成后记得复制到前端

---

**生成的题目已自动保存并备份，可以放心使用！** ✅




