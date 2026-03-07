# WRHITW Persona-based Verification - Complete Test Guide

基于 Persona 的相关方认证系统测试流程

---

## 📋 系统架构

### 单一 Persona 体系

```
User (真实账号)
  └── Persona (匿名身份，最多 5 个)
       └── EventStakeholderVerification (事件级验证)
            ├── Event (特定事件)
            └── Stakeholder (相关方身份)
```

**设计理念**：
- ✅ 所有认证都通过 Persona 进行
- ✅ 验证绑定到特定事件
- ✅ 保护用户隐私（评论时显示 Persona，不暴露真实账号）
- ✅ 一个 Persona 可以在多个事件中获得验证

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
| 普通用户 | test@example.com | test123 | 创建 Persona、申请认证 |
| 管理员 | admin | wrhitw_admin_2026 | 审核认证申请 |

---

## 🧪 完整测试流程

### 步骤 1: 创建 Persona

**访问**: http://localhost:3002/personas

1. 登录
   - Email: `test@example.com`
   - Password: `test123`

2. 创建 Persona
   - 点击 "Create New Persona"
   - 输入名称：`Iranian Civilian`
   - 选择颜色：蓝色
   - 点击 "Create Persona"

3. 验证创建成功
   - 看到新创建的 Persona 卡片
   - 显示名称和颜色

**预期结果**:
- ✅ 登录成功
- ✅ Persona 创建成功
- ✅ 显示在 Persona 列表中

---

### 步骤 2: 申请事件级验证

**访问**: 在 Persona 卡片上点击 "Apply for Verification"

1. 选择 Persona（如果未预填）
   - 选择刚创建的 `Iranian Civilian`

2. 选择事件
   - 从下拉列表中选择一个事件
   - 如："Middle East Conflict Update"

3. 选择相关方
   - 从下拉列表中选择 `Iranian Civilians (geopolitics)`

4. 填写申请理由
   ```
   I am a civilian living in Iran and want to share my perspective 
   on the current situation. I can provide firsthand accounts of 
   how ordinary people are affected.
   ```

5. 提交申请
   - 点击 "Submit Application"

6. 查看申请状态
   - 系统显示 "Application submitted"
   - 跳转到 /personas 页面

**预期结果**:
- ✅ 能看到相关方列表（25+ 个选项）
- ✅ 能看到事件列表
- ✅ 申请提交成功
- ✅ 状态显示为 Pending

---

### 步骤 3: 管理员审核申请

**访问**: http://localhost:3002/admin/verifications

1. 登录管理员账号
   - Username: `admin`
   - Password: `wrhitw_admin_2026`

2. 查看申请列表
   - 应该能看到待审核的申请
   - 显示 Persona 名称、用户邮箱、事件、相关方

3. 审核申请
   - 点击 "Approve" 或 "Reject"
   - 填写审核备注（可选）：
     ```
     Approved - verified as Iranian civilian
     ```
   - 确认操作

4. 验证结果
   - 申请状态变为 **Approved** 或 **Rejected**
   - 审核备注显示在申请记录中

**预期结果**:
- ✅ 管理员登录成功
- ✅ 能看到所有待审核申请
- ✅ 能批准/拒绝申请
- ✅ 状态更新正确

---

### 步骤 4: 用户查看已认证状态

**访问**: http://localhost:3002/personas

1. 用户登录

2. 查看 Persona 卡片
   - 如果申请被批准，显示 "✅ Verified" 徽章

3. 查看验证详情
   - 点击 "View Verifications"
   - 看到该 Persona 的所有验证记录
   - 显示事件、相关方、状态、审核备注

**预期结果**:
- ✅ Persona 显示已验证徽章
- ✅ 能看到验证详情

---

## 🔧 API 测试

### 使用测试脚本

```bash
cd wrhitw/apps/api
./venv/bin/python test_persona_flow.py
```

### 手动 curl 测试

