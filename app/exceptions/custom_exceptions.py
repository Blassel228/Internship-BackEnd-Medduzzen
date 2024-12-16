from fastapi import HTTPException


def check_user_permissions(company, user_id: int, member=None) -> None:
    if company is None:
        raise HTTPException(status_code=404, detail="There is no such a company")
    if member is None:
        if company.owner_id != user_id:
            raise HTTPException(status_code=403, detail="You have such right")
    else:
        if member.role != "admin":
            raise HTTPException(status_code=403, detail="You do not have such rights")
        if member.company_id != company.id:
            raise HTTPException(
                status_code=403, detail="You are not a member of the company"
            )
