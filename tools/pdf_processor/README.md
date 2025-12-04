# PDF真题录入工具

自动化处理PDF真题，提取题目、识别文本、辅助人工校验。

## 🚀 快速开始

### 1. 安装依赖

#### macOS
```bash
# 安装Tesseract OCR
brew install tesseract tesseract-lang

# 安装Python依赖
pip install -r requirements.txt
```

#### Ubuntu/Debian
```bash
# 安装Tesseract
sudo apt-get install tesseract-ocr tesseract-ocr-chi-sim

# 安装Python依赖
pip install -r requirements.txt
```

### 2. 使用流程

#### 步骤1：提取PDF页面
```bash
python pdf_extractor.py your_exam.pdf
```

输出：
- `temp/pdf_images/page_1.png`
- `temp/pdf_images/page_2.png`
- ...
- `temp/pdf_images/metadata.json`

#### 步骤2：OCR识别
```bash
python ocr_engine.py temp/pdf_images/page_1.png
```

输出：
- `temp/pdf_images/page_1.json` （包含OCR结果和坐标）

#### 步骤3：题目切分
```bash
python question_splitter.py temp/pdf_images/page_1.json
```

输出：
- `temp/pdf_images/questions_split.json` （切分后的题目列表）

---

## 📁 输出数据格式

### OCR结果
```json
{
  "imagePath": "temp/pdf_images/page_1.png",
  "ocrResult": {
    "fullText": "1. 计算：sin(30°) = ?\nA. 0.5\nB. 0.707\n...",
    "words": [
      {
        "text": "1.",
        "confidence": 95,
        "left": 100,
        "top": 200,
        "width": 30,
        "height": 20
      },
      ...
    ]
  },
  "formulaRegions": []
}
```

### 切分后的题目
```json
{
  "questionCount": 5,
  "questions": [
    {
      "questionNumber": 1,
      "rawText": "1. 计算：sin(30°) = ?",
      "options": [
        {
          "letter": "A",
          "content": "0.5",
          "hasFormula": false
        },
        {
          "letter": "B",
          "content": "0.707",
          "hasFormula": false
        }
      ],
      "hasFormula": true,
      "bounds": {
        "x": 100,
        "y": 200,
        "w": 500,
        "h": 200
      }
    }
  ]
}
```

---

## 🎯 Web校验工作台集成

切分后的数据会被Web管理后台使用：

### 工作流
```
1. 上传PDF → 后端预处理
2. 返回切分的题目列表
3. Web界面逐题校验
4. 左：显示原图，右：编辑表单
5. 修正OCR错误，添加LaTeX公式
6. 保存到题库
```

### API接口（待实现）
```
POST /api/pdf/upload        # 上传PDF
POST /api/pdf/process       # 触发预处理
GET  /api/pdf/questions     # 获取切分的题目
POST /api/pdf/verify        # 校验并保存题目
```

---

## 🔧 配置选项

### OCR语言
修改 `ocr_engine.py` 中的 `lang` 参数：
- `chi_sim` - 简体中文
- `eng` - 英文
- `chi_sim+eng` - 中英混合（推荐）

### 图像分辨率
修改 `pdf_extractor.py` 中的 `dpi` 参数：
- 150 DPI - 快速预览
- 300 DPI - 标准质量（推荐）
- 600 DPI - 高质量（识别困难文档）

---

## 📊 性能预期

### 处理速度
- PDF提取：0.5秒/页
- OCR识别：2-5秒/页
- 题目切分：0.1秒/页

### 准确率
- 纯文本：90-95%
- 数学公式：30-50%（需人工校验）
- 图表：0%（需人工处理）

---

## ⚠️ 已知限制

### OCR局限
- 数学公式识别率低（建议使用Mathpix）
- 复杂排版可能识别错误
- 手写体识别困难

### 切分算法
- 当前版本为基础算法
- 依赖题号格式规范
- 复杂布局需要优化

---

## 💡 改进建议

### 短期
1. 优化题目切分算法（基于坐标聚类）
2. 添加更多题号模式
3. 改进公式区域检测

### 中期
1. 集成Mathpix API（公式识别）
2. 使用深度学习模型（题目检测）
3. 支持图表提取

### 长期
1. 训练专用的数学试卷识别模型
2. 端到端的自动化流程
3. 多人协作校验系统

---

## 🧪 测试建议

### 测试文件
准备1-2页简单的PDF试卷：
- 题目格式规范
- 包含选择题
- 有少量数学公式

### 测试流程
1. 运行提取脚本
2. 检查图片质量
3. 运行OCR
4. 查看识别准确率
5. 运行切分
6. 验证题目结构

根据结果调整参数和算法。

---

## 📞 故障排查

### Tesseract未找到
```bash
# macOS
brew install tesseract tesseract-lang

# 查看版本
tesseract --version
```

### 识别语言包缺失
```bash
# macOS安装中文语言包
brew install tesseract-lang
```

### OCR质量差
- 提高PDF转图片的DPI
- 调整图像预处理参数
- 检查原始PDF清晰度

---

## 📚 相关资源

- [PyMuPDF文档](https://pymupdf.readthedocs.io/)
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract)
- [Mathpix API](https://mathpix.com/)

---

**从PDF到结构化题目，自动化您的真题录入！** 🚀

