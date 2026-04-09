# Macro Index 

## Taks 1: 展示宏观品种的价格

宏观品种主要是:
1. GOLD
2. OIL
3. BTC
4. ETH
5. 利率

希望有一个Dashboard可以展示这些价格指数，然后可以有一个金融的判断：
1.  RISK ON模式
2. RISK Off 模式
4. RISK ON 模式操作建议
5. RISK OFF 模式操作建议

GOLD，OIL，BTC，ETH，利率这些都代表什么，战争因素，通胀预期，实际利率，BTC/ETH资产查看，完成这个任务的计划分析，
理解这些指标的宏观含义，然后数据可以考虑hyperliquid获取，经济数据，可能从路易斯安联储网站上查看

请完成一个可行性报告，计划，架构设计，任务分解，所有记录都需要保留，如果代码实现就从一个全新的项目开始

## Task 2: Bug Fix

```
 > [backend internal] load metadata for docker.io/library/python:3.12-slim:
------
Dockerfile:1

--------------------

   1 | >>> FROM python:3.12-slim

   2 |     

   3 |     WORKDIR /app

--------------------

target backend: failed to solve: python:3.12-slim: failed to resolve source metadata for docker.io/library/python:3.12-slim: failed to copy: httpReadSeeker: failed open: failed to do request: Get "https://docker.registry.cyou/v2/library/python/blobs/sha256:d7b0b4e330022bb59824af47e157a93cc31c6af3a75ae6b14004444a14a6292f?ns=docker.io": EOF
```

## Task 2: Setup Local Dev Environment

1. use UV to setup python dev environment, add .gitignore
2. use pnpm to setup local dev environment
3. use docker to setup local dev environment
4. create script to run dev local environment
5. create .gitignore file
6. local dev environment 使用timescale docker作为数据库