from src.dihub.__internal.delegates import InjectedDelegate
from src.dihub.types import InjectToken


def inject(token: InjectToken) -> InjectedDelegate:
    return InjectedDelegate(token)
