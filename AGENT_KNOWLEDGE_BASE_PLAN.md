# LLM Wiki 驱动的 Agent 专用知识库系统规划

## 一、LLM Wiki 理论基础与研究综述

### 1.1 LLM Wiki 的核心定义

LLM Wiki 是一种**专为大型语言模型（LLM）和 AI Agent 设计**的新型知识库范式，与传统面向人类阅读的 Wiki（如 Wikipedia、MediaWiki）有本质区别：

| 维度 | 传统 Wiki | LLM Wiki |
|------|----------|----------|
| **主要读者** | 人类用户 | AI Agent + 人类 |
| **内容结构** | 自由文本为主 | 结构化 Schema + 文本 |
| **检索方式** | 关键词搜索 | 语义检索 + 图遍历 + 混合查询 |
| **链接语义** | 隐式超链接 | 显式关系类型（图谱边） |
| **更新机制** | 人工编辑 | 自然语言指令 + 自动验证 |
| **版本管理** | 简单历史 | 完整溯源 + 变更影响分析 |

### 1.2 关键学术论文与理论支撑

#### 核心论文调研

1. **WikiChat (2023)** - *Stanford University*
   - **核心贡献**: 通过将 LLM 输出 grounding 到 Wikipedia，减少幻觉达 87%
   - **启示**: 知识库必须提供可验证的引用来源

2. **KAPING (2023)** - *Knowledge-Augmented Prompting*
   - **核心贡献**: 利用结构化知识增强 In-Context Learning
   - **启示**: 知识库需要支持 few-shot 示例检索

3. **StructGPT (2023)** - *Microsoft Research*
   - **核心贡献**: LLM 推理结构化数据的通用框架（表格、图谱、数据库）
   - **启示**: 多模态知识表示的必要性

4. **GraphRAG (2024)** - *Microsoft*
   - **核心贡献**: 结合知识图谱与 RAG，提升复杂查询的准确率
   - **启示**: 纯向量检索不足，需要图结构辅助推理

5. **Self-RAG (2023)** - *IBM Research*
   - **核心贡献**: 让 LLM 自我反思检索结果的相关性和准确性
   - **启示**: 知识库需要提供置信度评分和证据链

### 1.3 LLM Wiki 的五大核心原则

基于理论研究，我们提炼出 LLM Wiki 的设计原则：

```
┌─────────────────────────────────────────────────────────────┐
│                    LLM Wiki 设计原则                         │
├─────────────────────────────────────────────────────────────┤
│  1. 机器可读优先 (Machine-First)                            │
│     - 所有内容必须有结构化 Schema                           │
│     - 支持 JSON-LD、RDF 等标准格式导出                       │
│                                                             │
│  2. 多模态表示 (Multi-Modal Representation)                 │
│     - 文本层：人类可读的自然语言                            │
│     - 向量层：语义嵌入（Embedding）                         │
│     - 图谱层：实体 - 关系 - 实体三元组                        │
│                                                             │
│  3. 可追溯性 (Traceability)                                 │
│     - 每个事实都有来源引用                                  │
│     - 版本历史完整可查                                      │
│     - 变更影响自动分析                                      │
│                                                             │
│  4. Agent 原生接口 (Agent-Native API)                       │
│     - 支持工具调用（Function Calling）                      │
│     - 支持流式响应                                          │
│     - 支持多轮对话上下文                                    │
│                                                             │
│  5. 动态演化 (Dynamic Evolution)                            │
│     - 支持增量更新                                          │
│     - 支持冲突检测与解决                                    │
│     - 支持知识质量自动评估                                  │
└─────────────────────────────────────────────────────────────┘
```

---

## 二、系统架构设计

### 2.1 整体架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                      Agent 交互层                                │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐        │
│  │ REST API │  │ GraphQL  │  │ WebSocket│  │ SDK      │        │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘        │
└───────┼─────────────┼─────────────┼─────────────┼──────────────┘
        │             │             │             │
        └─────────────┴──────┬──────┴─────────────┘
                             │
┌────────────────────────────▼────────────────────────────────────┐
│                    查询处理层 (Query Processor)                  │
│  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐    │
│  │ 意图识别       │  │ 查询重写       │  │ 多跳推理规划   │    │
│  │ (Intent Class) │  │ (Query Rewrite)│  │ (Multi-hop)    │    │
│  └────────────────┘  └────────────────┘  └────────────────┘    │
└────────────────────────────┬────────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────────┐
│                    知识检索层 (Retrieval Engine)                 │
│  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐    │
│  │ 向量检索       │  │ 图谱遍历       │  │ 关键词检索     │    │
│  │ (Vector DB)    │  │ (Graph DB)     │  │ (Full-text)    │    │
│  └───────┬────────┘  └───────┬────────┘  └───────┬────────┘    │
│          │                   │                   │              │
│          └───────────────────┼───────────────────┘              │
│                              │                                  │
│                    ┌─────────▼─────────┐                        │
│                    │ 融合排序 (Rerank)  │                        │
│                    └─────────┬─────────┘                        │
└──────────────────────────────┼──────────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────────┐
│                      存储层 (Storage Layer)                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ Qdrant/      │  │ Neo4j/       │  │ PostgreSQL/  │          │
│  │ Weaviate     │  │ NebulaGraph  │  │ MongoDB      │          │
│  │ (向量)       │  │ (图谱)       │  │ (文档)       │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└─────────────────────────────────────────────────────────────────┘
                               ▲
                               │
