# PDF真题录入系统 - 快速开始

## 🎯 系统概述

**解决问题：** 从PDF真题快速录入到题库，提升效率10倍

**核心流程：**
```
PDF文件 → Python预处理(80%自动) → Web人工校验(20%难点) → 结构化题库
```

---

## 📦 环境准备

### 步骤1：安装Tesseract OCR

#### macOS
```bash
brew install tesseract tesseract-lang
```

#### Ubuntu/Debian
```bash
sudo apt-get install tesseract-ocr tesseract-ocr-chi-sim
```

### 步骤2：安装Python依赖
```bash
cd tools/pdf_processor
./setup.sh
```

或手动安装：
```bash
pip3 install PyMuPDF pdf2image Pillow pytesseract opencv-python numpy
```

---

## 🚀 使用流程

### 方式A：命令行处理（测试用）

#### 1. 提取PDF页面
```bash
python3 pdf_extractor.py /path/to/exam.pdf
```

输出：
- `temp/pdf_images/page_1.png`
- `temp/pdf_images/page_2.png`
- ...
- `temp/pdf_images/metadata.json`

#### 2. OCR识别
```bash
python3 ocr_engine.py temp/pdf_images/page_1.png
```

输出：
- `temp/pdf_images/page_1.json` （含OCR结果和坐标）

#### 3. 题目切分
```bash
python3 question_splitter.py temp/pdf_images/page_1.json
```

输出：
- `temp/pdf_images/questions_split.json` （切分后的题目）

---

### 方式B：Web界面处理（生产用）⭐推荐

#### 1. 启动Web管理后台
```bash
cd math_seckill_admin
npm run dev
```

访问：http://localhost:5173

#### 2. 进入PDF导入页面
```
侧边栏 → 📄 PDF导入
```

#### 3. 上传PDF
- 拖拽PDF文件到上传区
- 自动开始处理
- 等待进度完成

#### 4. 开始校验
- 点击"开始校验题目"
- 进入左右对比界面

#### 5. 逐题校验
```
左侧：原始PDF图片（可缩放）
右侧：编辑表单（OCR已预填）

操作：
1. 检查题目文本是否正确
2. 修正OCR错误
3. 添加LaTeX公式
4. 选择知识点标签
5. 点击"保存此题"

重复：下一题...
```

---

## 📐 LaTeX公式处理

### 识别公式区域
系统会自动标记可能包含公式的区域（`hasFormula: true`）

### 输入LaTeX
在"公式"输入框中：
```latex
\sin(30^\circ) = \frac{1}{2}
```

### 实时预览
输入后立即看到渲染效果

### 快捷按钮
- 点击"分数" → 插入 `\frac{}{}`
- 点击"根号" → 插入 `\sqrt{}`
- 点击"sin" → 插入 `\sin`

---

## 💡 效率技巧

### 1. 批量处理
- 一次上传整个PDF
- 所有页面自动提取
- 逐题校验即可

### 2. 快捷键（建议）
- Tab: 下一个输入框
- Ctrl+S: 保存当前题
- Ctrl+→: 下一题
- Ctrl+←: 上一题

### 3. 知识点模板
- 预设常用知识点标签
- 快速多选
- 一键应用到多题

---

## 📊 预期效率

### 处理速度
```
传统手工录入：
  - 打字：5-8分钟/题
  - 公式：2-3分钟/题
  - 总计：10-15分钟/题

使用本系统：
  - OCR预填：自动（80%文本）
  - 校验修正：1-2分钟/题
  - LaTeX公式：1分钟/题
  - 总计：2-3分钟/题

效率提升：5-7倍！
```

### 准确率
```
文本：OCR 90-95% → 人工校验 100%
公式：人工LaTeX输入 100%
选项：OCR 85-90% → 人工校验 100%
```

---

## 🎯 数据流转

```
1. PDF文件
   ↓ (pdf_extractor.py)
2. 图片文件 (page_1.png, ...)
   ↓ (ocr_engine.py)
3. OCR结果 (page_1.json)
   ↓ (question_splitter.py)
4. 切分题目 (questions_split.json)
   ↓ (Web界面校验)
5. 结构化题目
   ↓ (保存API)
6. 题库数据库 (questions.json)
```

---

## 🧪 测试建议

### 准备测试PDF
- 1-2页
- 5-10道题
- 格式规范（题号清晰）
- 包含简单公式

### 测试步骤
1. 运行 `pdf_extractor.py`
2. 检查图片质量
3. 运行 `ocr_engine.py`
4. 查看识别文本
5. 运行 `question_splitter.py`
6. 验证切分结果

### 评估标准
- 题目切分准确率 > 80%
- 文本识别准确率 > 85%
- 选项识别准确率 > 80%

达标后可批量处理！

---

## ⚠️ 注意事项

### PDF质量要求
- ✅ 文字版PDF（最佳）
- ⚠️ 扫描版PDF（需高质量）
- ❌ 手写试卷（识别率低）

### 公式处理
- OCR无法准确识别数学公式
- 必须人工转换为LaTeX
- 建议使用Mathpix辅助

### 图表处理
- 系统会保存图表区域
- 需要人工裁剪上传
- 或在题目中引用图片URL

---

## 📞 故障排查

### Tesseract未找到
```bash
# 检查是否安装
tesseract --version

# macOS重新安装
brew reinstall tesseract
```

### 识别率低
1. 提高PDF提取分辨率（DPI: 300 → 600）
2. 检查PDF原始质量
3. 调整OCR预处理参数

### 切分错误
1. 检查题号格式是否规范
2. 查看OCR识别的原始文本
3. 手动调整切分参数

---

## 🎊 成功案例

**处理100道真题：**
```
PDF页数：20页
总题目：100道
处理时间：
  - 自动预处理：5分钟
  - 人工校验：200分钟（2分钟/题）
  - 总计：205分钟

传统手工录入需要：1000-1500分钟
效率提升：5-7倍！
```

---

**开始您的高效真题录入之旅！** 🚀

