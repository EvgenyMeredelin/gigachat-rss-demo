from collections.abc import abstractmethod, Iterator
from datetime import datetime
from functools import cached_property
from typing import ClassVar, Self
from zoneinfo import ZoneInfo

import pycld2
import requests

from environs import env
env.read_env()

from gigachat import GigaChat
from more_itertools import constrained_batches
from nltk.tokenize import sent_tokenize

from enums import TimezoneKey
from models import GigaChatAccessToken


class GigaChatTokenReleaser:
    """GigaChat API access token releaser. """

    def __init__(
        self,
        *,
        timezone_key: TimezoneKey,
        over_ssh_tunnel: bool = False
    ) -> None:

        self.timezone_key = timezone_key
        self.over_ssh_tunnel = over_ssh_tunnel
        # for code running on your local machine -
        # after port forwarding, or SSH tunneling
        if over_ssh_tunnel:
            port = env("TUNNEL_TARGET_PORT")
            self.url = f"http://localhost:{port}/token"
        # for code running on your virtual machine
        else:
            self.url = env("TOKEN_RELEASER_URL")

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
            url=self.url,
            headers={"IAM-User-ID": env("IAM_USER_ID")}
        )
        self.n_tokens_released += 1
        return GigaChatAccessToken(**response.json())

    def _update(self) -> None:
        if self._token_expired:
            self.token = self._release_token()


class BaseChunker(Iterator):
    """Abstract base chunker class. """

    @cached_property
    @abstractmethod
    def batches(self) -> Iterator:
        raise NotImplementedError

    def __iter__(self) -> Self:
        return self

    def __next__(self) -> str:
        return " ".join(next(self.batches))


class TextChunker(BaseChunker):
    """
    An iterator of text chunks that are multiple of sentences.
    The language for splitting sentences is detected automatically.
    The length of each chunk, including spaces between sentences,
    does not exceed the `TextChunker.chunk_maxlen`.
    """

    chunk_maxlen: ClassVar[int] = 10_000

    def __init__(self, text: str) -> None:
        self.text = " ".join(text.split())

    @cached_property
    def batches(self) -> Iterator:
        return constrained_batches(
            iterable=sent_tokenize(self.text, self.language),
            max_size=self.__class__.chunk_maxlen,
            get_len=self._get_sentence_length
        )

    @property
    def language(self) -> str:
        return pycld2.detect(self.text)[2][0][0].lower()

    def _get_sentence_length(self, sentence: str) -> int:
        return len(sentence) + 1  # plus trailing space


class GigaChunker(BaseChunker):
    """
    An iterator of text chunks that fully utilize the token
    context of the GigaChat, the `GigaChunker._context_size`.
    """

    _context_size: ClassVar[int] = 128_000

    def __init__(self, gigachat: GigaChat, text: str) -> None:
        self.gigachat = gigachat
        self.text_chunker = TextChunker(text)

    @cached_property
    def batches(self) -> Iterator:
        return constrained_batches(
            iterable=self.text_chunker,
            max_size=self.__class__._context_size,
            get_len=self._count_tokens
        )

    def _count_tokens(self, text: str) -> int:
        return self.gigachat.tokens_count([text])[0].tokens
