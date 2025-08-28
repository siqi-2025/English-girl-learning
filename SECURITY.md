# 🔐 安全说明 - Security Guidelines

## 敏感信息保护

本项目不包含任何敏感信息，包括但不限于：
- API密钥和令牌
- 用户账户信息
- 密码或认证信息
- 个人身份信息

## 环境变量配置

所有敏感配置通过环境变量提供：

```bash
# 必需的环境变量
export ENGLISH_LEARNING_ZHIPU_API_KEY="your-api-key-here"

# 可选配置
export ENGLISH_LEARNING_DEBUG=false
export ENGLISH_LEARNING_LOG_LEVEL=INFO
```

## Streamlit Cloud部署配置

在Streamlit Cloud的Secrets配置中添加：

```toml
[api]
ENGLISH_LEARNING_ZHIPU_API_KEY = "your-api-key-here"

[english_learning_settings]
MAX_UPLOAD_SIZE = 50
BATCH_SIZE = 5
PROJECT_NAME = "English Learning Assistant"
```

## 本地开发安全

1. 使用 `.streamlit/secrets.toml` 存储本地密钥（已在.gitignore中排除）
2. 不要将敏感信息硬编码到源代码中
3. 定期更新API密钥
4. 不要在公开场合分享配置信息

## 报告安全问题

如发现安全相关问题，请通过以下方式报告：
- 创建私有Issue
- 联系项目维护者

**注意**: 请勿在公开Issue中包含敏感信息。