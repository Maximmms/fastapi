import datetime
import token
from typing import Optional

import auth
import crud
import models
from dependency import SessionDependency, TokenDependency
from fastapi import FastAPI, HTTPException, Query
from lifespan import lifespan
from models import Advertisement, User
from schema import (
    BaseUserRequest,
    CreateAdvRequest,
    CreateUserRequest,
    GetAdvResponse,
    GetUserResponse,
    IdResponse,
    LoginRequest,
    LoginResponse,
    SearchAdvResponse,
    UpdateAdvRequest,
    UpdateUserRequest,
)
from sqlalchemy import String, or_, select

app = FastAPI(
    title="Advertisment API",
    terms_of_service="",
    description="list of advs",
    lifespan=lifespan,
)


@app.post("/advertisement", response_model=IdResponse)
async def create_advertisement(
    session: SessionDependency, item: CreateAdvRequest
) -> Advertisement:
    adv_dict = item.model_dump(exclude_unset=True)
    adv_orm_obj = Advertisement(**adv_dict, user_id=token.user_id)
    await crud.add_item(session, adv_orm_obj)
    return adv_orm_obj.id_dict


@app.get("/advertisement/{advertisement_id}", response_model=GetAdvResponse)
async def get_advertisement(
    session: SessionDependency, token: TokenDependency, advertisement_id: int
) -> Advertisement:
    adv_orm_obj = await crud.get_item_by_id(session, Advertisement, advertisement_id)
    if token.user.role == "admin" or adv_orm_obj.user_id == token.user_id:
        return adv_orm_obj.dict
    raise HTTPException(403, "Insufficient privileges")


@app.get("/advertisement", response_model=SearchAdvResponse)
async def search_advertisement(
    session: SessionDependency,
    title: Optional[str] = Query(None),
    description: Optional[str] = Query(None),
    price: Optional[int] = Query(None),
    owner: Optional[str] = Query(None),
    date_posted: Optional[str] = Query(None),
) -> SearchAdvResponse:
    if not any([title, description, price, owner, date_posted]):
        raise HTTPException(
            status_code=400, detail="At least one search parameter is required"
        )

    conditions = []

    if title:
        conditions.append(Advertisement.title.ilike(f"%{title}%"))
    if description:
        conditions.append(Advertisement.description.ilike(f"%{description}%"))
    if price:
        conditions.append(Advertisement.price == price)
    if owner:
        conditions.append(Advertisement.owner.ilike(f"%{owner}%"))
    if date_posted:
        try:
            date_obj = datetime.strptime(date_posted, "%Y-%m-%d").date()
            conditions.append(Advertisement.date_posted == date_obj)
        except ValueError:
            conditions.append(
                Advertisement.date_posted.cast(String).ilike(f"%{date_posted}%")
            )

    query = select(Advertisement).where(or_(*conditions)).limit(10000)

    result = await session.execute(query)
    advs = result.scalars().all()

    return SearchAdvResponse(advs=[GetAdvResponse.model_validate(adv) for adv in advs])


@app.patch("/advertisement/{advertisement_id}", response_model=IdResponse)
async def update_advertisement(
    session: SessionDependency,
    token: TokenDependency,
    advertisement_id: int,
    item: UpdateAdvRequest,
) -> Advertisement:
    orm_obj = await crud.get_item_by_id(
        session,
        Advertisement,
        advertisement_id,
    )
    if token.user.role == "admin" or orm_obj.user_id == token.user_id:
        if item.title is not None:
            orm_obj.title = item.title
        if item.description is not None:
            orm_obj.description = item.description

        await crud.add_item(session, orm_obj)
        return {"id": advertisement_id}
    raise HTTPException(403, "Insufficient privileges")


@app.delete("/advertisement/{advertisement_id}", response_model=IdResponse)
async def delete_advertisement(
    session: SessionDependency, token: TokenDependency, advertisement_id: int
) -> Advertisement:
    orm_obj = await crud.get_item_by_id(session, Advertisement, advertisement_id)
    if token.user.role == "admin" or orm_obj.user_id == token.user_id:
        await crud.delete_item(orm_obj)
        return {"id": advertisement_id}


@app.post("/login", tags=["login"], response_model=LoginResponse)
async def login(login_data: LoginRequest, session: SessionDependency) -> LoginResponse:
    query = select(models.User).where(models.User.name == login_data.name)
    user = await session.scalar(query)
    if user is None:
        raise HTTPException(401, "Invalid credentials")
    if not auth.check_password(login_data.password, user.password):
        raise HTTPException(401, "Invalid credentials")
    token = models.Token(user_id=user.id)
    await crud.add_item(session, token)
    return token.dict


@app.post("/user", tags=["user"], response_model=IdResponse)
async def create_user(user_data: CreateUserRequest, session: SessionDependency) -> User:
    user_dict = user_data.model_dump(exclude_unset=True)
    user_dict["password"] = auth.hash_password(user_dict["password"])
    user_orm_obj = models.User(**user_dict)
    await crud.add_item(session, user_orm_obj)
    return user_orm_obj.in_dict


@app.get("/user/{user_id}", tags=["user"], response_model=GetUserResponse)
async def get_user(user_id: int, session: SessionDependency) -> User:
    user_orm_obj = await crud.get_item_by_id(session, User, user_id)
    return user_orm_obj.dict


@app.delete("/user/{user_id}", tags=["user"], response_model=IdResponse)
async def delete_user(user_id: int, session: SessionDependency) -> User:
    user_orm_obj = await crud.get_item_by_id(session, User, user_id)
    if token.user.role == "admin" or user_orm_obj.user_id == token.user_id:
        await crud.delete_item(session, user_orm_obj)
        return user_orm_obj.user_id
    raise HTTPException(403, "Insufficient privileges")


@app.patch("/user/{user_id}", tags=["user"], response_model=IdResponse)
async def update_user(
    user_id: int, session: SessionDependency, user_data: UpdateUserRequest
) -> User:
    user_orm_obj = await crud.get_item_by_id(session, User, user_id)

    if token.user.role == "admin" or user_orm_obj.user_id == token.user_id:
        if user_data.name is not None:
            user_orm_obj.name = user_data.username
        if user_data.password is not None:
            user_orm_obj.password = auth.hash_password(user_data.password)
        if user_data.role is not None:
            user_orm_obj.role = user_data.role

        await crud.add_item(session, user_orm_obj)
        return {"id": user_orm_obj}
    raise HTTPException(403, "Insufficient privileges")
