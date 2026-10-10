"""下单参数兜底逻辑测试（离线）。

`create-order` 到店场景必须带 `takeWayCode`，而模型偶尔会漏传。
这个测试锁住兜底行为，防止以后改动把下单能力悄悄弄坏。
"""
from server.dialog.engine import DialogEngine


def test_carries_takeway_for_pickup():
    a = DialogEngine._fill_order_defaults(
        "create-order", {"storeCode": "1950814", "orderType": 1}
    )
    assert a["takeWayCode"] == "eat-in"


def test_keeps_explicit_takeway():
    a = DialogEngine._fill_order_defaults(
        "create-order", {"storeCode": "1950814", "orderType": 1, "takeWayCode": "locker-in"}
    )
    assert a["takeWayCode"] == "locker-in"


def test_delivery_has_no_takeway():
    """外送场景（orderType=2）不传 takeWayCode，传了反而会被官方接口报错。"""
    a = DialogEngine._fill_order_defaults(
        "create-order", {"storeCode": "1950814", "orderType": 2, "addressId": "x"}
    )
    assert "takeWayCode" not in a


def test_other_tools_untouched():
    a = DialogEngine._fill_order_defaults("query-meals", {"storeCode": "1950814"})
    assert a == {"storeCode": "1950814"}
