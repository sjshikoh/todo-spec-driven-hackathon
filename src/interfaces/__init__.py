"""
Console interface for the todo application.
Handles all user interaction through the console.
"""

from typing import Optional
from src.services import TodoService


class ConsoleInterface:
    """
    Console interface for the todo application.
    Handles all user interaction through the console.
    """

    def __init__(self, todo_service: TodoService):
        """
        Initialize the console interface with a todo service.

        Args:
            todo_service (TodoService): The service to handle task operations
        """
        self.todo_service = todo_service

    def display_menu(self):
        """
        Display the main menu options to the user.
        """
        print("\n" + "="*40)
        print("TODO APPLICATION")
        print("="*40)
        print("1. Add Task")
        print("2. View Task List")
        print("3. Update Task")
        print("4. Delete Task")
        print("5. Mark Task as Complete")
        print("6. Mark Task as Incomplete")
        print("7. Exit")
        print("="*40)

    def get_user_choice(self) -> int:
        """
        Get and validate the user's menu choice.

        Returns:
            int: The user's menu choice (1-7)
        """
        while True:
            try:
                choice = int(input("Enter your choice (1-7): "))
                if 1 <= choice <= 7:
                    return choice
                else:
                    print("Invalid choice. Please enter a number between 1 and 7.")
            except ValueError:
                print("Invalid input. Please enter a number.")

    def add_task_flow(self):
        """
        Handle the flow for adding a new task.
        """
        print("\n--- Add New Task ---")
        title = input("Enter task title: ").strip()

        if not title:
            print("Error: Task title cannot be empty or contain only whitespace")
            return

        description = input("Enter task description (optional, press Enter to skip): ").strip()

        try:
            task_id = self.todo_service.add_task(title, description)
            print(f"Task added successfully with ID: {task_id}")
        except ValueError as e:
            print(f"Error: {e}")

    def view_tasks_flow(self):
        """
        Handle the flow for viewing all tasks.
        """
        print("\n--- Task List ---")
        tasks = self.todo_service.get_all_tasks()

        if not tasks:
            print("No tasks found.")
            return

        for task in tasks:
            print(task)
            print("-" * 40)

    def update_task_flow(self):
        """
        Handle the flow for updating an existing task.
        """
        print("\n--- Update Task ---")

        # Get task ID
        try:
            task_id = int(input("Enter task ID to update: "))
        except ValueError:
            print("Invalid task ID. Please enter a number.")
            return

        # Check if task exists
        task = self.todo_service.get_task(task_id)
        if not task:
            print(f"Error: Task with ID {task_id} does not exist.")
            return

        print(f"Current task: {task}")

        # Get new title (optional)
        new_title = input(f"Enter new title (current: '{task.title}', press Enter to keep current): ").strip()
        new_title = new_title if new_title else None

        # Get new description (optional)
        new_description = input(f"Enter new description (current: '{task.description}', press Enter to keep current): ").strip()
        new_description = new_description if new_description != task.description else None

        # Update the task
        success = self.todo_service.update_task(task_id, new_title, new_description)
        if success:
            print("Task updated successfully.")
        else:
            print("Failed to update task.")

    def delete_task_flow(self):
        """
        Handle the flow for deleting a task.
        """
        print("\n--- Delete Task ---")

        try:
            task_id = int(input("Enter task ID to delete: "))
        except ValueError:
            print("Invalid task ID. Please enter a number.")
            return

        task = self.todo_service.get_task(task_id)
        if not task:
            print(f"Error: Task with ID {task_id} does not exist.")
            return

        print(f"Task to delete: {task}")
        confirm = input("Are you sure you want to delete this task? (y/N): ").lower()

        if confirm == 'y':
            success = self.todo_service.delete_task(task_id)
            if success:
                print("Task deleted successfully.")
            else:
                print("Failed to delete task.")
        else:
            print("Task deletion cancelled.")

    def mark_task_complete_flow(self):
        """
        Handle the flow for marking a task as complete.
        """
        print("\n--- Mark Task as Complete ---")

        try:
            task_id = int(input("Enter task ID to mark as complete: "))
        except ValueError:
            print("Invalid task ID. Please enter a number.")
            return

        task = self.todo_service.get_task(task_id)
        if not task:
            print(f"Error: Task with ID {task_id} does not exist.")
            return

        success = self.todo_service.mark_task_complete(task_id)
        if success:
            print("Task marked as complete successfully.")
        else:
            print("Failed to mark task as complete.")

    def mark_task_incomplete_flow(self):
        """
        Handle the flow for marking a task as incomplete.
        """
        print("\n--- Mark Task as Incomplete ---")

        try:
            task_id = int(input("Enter task ID to mark as incomplete: "))
        except ValueError:
            print("Invalid task ID. Please enter a number.")
            return

        task = self.todo_service.get_task(task_id)
        if not task:
            print(f"Error: Task with ID {task_id} does not exist.")
            return

        success = self.todo_service.mark_task_incomplete(task_id)
        if success:
            print("Task marked as incomplete successfully.")
        else:
            print("Failed to mark task as incomplete.")

    def run(self):
        """
        Run the main application loop.
        """
        print("Welcome to the Todo Application!")

        while True:
            self.display_menu()
            choice = self.get_user_choice()

            if choice == 1:
                self.add_task_flow()
            elif choice == 2:
                self.view_tasks_flow()
            elif choice == 3:
                self.update_task_flow()
            elif choice == 4:
                self.delete_task_flow()
            elif choice == 5:
                self.mark_task_complete_flow()
            elif choice == 6:
                self.mark_task_incomplete_flow()
            elif choice == 7:
                print("Thank you for using the Todo Application. Goodbye!")
                break

            # Pause to let user see the result before showing menu again
            input("\nPress Enter to continue...")