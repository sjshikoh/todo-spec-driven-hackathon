"""
Task API routes with JWT authentication and user isolation.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request
from pydantic import BaseModel
from sqlmodel import Session

from src.auth.jwt import get_current_user_id
from src.db.database import get_session
from src.services.task_service import TaskService
from src.models.task import Task


# ============ Pydantic Models ============

class TaskCreate(BaseModel):
    """Model for creating a new task."""
    title: str
    description: str = ""


class TaskUpdate(BaseModel):
    """Model for updating an existing task."""
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None


class TaskResponse(BaseModel):
    """Model for task response."""
    id: int
    user_id: str
    title: str
    description: str
    completed: bool
    created_at: str
    updated_at: str

    @classmethod
    def from_task(cls, task: Task) -> "TaskResponse":
        return cls(
            id=task.id,
            user_id=task.user_id,
            title=task.title,
            description=task.description,
            completed=task.completed,
            created_at=task.created_at.isoformat(),
            updated_at=task.updated_at.isoformat(),
        )


class MessageResponse(BaseModel):
    """Model for generic message responses."""
    message: str


# ============ Router ============

router = APIRouter(prefix="/tasks", tags=["tasks"])


# ============ Authentication Dependency ============

async def get_current_user(request: Request) -> str:
    """
    Dependency that extracts user ID from JWT in request headers.
    All protected routes must use this dependency.
    """
    return get_current_user_id(request)


# ============ Routes ============

@router.get("", response_model=List[TaskResponse])
async def get_all_tasks(
    user_id: str = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Get all tasks for the authenticated user.
    """
    tasks = TaskService.get_user_tasks(session, user_id)
    return [TaskResponse.from_task(task) for task in tasks]


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: int,
    user_id: str = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Get a specific task by ID.
    Returns 404 if task not found or doesn't belong to user.
    """
    task = TaskService.get_task(session, task_id, user_id)
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with ID {task_id} not found"
        )
    return TaskResponse.from_task(task)


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_data: TaskCreate,
    user_id: str = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Create a new task for the authenticated user.
    """
    if not task_data.title or not task_data.title.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Task title cannot be empty"
        )

    task = TaskService.create_task(
        session,
        user_id,
        task_data.title.strip(),
        task_data.description.strip()
    )
    return TaskResponse.from_task(task)


@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: int,
    task_data: TaskUpdate,
    user_id: str = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Update an existing task.
    Returns 404 if task not found or doesn't belong to user.
    """
    task = TaskService.update_task(
        session,
        task_id,
        user_id,
        title=task_data.title.strip() if task_data.title else None,
        description=task_data.description.strip() if task_data.description else None,
        completed=task_data.completed
    )
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with ID {task_id} not found"
        )
    return TaskResponse.from_task(task)


@router.delete("/{task_id}", response_model=MessageResponse)
async def delete_task(
    task_id: int,
    user_id: str = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Delete a task.
    Returns 404 if task not found or doesn't belong to user.
    """
    success = TaskService.delete_task(session, task_id, user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with ID {task_id} not found"
        )
    return MessageResponse(message=f"Task with ID {task_id} deleted successfully")


@router.post("/{task_id}/complete", response_model=TaskResponse)
async def mark_task_complete(
    task_id: int,
    user_id: str = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Mark a task as complete.
    Returns 404 if task not found or doesn't belong to user.
    """
    task = TaskService.mark_complete(session, task_id, user_id)
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with ID {task_id} not found"
        )
    return TaskResponse.from_task(task)


@router.post("/{task_id}/incomplete", response_model=TaskResponse)
async def mark_task_incomplete(
    task_id: int,
    user_id: str = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Mark a task as incomplete.
    Returns 404 if task not found or doesn't belong to user.
    """
    task = TaskService.mark_incomplete(session, task_id, user_id)
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with ID {task_id} not found"
        )
    return TaskResponse.from_task(task)
