from typing import Any, Optional
import json
from datetime import datetime, timedelta
import redis
from app.core.config import get_settings

settings = get_settings()

class CacheService:
    def __init__(self):
        self.redis_client = redis.Redis(
            host=settings.redis_host,
            port=settings.redis_port,
            db=0,
            decode_responses=True
        )
        
    async def get(self, key: str) -> Optional[Any]:
        """
        从缓存获取数据
        """
        try:
            data = self.redis_client.get(key)
            return json.loads(data) if data else None
        except Exception:
            return None
            
    async def set(
        self,
        key: str,
        value: Any,
        expire_seconds: int = 300  # 默认5分钟过期
    ) -> bool:
        """
        将数据存入缓存
        """
        try:
            self.redis_client.setex(
                key,
                expire_seconds,
                json.dumps(value)
            )
            return True
        except Exception:
            return False
            
    async def delete(self, key: str) -> bool:
        """
        删除缓存数据
        """
        try:
            self.redis_client.delete(key)
            return True
        except Exception:
            return False
            
    async def clear_pattern(self, pattern: str) -> bool:
        """
        清除匹配模式的所有缓存
        """
        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                self.redis_client.delete(*keys)
            return True
        except Exception:
            return False
            
    def generate_key(self, prefix: str, **kwargs) -> str:
        """
        生成缓存键
        """
        params = sorted(kwargs.items())
        param_str = "_".join(f"{k}:{v}" for k, v in params)
        return f"{prefix}:{param_str}" 