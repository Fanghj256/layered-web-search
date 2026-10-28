#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""UserPromptSubmit hook：提示词含「联网搜索」时，向对话注入分层搜索流程。

可选组件。默认不建议启用——对照实验显示软触发（AGENTS.md + skill）与硬触发
在质量上打平，且软触发成本更低。仅当你需要"任何含触发词的消息都必须走全流程"
时再装。

输出协议：stdout 输出一行合法 JSON，additionalContext 字段会被注入对话。
        （纯 ASCII 输出，避免 Windows 控制台编码问题）
"""
import json
import sys

_CONTEXT = """【联网搜索·触发】用户使用了约定触发词「联网搜索」，请立即按分层搜索流程执行本次调研，不要凭记忆作答：
1) 先判断问题类型：评价类（值不值得用）/ 探索类（找人、找灵感）先提醒用户适合人工搜索；
2) 先用 date 确认当前日期，模糊请求先澄清时间范围；
3) 粗搜：web_search_exa 发 1-2 个宽查询，query 用自然语言描述想要的页面，不要堆关键词；
4) 读全文：对高相关链接用 web_fetch_exa 抓正文；数字、公告号、日期必须来自正文，不能只信摘要；
5) 缺口驱动第二轮：web_search_advanced_exa 细化（机构实体名、startPublishedDate/endPublishedDate、includeDomains 限权威域名如 gov.cn）；
6) 降级兜底：web_fetch_exa 抓不到才用 Playwright 浏览器；代码类问题用 gh CLI（gh search code / clone + grep）；
7) 交叉验证：关键事实至少 2 个独立来源，冲突标注分歧；
8) 输出：分类归纳、能用表格用表格、每条附来源链接，标注「已证实/未证实/时效未知」。"""


def main() -> int:
    # 读取 stdin（hook runner 会传入事件 JSON），本脚本不依赖其内容
    try:
        sys.stdin.read()
    except Exception:
        pass
    print(json.dumps({"additionalContext": _CONTEXT}, ensure_ascii=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
