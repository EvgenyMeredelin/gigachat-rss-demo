from datetime import datetime
from zoneinfo import ZoneInfo

import requests
from environs import env
env.read_env()

from enums import TimezoneKey
from models import GigaChatAccessToken


class GigaChatTokenReleaser:
    """GigaChat API access token releaser. """

    def __init__(self, timezone_key: TimezoneKey) -> None:
        self.timezone_key = timezone_key
        self.n_tokens_released = 0
        self.token = self._release_token()

    def __call__(self) -> str:
        self._update()
        return self.token.value

    @property
    def timezone_key(self) -> TimezoneKey:
        return self._timezone_key

    @timezone_key.setter
    def timezone_key(self, value: TimezoneKey) -> None:
        assert value in TimezoneKey
        self._timezone_key = value
        self.zoneinfo = ZoneInfo(value)

    @property
    def _token_expired(self) -> bool:
        return datetime.now(self.zoneinfo) >= self.token.expires

    def _release_token(self) -> GigaChatAccessToken:
        response = requests.post(
            url=env("TOKEN_RELEASER_URL"),
            headers={"IAM-User-ID": env("IAM_USER_ID")}
        )
        self.n_tokens_released += 1
        return GigaChatAccessToken(**response.json())

    def _update(self) -> None:
        if self._token_expired:
            self.token = self._release_token()
