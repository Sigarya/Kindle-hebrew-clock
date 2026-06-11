from fastapi import APIRouter, Request, Query
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import Response

from app.services import clock, weather as weather_svc

router = APIRouter()

DEFAULT_FONT = clock.DEFAULT_FONT


@router.get(
    "/",
    responses={200: {"content": {"image/png": {}}}},
    response_class=Response,
)
@router.get(
    "/clock",
    responses={200: {"content": {"image/png": {}}}},
    response_class=Response,
)
@router.get(
    "/clock.png",
    responses={200: {"content": {"image/png": {}}}},
    response_class=Response,
)
async def get_clock(
    request: Request,
    font:      str = Query(default=DEFAULT_FONT),
    sleeptime: str = Query(default="0"),
    location:  str = Query(default="Tel Aviv"),
) -> Response:
    loc = location or "Tel Aviv"
    w = await weather_svc.get_weather(loc, request.app.state.http_client)
    img_bytes = await run_in_threadpool(
        clock.generate_clock_image,
        font_name  = font,
        sleep_time = sleeptime == "1",
        weather    = w,
    )
    return Response(
        content=img_bytes,
        media_type="image/png",
        headers={"Cache-Control": "no-cache"},
    )
