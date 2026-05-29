import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.platform.models.user import User
from app.volunteer_yatra.dependencies import get_current_user
from app.volunteer_yatra.schemas.task import TaskCreate, TaskResponse, TaskUpdate
from app.volunteer_yatra.services import task_service

router = APIRouter(prefix="/tasks", tags=["Volunteer Tasks"])


@router.get("", response_model=list[TaskResponse])
async def list_tasks(
    db: AsyncSession = Depends(get_db),
    opportunity_id: uuid.UUID | None = None,
    assigned_user_id: uuid.UUID | None = None,
    room_id: uuid.UUID | None = None,
):
    items = await task_service.list_tasks(
        db,
        opportunity_id=opportunity_id,
        assigned_user_id=assigned_user_id,
        room_id=room_id,
    )
    return [TaskResponse.model_validate(t) for t in items]


@router.post("", response_model=TaskResponse, status_code=201)
async def create_task(
    data: TaskCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    task = await task_service.create_task(db, user, data)
    return TaskResponse.model_validate(task)


@router.patch("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: uuid.UUID,
    data: TaskUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    task = await task_service.update_task(db, user, task_id, data)
    return TaskResponse.model_validate(task)
