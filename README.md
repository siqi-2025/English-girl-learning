# 📚 英语学习助手 - GLM-4V-Flash视觉识别系统

基于 **智普AI GLM-4V-Flash** 的英语教材智能视觉识别与文档生成系统

## 🎯 项目简介

这是一个创新的英语学习辅助工具，专门用于处理七年级英语教材。使用智普AI GLM-4V-Flash的先进视觉识别能力，直接从图片中识别英语文字，结合GLM-4-Flash进行智能分析，实现高精度的教材内容识别、智能分类和自动习题生成，提供完整的Web界面和云端部署方案。

## ✨ 核心特性

- 👁️ **GLM-4V-Flash视觉识别**：直接识别图片中的英语文字，准确率高达95%+
- 🤖 **智能内容分析**：自动分析课文类型、提取词汇、识别语法点
- 📝 **智能文档生成**：自动生成课文文档、词汇表、练习题
- 🎯 **词汇分级系统**：智能区分小学/初中词汇难度等级
- 📊 **批量处理**：支持文件夹批量处理，实时进度显示
- 🌐 **Web界面**：基于Streamlit的现代化Web界面
- ☁️ **云端部署**：支持Streamlit Cloud一键部署，无需复杂环境配置

## 🛠️ 技术栈

- **前端框架**: Streamlit 1.28+
- **视觉识别**: 智普AI GLM-4V-Flash
- **AI分析**: 智普AI GLM-4-Flash  
- **SDK**: ZhipuAI 2.0+
- **部署平台**: Streamlit Cloud
- **开发语言**: Python 3.11+

## 📁 项目结构

```
English-girl-learning/
├── src/                          # 源代码目录
│   ├── core/                     # 核心业务逻辑
│   │   ├── ocr_processor.py      # GLM-4V-Flash视觉识别处理器
│   │   ├── ai_analyzer.py        # 智普AI分析器（GLM-4V-Flash + GLM-4-Flash）
│   │   └── document_generator.py # 文档生成器
│   ├── ui/                       # 用户界面
│   │   └── main_interface.py     # Streamlit主界面
│   └── utils/                    # 工具模块
│       └── config.py             # 配置管理
├── .streamlit/                   # Streamlit配置
│   └── config.toml              # 应用配置
├── output/                       # 生成文档输出目录
├── streamlit_app.py             # 应用入口
├── requirements.txt             # 项目依赖
└── README.md                    # 项目文档
```

## 🚀 快速开始

### 1. 环境准备

```bash
# 克隆项目
git clone https://github.com/siqi-2025/English-girl-learning.git
cd English-girl-learning

# 创建虚拟环境
python -m venv english-learning-env
source english-learning-env/bin/activate  # Linux/Mac
# 或
english-learning-env\Scripts\activate     # Windows

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置API密钥

```bash
# 设置环境变量
export ENGLISH_LEARNING_ZHIPU_API_KEY="your_zhipu_api_key_here"

# Windows用户使用：
set ENGLISH_LEARNING_ZHIPU_API_KEY=your_zhipu_api_key_here
```

### 3. 运行应用

```bash
# 启动Streamlit应用
streamlit run streamlit_app.py
```

访问 `http://localhost:8501` 即可使用！

### 云端访问

应用部署后可通过以下URL访问：
- https://english-learning-assistant.streamlit.app (待部署)

## 📖 文档导航

项目包含完整的技术文档：

1. [项目需求文档](./01-项目需求文档-v1.0.md)
2. [系统架构设计](./02-系统架构设计-v1.0.md)  
3. [技术栈选型文档](./03-技术栈选型文档-v1.1.md)
4. [部署方案定型文档](./04-部署方案定型文档-v1.0.md)
5. [Streamlit云端部署指南](./05-Streamlit云端部署指南-v1.1.md)
6. [项目搭建开发指南](./06-项目搭建开发指南-v1.1.md)

## 🤝 贡献指南

欢迎贡献代码和建议！请查看 [CONTRIBUTING.md](./CONTRIBUTING.md) 了解详情。

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](./LICENSE) 文件了解详情。

## 👥 团队

- 开发者: siqi-2025
- 联系邮箱: siqi@1mlab.net

## 🙏 致谢

- PaddleOCR团队提供的优秀OCR引擎
- 智普AI提供的强大语言模型
- Streamlit团队提供的便捷部署平台

---

**项目版本**: v1.1 | **最后更新**: 2024-08-28