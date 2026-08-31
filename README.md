# LLM Wiki 驱动的 Agent 专用知识库系统

本项目实现了一个专为 AI Agent 设计的新型知识库系统——**LLM Wiki**，基于结构化 Schema、混合检索和知识图谱技术。

## 📚 项目组成

- **`/agent-wiki-kb`** - 核心知识库系统实现
  - 混合检索引擎（向量 + 图谱 + 关键词）
  - Agent 原生 API 接口
  - 知识图谱构建与遍历
  - 完整的内容管理和版本控制

## 🎯 核心特性

| 维度 | 传统 Wiki | LLM Wiki |
|------|----------|----------|
| **主要读者** | 人类用户 | AI Agent + 人类 |
| **内容结构** | 自由文本为主 | 结构化 Schema + 文本 |
| **检索方式** | 关键词搜索 | 语义检索 + 图遍历 + 混合查询 |
| **链接语义** | 隐式超链接 | 显式关系类型（图谱边） |
| **更新机制** | 人工编辑 | 自然语言指令 + 自动验证 |

### 设计原则

1. **机器可读优先 (Machine-First)** - 所有内容必须有结构化 Schema
2. **多模态表示 (Multi-Modal)** - 文本层 + 向量层 + 图谱层
3. **可追溯性 (Traceability)** - 完整来源引用和版本历史
4. **Agent 原生接口 (Agent-Native)** - 支持 Function Calling、流式响应
5. **动态演化 (Dynamic Evolution)** - 增量更新、冲突检测、质量评估

## 🚀 快速开始

```bash
# 进入核心项目目录
cd agent-wiki-kb

# 安装依赖
pip install -r requirements.txt

# 启动基础设施（Redis, Qdrant, Neo4j, PostgreSQL）
docker-compose up -d

# 初始化数据库
python scripts/init_db.py

# 启动服务
uvicorn src.api.main:app --reload
```

访问 API 文档：http://localhost:8000/docs

## 📖 详细文档

- [系统架构规划](./AGENT_KNOWLEDGE_BASE_PLAN.md) - 完整的理论基础、架构设计和开发路线图
- [Agent Wiki KB 文档](./agent-wiki-kb/README.md) - 核心系统的详细说明

## 🔧 技术栈

| 组件 | 技术选型 |
|------|---------|
| **Web 框架** | FastAPI |
| **向量数据库** | Qdrant |
| **图数据库** | Neo4j |
| **文档存储** | PostgreSQL (JSONB) |
| **嵌入模型** | BGE-M3 (中文优化) |
| **重排序模型** | BGE-Reranker |
| **部署** | Docker + Kubernetes |

## 📋 开发状态

- ✅ 阶段一：基础架构 MVP
- 🔄 阶段二：混合检索与知识图谱
- ⏳ 阶段三：Agent 集成与 SDK
- ⏳ 阶段四：运维优化与生产就绪

## 📄 许可证

MIT License

---

*基于 LLM Wiki 理论构建，参考 WikiChat、GraphRAG、Self-RAG 等前沿研究*
