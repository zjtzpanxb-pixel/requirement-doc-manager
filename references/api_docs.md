# 飞书 API 文档摘要

## 认证

```
认证方式：OAuth 2.0
Token 获取：POST https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal
```

## 文档创建 API

```
POST https://open.feishu.cn/open-apis/docx/v1/documents
Body: {
  "title": "文档标题",
  "folder_token": "文件夹 token"
}
```

## 文档内容更新

```
PUT https://open.feishu.cn/open-apis/docx/v1/documents/{document_id}/content
Body: {
  "content": "Markdown 内容"
}
```

## 配置步骤

1. 创建飞书应用
2. 获取 App ID 和 App Secret
3. 配置权限（文档读写）
4. 设置环境变量：
   ```bash
   export FEISHU_APP_ID=cli_xxx
   export FEISHU_APP_SECRET=xxx
   ```

## 错误处理

| 错误码 | 说明 | 处理 |
|--------|------|------|
| 0 | 成功 | - |
| 99991663 | 没有权限 | 检查应用权限 |
| 99991661 | 应用未发布 | 发布应用 |
