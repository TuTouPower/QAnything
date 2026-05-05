# QAnything 开发计划

基于 GitHub Issues 和 PRs 汇总的待修复 Bug 和待实现功能。
按优先级排序，P0 最高。

---

## Bug 修复

### P0 - 严重 Bug

#### 1. [BUG] 上传文件名过长导致死循环 (#607) ✅ 已修复
- **修复**: `general_utils.py` `truncate_filename()` 加了安全退出条件，防止后缀+时间戳超长时死循环
- **提交**: 修改了 `qanything_kernel/utils/general_utils.py`

#### 2. [BUG] 上传文件接口内存泄漏 (#580) ✅ 已修复
- **修复**: `embedding_tokenizer` 和 `rerank_tokenizer` 改为懒加载单例，不再在模块导入时加载，避免每个进程重复占用 ~1.8GB
- **提交**: 修改了 `qanything_kernel/utils/general_utils.py`（对应 PR #663）

#### 3. [BUG] recognizer 内存溢出 (#652) ✅ 已修复
- **修复**: `recognizer.py` 的 `__call__` 方法改为按 batch 转换 numpy 数组，不再一次性加载所有图片
- **提交**: 修改了 `qanything_kernel/dependent_server/pdf_parser_server/pdf_to_markdown/core/vision/recognizer.py`

#### 4. [BUG] 非流式 ollama 调用 response 内容跑到 history (#629) ✅ 已修复
- **修复**: `local_doc_qa.py` 中 `[DONE]` 事件处理时，用 `acc_resp` 更新 `response["result"]`，确保非流式模式下返回实际答案
- **提交**: 修改了 `qanything_kernel/core/local_doc_qa.py`

#### 5. [BUG] 重复添加列 llm_setting / 删除不存在的列 model (#588) ✅ 已修复
- **修复**: 先查 `INFORMATION_SCHEMA.COLUMNS` 检查列是否存在，再决定是否 ALTER TABLE
- **提交**: 修改了 `qanything_kernel/connector/database/mysql/mysql_client.py`

### P1 - 一般 Bug

#### 6. [BUG] 后端调用没有参数控制检索文件数量 (#655) ✅ 已确认非 Bug
- **结论**: `top_k` 参数已在 handler 中实现，API 支持传入，只是文档未记录
- **建议**: 更新 API 文档补充 `top_k` 参数说明

#### 7. [BUG] get_tags 接口前端调用但后端缺失 (#621) ✅ 已修复（Stub）
- **修复**: 添加了 `get_tags` 和 `update_tags` stub 接口，返回空标签列表防止前端报错
- **提交**: 修改了 `handler.py` 和 `sanic_api.py`

#### 8. [BUG] 模型回答出现乱码/截断 (#557) ⏸️ 待验证
- **原因**: 难以在无环境的情况下复现，可能是特定 LLM 模型 streaming 分块导致的 UTF-8 截断
- **状态**: 标记为待验证，需在实际环境中测试

#### 9. [BUG] 相同词向量查询结果为 0，不同查询得分反而高 (#594) ⏸️ 待验证
- **原因**: 可能是向量模型特性或嵌入维度不匹配（如 #560 的 dim 不匹配问题），需实际环境验证

#### 10. [BUG] HTML 文件不能直接上传 (#615) ✅ 已修复
- **修复**: 在 `split_file_to_docs` 中添加 `.html`/`.htm` 文件类型支持，使用 `UnstructuredHTMLLoader` 解析
- **提交**: 修改了 `qanything_kernel/core/retriever/general_document.py`

### P2 - 待评估的 PR（外部贡献者提交，未合并）

#### 11. [PR #645] Reranker Chunk Overlap 修复 ✅ 已应用
- **修复**: `process_group` 改为每个 cand_doc 独立收集 id_set，超出 CHUNK_SIZE 时立即保存，避免组间重叠
- **提交**: 修改了 `qanything_kernel/connector/database/milvus/milvus_client.py`

#### 12. [PR #644] LOCAL_RERANK_MAX_LENGTH -> LOCAL_EMBED_MAX_LENGTH ✅ 已修复
- **修复**: `embedding_onnx_backend.py` 中错误使用了 rerank 的 max_length 改为 embed 的
- **提交**: 修改了 `qanything_kernel/dependent_server/embedding_server/embedding_onnx_backend.py`

#### 13. [PR #663] 避免全局变量重复创建减少内存占用 ✅ 已修复（合并到 #2）
- **修复**: 同 #2 的懒加载方案

#### 14. [PR #667] 拼写错误修复 ✅ 已修复
- **修复**: `seperate` → `separate`，`occured` → `occurred`
- **提交**: 修改了 `milvus_client.py` 和 `utils_table_recover.py`

---

## 功能增强

### P1 - 高价值功能

#### 15. rewrite 默认上下文长度从 4096 提高 (#639) ✅ 已实现
- **修复**: `api_context_length` 默认值从 4096 提高到 32768
- **提交**: 修改了 `qanything_kernel/qanything_server/handler.py`

#### 16. PDF 解析添加页码信息到 metadata (#585) ✅ 已实现
- **修复**: `convert2markdown.py` 在页码变化时插入 `## 当前页数:N` 标记；`markdown_parser.py` 解析标记并设置真实页码；`parent_retriever.py` 保留 `page_id` metadata
- **提交**: 修改了 `convert2markdown.py`、`markdown_parser.py`、`parent_retriever.py`

#### 17. Excel 问答返回 sheet 名称 (#587) ✅ 已实现
- **修复**: `inject_metadata` 中将 `title_lst` 的第一个元素（即 sheet 名/章节标题）加入 `headers` 字典，传递到 API 响应和 LLM prompt
- **提交**: 修改了 `qanything_kernel/core/retriever/general_document.py`

### P2 - 有价值功能

#### 18. 问答接口支持历史记录 (#631) ✅ 已确认非 Bug
- **结论**: 代码中 history 已正确传递给 LLM（通过 `generatorAnswer` 构建 messages），问答结果不参考上下文属于模型行为问题
- **建议**: 检查所使用的 LLM 模型是否支持多轮对话

#### 19. 单文本向量化 API (#547) ⏸️ 待评估
- **方案**: 新增文本级别的 CRUD 接口

#### 20. 第三方组件配置通过环境变量暴露 (#619) ⏸️ 待评估
- **方案**: 关键配置参数提取到环境变量

---

## 已排除（不纳入计划）

- Docker 部署相关（#664, #665, #605, #576, #567, #564 等）— WSL 禁用 Docker
- 纯使用/Q&A 问题（#658, #643, #641, #640, #632, #608 等）
- 商务/合作类（#669, #668, #659, #544）
- 微信群满（#662）
- 需求过于宏大/模糊（#601 用户管理、#609 Confluence 集成、#559 代码仓库、#565 模型微调）
