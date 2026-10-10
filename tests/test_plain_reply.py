# -*- coding: utf-8 -*-
"""回复文本清洗：聊天气泡只显示纯文本，Markdown 必须洗掉。

实测踩坑：模型会把 `![今日报告卡](file:///D:/.../report_xx.png)`
连同**本地绝对路径**一起贴进对话；也会用 `**门店名**` 加粗。
气泡是 textContent 渲染，这些会原样露出来。
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from server.dialog.engine import DialogEngine as E  # noqa: E402


def test_strips_image_markdown_and_local_path():
    t = ("今天这顿：麦辣鸡腿汉堡 + 中薯 + 中可乐，一共 921 千卡。\n\n"
         "![今日报告卡](file:///D:/some/local/path/data/report_abc123.png)\n\n"
         "完事了，早点休息。")
    out = E._plain(t)
    assert "![" not in out and "]" not in out
    assert "file:///" not in out and "D:/" not in out
    assert "921 千卡" in out and "早点休息" in out


def test_strips_bold_and_links():
    out = E._plain("在**麦当劳北京西铁营中路招商蛇口餐厅**下单了，"
                   "详情见[订单页](https://example.com/x)")
    assert out == "在麦当劳北京西铁营中路招商蛇口餐厅下单了，详情见订单页"


def test_strips_headings_and_turns_bullets_into_dots():
    out = E._plain("# 今日报告\n- 麦辣鸡腿堡\n- 中薯条\n* 可乐中杯")
    assert "#" not in out
    assert out == "今日报告\n· 麦辣鸡腿堡\n· 中薯条\n· 可乐中杯"


def test_keeps_plain_text_untouched():
    s = "辛苦了啊。要不要整点热乎的垫垫？"
    assert E._plain(s) == s


def test_collapses_excess_blank_lines_and_handles_empty():
    assert E._plain("A\n\n\n\nB") == "A\n\nB"
    assert E._plain("") == ""
    assert E._plain(None) is None
