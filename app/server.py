import datetime
from typing import Optional

import crud
from dependency import SessionDependency
from fastapi import FastAPI, HTTPException, Query
from fastapi.params import Depends
from lifespan import lifespan
from models import Advertisement
from schema import (
    CreateAdvRequest,
    GetAdvResponse,
    IdResponse,
    SearchAdvResponse,
    SearchParams,
    UpdateAdvRequest,
)
from sqlalchemy import String, bindparam, or_, select


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
    adv = Advertisement(
        title=item.title, description=item.description, owner=item.owner
    )
    await crud.add_adv(session, adv)
    return adv.id_dict


@app.get("/advertisement/{advertisement_id}", response_model=GetAdvResponse)
async def get_advertisement(
    session: SessionDependency, advertisement_id: int
) -> Advertisement:
    adv = await crud.get_avd_by_id(session, Advertisement, advertisement_id)
    return adv.dict


@app.get("/advertisement", response_model=SearchAdvResponse)
async def search_advertisement(
    session: SessionDependency,
    title: Optional[str] = Query(None),
    description: Optional[str] = Query(None),
    owner: Optional[str] = Query(None),
    date_posted: Optional[str] = Query(None),
) -> SearchAdvResponse:

    if not any([title, description, owner, date_posted]):
        raise HTTPException(
            status_code=400, detail="At least one search parameter is required"
        )

    conditions = []

    if title:
        conditions.append(Advertisement.title.ilike(bindparam("title", f"%{title}%")))
    if description:
        conditions.append(
            Advertisement.description.ilike(
                bindparam("description", f"%{description}%")
            )
        )
    if owner:
        conditions.append(Advertisement.owner.ilike(bindparam("owner", f"%{owner}%")))
    if date_posted:
        try:
            date_obj = datetime.strptime(date_posted, "%Y-%m-%d").date()
            conditions.append(Advertisement.date_posted == date_obj)
        except ValueError:
            conditions.append(
                Advertisement.date_posted.cast(String).ilike(
                    bindparam("date_posted", f"%{date_posted}%")
                )
            )

    query = select(Advertisement).where(or_(*conditions)).limit(10000)

    result = await session.execute(query)
    advs = result.scalars().all()

    return SearchAdvResponse(advs=[GetAdvResponse.model_validate(adv) for adv in advs])


@app.patch("/advertisement/{adv_id}", response_model=IdResponse)
async def update_advertisement(
    session: SessionDependency, adv_id: int, item: UpdateAdvRequest
) -> Advertisement:
    adv = await crud.get_avd_by_id(session, Advertisement, adv_id)

    if item.title is not None:
        adv.title = item.title
    if item.description is not None:
        adv.description = item.description

    await crud.add_adv(session, adv)
    return {"id": adv_id}


@app.delete("/advertisement/{advertisement_id}", response_model=IdResponse)
async def delete_advertisement(
    session: SessionDependency, advertisement_id: int
) -> Advertisement:
    adv = await crud.get_avd_by_id(session, Advertisement, advertisement_id)
    await crud.delete_item(adv)
    return {"id": advertisement_id}
