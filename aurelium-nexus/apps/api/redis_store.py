import os
import time
import logging

logger = logging.getLogger('aurelium.redis')


class InMemoryStore:
    def __init__(self):
        self._revoked_jtis = {}  # token -> expiry
        self._revoked_subjects = {}  # subject -> expiry

    def set_revoked_jti(self, token: str, expiry: int):
        self._revoked_jtis[token] = expiry

    def is_jti_revoked(self, token: str) -> bool:
        exp = self._revoked_jtis.get(token)
        if not exp:
            return False
        if exp < int(time.time()):
            try:
                del self._revoked_jtis[token]
            except Exception:
                pass
            return False
        return True

    def revoke_subject(self, subject: str, expiry: int):
        self._revoked_subjects[subject] = expiry

    def is_subject_revoked(self, subject: str) -> bool:
        exp = self._revoked_subjects.get(subject)
        if not exp:
            return False
        if exp < int(time.time()):
            try:
                del self._revoked_subjects[subject]
            except Exception:
                pass
            return False
        return True


_STORE = None


def _get_redis_client():
    global _STORE
    if _STORE is not None:
        return _STORE
    # Try to use redis if available and REDIS_URL is set
    url = os.getenv('REDIS_URL')
    if url:
        try:
            import redis
            r = redis.from_url(url)

            class RedisStore:
                def __init__(self, rclient):
                    self.r = rclient

                def set_revoked_jti(self, token: str, expiry: int):
                    # store with TTL
                    ttl = max(1, expiry - int(time.time()))
                    try:
                        self.r.setex(f"revoked_jti:{token}", ttl, str(expiry))
                    except Exception:
                        logger.exception('redis setex failed')

                def is_jti_revoked(self, token: str) -> bool:
                    try:
                        return self.r.exists(f"revoked_jti:{token}") == 1
                    except Exception:
                        logger.exception('redis exists failed')
                        return False

                def revoke_subject(self, subject: str, expiry: int):
                    ttl = max(1, expiry - int(time.time()))
                    try:
                        self.r.setex(f"revoked_subject:{subject}", ttl, str(expiry))
                    except Exception:
                        logger.exception('redis setex failed')

                def is_subject_revoked(self, subject: str) -> bool:
                    try:
                        return self.r.exists(f"revoked_subject:{subject}") == 1
                    except Exception:
                        logger.exception('redis exists failed')
                        return False

            _STORE = RedisStore(r)
            logger.info('Using RedisStore for revocation')
            return _STORE
        except Exception:
            logger.exception('Redis not available, falling back to in-memory store')
    # Fallback
    _STORE = InMemoryStore()
    logger.info('Using InMemoryStore for revocation')
    return _STORE


def set_revoked_jti(token: str, expiry: int):
    _get_redis_client().set_revoked_jti(token, expiry)


def is_jti_revoked(token: str) -> bool:
    return _get_redis_client().is_jti_revoked(token)


def revoke_subject(subject: str, expiry: int):
    _get_redis_client().revoke_subject(subject, expiry)


def is_subject_revoked(subject: str) -> bool:
    return _get_redis_client().is_subject_revoked(subject)
