# Macro Index Dashboard - 任务分解

> 日期: 2026-04-08
> 状态: 初稿
> 前置文档: macro-feasibility.md, macro-architecture.md

---

## 阶段一：项目初始化 (Phase 1)

### Task 1.1: 创建项目骨架
- [ ] 初始化 `macro-dashboard/` 目录
- [ ] 创建 `backend/` FastAPI 项目结构
- [ ] 创建 `frontend/` Next.js 项目 (TypeScript + Tailwind)
- [ ] 编写 `docker-compose.yml` (TimescaleDB + Backend + Frontend)
- [ ] 编写 `.env.example` 和配置管理
- [ ] 验证 `docker compose up` 能正常启动

### Task 1.2: 数据库初始化
- [ ] 创建 TimescaleDB migration 脚本
- [ ] 建表: `prices`, `signals`, `regime_history` (均设为 hypertable)
- [ ] 配置自动压缩策略 (7天前数据压缩)
- [ ] 创建必要的索引

---

## 阶段二：数据采集层 (Phase 2)

### Task 2.1: HyperLiquid 数据适配器
- [ ] 实现 `adapters/hyperliquid.py`
  - `fetch_all_mids()` → 获取所有中间价
  - `fetch_perp_context(coin)` → 获取永续合约详情 (markPx, funding, OI)
  - `fetch_candle_snapshot(coin, interval, start_time)` → K线数据
- [ ] 编写单元测试 (mock API 响应)
- [ ] 验证: 手动调用能获取 BTC、ETH 实时数据

### Task 2.2: FRED 数据适配器
- [ ] 实现 `adapters/fred.py`
  - `fetch_series(series_id, start_date, end_date)` → 通用数据获取
  - `fetch_interest_rates()` → 批量获取 DFF, DGS2, DGS10, DGS30, T10Y2Y
  - `fetch_gold_price()` → 获取 GOLDAMGBD228NLBM
  - `fetch_oil_price()` → 获取 DCOILWTICO
- [ ] 处理 FRED 特殊情况 (缺值 "." → None)
- [ ] 编写单元测试
- [ ] 验证: 手动调用能获取各系列最新数据

### Task 2.3: 定时调度器
- [ ] 实现 `scheduler.py`
  - 每 5 分钟: 调用 HyperLiquid 获取 BTC/ETH 数据
  - 每 24 小时: 调用 FRED 获取利率/黄金/原油数据
  - 错误重试与日志记录
- [ ] 数据去重逻辑 (同一时间戳同一资产不重复写入)
- [ ] 验证: 启动后数据自动入库

---

## 阶段三：信号引擎 (Phase 3)

### Task 3.1: 趋势计算模块
- [ ] 实现 `services/signal_engine.py`
  - `_calculate_trend(asset, days)` → N日变化率
  - `_normalize(value, threshold)` → 归一化到 0~1
  - `_calculate_volatility(assets, days)` → 组合波动率

### Task 3.2: 风险评分引擎
- [ ] 实现 `services/risk_engine.py`
  - 5个因子计算: oil_trend, gold_trend, btc_momentum, yield_curve, volatility
  - 加权聚合为 risk_score
  - Regime 分类 (RISK_ON / NEUTRAL / RISK_OFF)
  - 因子评分明细记录

### Task 3.3: 操作建议引擎
- [ ] 实现 `services/allocation_engine.py`
  - 根据 Regime 生成建议配置比例
  - 根据 Regime 生成操作建议文本
  - 支持自定义权重

### Task 3.4: 信号引擎测试
- [ ] 编写集成测试 (使用历史数据)
- [ ] 边界条件测试 (数据不足、极端值)
- [ ] 验证: 给定已知数据，Regime 判定符合预期

---

## 阶段四：API 层 (Phase 4)

### Task 4.1: 价格 API
- [ ] `GET /api/v1/prices/current` → 所有资产最新价格
- [ ] `GET /api/v1/prices/{asset}/history?days=30` → 单资产历史
- [ ] 响应格式按架构文档设计

### Task 4.2: 信号 API
- [ ] `GET /api/v1/signals/current` → 当前各资产信号
- [ ] `GET /api/v1/signals/{asset}/history?days=30` → 信号历史

### Task 4.3: 市场状态 API
- [ ] `GET /api/v1/regime/current` → 当前 Regime + 评分 + 建议
- [ ] `GET /api/v1/regime/history?days=30` → Regime 变化历史

### Task 4.4: 配置 API
- [ ] `GET /api/v1/allocation/current` → 建议配置
- [ ] `GET /api/v1/allocation/history?days=30` → 配置变化历史

---

## 阶段五：前端 Dashboard (Phase 5)

### Task 5.1: 基础框架搭建
- [ ] Next.js App Router 布局
- [ ] API 客户端封装 (`lib/api.ts`)
- [ ] TypeScript 类型定义 (`lib/types.ts`)
- [ ] TanStack Query Provider 配置
- [ ] 自动刷新机制 (30秒轮询)

### Task 5.2: 价格展示组件
- [ ] `PriceTicker.tsx` → 4个资产价格卡片 (GOLD/OIL/BTC/ETH)
- [ ] `RatePanel.tsx` → 利率面板 (DFF/10Y/2Y/Spread)
- [ ] `PriceChart.tsx` → 价格走势图 (Recharts, 支持 Tab 切换资产)

### Task 5.3: 信号与状态组件
- [ ] `RegimeIndicator.tsx` → RISK ON/OFF 大指示器 (带颜色)
- [ ] `RiskScoreGauge.tsx` → 0~1 风险评分仪表盘
- [ ] `FactorBreakdown.tsx` → 各因子评分条形图

### Task 5.4: 配置与建议组件
- [ ] `AllocationPanel.tsx` → 建议配置饼图/条形图
- [ ] `SuggestionPanel.tsx` → 操作建议文字面板

### Task 5.5: 页面整合
- [ ] 组装所有组件到主页面
- [ ] 响应式布局 (桌面/平板/手机)
- [ ] 暗色/亮色主题支持

---

## 阶段六：部署与优化 (Phase 6)

### Task 6.1: Docker 化
- [ ] Backend Dockerfile (Python 多阶段构建)
- [ ] Frontend Dockerfile (Node 多阶段构建)
- [ ] docker-compose.yml 完善
- [ ] 健康检查端点

### Task 6.2: 文档
- [ ] README.md (安装、配置、启动说明)
- [ ] API 文档 (FastAPI 自动生成 Swagger)
- [ ] 配置说明

### Task 6.3: 后续优化 (可选)
- [ ] WebSocket 实时推送 (替代轮询)
- [ ] 历史回测功能 (验证模型准确性)
- [ ] 邮件/Telegram 通知 (Regime 切换时提醒)
- [ ] 更多数据源集成 (CoinGecko 补充实时黄金/原油)

---

## 里程碑

| 阶段 | 内容 | 优先级 |
|------|------|--------|
| Phase 1 | 项目骨架 + 数据库 | P0 |
| Phase 2 | 数据采集 (HyperLiquid + FRED) | P0 |
| Phase 3 | 信号引擎 (RISK ON/OFF) | P0 |
| Phase 4 | API 层 | P0 |
| Phase 5 | 前端 Dashboard | P0 |
| Phase 6 | 部署 + 优化 | P1 |

---

## 执行顺序

建议按 Phase 1 → 2 → 3 → 4 → 5 → 6 顺序执行，每个 Phase 完成后验证再进入下一个。Phase 2 和 Phase 3 可以部分并行（趋势计算模块与数据适配器无依赖关系）。
