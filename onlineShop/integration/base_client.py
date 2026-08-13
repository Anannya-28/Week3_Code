"""
BaseExternalClient — shared retry + timeout logic.
All integration clients (payment, notification, shipping) inherit from this.
"""

import asyncio
import logging
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

MAX_RETRIES: int = 3
BASE_BACKOFF: float = 0.5   
TIMEOUT: float = 5.0         


class ExternalClientError(Exception):
    """Raised when all retry attempts for an external call are exhausted."""


class BaseExternalClient(ABC):
    """
    Abstract base that wraps any coroutine with:
      - per-attempt asyncio timeout
      - exponential back-off retry
      - structured logging on every attempt, success, and failure
    """

    client_name: str = "external"  

    @abstractmethod
    async def _call(self, **kwargs) -> dict:
        """Single attempt at the external service. Implement in subclass."""

    async def execute(self, **kwargs) -> dict:
        """
        Public entry point: calls _call() with retry + timeout.
        Raises ExternalClientError if every attempt fails.
        """
        last_exc: Exception | None = None

        for attempt in range(1, MAX_RETRIES + 1):
            try:
                result = await asyncio.wait_for(
                    self._call(**kwargs),
                    timeout=TIMEOUT,
                )
                logger.info(
                    "%s_succeeded",
                    self.client_name,
                    extra={**kwargs, "attempt": attempt},
                )
                return result

            except asyncio.TimeoutError as exc:
                last_exc = exc
                logger.warning(
                    "%s_timeout",
                    self.client_name,
                    extra={**kwargs, "attempt": attempt, "timeout": TIMEOUT},
                )

            except Exception as exc:          
                last_exc = exc
                logger.warning(
                    "%s_error",
                    self.client_name,
                    extra={**kwargs, "attempt": attempt, "error": str(exc)},
                )

            if attempt < MAX_RETRIES:
                backoff = BASE_BACKOFF * (2 ** (attempt - 1))
                logger.debug(
                    "%s_retry_backoff",
                    self.client_name,
                    extra={**kwargs, "backoff_seconds": backoff},
                )
                await asyncio.sleep(backoff)

        logger.error(
            "%s_all_retries_failed",
            self.client_name,
            extra={**kwargs, "attempts": MAX_RETRIES},
        )
        raise ExternalClientError(
            f"{self.client_name} failed after {MAX_RETRIES} attempts"
        ) from last_exc