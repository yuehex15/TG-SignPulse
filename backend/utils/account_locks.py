from __future__ import annotations

import asyncio

_ACCOUNT_LOCKS: dict[str, asyncio.Lock] = {}
_ACCOUNT_LOCK_DICT_LOCK = asyncio.Lock()


async def get_account_lock(account_name: str) -> asyncio.Lock:
    """Get or create an account-specific lock.

    Uses a separate lock to protect the dictionary to avoid a race condition
    where two concurrent callers both create a new Lock for the same account.
    """
    lock = _ACCOUNT_LOCKS.get(account_name)
    if lock is not None:
        return lock
    async with _ACCOUNT_LOCK_DICT_LOCK:
        # Double-check after acquiring the dict lock.
        lock = _ACCOUNT_LOCKS.get(account_name)
        if lock is not None:
            return lock
        lock = asyncio.Lock()
        _ACCOUNT_LOCKS[account_name] = lock
    return lock
