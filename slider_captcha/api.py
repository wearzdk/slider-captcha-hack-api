import os
import random
import time
from fastapi import FastAPI, Body
from typing import Annotated, List

from pydantic import BaseModel, Field
from slider_captcha.cBezier import bezierTrajectory

from slider_captcha.captcha import SliderCaptcha
app = FastAPI()


def generate_slide_action(x: int):
    """
    生成滑动验证码轨迹
    """
    end_y = random.randint(0, 20)
    start = [0, 0]
    end = [x, end_y]
    bezier = bezierTrajectory()
    # 在终点来回摆动的次数
    cbb = random.randint(1, 3)
    # 摆动幅度
    yhh = random.randint(5, 10)
    # 滑动节点数
    numberList = random.randint(100, 120)
    trackArr = bezier.trackArray(
        start, end, numberList=numberList, le=4, deviation=10, type=2, cbb=cbb, yhh=yhh)['trackArray']
    # 全部取整
    for item in trackArr:
        item[0] = round(item[0])
        item[1] = round(item[1])
    return trackArr.tolist()


class SliderCaptchaResp(BaseModel):
    code: int = Field(200, description="状态码")
    x: int = Field(..., description="滑块x坐标")
    time_consuming: float = Field(..., description="耗时")
    track: list = Field([], description="轨迹")


@app.post("/slider_captcha")
async def slider_captcha(
    img_slider: Annotated[str, Body(description="滑块图片")],
    img_background: Annotated[str, Body(description="背景图片")],
    auto_cut: Annotated[bool, Body(description="是否自动裁剪滑块图片")] = True,
    with_track: Annotated[bool, Body(description="是否返回轨迹")] = False,
    key: Annotated[str, Body(description="验证密码")] = ""
) -> SliderCaptchaResp:
    """滑动验证码"""
    # 简单验证
    KEY = os.environ.get("SLIDER_CAPTCHA_KEY", "")
    if KEY and key != KEY:
        return SliderCaptchaResp(code=403, top_left=0, time_consuming=0, track=[])
    slider_captcha = SliderCaptcha()
    start_time = time.time()
    x = slider_captcha.do_captcha(img_slider, img_background, auto_cut)
    track = []
    if with_track:
        track = generate_slide_action(x)

    return SliderCaptchaResp(
        code=200,
        x=x,
        time_consuming=time.time() - start_time,
        track=track,
    )


@app.post("/track")
async def track(
    start: Annotated[str, Body(description="起始坐标 如0,0")],
    end: Annotated[str, Body(description="结束坐标 如100,10")],
    numberList: Annotated[int, Body(description="轨迹点数量")] = 100,
    le: Annotated[int, Body(description="贝塞尔曲线阶数 越大越复杂")] = 4,
    deviation: Annotated[int, Body(description="轨迹上下波动的范围")] = 10,
    bias: Annotated[float, Body(description="波动范围的分布位置")] = 0.5,
    type: Annotated[int, Body(
        description="滑动类型,0表示均速滑动，1表示先慢后快，2表示先快后慢，3表示先慢中间快后慢")] = 0,
    cbb: Annotated[int, Body(description="在终点来回摆动的次数")] = 0,
    yhh: Annotated[int, Body(description="摆动幅度")] = 10,
) -> List:
    """滑动验证码轨迹"""
    bezier = bezierTrajectory()
    start = start.split(",")
    start_int = [int(item) for item in start]
    end = end.split(",")
    end_int = [int(item) for item in end]
    trackArr = bezier.trackArray(
        start_int, end_int, numberList=numberList, le=le, deviation=deviation, type=type, cbb=cbb, yhh=yhh, bias=bias)['trackArray']

    # 全部取整
    for item in trackArr:
        item[0] = round(item[0])
        item[1] = round(item[1])
    return trackArr.tolist()
