from pydantic import BaseModel


class SFInnerEventRequest(BaseModel):
    body: dict
    headers: dict
    queryString: dict