┌──────────────────────────────┴──────────────────────────────────┐
│                    内容管理层 (Content Manager)                  │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────┐│
│  │ Schema 定义│  │ 版本控制   │  │ 质量验证   │  │ 权限管理   ││
│  └────────────┘  └────────────┘  └────────────┘  └────────────┘│
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 核心模块详细设计

#### 模块 1: 知识表示引擎 (Knowledge Representation Engine)

**功能**: 将原始内容转换为 LLM 友好的多模态表示

```python
class KnowledgeArticle:
    """
    LLM Wiki 的核心数据结构
    """
    id: str                    # 唯一标识符
    title: str                 # 标题
    content: str               # 人类可读文本
    structured_data: dict      # 结构化数据（JSON Schema 验证）
    embeddings: dict[str, list[float]]  # 多粒度嵌入（标题、段落、全文）
    graph_nodes: list[Node]    # 对应的图谱节点
    graph_edges: list[Edge]    # 对应的图谱边
    metadata: {
        "created_at": datetime,
        "updated_at": datetime,
        "version": int,
        "author": str,
        "source": str,         # 来源引用
        "confidence": float,   # 置信度评分
        "tags": list[str],
        "related_articles": list[str]
    }
    access_control: {
        "public": bool,
        "allowed_agents": list[str],
        "required_clearance": int
    }
```

#### 模块 2: Schema 管理系统

**功能**: 定义知识的类型系统和关系约束

```yaml
# Schema 示例：API 文档知识类型
schema:
  name: "API_Documentation"
  properties:
    api_name: {type: string, required: true}
    endpoint: {type: string, pattern: "^/[a-z/]+$"}
    method: {type: enum, values: [GET, POST, PUT, DELETE]}
    parameters:
      type: array
      items:
        name: string
        type: string
        required: boolean
        description: string
    response_schema: {type: object}
    rate_limit: {type: integer}
    authentication: {type: string}
  
  relations:
    - name: "belongs_to_service"
      target: "Service"
      cardinality: many-to-one
    
    - name: "depends_on_api"
      target: "API_Documentation"
      cardinality: many-to-many
    
    - name: "superseded_by"
      target: "API_Documentation"
      cardinality: one-to-one
```

#### 模块 3: 混合检索引擎

**功能**: 结合向量、图谱、关键词三种检索方式

```python
class HybridRetriever:
    def search(self, query: str, config: SearchConfig) -> SearchResult:
        # 第一阶段：并行检索
        vector_results = self.vector_db.search(query, top_k=config.k * 2)
        graph_results = self.graph_db.traverse(query, max_depth=config.depth)
        keyword_results = self.fulltext.search(query, top_k=config.k)
        
        # 第二阶段：结果融合
        candidates = self.fuse_results(
            vector_results, 
            graph_results, 
            keyword_results
        )
        
        # 第三阶段：重排序（使用 Cross-Encoder）
        reranked = self.reranker.rank(query, candidates)
        
        # 第四阶段：多样性选择（MMR）
        final_results = self.mmr_select(reranked, diversity=config.diversity)
        
        return SearchResult(
            articles=final_results[:config.k],
            evidence_chain=self.build_evidence_chain(final_results),
            confidence_scores=self.calculate_confidence(final_results)
        )
```

#### 模块 4: Agent 接口层

**功能**: 提供多种 Agent 集成方式

```python
# OpenAI Function Calling 格式
tools = [
    {
        "type": "function",
        "function": {
            "name": "search_knowledge_base",
            "description": "在知识库中搜索相关信息",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "搜索查询"},
                    "article_types": {"type": "array", "items": {"type": "string"}},
                    "max_results": {"type": "integer", "default": 5},
                    "include_evidence": {"type": "boolean", "default": True}
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "traverse_knowledge_graph",
            "description": "在知识图谱中进行多跳查询",
            "parameters": {
                "type": "object",
                "properties": {
                    "start_entity": {"type": "string"},
                    "relation_path": {"type": "array", "items": {"type": "string"}},
                    "max_depth": {"type": "integer", "default": 3}
                },
                "required": ["start_entity"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "update_article",
            "description": "更新或创建知识条目",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "content": {"type": "string"},
                    "structured_data": {"type": "object"},
                    "operation": {"type": "enum", "values": ["create", "update", "delete"]}
                },
                "required": ["title", "operation"]
            }
        }
    }
]
```

