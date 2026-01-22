'use client';

import { Task } from '@/lib/api';
import TaskCard from './TaskCard';

interface TaskListProps {
  tasks: Task[];
  onToggleComplete: (task: Task) => Promise<void>;
  onDelete: (id: number) => Promise<void>;
  loading: boolean;
  deletingId: number | null;
}

export default function TaskList({ tasks, onToggleComplete, onDelete, loading, deletingId }: TaskListProps) {
  if (loading) {
    return (
      <div className="flex justify-center items-center py-12">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (!tasks || tasks.length === 0) {
    return (
      <div className="text-center py-12">
        <svg
          className="mx-auto h-12 w-12 text-gray-400"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4"
          />
        </svg>
        <h3 className="mt-2 text-lg font-medium text-gray-900">No tasks yet</h3>
        <p className="mt-1 text-gray-500">Get started by creating a new task.</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {tasks.map((task) => (
        <TaskCard
          key={task.id}
          task={task}
          onToggleComplete={onToggleComplete}
          onDelete={onDelete}
          isDeleting={deletingId === task.id}
        />
      ))}
    </div>
  );
}
