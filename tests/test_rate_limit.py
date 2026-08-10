"""Tests for rate limiter."""
from __future__ import annotations

import time

import pytest
from fastapi import HTTPException

from backend.core.rate_limit import InMemoryRateLimiter


class TestInMemoryRateLimiter:
    def setup_method(self):
        self.limiter = InMemoryRateLimiter()

    def test_first_hit_passes(self):
        """First hit within the limit should pass."""
        self.limiter.hit(
            scope="test",
            key="user1",
            max_attempts=5,
            window_seconds=60,
            block_seconds=120,
            detail="too many",
        )
        # No exception raised = pass

    def test_under_limit_passes(self):
        """Hits up to max_attempts should pass."""
        for _ in range(5):
            self.limiter.hit(
                scope="test",
                key="user2",
                max_attempts=5,
                window_seconds=60,
                block_seconds=120,
                detail="too many",
            )
        # No exception = pass

    def test_exceeds_limit_blocks(self):
        """Exceeding max_attempts should raise 429."""
        for _ in range(5):
            self.limiter.hit(
                scope="test",
                key="user3",
                max_attempts=5,
                window_seconds=60,
                block_seconds=120,
                detail="too many requests",
            )
        with pytest.raises(HTTPException) as exc:
            self.limiter.hit(
                scope="test",
                key="user3",
                max_attempts=5,
                window_seconds=60,
                block_seconds=120,
                detail="too many requests",
            )
        assert exc.value.status_code == 429
        assert "Retry-After" in exc.value.headers

    def test_different_keys_independent(self):
        """Different keys should not share rate limits."""
        for _ in range(5):
            self.limiter.hit(
                scope="test",
                key="user_a",
                max_attempts=5,
                window_seconds=60,
                block_seconds=120,
                detail="too many",
            )
        # Key 'user_a' is blocked now, but 'user_b' should still pass
        self.limiter.hit(
            scope="test",
            key="user_b",
            max_attempts=5,
            window_seconds=60,
            block_seconds=120,
            detail="too many",
        )

    def test_reset_clears_block(self):
        """Reset should clear the block for a specific key."""
        for _ in range(5):
            self.limiter.hit(
                scope="test",
                key="user4",
                max_attempts=5,
                window_seconds=60,
                block_seconds=120,
                detail="too many",
            )
        with pytest.raises(HTTPException):
            self.limiter.hit(
                scope="test",
                key="user4",
                max_attempts=5,
                window_seconds=60,
                block_seconds=120,
                detail="too many",
            )
        self.limiter.reset("test", "user4")
        # After reset, should pass again
        self.limiter.hit(
            scope="test",
            key="user4",
            max_attempts=5,
            window_seconds=60,
            block_seconds=120,
            detail="too many",
        )

    def test_window_expires(self):
        """Old attempts should expire after the window."""
        for _ in range(5):
            self.limiter.hit(
                scope="test",
                key="user5",
                max_attempts=5,
                window_seconds=1,   # 1 second window
                block_seconds=2,
                detail="too many",
            )
        # Wait for window to expire
        time.sleep(1.1)
        # Should pass again because old attempts expired
        self.limiter.hit(
            scope="test",
            key="user5",
            max_attempts=5,
            window_seconds=1,
            block_seconds=2,
            detail="too many",
        )

    def test_reset_all(self):
        """reset_all should clear all buckets."""
        for _ in range(5):
            self.limiter.hit(
                scope="test",
                key="user6",
                max_attempts=5,
                window_seconds=60,
                block_seconds=120,
                detail="too many",
            )
        with pytest.raises(HTTPException):
            self.limiter.hit(
                scope="test",
                key="user6",
                max_attempts=5,
                window_seconds=60,
                block_seconds=120,
                detail="too many",
            )
        self.limiter.reset_all()
        self.limiter.hit(
            scope="test",
            key="user6",
            max_attempts=5,
            window_seconds=60,
            block_seconds=120,
            detail="too many",
        )