```bash
# 设置变量
API_URL="http://localhost:8080"
USER_AUTH=$(echo -n 'test@example.com:test123' | base64)
ADMIN_AUTH=$(echo -n 'admin:wrhitw_admin_2026' | base64)

# 1. 获取我的 Personas
curl "$API_URL/api/personas" \
  -H "Authorization: Basic $USER_AUTH"

# 2. 创建 Persona
curl -X POST "$API_URL/api/personas" \
  -H "Authorization: Basic $USER_AUTH" \
  -H "Content-Type: application/json" \
  -d '{
    "persona_name": "Test Civilian",
    "avatar_color": "blue"
  }'

# 3. 获取相关方列表（公开）
curl "$API_URL/api/stakeholders/list"

# 4. 获取事件列表
curl "$API_URL/api/events?status=active&page_size=10"

# 5. 为 Persona 申请验证
curl -X POST "$API_URL/api/personas/<PERSONA_ID>/verify" \
  -H "Authorization: Basic $USER_AUTH" \
  -H "Content-Type: application/json" \
  -d '{
    "event_id": "<EVENT_ID>",
    "stakeholder_id": "<STAKEHOLDER_ID>",
    "application_text": "I am a test user"
  }'

# 6. 查看 Persona 的验证记录
curl "$API_URL/api/personas/<PERSONA_ID>/verifications" \
  -H "Authorization: Basic $USER_AUTH"

# 7. 管理员查看所有待审核申请
curl "$API_URL/api/personas/admin/verifications?status_filter=pending" \
  -H "Authorization: Basic $ADMIN_AUTH"

# 8. 批准申请
curl -X POST "$API_URL/api/personas/admin/verifications/<VERIFICATION_ID>/approve" \
  -H "Authorization: Basic $ADMIN_AUTH" \
  -H "Content-Type: application/json" \
  -d '{"review_notes": "Approved for testing"}'
```

---

## ✅ 测试检查清单

### 基础功能
- [ ] 数据库迁移成功执行
- [ ] 测试用户创建成功
- [ ] 相关方数据创建成功（25+ 个）
- [ ] 后端 API 启动正常（端口 8080）
- [ ] 前端页面启动正常（端口 3002）

### Persona 管理
- [ ] 用户能成功登录
- [ ] 能创建 Persona（最多 5 个）
- [ ] 能查看 Persona 列表
- [ ] 能删除 Persona
- [ ] 达到上限时显示提示

### 验证申请
- [ ] 能为 Persona 申请验证
- [ ] 能选择事件
- [ ] 能选择相关方
- [ ] 申请状态显示正确（Pending）
- [ ] 能查看验证历史

### 管理员审核
- [ ] 管理员能成功登录
- [ ] 能查看所有待审核申请
- [ ] 能批准申请
- [ ] 能拒绝申请
- [ ] 能添加审核备注
- [ ] 状态更新正确

### 集成测试
- [ ] 用户申请后管理员能看到
- [ ] 管理员批准后 Persona 显示 Verified 徽章
- [ ] API 和前端数据一致

---

## 🎯 关键设计决策

### 为什么选择单一 Persona 体系？

| 特性 | 用户级认证 | Persona 级认证 |
|------|-----------|---------------|
| **隐私保护** | ❌ 关联真实账号 | ✅ 匿名身份 |
| **事件绑定** | ❌ 全局验证 | ✅ 精确到事件 |
| **徽章显示** | ❌ 不明确 | ✅ 评论时显示 |
| **灵活性** | ❌ 一个身份 | ✅ 多个身份 |

### Persona 使用场景

1. **地缘政治事件**
   - Persona: "Iranian Civilian"
   - 验证：在特定冲突事件中作为伊朗平民发声

2. **科技行业事件**
   - Persona: "Tech Worker"
   - 验证：在 AI 监管讨论中作为从业者发声

3. **多身份用户**
   - 一个用户可以有多个 Persona
   - 例如：同时是 "Iranian Civilian" 和 "Software Engineer"
   - 在不同事件中使用不同身份

---

## 🐛 已知问题

1. **密码未加密** - 测试环境使用明文密码，生产环境需要 bcrypt 加密
2. **评论系统未集成** - Persona 徽章暂未在评论中显示
3. **事件数据** - 需要手动创建测试事件

---

## 📝 故障排查

### 问题：登录后看不到 Persona 列表

**原因**: API 认证失败

**解决**:
1. 检查浏览器控制台是否有 401 错误
2. 确认后端 API 在 `http://localhost:8080` 运行
3. 检查用户是否存在：`./venv/bin/python create_test_user.py`

### 问题：申请验证时看不到相关方选项

**原因**: API 路径错误或数据未加载

**解决**:
1. 确认已运行 `seed_stakeholders.py`
2. 检查 `/api/stakeholders/list` 是否返回数据
3. 检查浏览器控制台网络请求

### 问题：管理员看不到申请

**原因**: 路由或认证问题

**解决**:
1. 确认使用管理员账号登录
2. 检查 API 路径：`/api/personas/admin/verifications`
3. 查看后端日志：`tail -f /tmp/wrhitw_api.log`

---

## 📚 相关文档

- [ADMIN.md](./ADMIN.md) - 管理员后台使用指南
- [API 文档](http://localhost:8080/docs) - FastAPI Swagger UI
- [TEST_VERIFICATION.md](./TEST_VERIFICATION.md) - 旧版测试文档（已废弃）

---

**Last Updated**: 2026-03-07  
**Status**: ✅ Ready for Testing  
**System**: Persona-based Verification (Single-tier)
