# MCP 真实工具清单（实测生成，勿手改）

- 生效地址：`https://mcp.mcd.cn`
- 协议版本：`2025-06-18`（官方要求 ≤ 2025-06-18）
- 工具总数：35

| 工具名 | 说明 |
|---|---|
| `query-promotions` | Description: 查询当前门店企业团餐场景下可用的促销规则（满减/满折），仅返回当前时间有效且适用在售餐品的规则原始数据 When： - 企业团餐场景(beType=6)下，用户搭配方案前需要了解当前门店有哪些可用的促销活动/满减满 |
| `query-my-prizes` | Description: 查询当前登录会员通过积分抽奖获得的本期及历史奖品（可用/已使用/已过期/已领取/已失效）。 When： - 用户询问"我抽中了什么奖品" - 用户询问"我的奖品还有哪些能用" - 用户询问"查我的抽奖记录" Inp |
| `query-party-store` | Description: 查询指定城市下支持主题派对的门店列表。当用户选择了城市后，需要查看该城市有哪些门店可举办生日类派对/主题类派对/麦麦体验营/品鉴会/读书会/积分兑换活动时使用 Preconditions： - 必须先通过 quer |
| `query-my-coupons` | 获取用户卡包中的优惠券资产信息，用于“我有什么券 / 券详情查看”等展示与管理场景。 注意：该接口返回的是用户拥有的券，不进行门店、渠道、配送方式等下单规则校验，因此不承诺可用于当前订单。 若业务目标是“当前门店/当前订单可用的券”，请调用 |
| `query-meals` | Description: 餐品列表, 支持到店自提(orderType=1)和外送(orderType=2)两种场景 企业团餐场景下，可按照这个规则给用户进行搭配 - **20元以下**: 小食 - **20-30元**：汉堡+小食 或 汉 |
| `query-meal-detail` | Description: 餐品详情, 支持到店自提(orderType=1)和外送(orderType=2)两种场景 When: - 用户想要了解餐品有哪些组成 - 用户想要更换套餐的组成或者更换特制商品 Input: - storeCod |
| `calculate-price` | Description: 计算商品的价格（含优惠），支持到店自提(orderType=1)和外送(orderType=2)两种场景 When： - 用户问"这些商品多少钱" - 用户问"总价是多少" Input: - reservation |
| `order-list` | Description: 查询麦当劳历史订单，非商城订单，商城订单需要使用mall-order-list When： - 用户询问"帮我查询一下历史订单" - 用户询问"我买了什么麦当劳餐品" |
| `mall-create-order` | 创建积分兑换订单，仅支持shopId=2（从 mall-product-detail 获取） - 当用户询问"用积分兑换这个商品"、"兑换这个券"、用户确认兑换商品时使用,切记：如果单个商品一个订单下单；如果用户需要兑换多个商品‘必须’分别 |
| `query-party-store-session` | Description: 查询指定门店、指定日期下的生日类派对/主题类派对/麦麦体验营/品鉴会/读书会/积分兑换活动场次列表。当用户选择了日期后，需要查看当天有哪些场次可预约时使用。 When： - 用户询问"查看主题活动场次列表" - 用 |
| `query-store-coupons` | Description: 查询【指定门店+订单类型】下可使用的优惠券，支持到店(orderType=1,含到店自取和得来速)和外送(orderType=2,含麦乐送和团餐) When： - 当用户已获取到门店时，用户询问"我有什么优惠券可以 |
| `create-order` | Description: 创建麦当劳订单，支持到店(orderType=1)和外送(orderType=2)两种场景下单, 必须先确定订单类型，必填 (1：到店，2外送) When： - 用户说"我要下单" - 用户说"创建订单" Inpu |
| `party-order-create` | Description: 创建生日类派对/主题类派对/麦麦体验营/品鉴会/读书会/积分兑换活动, 仅支持shopId=5（从 mall-product-detail 获取）的调用，   支持包场(partyType=1)、拼团(partyT |
| `campaign-calendar` | 查询麦当劳中国当月的营销活动日历，返回进行中、往期和未来日期的活动。适用于查看用户进行中和即将到来的可参与活动，还可查询用户对活动的订阅状态。 When：   - 用户问"最近有什么活动"、"这个月有什么优惠活动"、"有什么可以参加的"   |
| `now-time-info` | 获取当前时间信息 - 返回当前服务器的完整时间信息，包括： - 时间戳（毫秒级） - 格式化的日期时间 - 年月日信息 - 时区和UTC时间 在你不知道当前时间，并且用户需要指定日期查询活动日历的时候有用  |
| `delivery-create-address` | Description: 创建用户配送地址 When： - 用户想添加新的配送地址 Input: - city: 城市名称，必填，必须从用户输入中获取实际城市名称，如"南京市" - contactName: 联系人姓名，必填，必须从用户输入 |
| `query-party-store-date` | Description: 查询指定门店支持生日类派对/主题类派对/麦麦体验营/品鉴会/读书会/积分兑换活动的可预约日期列表。当用户选择了门店后，需要查看该门店哪些日期可预约时使用。 When： - 用户询问"这家店哪天可以预约" - 用户询 |
| `query-lottery-info` | Description: 查看当前积分抽奖活动信息，包括活动基本信息、抽奖消耗规则、单次所需积分、剩余可抽次数、当前可用积分与公开奖品列表，不执行抽奖。 When： - 用户询问"积分抽奖有什么奖品" - 用户询问"抽一次要多少积分" -  |
| `mall-points-products` | 查询可兑换餐品券列表 - 当用户询问"有哪些积分兑换商品"、"积分可以兑换什么"、"查看积分商城"时使用 支持类目规则筛选：商品券(1>4)、实物商品(2)、周边产品(2>8)、实物礼品卡(2>9)、生日类派对(1>6>20)、主题类派对( |
| `draw-lottery` | Description: 使用后台配置的抽奖消耗规则参加一次当前积分抽奖并返回结果，服务端原子完成次数或积分扣减与抽奖。 重要约束：仅能在向用户展示 query-lottery-info 返回的 drawDecision.nextConsu |
| `mall-order-detail` | Description: 查询麦麦商城订单详情 When： - 用户询问"麦麦商城的订单详情" Next: - 引导用户："您可以打开麦当劳APP查看凭证等其他信息" |
| `available-coupons` | 查询用户当前可领取的麦麦省的优惠券列表。返回券名称、图片、状态和促销标签。当用户询问有什么优惠、可以领什么券时使用此工具。 |
| `list-nutrition-foods` | 获取麦当劳常见餐品的营养成分数据，包括能量、蛋白质、脂肪、碳水化合物、钠、钙等信息，当用户咨询麦当劳餐品的热量、营养，帮助用户搭配指定热量套餐时有用 |
| `delivery-query-addresses` | Description: 外送场景下，查询用户配送地址列表 When： - 用户想点麦乐送 - 用户想吃麦当劳，并配送到家 - 我想点团餐 Next： - 1:引导用户创建新的配送地址 - 2:当用户选择企业团餐时，需要引导用户提供预算金额 |
| `delivery-query-stores` | Description: 外送场景下，用户选择完地址后，需要根据地址ID，查询用户当前地址可配送的门店 When: - 外送场景下，用户选择完配送地址后 - 用户问"这个地址能送到哪些店" 注意：到店场景请使用 query-nearby-s |
| `cancel-order` | Description: 取消订单，非商城订单 When： - 用户说"取消订单"、"我要取消" - 用户说"帮我取消一下订单" Input: - cancelReasonCode: 取消原因code，必填，可选值：1=改主意了, 2=重复 |
| `query-my-account` | 查询用户积分账户详情 - 当用户询问"我有多少积分"、"查下我的积分"、"积分余额"、"查询过期积分"时使用  |
| `query-party-city` | Description: 活动派对商品配置场次城市列表, 必须先确定spuId(从 mall-points-products 获取）或查询商品详情（从 mall-product-detail 获取) When： - 用户询问"主题派对在哪些 |
| `query-order` | Description: 查询订单详细信息 When： - 用户询问"查下订单详情"、"订单状态"、"我的订单" - 用户提供了麦当劳订单编号想查询配送进度 - 用户说我已支付或者支付失败时，查询一下最新的订单状态 |
| `query-nearby-stores` | Description: 到店场景下，查询用户可点餐门店，需要用户明确是到店自取还是车道取餐 - beType=1(到店自提): 返回的门店无 beCode，后续工具调用不传 beCode - beType=5(得来速): 返回的门店有 b |
| `query-meal-assistance` | Description: 仅支持企业团餐场景(beType=6)在calculate-price前需要获取当前门店可用的助餐服务 When： - 企业团餐场景(beType=6)下，用户选完商品后、计算价格前 - 用户问"有什么助餐服务"、 |
| `query-survey-coupon` | Description: 按订单号查询当前 MCP 用户本人订单的 CSAT 满意度答卷，并返回该订单关联奖券的标题、核销时间、核销状态和点餐方式。 When: 用户询问某个订单的满意度答卷结果时使用；用户询问某个订单关联奖券的内容、核销时 |
| `mall-product-detail` | 查询积分兑换商品详情 - 当用户询问"这个商品详情是什么"、"查看商品详细信息"、用户点击商品查看详情时使用 返回商品的所有SKU规格信息，用户需要选择具体SKU后才能下单兑换  前提条件： - 已知商品SPU ID，需要从查询可兑换餐品券 |
| `mall-order-list` | Description: 查询麦麦商城订单列表 When： - 用户询问"查看我的麦当劳商城订单列表" |
| `auto-bind-coupons` | 自动领取麦麦省所有当前可用的麦当劳优惠券。无需指定具体的优惠券和couponId，系统会自动领取用户可领的所有券。当用户说"帮我领券"、"自动领取优惠券"、"一键领券"时使用此工具。 |

## 入参 Schema

```json
{
  "query-promotions": {
    "properties": {
      "beCode": {
        "description": "业务编码，与storeCode 配对使用，团餐场景必传（从 delivery-query-stores 获取）",
        "type": "string"
      },
      "beType": {
        "description": "业务类型，固定传 6（企业团餐）",
        "enum": [
          6
        ],
        "type": "integer"
      },
      "orderType": {
        "description": "订单类型，团餐场景固定传 2（外送）",
        "enum": [
          2
        ],
        "type": "integer"
      },
      "reservationDate": {
        "description": "预约场景必传，非预约场景不传。格式:yyyy-MM-dd HH:mm",
        "type": "string"
      },
      "storeCode": {
        "description": "门店编码（storeCode）, 不能为空",
        "type": "string"
      }
    },
    "required": [
      "storeCode",
      "orderType",
      "beType"
    ],
    "type": "object"
  },
  "query-my-prizes": {
    "properties": {
      "pageNum": {
        "description": "页码，默认第1页",
        "type": "string"
      },
      "pageSize": {
        "description": "每页条数，默认10条，最大50条",
        "type": "string"
      }
    },
    "type": "object"
  },
  "query-party-store": {
    "properties": {
      "code": {
        "description": "城市code",
        "type": "string"
      },
      "latitude": {
        "description": "纬度，从 query-party-city 返回结果的 data[].latitude 获取",
        "type": "number"
      },
      "longitude": {
        "description": "经度，从 query-party-city 返回结果的 data[].longitude 获取",
        "type": "number"
      },
      "spuId": {
        "description": "spuId，从 mall-points-products 或 mall-product-detail 获取",
        "type": "number"
      }
    },
    "required": [
      "code"
    ],
    "type": "object"
  },
  "query-my-coupons": {
    "properties": {
      "page": {
        "description": "页码，默认第1页，最多5页",
        "type": "string"
      },
      "pageSize": {
        "description": "每页条数，默认200条，最大200条",
        "type": "string"
      }
    },
    "type": "object"
  },
  "query-meals": {
    "properties": {
      "beCode": {
        "description": "业务编码，与storeCode 配对使用，从query-nearby-stores或delivery-query-stores返回结果中获取。得来速(beType=5)/外送(orderType=2)/团餐场景必传，到店自取(beType=1)场景不传",
        "type": "string"
      },
      "beType": {
        "description": "1-到店取餐，2-麦乐送到家，5-得来速(DT)，6-企业团餐",
        "enum": [
          1,
          2,
          5,
          6
        ],
        "type": "integer"
      },
      "orderType": {
        "description": "订单类型，1-到店（含到店自取+得来速车道取餐），2-外送（含麦乐送+企业团餐）",
        "enum": [
          1,
          2
        ],
        "type": "integer"
      },
      "reservationDate": {
        "description": "预约场景必传，非预约场景不传。格式:yyyy-MM-dd HH:mm",
        "type": "string"
      },
      "storeCode": {
        "description": "门店编码（storeCode）, 不能为空",
        "type": "string"
      }
    },
    "required": [
      "storeCode",
      "orderType",
      "beType"
    ],
    "type": "object"
  },
  "query-meal-detail": {
    "properties": {
      "beCode": {
        "description": "业务编码，与storeCode 配对使用，从query-nearby-stores或delivery-query-stores返回结果中获取。得来速(beType=5)/外送(orderType=2)/团餐场景必传，到店自取(beType=1)场景不传",
        "type": "string"
      },
      "beType": {
        "description": "1-到店取餐，2-麦乐送到家，5-得来速(DT)，6-企业团餐",
        "enum": [
          1,
          2,
          5,
          6
        ],
        "type": "integer"
      },
      "code": {
        "description": "餐品唯一编码，快餐门店内唯一标识单个餐品的编码",
        "type": "string"
      },
      "orderType": {
        "description": "到店自提场景:orderType=1 && beCode 是个无效参数，不要传，传了会报错；外送场景:orderType=2 && beCode 为delivery-query-address中的beCode；得来速(DT)场景：orderType=1 && beCode 为query-nearby-store中的beCode",
        "enum": [
          1,
          2
        ],
        "type": "integer"
      },
      "reservationDate": {
        "description": "预约场景必传，非预约场景不传。格式:yyyy-MM-dd HH:mm",
        "type": "string"
      },
      "storeCode": {
        "description": "门店编码（storeCode）, 不能为空",
        "type": "string"
      }
    },
    "required": [
      "storeCode",
      "orderType",
      "beType",
      "code"
    ],
    "type": "object"
  },
  "calculate-price": {
    "properties": {
      "beCode": {
        "description": "业务编码，与storeCode 配对使用，从query-nearby-stores或delivery-query-stores返回结果中获取。得来速(beType=5)/外送(orderType=2)/团餐场景必传，到店自取(beType=1)场景不传",
        "type": "string"
      },
      "beType": {
        "description": "1-到店取餐，2-麦乐送到家，5-得来速(DT)，6-企业团餐",
        "enum": [
          1,
          2,
          5,
          6
        ],
        "type": "integer"
      },
      "gmServiceCode": {
        "description": "团餐-助餐服务码",
        "type": "string"
      },
      "items": {
        "description": "待价格计算的商品列表",
        "items": {
          "description": "",
          "properties": {
            "couponCode": {
              "description": "优惠券code",
              "type": "string"
            },
            "couponId": {
              "description": "优惠券Id",
              "type": "string"
            },
            "modification": {
              "description": "商品特制选项",
              "properties": {
                "values": {
                  "description": "特制选项列表",
                  "items": {
                    "properties": {
                      "code": {
                        "description": "特制code",
                        "type": "string"
                      },
                      "key": {
                        "description": "特制key",
                        "type": "string"
                      },
                      "quantity": {
                        "description": "特制数量",
                        "type": "integer"
                      }
                    },
                    "type": "object"
                  },
                  "type": "array"
                }
              },
              "type": "object"
            },
            "productCode": {
              "description": "商品code",
              "type": "string"
            },
            "quantity": {
              "description": "数量，必填，不能为空，且大于等于1",
              "type": "integer"
            },
            "roundList": {
              "description": "套餐子项",
              "items": {
                "properties": {
                  "comboItemList": {
                    "description": "套餐套餐round下商品",
                    "items": {
                      "properties": {
                        "code": {
                          "description": "商品编码",
                          "type": "string"
                        },
                        "modification": {
                          "description": "商品特制选项",
                          "properties": {
                            "values": {
                              "description": "特制选项列表",
                              "items": {
                                "properties": {
                                  "code": {
                                    "description": "特制code",
                                    "type": "string"
                                  },
                                  "key": {
                                    "description": "特制key",
                                    "type": "string"
                                  },
                                  "quantity": {
                                    "description": "特制数量",
                                    "type": "integer"
                                  }
                                },
                                "type": "object"
                              },
                              "type": "array"
                            }
                          },
                          "type": "object"
                        },
                        "quantity": {
                          "description": "商品数量",
                          "type": "integer"
                        }
                      },
                      "type": "object"
                    },
                    "type": "array"
                  },
                  "round": {
                    "description": "套餐round",
                    "type": "string"
                  }
                },
                "type": "object"
              },
              "type": "array"
            }
          },
          "type": "object"
        },
        "type": "array"
      },
      "needTableware": {
        "description": "是否需要餐具，true需要，false不需要",
        "type": "boolean"
      },
      "orderType": {
        "description": "订单类型，1-到店（含到店自取+得来速车道取餐），2-外送（含麦乐送+企业团餐）",
        "enum": [
          1,
          2
        ],
        "type": "integer"
      },
      "reservationDate": {
        "description": "预约场景必传，非预约场景不传。格式:yyyy-MM-dd HH:mm",
        "type": "string"
      },
      "storeCode": {
        "description": "门店编码（storeCode）, 不能为空",
        "type": "string"
      },
      "withOrder": {
        "description": "随单购商品",
        "properties": {
          "cardId": {
            "description": "随单购卡id",
            "type": "string"
          },
          "cardType": {
            "description": "随单购卡类型",
            "type": "integer"
          },
          "membershipCode": {
            "description": "随单购会员code",
            "type": "string"
          },
          "membershipSpecId": {
            "description": "随单购规格id",
            "type": "string"
          }
        },
        "type": "object"
      }
    },
    "required": [
      "storeCode",
      "orderType",
      "beType"
    ],
    "type": "object"
  },
  "order-list": {
    "properties": {},
    "type": "object"
  },
  "mall-create-order": {
    "properties": {
      "addressId": {
        "description": "配送地址ID，spuCategory=\"2\"时必填",
        "type": "string"
      },
      "count": {
        "description": "兑换数量",
        "type": "integer"
      },
      "skuId": {
        "description": "商品SKU ID，需要从查询可兑换餐品券列表或查询商品详情中获取",
        "type": "integer"
      },
      "spuCategory": {
        "description": "类目，商品类别，\"1\"虚拟商品, \"2\"实体物品，需要从查询可兑换餐品券列表或查询商品详情中获取",
        "type": "string"
      }
    },
    "required": [
      "skuId",
      "spuCategory"
    ],
    "type": "object"
  },
  "query-party-store-session": {
    "properties": {
      "dateStr": {
        "description": "门店日期",
        "type": "string"
      },
      "spuId": {
        "description": "spuId",
        "type": "number"
      },
      "storeCode": {
        "description": "门店code",
        "type": "string"
      }
    },
    "required": [
      "spuId",
      "storeCode",
      "dateStr"
    ],
    "type": "object"
  },
  "query-store-coupons": {
    "properties": {
      "beCode": {
        "description": "业务编码，与storeCode 配对使用，从query-nearby-stores或delivery-query-stores返回结果中获取。得来速(beType=5)/外送(orderType=2)/团餐场景必传，到店自取(beType=1)场景不传",
        "type": "string"
      },
      "beType": {
        "description": "1-到店取餐，2-麦乐送到家，5-得来速(DT)，6-企业团餐",
        "enum": [
          1,
          2,
          5,
          6
        ],
        "type": "integer"
      },
      "orderType": {
        "description": "订单类型, 1-到店（含到店自取+得来速车道取餐），2-外送（含麦乐送+企业团餐）",
        "enum": [
          1,
          2
        ],
        "type": "integer"
      },
      "reservationDate": {
        "description": "预约场景必传，非预约场景不传。格式 yyyy-MM-dd HH:mm",
        "type": "string"
      },
      "storeCode": {
        "description": "门店编码必须全部由数字组成",
        "type": "string"
      }
    },
    "required": [
      "orderType",
      "beType",
      "storeCode"
    ],
    "type": "object"
  },
  "create-order": {
    "properties": {
      "addressId": {
        "description": "配送地址id，外送or团餐的地址",
        "type": "string"
      },
      "beCode": {
        "description": "业务编码，与storeCode 配对使用，从query-nearby-stores或delivery-query-stores返回结果中获取。得来速(beType=5)/外送(orderType=2)/团餐场景必传，到店自取(beType=1)场景不传",
        "type": "string"
      },
      "beType": {
        "description": "1-到店取餐，2-麦乐送到家，5-得来速(DT)，6-企业团餐",
        "enum": [
          1,
          2,
          5,
          6
        ],
        "type": "integer"
      },
      "gmServiceCode": {
        "description": "企业团餐场景(beType=6)下，必传，参数来自query-meal-assistance",
        "type": "string"
      },
      "items": {
        "description": "待价格计算的商品列表",
        "items": {
          "description": "",
          "properties": {
            "couponCode": {
              "description": "优惠券code",
              "type": "string"
            },
            "couponId": {
              "description": "优惠券Id",
              "type": "string"
            },
            "modification": {
              "description": "商品特制选项",
              "properties": {
                "values": {
                  "description": "特制选项列表",
                  "items": {
                    "properties": {
                      "code": {
                        "description": "特制code",
                        "type": "string"
                      },
                      "key": {
                        "description": "特制key",
                        "type": "string"
                      },
                      "quantity": {
                        "description": "特制数量",
                        "type": "integer"
                      }
                    },
                    "type": "object"
                  },
                  "type": "array"
                }
              },
              "type": "object"
            },
            "productCode": {
              "description": "商品code",
              "type": "string"
            },
            "quantity": {
              "description": "数量",
              "type": "integer"
            },
            "roundList": {
              "description": "套餐子项",
              "items": {
                "properties": {
                  "comboItemList": {
                    "description": "套餐套餐round下商品",
                    "items": {
                      "properties": {
                        "code": {
                          "description": "商品编码",
                          "type": "string"
                        },
                        "modification": {
                          "description": "商品特制选项",
                          "properties": {
                            "values": {
                              "description": "特制选项列表",
                              "items": {
                                "properties": {
                                  "code": {
                                    "description": "特制code",
                                    "type": "string"
                                  },
                                  "key": {
                                    "description": "特制key",
                                    "type": "string"
                                  },
                                  "quantity": {
                                    "description": "特制数量",
                                    "type": "integer"
                                  }
                                },
                                "type": "object"
                              },
                              "type": "array"
                            }
                          },
                          "type": "object"
                        },
                        "quantity": {
                          "description": "商品数量",
                          "type": "integer"
                        }
                      },
                      "type": "object"
                    },
                    "type": "array"
                  },
                  "round": {
                    "description": "套餐round",
                    "type": "string"
                  }
                },
                "type": "object"
              },
              "type": "array"
            }
          },
          "type": "object"
        },
        "type": "array"
      },
      "needTableware": {
        "description": "是否需要餐具，true需要，false不需要",
        "type": "boolean"
      },
      "orderType": {
        "description": "订单类型，1-到店（含到店自取+得来速车道取餐），2-外送（含麦乐送+企业团餐）",
        "enum": [
          1,
          2
        ],
        "type": "integer"
      },
      "remark": {
        "description": "订单备注（选填，最多50字），如\"无接触配送\"，仅orderType=2场景下需要引导用户填写",
        "type": "string"
      },
      "reservationDate": {
        "description": "预约场景必传，非预约场景不传。格式:yyyy-MM-dd HH:mm",
        "type": "string"
      },
      "storeCode": {
        "description": "门店编码（storeCode）, 不能为空",
        "type": "string"
      },
      "takeWayCode": {
        "description": "到店/得来速场景(orderType=1)必传，外送/团餐场景(orderType=2)不传。值从 calculate-price 返回的takeWayList[].code 中选取",
        "type": "string"
      },
      "withOrder": {
        "description": "随单购商品",
        "properties": {
          "cardId": {
            "description": "随单购卡id",
            "type": "string"
          },
          "cardType": {
            "description": "随单购卡类型",
            "type": "integer"
          },
          "membershipCode": {
            "description": "随单购OMM code",
            "type": "string"
          },
          "membershipSpecId": {
            "description": "随单购OMM 规格id",
            "type": "string"
          }
        },
        "type": "object"
      }
    },
    "required": [
      "storeCode",
      "orderType",
      "beType"
    ],
    "type": "object"
  },
  "party-order-create": {
    "properties": {
      "code": {
        "description": "城市code",
        "type": "string"
      },
      "count": {
        "description": "count",
        "type": "integer"
      },
      "dateStr": {
        "description": "店铺日期",
        "type": "string"
      },
      "id": {
        "description": "场次Id",
        "type": "number"
      },
      "leftNum": {
        "description": "场次余位",
        "type": "integer"
      },
      "partyTimeInfo": {
        "description": "场次信息",
        "properties": {
          "id": {
            "description": "场次id",
            "type": "number"
          },
          "leftNum": {
            "description": "场次剩余余位",
            "type": "integer"
          },
          "partyMax": {
            "description": "场次最大成团人数",
            "type": "integer"
          },
          "partyMin": {
            "description": "场次最小成团人数",
            "type": "integer"
          },
          "price": {
            "description": "价格",
            "type": "integer"
          },
          "timeEnd": {
            "description": "场次结束时间",
            "type": "string"
          },
          "timeStart": {
            "description": "场次开始时间",
            "type": "string"
          }
        },
        "type": "object"
      },
      "partyType": {
        "description": "派对类型，1-包场，2-拼团",
        "type": "integer"
      },
      "skuId": {
        "description": "skuId",
        "type": "number"
      },
      "spuId": {
        "description": "spuId",
        "type": "number"
      },
      "storeCode": {
        "description": "门店",
        "type": "string"
      },
      "timeEnd": {
        "description": "场次结束时间",
        "type": "string"
      },
      "timeStart": {
        "description": "场次开始时间",
        "type": "string"
      }
    },
    "required": [
      "partyType"
    ],
    "type": "object"
  },
  "campaign-calendar": {
    "properties": {
      "specifiedDate": {
        "description": "可选的查询基准日期（格式：yyyy-MM-dd）；若传入，则以该日为锚点，返回当天及时间线上与其最邻近的前后各一个有活动的日子（共三天）；若不填，默认返回当前月所有活动",
        "type": "string"
      }
    },
    "type": "object"
  },
  "now-time-info": {
    "properties": {},
    "type": "object"
  },
  "delivery-create-address": {
    "properties": {
      "address": {
        "description": "配送地址",
        "type": "string"
      },
      "addressDetail": {
        "description": "配送地址门牌号",
        "type": "string"
      },
      "city": {
        "description": "城市",
        "type": "string"
      },
      "contactName": {
        "description": "联系人姓名",
        "type": "string"
      },
      "gender": {
        "description": "性别",
        "type": "string"
      },
      "phone": {
        "description": "要求为11位纯数字",
        "type": "string"
      }
    },
    "required": [
      "address",
      "addressDetail",
      "city",
      "contactName",
      "phone"
    ],
    "type": "object"
  },
  "query-party-store-date": {
    "properties": {
      "spuId": {
        "description": "spuId",
        "type": "number"
      },
      "storeCode": {
        "description": "门店code",
        "type": "string"
      }
    },
    "required": [
      "spuId",
      "storeCode"
    ],
    "type": "object"
  },
  "query-lottery-info": {
    "properties": {},
    "type": "object"
  },
  "mall-points-products": {
    "properties": {
      "catRuleIds": {
        "description": "类目规则筛选，支持多选（逗号分隔），非必传，不传时默认查询所有类型。\n可选值：\n- 1>4: 商品券（非预付优惠券）\n- 2: 实物商品\n- 2>8: 周边产品\n- 2>9: 实物礼品卡\n- 1>6>20: 生日类派对\n- 1>6>21: 主题类派对\n- 1>6>22: 麦麦体验营\n- 1>6>25: 品鉴会\n- 1>6>34: 读书会\n- 1>6>40: 积分兑换活动\n示例：1>4,2\n",
        "type": "string"
      }
    },
    "type": "object"
  },
  "draw-lottery": {
    "properties": {},
    "type": "object"
  },
  "mall-order-detail": {
    "properties": {
      "orderId": {
        "description": "订单号",
        "type": "string"
      }
    },
    "required": [
      "orderId"
    ],
    "type": "object"
  },
  "available-coupons": {
    "properties": {},
    "type": "object"
  },
  "list-nutrition-foods": {
    "properties": {},
    "type": "object"
  },
  "delivery-query-addresses": {
    "properties": {},
    "type": "object"
  },
  "delivery-query-stores": {
    "properties": {
      "addressId": {
        "description": "地址ID，来源delivery-query-address",
        "type": "string"
      },
      "beType": {
        "description": "beType：2: 麦乐送，6：团餐",
        "type": "integer"
      }
    },
    "required": [
      "beType",
      "addressId"
    ],
    "type": "object"
  },
  "cancel-order": {
    "properties": {
      "cancelReasonCode": {
        "description": "取消原因code，默认为1",
        "type": "string"
      },
      "orderId": {
        "description": "订单号",
        "type": "string"
      }
    },
    "required": [
      "orderId",
      "cancelReasonCode"
    ],
    "type": "object"
  },
  "query-my-account": {
    "properties": {},
    "type": "object"
  },
  "query-party-city": {
    "properties": {
      "spuId": {
        "description": "spuId",
        "type": "number"
      }
    },
    "required": [
      "spuId"
    ],
    "type": "object"
  },
  "query-order": {
    "properties": {
      "orderId": {
        "description": "No comments found.",
        "type": "string"
      }
    },
    "required": [
      "orderId"
    ],
    "type": "object"
  },
  "query-nearby-stores": {
    "properties": {
      "beType": {
        "description": "beType必传，1：到店自提, 5-得来速车道取餐(Drive Through)",
        "enum": [
          1,
          5
        ],
        "type": "integer"
      },
      "city": {
        "description": "城市名",
        "type": "string"
      },
      "keyword": {
        "description": "关键词",
        "type": "string"
      },
      "searchType": {
        "default": 1,
        "description": "searchType=2 按位置进行搜索， searchType=1 搜索收藏餐厅，默认searchType=1",
        "enum": [
          1,
          2
        ],
        "type": "integer"
      }
    },
    "required": [
      "beType",
      "searchType"
    ],
    "type": "object"
  },
  "query-meal-assistance": {
    "properties": {
      "beCode": {
        "description": "BE编码（Business Entity Code）",
        "type": "string"
      },
      "beType": {
        "description": "固定传 6（企业团餐），此接口仅团餐场景使用",
        "enum": [
          6
        ],
        "type": "integer"
      },
      "orderType": {
        "description": "到店自提场景: orderType=1 && beCode 是个无效参数，不要传，传了会报错\n外送场景: orderType=2 && beCode 为delivery-query-address中的beCode\n得来速(DT)场景：orderType=1 && beCode 为query-nearby-store中的beCode",
        "type": "integer"
      },
      "reservationDate": {
        "description": "预约时间，仅当用户要预约下单时，该字段必传，格式形如 2020-08-08 09:30",
        "type": "string"
      },
      "storeCode": {
        "description": "门店编码（storeCode）, 不能为空",
        "type": "string"
      }
    },
    "required": [
      "storeCode"
    ],
    "type": "object"
  },
  "query-survey-coupon": {
    "properties": {
      "orderId": {
        "description": "订单号。必填。类型为字符串，仅允许字母、数字、下划线和连字符，最长 64 位，格式示例：1030108270000795607354880945。数据来源为用户明确提供的订单号或上游订单查询工具返回的订单号；Agent 不要自行编造或改写该值。",
        "type": "string"
      }
    },
    "required": [
      "orderId"
    ],
    "type": "object"
  },
  "mall-product-detail": {
    "properties": {
      "spuId": {
        "description": "商品SPU ID，需要从查询可兑换餐品券列表让用户选择一个spu才可以",
        "type": "integer"
      }
    },
    "required": [
      "spuId"
    ],
    "type": "object"
  },
  "mall-order-list": {
    "properties": {
      "lastId": {
        "description": "最后一个订单id",
        "type": "number"
      },
      "size": {
        "default": 10,
        "description": "查询数量，默认10，超过10按10条查询",
        "type": "integer"
      }
    },
    "type": "object"
  },
  "auto-bind-coupons": {
    "properties": {},
    "type": "object"
  }
}
```