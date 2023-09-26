import json
import logging
import os

from fastapi import FastAPI
from fastapi import Request
from fastapi.middleware.cors import CORSMiddleware

from sandbox_func.request.SFInnerEventRequest import SFInnerEventRequest
from sandbox_func.common.lang import logger_setting
from sandbox_func.request.SFRequest import SFRequest
from sandbox_func.service.SandboxFuncService import SandboxFuncService
from sandbox_func.service.SandboxCallbackService import SandboxCallbackService

logger_setting.init()
logger = logging.getLogger(__name__)
app = FastAPI(title="Autowork Sandbox Function")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health():
    return {
        "pid": os.getpid()
    }


@app.post("/sandbox/call/{app_id}/{func_id}")
async def call_sandbox_func(app_id: str, func_id: str, req: Request):
    try:
        service = SandboxFuncService()
        data = await req.body()
        if data != b'':
            data = await req.json()

        request = SFRequest(app_id=app_id, func_id=func_id, input=data)
        response = await service.call(request)

        # 回调
        SandboxCallbackService.callback(request, response)

        if response.result:
            return response.result
        elif response.error:
            return {"message": str(response.error), "success": False}
    except BaseException as e:
        logger.exception(e)
        return {"message": str(e), "success": False}


@app.post("/event-invoke")
async def call_sandbox_func_async(req: Request):
    try:
        service = SandboxFuncService()
        data = await req.json()
        param = json.loads(data['body'])
        if param is None or param['appId'] is None or param['funcId'] is None:
            return {"message": '参数错误，请指定云函数的appId与funcId', "success": False}

        request = SFRequest(app_id=param['appId'], func_id=param['funcId'], input=param['input'])
        response = await service.call(request)

        # 如果是异步执行，且请求参数指定了hook，则进行回调
        exec_mode = os.getenv('exec_mode')
        if exec_mode == 'async':
            SandboxCallbackService.callback(request, response)

        if response.result:
            return response.result
        elif response.error:
            return {"message": str(response.error), "success": False}
    except BaseException as e:
        logger.exception(e)
        return {"message": str(e), "success": False}

