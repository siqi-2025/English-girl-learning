# 📚 English Learning Assistant

基于AI增强OCR的英语学习助手 - English Learning Assistant with AI-Enhanced OCR

## 🎯 项目简介

这是一个创新的英语学习辅助工具，专门用于处理七年级英语教材。通过结合最新的AI增强OCR技术（PaddleOCR 3.1）和智普AI（GLM-4.5-flash），实现高精度的教材内容识别、智能分类和自动习题生成。

## ✨ 核心功能

- 🔍 **AI增强OCR识别**: 使用PaddleOCR 3.1 + 智普AI双重增强，识别准确率提升30%+
- 📝 **智能内容分类**: 自动识别课文、词汇、语法点并分类整理
- 📚 **Markdown文档生成**: 按单元生成结构化的学习文档
- 🎓 **智能习题生成**: 自动生成中英互译、填空、默写等多种题型
- ☁️ **云端部署**: 基于Streamlit Cloud的Web应用，随时随地访问

## 🛠️ 技术栈

- **前端框架**: Streamlit 1.28+
- **OCR引擎**: PaddleOCR 3.1 (AI增强版)
- **AI服务**: 智普AI GLM-4.5-flash
- **部署平台**: Streamlit Cloud
- **开发语言**: Python 3.8+

## 📁 项目结构

```
English-girl-learning/
├── streamlit_app.py          # 应用入口
├── requirements.txt          # 依赖配置
├── src/                      # 源代码
│   ├── ui/                  # Streamlit界面
│   ├── core/                # 核心业务逻辑
│   └── utils/               # 工具函数
├── config/                   # 配置文件
├── docs/                     # 项目文档
└── tests/                    # 测试用例
```

## 🚀 快速开始

### 本地开发

1. 克隆项目
```bash
git clone https://github.com/siqi-2025/English-girl-learning.git
cd English-girl-learning
```

2. 创建虚拟环境
```bash
python -m venv english-learning-env
source english-learning-env/bin/activate  # Windows: english-learning-env\Scripts\activate
```

3. 安装依赖
```bash
pip install -r requirements.txt
```

4. 配置环境变量
```bash
export ENGLISH_LEARNING_ZHIPU_API_KEY="your-api-key"
```

5. 运行应用
```bash
streamlit run streamlit_app.py
```

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