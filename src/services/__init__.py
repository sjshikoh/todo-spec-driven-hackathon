"""
Todo service for managing tasks in the application.
Implements all core functionality for task management.
"""

from typing import List, Optional
from src.models import Task


class TodoService:
    """
    Service class for managing tasks in the todo application.
    Implements all core functionality with in-memory storage.
    """

    def __init__(self):
        """
        Initialize the TodoService with empty task storage.
        """
        self._tasks = {}
        self._next_id = 1

    def _get_next_id(self) -> int:
        """
        Get the next available task ID.

        Returns:
            int: The next available task ID
        """
        while self._next_id in self._tasks:
            self._next_id += 1
        return self._next_id

    def add_task(self, title: str, description: str = "") -> int:
        """
        Add a new task to the application.

        Args:
            title (str): Title of the task (required)
            description (str): Description of the task (optional)

        Returns:
            int: The ID of the newly created task

        Raises:
            ValueError: If title is invalid
        """
        task_id = self._get_next_id()
        task = Task(task_id, title, description, completed=False)
        self._tasks[task_id] = task
        self._next_id = task_id + 1
        return task_id

    def get_task(self, task_id: int) -> Optional[Task]:
        """
        Retrieve a task by its ID.

        Args:
            task_id (int): The ID of the task to retrieve

        Returns:
            Task: The task object if found, None otherwise
        """
        return self._tasks.get(task_id)

    def get_all_tasks(self) -> List[Task]:
        """
        Retrieve all tasks in the application.

        Returns:
            List[Task]: List of all task objects, sorted by ID
        """
        return sorted(self._tasks.values(), key=lambda x: x.id)

    def update_task(self, task_id: int, title: str = None, description: str = None) -> bool:
        """
        Update an existing task.

        Args:
            task_id (int): The ID of the task to update
            title (str, optional): New title for the task
            description (str, optional): New description for the task

        Returns:
            bool: True if the task was updated successfully, False otherwise
        """
        if task_id not in self._tasks:
            return False

        task = self._tasks[task_id]

        # Update title if provided
        if title is not None:
            if title and title.strip():
                task.title = title.strip()
            elif title.strip() == "":
                # If an empty title is provided, don't update
                pass

        # Update description if provided
        if description is not None:
            task.description = description.strip() if description else ""

        return True

    def delete_task(self, task_id: int) -> bool:
        """
        Delete a task by its ID.

        Args:
            task_id (int): The ID of the task to delete

        Returns:
            bool: True if the task was deleted successfully, False otherwise
        """
        if task_id not in self._tasks:
            return False

        del self._tasks[task_id]
        return True

    def mark_task_complete(self, task_id: int) -> bool:
        """
        Mark a task as complete.

        Args:
            task_id (int): The ID of the task to mark as complete

        Returns:
            bool: True if the task was marked as complete successfully, False otherwise
        """
        if task_id not in self._tasks:
            return False

        self._tasks[task_id].completed = True
        return True

    def mark_task_incomplete(self, task_id: int) -> bool:
        """
        Mark a task as incomplete.

        Args:
            task_id (int): The ID of the task to mark as incomplete

        Returns:
            bool: True if the task was marked as incomplete successfully, False otherwise
        """
        if task_id not in self._tasks:
            return False

        self._tasks[task_id].completed = False
        return True