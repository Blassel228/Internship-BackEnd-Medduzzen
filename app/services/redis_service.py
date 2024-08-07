import csv
import json
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.CRUD.company_crud import company_crud
from app.CRUD.member_crud import member_crud
from app.db.base import redis_connect
from app.exceptions.custom_exceptions import check_user_permissions


class RedisService:
    def __init__(self):
        self.redis = redis_connect()

    async def cache_quiz_result(self, data: dict) -> None:
        data_json = json.dumps(data)
        key = f"quiz_result:{data['quiz_id']}:{data['user_id']}:{data['company_id']}"
        self.redis.set(key, data_json, ex=172800)

    async def get_from_cache(
        self, key: str, user_id: int, db: AsyncSession, company_name: str
    ) -> list:
        member = await member_crud.get_one(id_=user_id, db=db)
        company = await company_crud.get_one_by_filter(
            filters={"name": company_name}, db=db
        )
        check_user_permissions(member=member, company=company, user_id=user_id)
        keys = await self.redis.keys(key)
        cache = await self.redis.mget(keys)
        if not cache:
            raise HTTPException(status_code=404, detail="Cache was not found")
        parsed_values = [json.loads(value) for value in cache]
        return parsed_values

    async def admin_get_cache_for_user(
        self, id_: int, quiz_id: int, user_id: int, db: AsyncSession, company_name: str
    ) -> list:
        key = f"quiz_result:{quiz_id}:{id_}:*"
        return await self.get_from_cache(
            key=key, db=db, user_id=user_id, company_name=company_name
        )

    async def get_cached_result(
        self, quiz_id: int, user_id: int, db: AsyncSession, company_name: str
    ) -> list:
        key = f"quiz_result:{quiz_id}:{user_id}:*"
        return await self.get_from_cache(
            key=key, db=db, user_id=user_id, company_name=company_name
        )

    async def user_get_its_result(self, user_id: int) -> list:
        key = f"quiz_result:*:{user_id}:*"
        keys = await self.redis.keys(key)
        cache = await self.redis.mget(keys)
        if not cache:
            raise HTTPException(status_code=404, detail="Cache was not found")
        parsed_values = [json.loads(value) for value in cache]
        return parsed_values

    async def admin_get_all_cache_by_company_id(
        self, user_id: int, company_name: str, db: AsyncSession
    ) -> list:
        company = await company_crud.get_one_by_filter(
            filters={"name": company_name}, db=db
        )
        if company is None:
            raise HTTPException(status_code=404, detail="There is no such a company")
        key = f"quiz_result:*:*:{company.id}"
        return await self.get_from_cache(
            key=key, db=db, user_id=user_id, company_name=company_name
        )

    async def admin_get_all_results_by_quiz_id(
        self, quiz_id: int, user_id: int, company_name: str, db: AsyncSession
    ) -> list:
        key = f"quiz_result:{quiz_id}:*:*"
        return await self.get_from_cache(
            key=key, db=db, user_id=user_id, company_name=company_name
        )

    async def export_cached_results_for_one_user_to_csv(
        self, user_id: int, id_: int, quiz_id: int, company_name: str, db: AsyncSession
    ):

        cache = await self.admin_get_cache_for_user(
            id_=id_, quiz_id=quiz_id, db=db, company_name=company_name, user_id=user_id
        )

        if cache is None:
            raise HTTPException(status_code=404, detail="Cache was not found")

        headers = []
        row = []

        for key in cache[0].keys():
            headers.append(key)

        for user_cache in cache:
            for user_data in user_cache.values():
                row.append(user_data)

        with open("cache.csv", "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(headers)
            writer.writerow(row)
        return cache

    async def export_all_cached_results_to_csv(
        self, user_id: int, quiz_id: int, company_name: str, db: AsyncSession
    ) -> list:

        cache = await self.admin_get_all_results_by_quiz_id(
            user_id=user_id, quiz_id=quiz_id, db=db, company_name=company_name
        )

        if cache is None:
            raise HTTPException(status_code=404, detail="Cache was not found")

        headers = []
        row = []

        for key in cache[0].keys():
            headers.append(key)

        with open("cache.csv", "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(headers)
            for user in cache:
                for user_data in user.values():
                    row.append(user_data)
                writer.writerow(row)
                row = []

        return cache


redis_service = RedisService()
