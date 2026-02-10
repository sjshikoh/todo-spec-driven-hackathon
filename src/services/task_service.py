"""
Task service for database operations.
Handles CRUD operations for tasks with user isolation.
"""

from typing import List, Optional
from sqlmodel import Session, select
from src.models.task import Task


class TaskService:
    """Service class for task database operations."""

    @staticmethod
    def get_user_tasks(session: Session, user_id: str) -> List[Task]:
        """
        Get all tasks for a specific user.

        Args:
            session: Database session
            user_id: The user's ID from JWT

        Returns:
            List of tasks belonging to the user, ordered by creation date
        """
        statement = (
            select(Task)
            .where(Task.user_id == user_id)
            .order_by(Task.created_at.desc())
        )
        return list(session.exec(statement))

    @staticmethod
    def get_task(session: Session, task_id: int, user_id: str) -> Optional[Task]:
        """
        Get a specific task by ID, ensuring it belongs to the user.

        Args:
            session: Database session
            task_id: The task ID
            user_id: The user's ID from JWT

        Returns:
            The task if found and belongs to user, None otherwise
        """
        statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)
        result = session.exec(statement)
        return result.one_or_none()

    @staticmethod
    def create_task(session: Session, user_id: str, title: str, description: str = "") -> Task:
        """
        Create a new task for a user.

        Args:
            session: Database session
            user_id: The user's ID from JWT
            title: Task title
            description: Task description (optional)

        Returns:
            The created task
        """
        task = Task(user_id=user_id, title=title, description=description)
        session.add(task)
        session.commit()
        session.refresh(task)
        return task

    @staticmethod
    def update_task(
        session: Session,
        task_id: int,
        user_id: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        completed: Optional[bool] = None
    ) -> Optional[Task]:
        """
        Update an existing task, ensuring it belongs to the user.

        Args:
            session: Database session
            task_id: The task ID
            user_id: The user's ID from JWT
            title: New title (optional)
            description: New description (optional)
            completed: New completed status (optional)

        Returns:
            The updated task if found, None otherwise
        """
        task = TaskService.get_task(session, task_id, user_id)
        if task is None:
            return None

        if title is not None:
            task.title = title
        if description is not None:
            task.description = description
        if completed is not None:
            task.completed = completed

        session.commit()
        session.refresh(task)
        return task

    @staticmethod
    def delete_task(session: Session, task_id: int, user_id: str) -> bool:
        """
        Delete a task, ensuring it belongs to the user.

        Args:
            session: Database session
            task_id: The task ID
            user_id: The user's ID from JWT

        Returns:
            True if task was deleted, False if not found
        """
        task = TaskService.get_task(session, task_id, user_id)
        if task is None:
            return False

        session.delete(task)
        session.commit()
        return True

    @staticmethod
    def mark_complete(session: Session, task_id: int, user_id: str) -> Optional[Task]:
        """
        Mark a task as complete.

        Args:
            session: Database session
            task_id: The task ID
            user_id: The user's ID from JWT

        Returns:
            The updated task if found, None otherwise
        """
        return TaskService.update_task(session, task_id, user_id, completed=True)

    @staticmethod
    def mark_incomplete(session: Session, task_id: int, user_id: str) -> Optional[Task]:
        """
        Mark a task as incomplete.

        Args:
            session: Database session
            task_id: The task ID
            user_id: The user's ID from JWT

        Returns:
            The updated task if found, None otherwise
        """
        return TaskService.update_task(session, task_id, user_id, completed=False)
