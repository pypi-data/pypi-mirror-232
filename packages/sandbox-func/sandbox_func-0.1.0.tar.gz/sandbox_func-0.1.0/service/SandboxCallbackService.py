import json

import httpx
from sandbox_func.common.log.AwLogger import AwLogger
from sandbox_func import SFResponse, SFRequest

log = AwLogger.getLogger(__name__)


class SandboxCallbackService:
    """异步任务回调处理，如果request里包含hook信息，则进行回调"""

    def __init__(self, request: SFRequest, response: SFResponse):
        self.req = request
        self.res = response

    @staticmethod
    def callback(req: SFRequest, res: SFResponse):
        hook = req.input.get('hook')
        if hook is not None:
            callback_url = dict(hook).get('url')
            data = {"result": res.result, "input": req.input, "progress": res.job.job_progress, "success": res.job.job_success, "error": res.job.job_error}
            client = httpx.Client()
            try:
                client.post(callback_url, json=json.dumps(data, ensure_ascii=False, default=lambda dclass: dclass.data))
                raise Exception('log test')
            except Exception as e:
                log.error(f"[SandboxCallbackService]:{e}")
