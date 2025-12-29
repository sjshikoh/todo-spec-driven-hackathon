"""
Task model for the todo application.
Defines the structure and validation for task objects.
"""

class Task:
    """
    Represents a task in the todo application.

    Attributes:
        id (int): Unique identifier for the task
        title (str): Title of the task (required)
        description (str): Description of the task (optional)
        completed (bool): Completion status of the task
    """

    def __init__(self, task_id, title, description="", completed=False):
        """
        Initialize a new Task object.

        Args:
            task_id (int): Unique identifier for the task
            title (str): Title of the task (required)
            description (str): Description of the task (optional)
            completed (bool): Completion status of the task (default: False)

        Raises:
            ValueError: If title is empty or contains only whitespace
        """
        if not title or not title.strip():
            raise ValueError("Task title cannot be empty or contain only whitespace")

        self.id = task_id
        self.title = title.strip()
        self.description = description.strip() if description else ""
        self.completed = completed

    def __str__(self):
        """
        Return a string representation of the task for display.

        Returns:
            str: Formatted string representation of the task
        """
        status = "✓" if self.completed else "○"
        result = f"[{status}] ID: {self.id} - {self.title}"
        if self.description:
            result += f"\n    Description: {self.description}"
        return result