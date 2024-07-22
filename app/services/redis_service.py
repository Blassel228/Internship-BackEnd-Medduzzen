import json
from app.db.base import redis_connect


class RedisService:
    async def cache_quiz_result(self, data: dict):
        redis = await redis_connect()
        data_json = json.dumps(data)
        key = f"quiz_result:{data['quiz']['id']}:{data['user']['id']}"
        await redis.set(key, data_json, ex=172800)

    async def get_cached_result(self, quiz_id, user_id):
        redis = await redis_connect()
        key = f"quiz_result:{quiz_id}:{user_id}"
        cached_data_json = await redis.get(key)
        if cached_data_json:
            return json.loads(cached_data_json)
        return None


redis_service = RedisService()
