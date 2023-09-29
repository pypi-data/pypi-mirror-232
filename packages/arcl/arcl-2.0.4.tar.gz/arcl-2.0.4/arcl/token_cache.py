from msal_extensions import (
    FilePersistence,
    PersistedTokenCache,
    build_encrypted_persistence,
)

from arcl.config import get_token_path


def build_persistence(location, fallback_to_plaintext=False):
    """Build a suitable persistence instance based your current OS"""
    try:
        return build_encrypted_persistence(location)
    except:  # pylint:disable=bare-except
        if not fallback_to_plaintext:
            raise
        return FilePersistence(location)


def get_token_cache(env):
    """Get token from the cache"""
    persistence = build_persistence(get_token_path(env), True)
    token_cache = PersistedTokenCache(persistence)
    return token_cache
