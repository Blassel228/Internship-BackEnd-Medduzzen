import csv
import json
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.CRUD.company_crud import company_crud
from app.CRUD.member_crud import member_crud
from app.db.base import redis_connect


class RedisService:
    async def cache_quiz_result(self, data: dict):
        redis = await redis_connect()
        data_json = json.dumps(data)
        key = f"quiz_result:{data['quiz_id']}:{data['user_id']}:{data['company_id']}"
        print(key)
        await redis.set(key, data_json, ex=172800)
        await redis.close()

    async def get_from_cache(
        self, key: str, user_id: int, db: AsyncSession, company_name: str
    ):
        member = await member_crud.get_one(id_=user_id, db=db)
        company = await company_crud.get_one_by_filter(
            filters={"name": company_name}, db=db
        )
        if company is None:
            raise HTTPException(status_code=404, detail="There is no such a company")
        if member is None:
            if company.owner_id != user_id:
                raise HTTPException(
                    status_code=403, detail="You have no right to get all users results"
                )
        if member is not None:
            if member.role != "admin":
                raise HTTPException(
                    status_code=403, detail="You do not have such rights"
                )
            if member.company_id != company.id:
                raise HTTPException(
                    status_code=403, detail="You are not a member of the company"
                )

        redis = await redis_connect()
        keys = await redis.keys(key)
        cache = await redis.mget(keys)
        if cache:
            parsed_values = [json.loads(value) for value in cache]
            return parsed_values
        await redis.close()
        return None

    async def admin_get_cache_for_user(
        self, id_: int, quiz_id: int, user_id: int, db: AsyncSession, company_name: str
    ):
        key = f"quiz_result:{quiz_id}:{id_}:*"
        return await self.get_from_cache(
            key=key, db=db, user_id=user_id, company_name=company_name
        )

    async def get_cached_result(
        self, quiz_id: int, user_id: int, db: AsyncSession, company_name: str
    ):
        key = f"quiz_result:{quiz_id}:{user_id}:*"
        return await self.get_from_cache(
            key=key, db=db, user_id=user_id, company_name=company_name
        )

    async def user_get_its_result(self, user_id: int):
        key = f"quiz_result:*:{user_id}:*"
        redis = await redis_connect()
        keys = await redis.keys(key)
        cache = await redis.mget(keys)
        if cache:
            parsed_values = [json.loads(value) for value in cache]
            return parsed_values

    async def admin_get_all_cache_by_company_id(
        self, user_id: int, company_name: str, db: AsyncSession
    ):
        company = await company_crud.get_one_by_filter(
            filters={"name": company_name}, db=db
        )
        key = f"quiz_result:*:*:{company.id}"
        return await self.get_from_cache(
            key=key, db=db, user_id=user_id, company_name=company_name
        )

    async def admin_get_all_results_by_quiz_id(
        self, quiz_id: int, user_id: int, company_name: str, db: AsyncSession
    ):
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
    ):

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

    async def get(self, key):
        redis = await redis_connect()
        res = await redis.get(key)
        await redis.close()
        return res

    async def delete(self, key):
        redis = await redis_connect()
        res = await redis.get(key)
        await redis.delete(key)
        await redis.close()
        return res


redis_service = RedisService()
