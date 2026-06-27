from urllib.parse import urlencode

import httpx
from fastapi import APIRouter, HTTPException, Request, Response

from app.core.config import settings

router = APIRouter(tags=["campus-map"])
proxy_router = APIRouter()

AMAP_REST_BASE = "https://restapi.amap.com"


@router.get("/campus-map/config")
def campus_map_config():
    if not settings.AMAP_WEB_KEY or not settings.AMAP_SECURITY_JS_CODE:
        raise HTTPException(status_code=503, detail="校园地图服务尚未配置")
    return {
        "success": True,
        "data": {
            "key": settings.AMAP_WEB_KEY,
            "center": [113.6416887, 34.862226],
            "zoom": 17,
        },
    }


@proxy_router.api_route(
    "/_AMapService/{path:path}",
    methods=["GET", "POST"],
    include_in_schema=False,
)
async def amap_security_proxy(path: str, request: Request):
    if not settings.AMAP_SECURITY_JS_CODE:
        raise HTTPException(status_code=503, detail="校园地图安全代理尚未配置")

    params = list(request.query_params.multi_items())
    params = [(key, value) for key, value in params if key != "jscode"]
    params.append(("jscode", settings.AMAP_SECURITY_JS_CODE))
    target_url = f"{AMAP_REST_BASE}/{path}?{urlencode(params)}"

    body = await request.body()
    headers = {
        "content-type": request.headers.get(
            "content-type", "application/x-www-form-urlencoded"
        )
    }
    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            upstream = await client.request(
                request.method,
                target_url,
                content=body or None,
                headers=headers,
            )
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail="高德地图代理请求失败") from exc

    # 检测是否为 JSONP 请求（高德 SDK 通过 JSONP 发起跨域安全请求）
    is_jsonp = any(key == "callback" for key, _ in params)

    # JSONP 响应必须返回 application/javascript，否则浏览器 strict MIME 检测会拒绝执行
    response_headers: dict[str, str] = {}
    if is_jsonp:
        response_headers["content-type"] = "application/javascript; charset=utf-8"
    else:
        content_type = upstream.headers.get("content-type")
        if content_type:
            response_headers["content-type"] = content_type

    response_content = upstream.content
    # 上游可能返回纯 JSON 而非 JSONP 包裹，此时手动包裹 callback
    if is_jsonp and response_content:
        text = response_content.decode("utf-8", errors="replace").lstrip()
        if not text.startswith("callback(") and not text.startswith("jsonp_"):
            cb_param = [v for k, v in params if k == "callback"]
            cb_name = cb_param[0] if cb_param else "callback"
            response_content = f"/**/ {cb_name}({text});".encode("utf-8")

    return Response(
        content=response_content,
        status_code=upstream.status_code,
        headers=response_headers,
    )
