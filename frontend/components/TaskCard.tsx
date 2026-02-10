'use client';

import { Task } from '@/lib/api';
import Link from 'next/link';

interface TaskCardProps {
  task: Task;
  onToggleComplete: (task: Task) => Promise<void>;
  onDelete: (id: number) => Promise<void>;
  isDeleting: boolean;
}

export default function TaskCard({ task, onToggleComplete, onDelete, isDeleting }: TaskCardProps) {
  return (
    <div className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow">
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <div className="flex items-center gap-3 mb-2">
            <span className="text-sm text-gray-500">#{task.id}</span>
            <h3 className={`text-lg font-semibold ${task.completed ? 'line-through text-gray-400' : 'text-gray-900'}`}>
              {task.title}
            </h3>
          </div>
          {task.description && (
            <p className={`text-gray-600 ${task.completed ? 'line-through text-gray-400' : ''}`}>
              {task.description}
            </p>
          )}
          <div className="mt-3">
            <span
              className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                task.completed
                  ? 'bg-green-100 text-green-800'
                  : 'bg-yellow-100 text-yellow-800'
              }`}
            >
              {task.completed ? 'Completed' : 'Incomplete'}
            </span>
          </div>
        </div>
        <div className="flex items-center gap-2 ml-4">
          <button
            onClick={() => onToggleComplete(task)}
            disabled={isDeleting}
            className={`px-3 py-1 rounded-md text-sm font-medium transition-colors ${
              task.completed
                ? 'bg-yellow-100 text-yellow-700 hover:bg-yellow-200'
                : 'bg-green-100 text-green-700 hover:bg-green-200'
            } disabled:opacity-50`}
          >
            {task.completed ? 'Mark Incomplete' : 'Mark Complete'}
          </button>
          <Link
            href={`/dashboard/task/${task.id}`}
            className="px-3 py-1 bg-blue-100 text-blue-700 rounded-md text-sm font-medium hover:bg-blue-200 transition-colors"
          >
            Edit
          </Link>
          <button
            onClick={() => onDelete(task.id)}
            disabled={isDeleting}
            className="px-3 py-1 bg-red-100 text-red-700 rounded-md text-sm font-medium hover:bg-red-200 transition-colors disabled:opacity-50"
          >
            {isDeleting ? 'Deleting...' : 'Delete'}
          </button>
        </div>
      </div>
    </div>
  );
}
