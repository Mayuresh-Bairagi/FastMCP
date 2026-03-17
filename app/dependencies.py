from functools import lru_cache

from app.core.config import Settings, get_settings
from app.core.security import SecurityService
from app.services.mcp_service import MCPService


@lru_cache(maxsize=1)
def settings() -> Settings:
    return get_settings()


@lru_cache(maxsize=1)
def security_service() -> SecurityService:
    return SecurityService(settings())


@lru_cache(maxsize=1)
def mcp_service() -> MCPService:
    return MCPService(settings(), security_service())
