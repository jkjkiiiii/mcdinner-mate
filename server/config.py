"""全局配置。从 .env 读取；占位符未填时启动即报错，避免带着空配置跑半天。"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")

_PLACEHOLDER_PREFIX = "{{"


def _need(name: str, default: str | None = None) -> str:
    v = os.getenv(name, default)
    if v is None or v.strip() == "" or v.strip().startswith(_PLACEHOLDER_PREFIX):
        raise RuntimeError(
            f"缺少必需配置 {name}。请复制 .env.example 为 .env 并填写（ROOT={ROOT}）"
        )
    return v.strip()


@dataclass
class Settings:
    # 麦当劳 MCP
    mcp_token: str
    mcp_server_url: str = "https://mcp.mcd.cn"

    # 大模型（OpenAI 兼容协议，默认本地 vLLM）
    llm_base_url: str = "http://localhost:8001/v1"
    llm_api_key: str = "EMPTY"
    llm_model: str = "Qwen3.8-27B-VL"

    # 账号（个人信息，只存 .env，严禁入库）
    test_phone: str = ""
    default_store_id: str = ""
    delivery_address: str = ""
    address_id: str = ""
    lat: float = 39.8628
    lon: float = 116.3669

    # 语音
    asr_model: str = "large-v3"
    asr_device: str = "cuda"
    asr_compute_type: str = "float16"
    tts_voice: str = "zh-CN-XiaoxiaoNeural"

    # 人设：gentle（默认，合规安全）/ sarcastic（仅吐槽工作与生活）
    portrait_mode: str = "gentle"

    # MCP 缓存与限流
    cache_ttl: int = 1800          # 静态数据缓存 30 分钟
    max_retry: int = 1             # 读接口失败重试次数（写接口永不重试）

    # 服务
    host: str = "0.0.0.0"
    port: int = 8000
    db_path: str = str(ROOT / "data" / "mcdinner.db")

    # 只允许这些工具走缓存（其余一律实时）
    cacheable_tools: tuple[str, ...] = field(default=(
        "list-nutrition-foods", "query-meals", "query-meal-detail",
        "campaign-calendar", "query-nearby-stores", "query-store-coupons",
        "available-coupons", "query-my-coupons", "delivery-query-addresses",
        "delivery-query-stores", "query-my-account", "mall-points-products",
        "mall-product-detail", "now-time-info",
    ))

    # 写操作：任何情况下都不重试，避免重复下单 / 重复领券
    mutating_tools: tuple[str, ...] = field(default=(
        "create-order", "cancel-order", "auto-bind-coupons",
        "draw-lottery", "mall-create-order", "party-order-create",
        "delivery-create-address",
    ))


def load_settings() -> Settings:
    return Settings(
        mcp_token=_need("MCP_TOKEN"),
        mcp_server_url=os.getenv("MCP_SERVER_URL", "https://mcp.mcd.cn").strip(),
        llm_base_url=os.getenv("LLM_BASE_URL", "http://localhost:8001/v1").strip(),
        llm_api_key=os.getenv("LLM_API_KEY", "EMPTY").strip() or "EMPTY",
        llm_model=os.getenv("LLM_MODEL", "Qwen3.8-27B-VL").strip(),
        test_phone=os.getenv("TEST_PHONE", "").strip(),
        default_store_id=os.getenv("DEFAULT_STORE_ID", "").strip(),
        delivery_address=os.getenv("DELIVERY_ADDRESS", "").strip(),
        address_id=os.getenv("ADDRESS_ID", "").strip(),
        lat=float(os.getenv("LAT", "39.8628")),
        lon=float(os.getenv("LON", "116.3669")),
        asr_model=os.getenv("ASR_MODEL", "large-v3"),
        asr_device=os.getenv("ASR_DEVICE", "cuda"),
        asr_compute_type=os.getenv("ASR_COMPUTE_TYPE", "float16"),
        tts_voice=os.getenv("TTS_VOICE", "zh-CN-XiaoxiaoNeural"),
        portrait_mode=os.getenv("PORTRAIT_MODE", "gentle"),
        cache_ttl=int(os.getenv("CACHE_TTL", "1800")),
        max_retry=int(os.getenv("MAX_RETRY", "1")),
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", "8000")),
    )


settings = load_settings()
