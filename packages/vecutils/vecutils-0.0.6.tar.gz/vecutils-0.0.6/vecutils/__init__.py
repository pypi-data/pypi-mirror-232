import logging
from collections.abc import Awaitable, Callable, Iterable

import httpx

from vecutils.utils import chunk, gather_with_concurrency

logger = logging.getLogger(__name__)


async def batch_create_embeddings(
    texts: Iterable[str],
    embedding_fn: Callable[[list[str]], Awaitable[list[list[float]]]],
    batch_size: int = 16,
    concurrency: int = 10,
) -> list[tuple[int, list[float]]]:
    async def _create_embeddings(ordered_batch):
        indices, batch = zip(*ordered_batch, strict=True)
        try:
            embeddings = await embedding_fn(batch)

        except Exception:
            logger.exception("failed to create embeddings, texts: %s", batch)

            return False, zip(indices, batch, strict=True)

        return True, list(zip(indices, embeddings, strict=True))

    min_split_batch_size = 2
    ordered_embeddings = []

    futures = []
    for ordered_batch in chunk(enumerate(texts), size=batch_size):
        futures += [_create_embeddings(ordered_batch)]

    while True:
        if not futures:
            break

        responses = await gather_with_concurrency(concurrency, *futures)
        futures = []
        for response in responses:
            success, payload_or_result = response
            if success:
                ordered_embeddings += payload_or_result
                continue

            indices, batch = zip(*payload_or_result, strict=True)
            size = len(indices)
            if size >= min_split_batch_size:
                size //= 2
                futures += [
                    _create_embeddings(zip(indices[:size], batch[:size], strict=True)),
                ]
                futures += [
                    _create_embeddings(zip(indices[size:], batch[size:], strict=True)),
                ]
                continue

    ordered_embeddings.sort(key=lambda x: x[0])

    return ordered_embeddings


class Vectorizer:
    def __init__(self, url: str, model: str, timeout: int = 60) -> None:
        self.url = url
        self.model = model

        self.client = httpx.AsyncClient(timeout=timeout)

    def _format_response(self, response):
        return [x["embedding"] for x in response.json()["data"]]

    def create_embeddings(
        self,
        texts: list[str],
        timeout: int = 60,
    ) -> list[list[float]]:
        response = httpx.post(
            self.url,
            json={
                "input": texts,
                "model": self.model,
            },
            timeout=timeout,
        )

        return self._format_response(response)

    async def acreate_embeddings(
        self,
        texts: list[str],
        timeout: int = 60,
    ) -> list[list[float]]:
        response = await self.client.post(
            self.url,
            json={
                "input": texts,
                "model": self.model,
            },
            timeout=timeout,
        )

        return self._format_response(response)
