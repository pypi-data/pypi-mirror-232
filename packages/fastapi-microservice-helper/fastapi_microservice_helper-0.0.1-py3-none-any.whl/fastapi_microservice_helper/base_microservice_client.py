from dataclasses import dataclass

from fastapi.encoders import jsonable_encoder
from requests import Session, Request


@dataclass
class MicroserviceOption:
    is_json: bool = True
    headers: dict = None


class BaseMicroserviceClient:
    http_client: Session = Session()

    @staticmethod
    def send(url: str, query_params: dict, body_params: any, option: MicroserviceOption = None):
        if not option:
            option = MicroserviceOption()
        request_config = {
            'method': 'POST',
            'url': url,
            'headers': option.headers,
            'params': query_params,
            'data': body_params if not option.is_json else None,
            'json': jsonable_encoder(body_params) if option.is_json else None,
        }

        prepped_request = BaseMicroserviceClient.http_client.prepare_request(Request(**request_config))
        return BaseMicroserviceClient.http_client.send(prepped_request)