---

## 三、技术栈选型

### 3.1 后端框架

| 组件 | 推荐方案 | 备选方案 | 理由 |
|------|---------|---------|------|
| **Web 框架** | FastAPI | Flask/Fiber | 异步支持、自动 OpenAPI 文档、Pydantic 集成 |
| **任务队列** | Celery + Redis | RQ/Croniter | 成熟稳定、支持定时任务 |
| **缓存** | Redis | Memcached | 支持数据结构丰富、持久化 |

### 3.2 数据存储

| 存储类型 | 推荐方案 | 备选方案 | 理由 |
|---------|---------|---------|------|
| **向量数据库** | Qdrant | Weaviate/Milvus | Rust 编写性能优、支持 payload 过滤、开源 |
| **图数据库** | Neo4j | NebulaGraph/TigerGraph | 生态成熟、Cypher 查询强大 |
| **文档存储** | PostgreSQL (JSONB) | MongoDB | ACID 事务、成熟稳定 |
| **全文检索** | Elasticsearch | Meilisearch | 功能全面、生态完善 |

### 3.3 AI/ML组件

| 组件 | 推荐方案 | 理由 |
|------|---------|------|
| **嵌入模型** | BGE-M3 (中文优化) | 支持多语言、长文本、稠密 + 稀疏 |
| **重排序模型** | BGE-Reranker | 高精度、支持跨语言 |
| **LLM 集成** | LangChain/LlamaIndex | 生态丰富、支持多种 LLM |
| **图谱构建** | spaCy + 自定义 NER | 灵活可控、支持领域定制 |

### 3.4 部署与运维

| 组件 | 推荐方案 |
|------|---------|
| **容器化** | Docker + Docker Compose |
| **编排** | Kubernetes (生产环境) |
| **监控** | Prometheus + Grafana |
| **日志** | ELK Stack (Elasticsearch + Logstash + Kibana) |
| **CI/CD** | GitHub Actions |

---

## 四、开发路线图

### 阶段一：基础架构搭建（2-3 周）

**目标**: 完成核心基础设施，支持基本的 CRUD 操作

```
Week 1:
├── 项目初始化（FastAPI 骨架）
├── Docker Compose 配置（PostgreSQL, Redis, Qdrant, Neo4j）
├── 数据库 Schema 设计与迁移脚本
└── 基础 API 路由（健康检查、认证）

Week 2:
├── 文章 CRUD API
├── Schema 管理系统原型
├── 基础版本控制（Git-like 快照）
└── 单元测试框架搭建

Week 3:
├── 嵌入模型集成（BGE-M3）
├── 向量索引自动构建
├── 基础搜索 API（仅向量检索）
└── API 文档生成（OpenAPI/Swagger）
```

**交付物**:
- 可运行的最小可行产品（MVP）
- 基础 API 文档
- 单元测试覆盖率 > 70%

### 阶段二：核心功能开发（3-4 周）

**目标**: 实现混合检索、知识图谱、高级查询功能

```
Week 4-5:
├── 知识图谱构建管道（从文本抽取实体和关系）
├── Neo4j 集成与 Cypher 查询接口
├── 图谱遍历 API（单跳、多跳）
└── 实体链接（将文本提及链接到图谱节点）

Week 6:
├── 混合检索引擎（向量 + 图谱 + 关键词）
├── 结果融合算法（RRF - Reciprocal Rank Fusion）
├── 重排序模型集成（BGE-Reranker）
└── 性能基准测试与优化

Week 7:
├── 多跳推理规划器
├── 证据链构建
├── 置信度评分系统
└── 查询缓存策略
```

**交付物**:
- 完整的检索系统
- 知识图谱可视化界面（可选）
- 性能测试报告

### 阶段三：Agent 集成与高级功能（2-3 周）

**目标**: 提供完善的 Agent 接口，支持复杂场景

```
Week 8:
├── OpenAI Function Calling 格式适配
├── LangChain Tool 封装
├── LlamaIndex Retriever 封装
└── 多 Agent 权限管理

Week 9:
├── 流式响应支持（SSE/WebSocket）
├── 对话上下文管理
├── 查询建议与自动补全
└── 错误处理与降级策略

Week 10 (可选):
├── 自然语言更新接口（通过 LLM 解析更新指令）
├── 冲突检测与解决
├── 知识质量自动评估
└── A/B 测试框架
```

**交付物**:
- Agent SDK（Python/TypeScript）
- 集成示例代码
- 开发者文档

### 阶段四：运维优化与生产就绪（2 周）

