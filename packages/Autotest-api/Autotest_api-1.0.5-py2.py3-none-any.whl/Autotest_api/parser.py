from pydantic import BaseModel, Field, validator
from typing import Optional, Union, Any, List, Dict


class HooksModel(BaseModel):
    """hook 钩子格式校验"""
    request: List[str] = []
    response: List[str] = []


class ConfigModel(BaseModel):
    """config 配置 模型校验"""
    name: Optional[str] = ''
    base_url: Optional[str] = None
    variables: Union[str, Dict] = {}
    fixtures: Union[str, List[str]] = []
    parameters: Union[List, str, Dict] = None
    allure: Dict = {}
    mark: Union[str, List[str]] = []
    hooks: HooksModel = {}
    export: Union[str, List[str]] = []

    @validator('export', pre=True)
    def pre_export(cls, value):
        """export 支持list 和 str"""
        if isinstance(value, str):
            exports = value.split(',')
            return [e.lstrip(" ").rstrip(" ") for e in exports]
        else:
            return value

    @validator('base_url')
    def check_base_url(cls, value):
        """判断 base_url合法性"""
        if str(value).startswith('http://') or str(value).startswith('https://') \
                or str(value).startswith('ws://') or str(value).startswith('wss://'):
            return value
        else:
            raise ValueError('base_url must start with "http://" or "https://" ')


class RequestModel(BaseModel):
    """request 发送请求模型"""
    url: str = ...
    method: str = ...
    params: Optional[Any] = None
    data: Optional[Any] = None
    headers: Optional[Any] = None
    cookies: Optional[Any] = None
    files: Optional[Any] = None
    auth: Optional[Any] = None
    timeout: Optional[Any] = None
    allow_redirects: Optional[bool] = True
    proxies: Optional[Any] = None
    hooks: HooksModel = {}
    stream: Optional[Any] = None
    verify: Optional[Any] = None
    cert: Optional[Any] = None
    json_: Optional[Any] = Field(alias='json', default=None)

    @validator('method')
    def check_method(cls, value):
        """判断 method 合法性"""
        if str(value).upper() in ["GET", "POST", "PUT", "DELETE", "HEAD", "OPTIONS", "PATCH"]:
            return value
        else:
            raise ValueError('method must be : "GET", "POST", "PUT", "DELETE", "HEAD", "OPTIONS", "PATCH"')


class StepModel(BaseModel):
    """test step 模型校验"""
    name: Optional[str]
    variables: Union[str, Dict] = {}
    fixtures: Union[str, List[str]] = []
    parameters: Union[List, str, Dict] = None
    allure: Dict = {}
    mark: Union[str, List[str]] = []
    export: Union[str, List[str]] = []
    print: Optional[str] = None
    sleep: Union[int, float, str] = 0
    skip: Optional[str] = None
    skipif: Optional[str] = None
    api: Optional[str] = None
    ws: Optional[dict] = {}
    send: Optional[Any] = None
    recv: Optional[Any] = None
    request: Optional[RequestModel] = {}
    extract: Optional[dict] = None
    validate_: Optional[List[dict]] = Field(alias='validate', default={})

    # class Config:
    #     allow_population_by_field_name = True
    #     extra = Extra.allow

    @validator('export', pre=True)
    def pre_export(cls, value):
        """export 支持list 和 str"""
        if isinstance(value, str):
            exports = value.split(',')
            return [e.lstrip(" ").rstrip(" ") for e in exports]
        else:
            return value


def verify_case_raw(raw_dict: dict):
    """
    校验 yaml 文件内容
    """
    new_dict = dict()
    if isinstance(raw_dict, dict):
        for key, value in raw_dict.items():
            if key == 'config':
                conf = ConfigModel(**value)
                new_dict[key] = conf.dict(exclude_unset=True, by_alias=True)
            else:
                if isinstance(value, dict):
                    step = StepModel(**value)
                    new_dict[key] = step.dict(exclude_unset=True, by_alias=True)
                elif isinstance(value, list):
                    steps = []
                    for step in value:
                        if isinstance(step, dict):
                            new_step = StepModel(**step)
                            steps.append(new_step.dict(exclude_unset=True, by_alias=True))
                    new_dict[key] = steps
                else:
                    new_dict[key] = []
    return new_dict
