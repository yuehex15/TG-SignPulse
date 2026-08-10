"""Tests for account lock (race condition fix)."""
from __future__ import annotations

import asyncio

import pytest


@pytest.mark.asyncio
async def test_same_account_returns_same_lock():
    """Calling get_account_lock twice with the same name returns the same Lock."""
    from backend.utils.account_locks import get_account_lock

    lock1 = await get_account_lock("test_account")
    lock2 = await get_account_lock("test_account")
    assert lock1 is lock2, "Should return the same Lock object"


@pytest.mark.asyncio
async def test_different_accounts_different_locks():
    """Different account names get different Lock objects."""
    from backend.utils.account_locks import get_account_lock

    lock_a = await get_account_lock("account_a")
    lock_b = await get_account_lock("account_b")
    assert lock_a is not lock_b, "Different accounts should have different locks"


@pytest.mark.asyncio
async def test_concurrent_get_account_lock():
    """100 concurrent calls to get_account_lock for the same account
    should all receive the same Lock object (no race condition)."""
    from backend.utils.account_locks import get_account_lock

    async def worker(results: list, name: str):
        lock = await get_account_lock(name)
        results.append(id(lock))

    results: list = []
    tasks = [worker(results, "parallel_account") for _ in range(100)]
    await asyncio.gather(*tasks)

    unique_ids = len(set(results))
    assert unique_ids == 1, f"Expected 1 unique Lock, got {unique_ids}"


@pytest.mark.asyncio
async def test_lock_actually_acquires():
    """The Lock returned by get_account_lock works as expected."""
    from backend.utils.account_locks import get_account_lock

    lock = await get_account_lock("locking_test")
    async with lock:
        # If we get here without deadlock, the lock works
        pass
    assert not lock.locked(), "Lock should be released after context manager"