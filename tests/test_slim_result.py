"""工具结果瘦身测试（离线）。

`query-meals` 原始返回 7000+ 字符且带图片 URL，会被 6000 字符上限截断成
半截 JSON，模型读不懂就只能反复 query-meal-detail 去翻。这里锁住瘦身行为。
"""
from server.dialog.engine import DialogEngine

FAKE_MENU = {
    "data": {
        "meals": {
            "9900005456": {
                "name": "麦辣鸡腿汉堡三件套",
                "currentPrice": "33.5",
                "originalPrice": "47",
                "image": "https://menu-img.mcd.cn/pcm/prod/menu/20260824/product/MS_9900005456_320.png",
                "canWithOrder": False,
            },
            "521741": {
                "name": "脆薯饼",
                "currentPrice": "8",
                "originalPrice": "8",
                "image": "https://menu-img.mcd.cn/x.png",
            },
        }
    }
}


def test_query_meals_slimmed():
    out = DialogEngine._slim_result("query-meals", FAKE_MENU)
    assert out is not None
    # 算价必需的三样：商品码、名称、现价
    assert "9900005456" in out
    assert "麦辣鸡腿汉堡三件套" in out
    assert "33.5" in out
    # 噪音必须去掉，否则又会被截断
    assert "menu-img.mcd.cn" not in out
    assert "canWithOrder" not in out


def test_slim_result_is_compact():
    """两项菜单的瘦身结果要远小于原始 JSON。"""
    import json
    raw = len(json.dumps(FAKE_MENU, ensure_ascii=False))
    slim = len(DialogEngine._slim_result("query-meals", FAKE_MENU))
    assert slim < raw / 2


def test_other_tools_untouched():
    assert DialogEngine._slim_result("order-list", {"data": []}) is None
    assert DialogEngine._slim_result("calculate-price", {"price": 4150}) is None


def test_empty_menu_falls_back():
    """空菜单不要返回空串，交给上层照常序列化。"""
    assert DialogEngine._slim_result("query-meals", {"data": {"meals": {}}}) is None
