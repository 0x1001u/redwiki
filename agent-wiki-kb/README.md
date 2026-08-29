# Agent Wiki KB - LLM Wiki 驱动的 Agent 专用知识库

基于 LLM Wiki 理论构建的结构化知识库系统，专为 AI Agent 设计。

## 核心特性

- **机器可读优先**：结构化 Schema、语义嵌入、知识图谱
- **混合检索**：向量检索 + 图遍历 + 关键词搜索
- **Agent 原生接口**：REST API、SDK、自然语言查询
- **可追溯性**：完整的知识来源和版本历史
- **动态演化**：支持知识的增量更新和自动验证

## 项目结构

```
agent-wiki-kb/
├── src/                    # 源代码
│   ├── api/               # API 端点
│   ├── core/              # 核心逻辑
│   ├── models/            # 数据模型
│   ├── services/          # 业务服务
│   └── utils/             # 工具函数
├── tests/                 # 测试代码
├── config/                # 配置文件
├── docs/                  # 文档
├── data/                  # 数据文件
├── scripts/               # 脚本工具
├── requirements.txt       # Python 依赖
├── docker-compose.yml     # Docker 编排
└── README.md             # 项目说明
```

## 快速开始

### 环境要求

- Python 3.10+
- Docker & Docker Compose
- Redis (缓存)
- Qdrant (向量数据库)
- Neo4j (图数据库)
- PostgreSQL (文档存储)

### 安装步骤

1. 克隆仓库并进入目录
2. 创建虚拟环境：`python -m venv venv && source venv/bin/activate`
3. 安装依赖：`pip install -r requirements.txt`
4. 启动基础设施：`docker-compose up -d`
5. 运行迁移：`python scripts/init_db.py`
6. 启动服务：`uvicorn src.api.main:app --reload`

### API 访问

服务启动后访问：http://localhost:8000
API 文档：http://localhost:8000/docs

## 核心 API

### 知识条目管理

```bash
# 创建知识条目
POST /api/v1/knowledge
{
  "title": "Transformer 架构",
  "content": "Transformer 是一种...",
  "schema_type": "concept",
  "metadata": {...}
}

# 查询知识
GET /api/v1/knowledge/search?query=Transformer&mode=hybrid

# 获取关联知识
GET /api/v1/knowledge/{id}/relations
```

### Agent 查询接口

```bash
# 自然语言查询
POST /api/v1/agent/query
{
  "question": "Transformer 的核心组件有哪些？",
  "context_window": 5,
  "require_sources": true
}
```

## 开发路线图

- [x] 阶段一：基础架构 MVP
- [ ] 阶段二：混合检索与知识图谱
- [ ] 阶段三：Agent 集成与 SDK
- [ ] 阶段四：运维优化与生产就绪

## 许可证

MIT License
