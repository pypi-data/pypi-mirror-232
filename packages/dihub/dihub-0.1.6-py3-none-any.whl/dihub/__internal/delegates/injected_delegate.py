from src.dihub.__internal.helpers import get_inject_token_str
from src.dihub.types import InjectToken


class InjectedDelegate:
    __token: InjectToken

    def __init__(self, token: InjectToken):
        self.__token = token

    @property
    def token(self) -> str:
        return get_inject_token_str(self.__token)
