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

_CONTEXT = """【联网搜索·触发】用户使用了约定触发词「联网搜索」，请立即按 web-research 技能的分层流程执行本次调研，不要凭记忆作答：
1) 先判断问题类型：评价类（值不值得用）/ 探索类（找人、找灵感）先提醒用户适合人工搜索；模糊请求先澄清时间范围；
2) 事实类走完整流程：确认日期 → 粗搜 → 抓正文 → 缺口驱动第二轮 → 按来源选择浏览器兜底 → 交叉验证；
3) 数字、公告号、日期、引文必须来自正文并附来源；关键事实至少 2 个独立来源，冲突标注分歧；
4) 输出标注「已证实/未证实/时效未知」，不确定就写不确定。"""


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
