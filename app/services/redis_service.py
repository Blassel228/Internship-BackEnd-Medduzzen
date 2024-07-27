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

    async def get_from_cache(self, key):
        redis = await redis_connect()
        cached_data_json = await redis.get(key)
        if cached_data_json:
            return json.loads(cached_data_json)
        await redis.close()
        return None

    async def get_cached_result(self, quiz_id: int, user_id: int):
        key = f"quiz_result:{quiz_id}:{user_id}:*"
        return await self.get_from_cache(key)

    async def user_get_its_result(self, user_id: int):
        key = f"quiz_result:*:{user_id}:*"
        return await self.get_from_cache(key)

    async def admin_get_all_company_results(self, user_id: int, db: AsyncSession):
        member = await member_crud.get_one(id_=user_id, db=db)
        if member is None or member.role != "admin":
            company = await company_crud.get_one(id_=member.company_id)
            if company is None:
                raise HTTPException(
                    status_code=403, detail="You are not a member of this company."
                )
            if user_id != company.owner_id:
                raise HTTPException(
                    status_code=403, detail="You are not a member of this company."
                )
        company = await company_crud.get_one(id_=member.company_id)
        key = f"quiz_result:*:*:{company.id}"
        return await self.get_from_cache(key)

    async def admin_get_all_results_by_quiz_id(
        self, quiz_id: int, user_id: int, db: AsyncSession
    ):
        member = await member_crud.get_one(id_=user_id, db=db)
        if member is None or member.role != "admin":
            company = await company_crud.get_one(id_=member.company_id)
            if company is None:
                raise HTTPException(
                    status_code=403, detail="You are not a member of this company."
                )
            if user_id != company.owner_id:
                raise HTTPException(
                    status_code=403, detail="You are not a member of this company."
                )
        key = f"quiz_result:{quiz_id}*"
        return await self.get_from_cache(key)

    async def admin_get_cache_for_user(self, id_: int):
        key = f"quiz_result:*:{id_}:*"
        return await self.get_from_cache(key)

    async def export_cached_results_to_csv(
        self, user_id: int, id_: int, db: AsyncSession
    ):
        member = await member_crud.get_one(id_=user_id, db=db)
        if member is None or member.role != "admin":
            company = await company_crud.get_one(id_=member.company_id)
            if company is None:
                raise HTTPException(
                    status_code=403, detail="You are not a member of this company."
                )
            if user_id != company.owner_id:
                raise HTTPException(
                    status_code=403, detail="You are not a member of this company."
                )

        cache = await self.admin_get_cache_for_user(id_=id_)

        headers = []
        row = []

        for key in cache.keys():
            headers.append(key)

        for user_cache in cache:
            for user_data in user_cache.values():
                row.append(user_data)

        with open("cache.csv", "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(headers)
            writer.writerow(row)


redis_service = RedisService()
