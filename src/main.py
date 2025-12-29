#!/usr/bin/env python3
"""
Main entry point for the Todo Application.
Implements the console-based todo application with in-memory storage.
"""

from src.services import TodoService
from src.interfaces import ConsoleInterface


def main():
    """
    Main function to run the todo application.
    Initializes services and starts the console interface.
    """
    # Initialize the todo service
    todo_service = TodoService()

    # Initialize the console interface with the todo service
    console_interface = ConsoleInterface(todo_service)

    # Run the application
    console_interface.run()


if __name__ == "__main__":
    main()