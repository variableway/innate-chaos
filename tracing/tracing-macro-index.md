# Macro Index Dashboard - 任务追踪

> Task 文件: tasks/macro/macro-index.md
> 创建时间: 2026-04-08
> 状态: 全部实现完成

---

## 原始任务内容

展示宏观品种（GOLD/OIL/BTC/ETH/利率）价格 Dashboard，提供 RISK ON/OFF 判断和操作建议。
数据源: HyperLiquid (加密货币), FRED (经济数据)。
要求: 可行性报告、计划、架构设计、任务分解、全新项目实现。

---

## 研究结果

### HyperLiquid API
- 完全免费，无需认证
- POST https://api.hyperliquid.xyz/info
- allMids 获取所有中间价 (weight 2, ~600 req/min)
- metaAndAssetCtxs 获取详细合约信息 (markPx, funding, OI)

### FRED API
- 完全免费，需注册 API Key
- 覆盖利率 (DFF, DGS2, DGS10, DGS30, T10Y2Y)、黄金 (GOLDAMGBD228NLBM)、原油 (DCOILWTICO)
- 数据延迟 T+1

### 现有代码库
- 已有 FastAPI + Next.js + TimescaleDB 架构
- 已有 HyperLiquid SDK 集成、价格追踪、信号引擎、Regime 分类
- 宏观 Dashboard 将从全新项目开始

---

## 已交付文档

1. `tasks/macro/macro-feasibility.md` - 可行性报告
   - 各宏观指标含义分析
   - 数据源可行性分析
   - RISK ON/OFF 判定模型设计
   - 技术可行性结论

2. `tasks/macro/macro-architecture.md` - 架构设计
   - 系统架构图
   - 项目目录结构
   - 数据模型设计 (SQL)
   - API 设计 (REST)
   - 信号引擎设计
   - 前端组件与布局设计
   - 技术栈选型

3. `tasks/macro/macro-tasks.md` - 任务分解
   - 6个阶段，共 20+ 子任务
   - 里程碑与优先级
   - 执行顺序建议

---

## 下一步

按 macro-tasks.md 中 Phase 1-6 顺序执行代码实现。

---

## 实现记录 (2026-04-08)

### 已完成项目: `findicators/`

#### 后端 (FastAPI)
- `app/config.py` - Pydantic Settings 配置管理
- `app/database.py` - SQLAlchemy async + TimescaleDB hypertable 初始化
- `app/models/` - Price, Signal, RegimeHistory 数据模型
- `app/schemas/` - Pydantic 响应 schema
- `app/adapters/hyperliquid.py` - BTC/ETH 实时价格 (免费无认证)
- `app/adapters/fred.py` - 利率/黄金/原油经济数据 (FRED API)
- `app/services/signal_engine.py` - 5因子加权风险评分引擎
- `app/services/risk_engine.py` - Regime 评估与持久化
- `app/services/allocation_engine.py` - 配置建议 (RISK_ON/NEUTRAL/RISK_OFF)
- `app/services/price_service.py` - 价格聚合与存储
- `app/api/` - 4组 REST API (prices, signals, regime, allocation)
- `app/scheduler.py` - APScheduler 定时任务
- `app/main.py` - FastAPI 入口 + CORS + 生命周期

#### 前端 (Next.js 14 + TypeScript + Tailwind)
- 8个组件: PriceTicker, RatePanel, RegimeIndicator, PriceChart, FactorBreakdown, AllocationPanel, SuggestionPanel, Providers
- 暗色主题、响应式布局、Skeleton 加载态
- TanStack Query 30s 自动刷新
- 构建验证通过，无 TypeScript 错误

#### 基础设施
- `docker-compose.yml` (TimescaleDB + Backend + Frontend)
- `backend/Dockerfile`
- `frontend/Dockerfile`
- `.gitignore`
- `README.md`
