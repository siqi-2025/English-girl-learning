# 更新日志

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