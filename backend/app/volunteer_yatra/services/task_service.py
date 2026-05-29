import uuid

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.platform.models.user import User
from app.volunteer_yatra.models.task import VolunteerTask
from app.volunteer_yatra.schemas.task import TaskCreate, TaskUpdate
from app.volunteer_yatra.services.opportunity_service import get_opportunity


async def create_task(db: AsyncSession, user: User, data: TaskCreate) -> VolunteerTask:
    opp = await get_opportunity(db, data.opportunity_id)
    if opp.host_user_id != user.id:
        raise HTTPException(status_code=403, detail="Only the host can create tasks")
    task = VolunteerTask(
        opportunity_id=data.opportunity_id,
        room_id=opp.room_id,
        title=data.title,
        description=data.description,
        assigned_user_id=data.assigned_user_id,
        due_date=data.due_date,
    )
    db.add(task)
    await db.flush()
    await db.refresh(task)
    return task


async def get_task(db: AsyncSession, task_id: uuid.UUID) -> VolunteerTask:
    result = await db.execute(select(VolunteerTask).where(VolunteerTask.id == task_id))
    task = result.scalar_one_or_none()
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


async def update_task(
    db: AsyncSession, user: User, task_id: uuid.UUID, data: TaskUpdate
) -> VolunteerTask:
    task = await get_task(db, task_id)
    opp = await get_opportunity(db, task.opportunity_id)
    is_host = opp.host_user_id == user.id
    is_assignee = task.assigned_user_id == user.id
    if not is_host and not is_assignee:
        raise HTTPException(status_code=403, detail="Not authorized to update this task")

    updates = data.model_dump(exclude_unset=True)
    if not is_host:
        allowed = {"status"}
        updates = {k: v for k, v in updates.items() if k in allowed}
        if not updates:
            raise HTTPException(status_code=403, detail="Volunteers can only update task status")

    for field, value in updates.items():
        setattr(task, field, value)
    await db.flush()
    await db.refresh(task)
    return task


async def list_tasks(
    db: AsyncSession,
    *,
    opportunity_id: uuid.UUID | None = None,
    assigned_user_id: uuid.UUID | None = None,
    room_id: uuid.UUID | None = None,
) -> list[VolunteerTask]:
    query = select(VolunteerTask)
    if opportunity_id:
        query = query.where(VolunteerTask.opportunity_id == opportunity_id)
    if assigned_user_id:
        query = query.where(VolunteerTask.assigned_user_id == assigned_user_id)
    if room_id:
        query = query.where(VolunteerTask.room_id == room_id)
    result = await db.execute(query.order_by(VolunteerTask.created_at.desc()))
    return list(result.scalars().all())
