# Skills 弹窗界面设计文档

**日期**: 2026-02-01  
**主题**: Skills 命令 TUI 弹窗界面  
**状态**: 已确认，待实施

---

## 1. 功能概述

为 DeepAgents CLI 增加一个通过 `/skills` 命令触发的模态弹窗界面，让用户可以直观地浏览和选择已安装的 skills。选中后自动在输入框插入 `/use-skill [skill-name]` 命令。

---

## 2. 触发机制

- **触发命令**: 用户在 `ChatInput` 中输入 `/skills` 并提交
- **拦截方式**: `ChatInput` 组件检测到 `/skills` 命令后，不将其作为普通消息发送，而是发送 `ShowSkillsModal` 事件给主 App
- **事件类型**: 使用 Textual 的 `Message` 类定义自定义事件

---

## 3. 架构设计

### 3.1 组件层级

```
DeepAgentsApp (主应用)
└── SkillsModal (ModalScreen)
    ├── Header (Static) - 标题栏
    ├── SkillGrid (Grid/DataTable) - 技能卡片网格
    │   └── SkillCard (自定义 Widget) × N
    └── Footer (Static) - 操作提示
```

### 3.2 核心组件

| 组件名 | 类型 | 职责 |
|--------|------|------|
| `SkillsModal` | `ModalScreen` | 模态弹窗容器，管理生命周期 |
| `SkillCard` | `Widget` | 单个技能卡片展示 |
| `ShowSkillsModal` | `Message` | 从 ChatInput 到 App 的触发消息 |
| `SkillsSelected` | `Message` | 从 SkillsModal 到 App 的结果消息 |

---

## 4. 数据模型

### 4.1 技能卡片数据

```python
@dataclass
class SkillCardData:
    name: str                    # 技能名称
    description: str             # 截断的描述（前 40 字符 + "..."）
    full_description: str        # 完整描述
    source: str                  # "user" 或 "project"
    path: Path                   # SKILL.md 文件路径
```

### 4.2 数据来源

复用现有的 `list_skills()` 函数从以下位置加载：
1. User skills: `~/.deepagents/{agent}/skills/`
2. Project skills: `{project_root}/.deepagents/skills/`

**优先级**: Project skills 覆盖 User skills（同名时）

---

## 5. UI 布局设计

### 5.1 弹窗尺寸

- **宽度**: 屏幕宽度的 80%（最小 60 字符，最大 120 字符）
- **高度**: 屏幕高度的 70%（最小 15 行，最大 30 行）
- **位置**: 居中显示
- **背景**: 半透明遮罩（dim 效果）

### 5.2 内部布局

```
┌─────────────────────────────────────────────────┐
│  Select a Skill to Use          [agent] (5)    │  ← Header
├─────────────────────────────────────────────────┤
│ ┌─────────────┐  ┌─────────────┐               │
│ │ web-search  │  │ code-review │               │
│ │ [User]      │  │ [Project]   │               │  ← SkillGrid
│ │ Search web..│  │ Review code │               │
│ └─────────────┘  └─────────────┘               │
│ ┌─────────────┐                                │
│ │ data-analysis│                               │
│ │ [User]      │                                │
│ │ Analyze dat…│                                │
│ └─────────────┘                                │
├─────────────────────────────────────────────────┤
│  ↑↓←→ Navigate | Enter Select | Esc Cancel     │  ← Footer
└─────────────────────────────────────────────────┘
```

### 5.3 视觉样式

| 元素 | 样式 |
|------|------|
| 弹窗边框 | 主色 (`#10b981`) |
| 标题 | 加粗白色 |
| Skill 名称 | 加粗主色 |
| 来源标签 - User | 青色 (`cyan`) |
| 来源标签 - Project | 绿色 (`green`) |
| 描述 | 灰色 (`dim`) |
| 选中卡片 | 高亮边框 |
| Footer | 灰色提示文字 |

---

## 6. 交互设计

### 6.1 键盘导航

| 按键 | 动作 |
|------|------|
| `↑` / `↓` / `←` / `→` | 在卡片网格中导航 |
| `Enter` | 选中当前 skill |
| `Esc` | 取消并关闭弹窗 |
| `Ctrl+C` | 取消并关闭弹窗 |

**导航规则**:
- 网格布局：支持行列循环（到边界回绕）
- 空网格：不响应方向键，仅响应 Esc

### 6.2 选中后处理流程

1. 用户按 `Enter` 选中 skill
2. `SkillsModal` 发送 `SkillsSelected(skill_name)` 消息
3. `DeepAgentsApp` 接收到消息：
   - 调用 `self.pop_screen()` 关闭弹窗
   - 在 `ChatInput` 中设置值：`/use-skill {skill_name}`
   - 聚焦 `ChatInput` 等待用户继续输入

---

## 7. 错误处理

### 7.1 空状态

当没有可用 skills 时，显示：

```
┌─────────────────────────────────────────────────┐
│  Select a Skill to Use                         │
├─────────────────────────────────────────────────┤
│                                                 │
│         No skills found.                        │
│                                                 │
│    Create one with:                             │
│    deepagents skills create <name>              │
│                                                 │
├─────────────────────────────────────────────────┤
│  Esc to close                                  │
└─────────────────────────────────────────────────┘
```

### 7.2 文件读取错误

- 个别 skill 文件损坏：跳过并记录警告日志，继续加载其他 skills
- 目录权限错误：视为空目录，不影响其他来源

### 7.3 路径安全

复用现有的 `_validate_skill_path()` 函数验证所有路径，防止目录遍历攻击。

---

## 8. 实现文件清单

| 文件路径 | 类型 | 说明 |
|----------|------|------|
| `deepagents_cli/widgets/skills_modal.py` | 新建 | `SkillsModal` 和 `SkillCard` 组件 |
| `deepagents_cli/widgets/chat_input.py` | 修改 | 添加 `/skills` 命令检测和事件发送 |
| `deepagents_cli/app.py` | 修改 | 添加弹窗打开和事件处理逻辑 |

---

## 9. 测试策略

### 9.1 单元测试

- `test_skills_modal.py`: 测试组件渲染、导航、选中逻辑
- `test_chat_input_skills.py`: 测试 `/skills` 命令拦截

### 9.2 集成测试

- 测试空目录场景
- 测试混合 User + Project skills
- 测试键盘导航和选中流程

---

## 10. 实施顺序

1. 创建 `SkillCard` widget（独立测试）
2. 创建 `SkillsModal` 弹窗（集成测试）
3. 修改 `ChatInput` 添加 `/skills` 检测
4. 修改 `DeepAgentsApp` 添加事件处理
5. 端到端测试
6. 代码审查和优化

---

**设计确认**: 用户已确认所有章节（架构、数据模型、UI 布局、交互设计、错误处理）
