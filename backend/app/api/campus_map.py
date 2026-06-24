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

    response_headers = {}
    content_type = upstream.headers.get("content-type")
    if content_type:
        response_headers["content-type"] = content_type
    return Response(
        content=upstream.content,
        status_code=upstream.status_code,
        headers=response_headers,
    )
