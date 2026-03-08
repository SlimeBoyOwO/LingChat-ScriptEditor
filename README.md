# ✨ LingChat剧本编辑器 ✨


<img width="1521" height="704" alt="logo" src="https://github.com/user-attachments/assets/61a79519-45a9-4e8f-9c43-1bf5aa41cbcd" />


一个为 LingChat 打造的可爱视觉化剧本编辑器~ 这是一个基于大语言模型（LLM）互动游戏的剧本创作工具，你可以通过超直观的视觉界面来创作和定制属于你的游戏剧本哦！(≧◡≦)

## 🌟 特色功能

- **🎨 可爱的视觉化编辑器** - 拖拖拽拽就能创作游戏剧本，超级简单！
- **📖 章节流程管理** - 可视化地查看和管理章节之间的连接关系~
- **🎪 丰富的事件系统** - 创建各种类型的事件（对话、选项、场景切换等）
- **💖 角色管理** - 定义角色的表情和AI性格，让角色更生动！
- **🎵 资源管理** - 整理背景图、BGM和音效资源
- **👀 实时预览** - 所有的修改都能立即看到效果哦
- **💻 跨平台支持** - 作为独立的桌面应用使用~

## 📸 运行展示

<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/60512255-efb1-4266-bb84-221c93a151a0" />
<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/be048615-1f7e-48b0-a0f7-ae65d3800efd" />
<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/76ec22cd-f17a-43d5-85dc-505cd59a5a91" />
<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/9c310aca-a0e7-40d2-8d51-538d963158a0" />

用户引导（风雪版）
https://github.com/user-attachments/assets/723afa46-a555-411a-bb07-8e6af35a1729

剧本预览
https://github.com/user-attachments/assets/d6c95e72-8755-44ae-8f2b-246a59a5d936

## 📥 安装指南

### 下载发行版
从 [Releases](../../releases) 或者 https://github.com/Ratman463/LingChat-ScriptEditor/releases 页面下载最新版本~

### 运行应用
1. 解压下载的压缩包（或者通过安装程序安装）
2. 运行 `LingChat Script Editor.exe`
3. 开始创作！

## 🛠️ 开发设置

### 环境要求
- Node.js v20.19.0+ 或 v22.12.0+
- pnpm
- Python 3.13
- pip

### 快速开始

1. **克隆仓库**
   ```bash
   git clone https://github.com/your-username/LingChat-ScriptEditor.git
   cd LingChat-ScriptEditor
   ```

2. **安装依赖**
   ```bash
   # 前端
   cd frontend
   pnpm install
   
   # 后端
   cd ../backend
   pip install -r requirements.txt
   ```

3. **运行开发模式**
   点击start.bat运行

## 📁 项目结构

```
LingChat-ScriptEditor/
├── frontend/                    # Vue.js + Electron 前端
│   ├── src/
│   │   ├── components/          # Vue 组件
│   │   │   ├── ChapterFlowCanvas.vue    # 主编辑器画布
│   │   │   ├── ChapterNode.vue          # 章节节点组件
│   │   │   └── EventCanvas.vue          # 事件编辑画布
│   │   ├── views/               # 页面视图
│   │   │   ├── HomeView.vue     # 剧本选择页面
│   │   │   └── EditorView.vue   # 主编辑器页面
│   │   ├── stores/              # Pinia 状态管理
│   │   └── config/              # 配置文件
│   ├── electron/                # Electron 主进程
│   └── public/                  # 静态资源
│
├── backend/                     # FastAPI Python 后端
│   ├── src/
│   │   ├── main.py              # FastAPI 应用
│   │   ├── models.py            # Pydantic 模型
│   │   └── routers/             # API 路由
│   │       ├── scripts.py       # 剧本管理
│   │       ├── assets.py        # 资源管理
│   │       └── characters.py    # 角色管理
│   ├── scripts/                 # 游戏剧本（用户数据）
│   └── run.py                   # 入口文件
│
├── README.md                    # 本文件
└── README_BUILD.md              # 构建说明
```

## 📝 剧本格式

剧本以 YAML 格式存储，结构如下：

```
scripts/
└── my_script/
    ├── story_config.yaml        # 剧本元数据
    ├── Characters/              # 角色定义
    │   └── CharacterName/
    │       ├── settings.txt     # 角色设置
    │       └── avatar/          # 表情图片
    ├── Assests/                 # 资源
    │   ├── Backgrounds/         # 背景图
    │   ├── Musics/              # 音乐
    │   └── Sounds/              # 音效
    └── Chapters/               # 章节 YAML 文件
        └── intro.yaml
```

### 章节示例（YAML）

```yaml
events:
  - type: scene
    background: "school.png"
    music: "morning.mp3"
  
  - type: dialogue
    character: "Alice"
    expression: "happy"
    text: "早上好呀！✨"
  
  - type: choice
    text: "你要怎么回应呢？"
    options:
      - text: "打个招呼"
        next: "chapter2.yaml"
      - text: "转身离开"
        next: "chapter3.yaml"
  
  - type: end
    next: "chapter2.yaml"
```

## 🎭 支持的事件类型

| 事件类型 | 描述 |
|---------|------|
| `scene` | 设置背景和音乐 |
| `dialogue` | 角色对话带表情 |
| `choice` | 玩家选择分支 |
| `narration` | 旁白文本 |
| `condition` | 条件分支 |
| `ai_mode` | 启用AI驱动的对话 |
| `end` | 章节结束并链接下一章 |

## 💻 技术栈

### 前端
- **Vue.js 3** - UI 框架
- **TypeScript** - 类型安全
- **Pinia** - 状态管理
- **Vue Router** - 路由导航
- **Tailwind CSS** - 样式框架
- **Electron** - 桌面应用框架

### 后端
- **FastAPI** - Python Web 框架
- **Uvicorn** - ASGI 服务器
- **Pydantic** - 数据验证
- **PyYAML** - YAML 处理

## 🤝 贡献指南

欢迎贡献哦！贡献前请先提issue，描述一下解决的问题或者新增的feature，审核通过后再提交 Pull Request 就好啦~

1. Fork 仓库
2. 创建你的特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交修改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 详情请查看 [LICENSE](LICENSE) 文件 （目前还不确定用啥license)

## 🙏 致谢

- 基于 [Vue.js](https://vuejs.org/) 构建
- 桌面框架来自 [Electron](https://www.electronjs.org/)
- 后端由 [FastAPI](https://fastapi.tiangolo.com/) 提供支持
- 看到这里的你

© LingChat 制作团队
---
