from pydantic import BaseModel, AnyHttpUrl, ValidationError

class task(BaseModel):
    id: str
    status: str
    result: list[int]
    result_url: list[str]
    
class url_list(BaseModel):
    urls: list[str]