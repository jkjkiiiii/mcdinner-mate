"""MCP 客户端单元测试（离线，不联网、不需要 Token）。

重点覆盖两个数据坑：
1. 营养接口返回 toon 紧凑格式，必须解析正确 —— 否则会编造热量
2. 接口金额单位为「分」，必须正确转「元」
"""
import pytest

from server.mcp_client import (
    fen_to_yuan,
    match_nutrition,
    nutrition_index,
    parse_toon,
)

# 取自真实接口返回（脱敏后片段，仅营养数据，不含任何个人信息）
SAMPLE_TOON = (
    "[160]{productName,nutritionDescription,energyKj,energyKcal,protein,"
    "fat,carbohydrate,sodium,calcium}:\n"
    "  猪柳麦满分,null,1288,308,16,16,24,781,213\n"
    "  中薯条,null,1210,289,4,12,38,165,18\n"
    "  麦乐鸡5块,null,890,213,12,12,13,422,9\n"
    "  麦辣鸡翅-2块,null,937,224,13,15,9,537,13\n"
)


def test_parse_toon_header_and_rows():
    rows = parse_toon(SAMPLE_TOON)
    assert len(rows) == 4
    assert rows[0]["productName"] == "猪柳麦满分"
    assert rows[0]["energyKcal"] == "308"
    assert rows[1]["productName"] == "中薯条"


def test_parse_toon_empty_and_malformed():
    assert parse_toon("") == []
    assert parse_toon("no header here") == []
    assert parse_toon("[2]{a,b}:\n  x\n") == []      # 列数不足，整行跳过


def test_parse_toon_name_containing_comma():
    # 名称含逗号时，多余部分应并入首列而不是错位
    txt = "[2]{productName,kcal}:\n  双层吉士,去酸黄瓜,460\n  薯条,210\n"
    rows = parse_toon(txt)
    assert len(rows) == 2
    assert rows[0]["productName"] == "双层吉士,去酸黄瓜"
    assert rows[0]["kcal"] == "460"


def test_nutrition_index_types():
    rows = parse_toon(SAMPLE_TOON)
    idx = nutrition_index(rows)
    assert idx["中薯条"]["energyKcal"] == 289
    assert isinstance(idx["中薯条"]["energyKcal"], int)
    assert idx["猪柳麦满分"]["nutritionDescription"] is None   # "null" → None


def test_match_nutrition_exact_and_fuzzy():
    idx = nutrition_index(parse_toon(SAMPLE_TOON))
    name, item = match_nutrition(idx, "中薯条")
    assert name == "中薯条" and item["energyKcal"] == 289

    name, item = match_nutrition(idx, "麦辣鸡翅")
    assert name == "麦辣鸡翅-2块"          # 包含匹配

    assert match_nutrition(idx, "") is None
    # 完全不相干时返回 None —— 上层据此拒绝回答，绝不编造
    assert match_nutrition(idx, "佛跳墙") is None


def test_fen_to_yuan():
    assert fen_to_yuan(2880) == 28.80
    assert fen_to_yuan("2880") == 28.80
    assert fen_to_yuan(0) == 0.0
    assert fen_to_yuan(None) is None
    assert fen_to_yuan("") is None
    assert fen_to_yuan("abc") is None      # 无法解析时不猜
