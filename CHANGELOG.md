# 更新日志

## v2.0.0 - 2025-08-29
### 🎉 重大更新 - 现代化UI重设计
- 全新左右分栏布局设计
  - 左侧：识别文本内容展示区
  - 右侧：图片缩略图列表
- 简化的文档导出功能
  - 一键导出所有识别文本
  - Markdown格式，包含完整统计信息
- 精简的侧边栏设计
  - 移除冗余配置选项
  - 保留核心功能和统计信息
- 优化的处理流程
  - 使用modern status组件显示进度
  - 清理了所有调试信息
  - 更简洁的用户交互

### 🚀 用户体验改进
- 支持多文件同时处理
- 智能文件选择器
- 实时处理状态显示
- 响应式布局设计

## v1.8.0 - 2025-08-29
### 修复
- 修复GLM-4V-Flash API调用格式问题
  - 添加system角色消息
  - 调整content数组顺序（text在前，image_url在后）
  - 更新API参数为官方推荐值（top_p=0.6, temperature=0.8）

### 优化
- 简化图片处理流程
  - 移除所有备用图床方案
  - 只保留GitHub图床作为唯一方案
  - 删除不必要的静态文件处理代码
  
### 代码清理
- 删除_save_file_to_static_and_get_url方法
- 删除_get_real_streamlit_media_url方法
- 删除_save_to_static_and_get_correct_url方法
- 删除_get_streamlit_file_url方法

## v1.7.0 - 2025-08-29
- 实现官方Streamlit静态文件服务
- 添加GitHub图床支持
- 改进错误处理和调试信息

## v1.6.0 - 2025-08-28
- 切换到GLM-4V-Flash纯视觉识别
- 移除PaddleOCR依赖
- 优化图片处理流程