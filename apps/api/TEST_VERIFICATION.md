# WRHITW Stakeholder Verification - Complete Test Guide

完整的相关方认证系统测试流程

---

## 📋 前置准备

### 1. 执行数据库迁移

```bash
cd wrhitw/apps/api

# 执行相关方系统迁移
./venv/bin/python migrate_add_stakeholders.py

# 执行 Persona 系统迁移
./venv/bin/python migrate_add_personas.py
```

### 2. 创建测试数据

```bash
# 创建测试用户
./venv/bin/python create_test_user.py

# 创建相关方种子数据
./venv/bin/python seed_stakeholders.py
```

### 3. 启动服务

```bash
# Terminal 1: 启动后端 API (端口 8080)
cd wrhitw/apps/api
./venv/bin/uvicorn app.main:app --reload --port 8080

# Terminal 2: 启动前端 (端口 3001)
cd wrhitw/apps/web
npm run dev
```

---

## 🔑 测试账号

| 角色 | 账号 | 密码 | 用途 |
|------|------|------|------|
| 普通用户 | test@example.com | test123 | 申请相关方认证 |
| 管理员 | admin | wrhitw_admin_2026 | 审核认证申请 |

---

## 🧪 测试场景

### 场景 1: 用户申请认证

**测试步骤**：

1. 访问用户认证页面
   ```
   http://localhost:3001/verify
   ```

2. 登录
   - Email: `test@example.com`
   - Password: `test123`
   - 点击 "Sign In"

3. 提交申请
   - 切换到 "Apply for Verification" 标签
   - 选择一个相关方（如 "Iranian Civilians"）
   - 填写申请理由（英文）：
     ```
     I am a civilian living in Iran and want to share my perspective 
     on the current situation.
     ```
   - Proof Type: 选择 "Self Declaration"
   - 点击 "Submit Application"

4. 查看申请状态
   - 切换到 "My Applications" 标签
   - 应该看到刚提交的申请，状态为 **Pending**

**预期结果**：
- ✅ 登录成功
- ✅ 能看到相关方列表（20+ 个选项）
- ✅ 申请提交成功
- ✅ 申请状态显示为 Pending

---

### 场景 2: 管理员审核申请

**测试步骤**：

1. 访问管理后台审核页面
   ```
   http://localhost:3001/admin/verifications
   ```

2. 登录管理员账号
   - Username: `admin`
   - Password: `wrhitw_admin_2026`

3. 查看申请列表
   - 应该能看到待审核的申请（状态过滤：Pending）
   - 看到申请人邮箱、申请的相关方、申请理由

4. 审核申请
   - 点击 "Approve" 或 "Reject"
   - 填写审核备注（可选）：
     ```
     Approved for testing - verified user
     ```
   - 确认操作

5. 验证结果
   - 申请状态变为 **Approved** 或 **Rejected**
   - 审核备注显示在申请记录中

**预期结果**：
- ✅ 管理员登录成功
- ✅ 能看到所有待审核申请
- ✅ 能批准/拒绝申请
- ✅ 状态更新正确

---

### 场景 3: 用户查看已认证角色

**测试步骤**：

1. 用户再次登录 `/verify`

2. 切换到 "My Applications" 标签

3. 如果申请被批准
   - 状态显示为 **Approved**
   - 显示管理员备注

4. （未来功能）在事件详情页
   - 评论时会显示已认证的相关方徽章

**预期结果**：
- ✅ 能看到批准的申请
- ✅ 状态正确显示

---

## 🔧 API 测试（可选）

### 使用 curl 测试 API

```bash
# 设置变量
API_URL="http://localhost:8080"
USER_AUTH=$(echo -n 'test@example.com:test123' | base64)
ADMIN_AUTH=$(echo -n 'admin:wrhitw_admin_2026' | base64)

# 1. 获取相关方列表（管理员）
curl "$API_URL/api/stakeholders/admin/stakeholders" \
  -H "Authorization: Basic $ADMIN_AUTH"

# 2. 用户申请认证
curl -X POST "$API_URL/api/stakeholders/apply" \
  -H "Authorization: Basic $USER_AUTH" \
  -H "Content-Type: application/json" \
  -d '{
    "stakeholder_id": "<STAKEHOLDER_ID>",
    "application_text": "I am a test user from Iran",
    "proof_type": "self_declaration"
  }'

# 3. 查看我的申请
curl "$API_URL/api/stakeholders/my-applications" \
  -H "Authorization: Basic $USER_AUTH"

# 4. 管理员查看所有申请
curl "$API_URL/api/stakeholders/admin/applications" \
  -H "Authorization: Basic $ADMIN_AUTH"

# 5. 批准申请
curl -X POST "$API_URL/api/stakeholders/admin/applications/<APPLICATION_ID>/approve" \
  -H "Authorization: Basic $ADMIN_AUTH" \
  -H "Content-Type: application/json" \
  -d '{"review_notes": "Approved for testing"}'

# 6. 查看用户已认证角色
curl "$API_URL/api/stakeholders/my-roles" \
  -H "Authorization: Basic $USER_AUTH"
```

---

## ✅ 测试检查清单

### 基础功能
- [ ] 数据库迁移成功执行
- [ ] 测试用户创建成功
- [ ] 相关方数据创建成功（20+ 个）
- [ ] 后端 API 启动正常（端口 8080）
- [ ] 前端页面启动正常（端口 3001）

### 用户申请流程
- [ ] 用户能成功登录
- [ ] 能看到相关方列表
- [ ] 能提交申请
- [ ] 申请状态显示正确（Pending）
- [ ] 能查看自己的申请历史

### 管理员审核流程
- [ ] 管理员能成功登录
- [ ] 能查看所有待审核申请
- [ ] 能批准申请
- [ ] 能拒绝申请
- [ ] 能添加审核备注
- [ ] 状态更新正确

### 集成测试
- [ ] 用户申请后管理员能看到
- [ ] 管理员批准后用户能看到状态变化
- [ ] API 和前端数据一致

---

## 🐛 已知问题

1. **密码未加密** - 测试环境使用明文密码，生产环境需要 bcrypt 加密
2. **评论系统未集成** - 相关方徽章暂未在评论中显示
3. **事件级验证未完成** - 目前是全球验证，事件级验证待开发

---

## 📝 故障排查

### 问题：登录后看不到相关方列表

**原因**：API 路径错误或认证失败

**解决**：
1. 检查浏览器控制台是否有 401/404 错误
2. 确认后端 API 在 `http://localhost:8080` 运行
3. 检查前端 `.env.local` 中的 `NEXT_PUBLIC_API_URL`

### 问题：申请提交失败

**原因**：相关方 ID 不存在或认证失败

**解决**：
1. 确认已运行 `seed_stakeholders.py`
2. 检查后端日志：`tail -f /tmp/wrhitw_api.log`
3. 用 curl 测试 API 确认后端正常

### 问题：管理员看不到申请

**原因**：API 路径不匹配

**解决**：
1. 确认前端调用 `/api/stakeholders/admin/applications`
2. 确认后端路由已注册
3. 检查管理员认证是否正确

---

## 📚 相关文档

- [ADMIN.md](./ADMIN.md) - 管理员后台使用指南
- [CRON_SETUP.md](./CRON_SETUP.md) - 定时新闻抓取配置
- [API 文档](http://localhost:8080/docs) - FastAPI Swagger UI

---

**Last Updated**: 2026-03-07  
**Status**: ✅ Ready for Testing  
**Tester**: WRHITW Team