**目标**: 系统稳定性、安全性、可扩展性

```
Week 11:
├── 监控告警系统（Prometheus + Grafana）
├── 日志聚合与分析（ELK）
├── 备份与恢复策略
└── 安全审计（SQL 注入、XSS、认证授权）

Week 12:
├── 性能优化（连接池、缓存策略、索引优化）
├── 压力测试与容量规划
├── 高可用配置（主从复制、故障转移）
└── 部署文档与运维手册
```

**交付物**:
- 生产环境部署指南
- 运维手册
- SLA 承诺文档

---

## 五、关键设计决策

### 5.1 知识表示策略

**决策**: 采用"三层表示法"（文本层 + 向量层 + 图谱层）

**理由**:
- 单一表示无法满足所有查询场景
- 向量擅长语义相似性，图谱擅长关系推理
- 文本层保证人类可读性

**权衡**: 存储成本增加约 3 倍，但查询灵活性大幅提升

### 5.2 检索策略

**决策**: 混合检索 + 学习排序（Learning to Rank）

**理由**:
- 纯向量检索在精确匹配上表现不佳
- 纯关键词检索无法理解语义
- 混合检索结合两者优势

**实现**: RRF（Reciprocal Rank Fusion）+ Cross-Encoder 重排序

### 5.3 更新策略

**决策**: 乐观并发控制 + 版本追溯

**理由**:
- Agent 可能同时更新同一知识
- 需要保留完整历史用于审计和回滚
- 支持时间旅行查询（查询某时刻的知识状态）

### 5.4 扩展策略

**决策**: 微服务架构 + 事件驱动

**理由**:
- 各模块（检索、图谱、嵌入）可独立扩展
- 新功能可通过事件订阅无缝集成
- 便于未来支持多租户

---

## 六、风险评估与应对

| 风险 | 可能性 | 影响 | 应对措施 |
|------|-------|------|---------|
| **嵌入模型效果不佳** | 中 | 高 | 预留多模型切换能力，支持 fine-tuning |
| **图谱构建准确率低** | 高 | 中 | 人工审核 + 置信度阈值 + 持续迭代 NER 模型 |
| **查询延迟过高** | 中 | 高 | 多级缓存 + 异步索引 + 查询超时控制 |
| **知识冲突** | 高 | 中 | 版本控制 + 冲突检测算法 + 人工仲裁接口 |
| **Agent 滥用** | 中 | 高 | 速率限制 + 权限分级 + 操作审计日志 |

---

## 七、下一步行动

### 立即执行（本周）

1. ✅ 完成本规划文档评审
2. ⬜ 确认技术栈最终选型
3. ⬜ 搭建开发环境（Docker Compose）
4. ⬜ 创建 Git 仓库与 CI/CD 流水线
5. ⬜ 编写详细的技术设计文档（TDD）

### 短期目标（2 周内）

1. ⬜ 完成阶段一基础架构
2. ⬜ 实现第一个端到端用例（文章创建→索引→检索）
3. ⬜ 编写开发者入门文档

### 中期目标（6 周内）

1. ⬜ 完成阶段二核心功能
2. ⬜ 进行第一轮性能测试
3. ⬜ 邀请早期用户试用并收集反馈

---

## 八、附录

### 附录 A: API 设计示例

```yaml
# 搜索接口
POST /api/v1/search
Request:
  query: "如何认证 API？"
  filters:
    article_types: ["API_Documentation"]
    min_confidence: 0.7
  options:
    include_vectors: false
    include_graph: true
    max_depth: 2

Response:
  results:
    - id: "api-auth-guide"
      title: "API 认证指南"
      score: 0.92
      snippet: "API 认证使用 JWT 令牌..."
      evidence:
        - source: "官方文档 v2.3"
          url: "https://..."
      graph_path:
        - node: "API 认证"
          relation: "uses_method"
          node: "JWT"
  
  meta:
    total_hits: 15
    search_time_ms: 45
    used_sources: ["vector", "graph", "fulltext"]
```

### 附录 B: 参考资源

1. **论文**:
   - WikiChat: https://arxiv.org/abs/2305.14292
   - GraphRAG: https://www.microsoft.com/en-us/research/project/graphrag/
   - Self-RAG: https://arxiv.org/abs/2310.11511

2. **开源项目**:
   - LangChain: https://github.com/langchain-ai/langchain
   - LlamaIndex: https://github.com/run-llama/llama_index
   - Qdrant: https://github.com/qdrant/qdrant

3. **工具**:
   - BGE Embedding: https://huggingface.co/BAAI/bge-m3
   - Neo4j: https://neo4j.com/
   - FastAPI: https://fastapi.tiangolo.com/

---

*文档版本：v1.0*  
*创建日期：2025 年*  
*作者：AI Assistant*
