'use client';

import { useState, useEffect } from 'react';
import { useRouter, useParams } from 'next/navigation';
import Link from 'next/link';
import { useAuth } from '@/components/AuthProvider';
import TaskForm from '@/components/TaskForm';
import { api } from '@/lib/api';
import { Task } from '@/lib/api';

export default function EditTaskPage() {
  const { user, loading } = useAuth();
  const router = useRouter();
  const params = useParams();
  const taskId = params?.id as string;
  const [task, setTask] = useState<Task | null>(null);
  const [taskLoading, setTaskLoading] = useState(true);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!loading && !user) {
      router.push('/login');
    }
  }, [user, loading, router]);

  useEffect(() => {
    if (!taskId || !user) return;

    const fetchTask = async () => {
      try {
        const data = await api.getTask(parseInt(taskId));
        setTask(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch task');
      } finally {
        setTaskLoading(false);
      }
    };

    fetchTask();
  }, [taskId, user]);

  const handleSubmit = async (formData: { title: string; description: string }) => {
    setIsLoading(true);
    try {
      await api.updateTask(parseInt(taskId), {
        title: formData.title,
        description: formData.description,
      });
      router.push('/dashboard');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update task');
    } finally {
      setIsLoading(false);
    }
  };

  const handleToggleComplete = async () => {
    if (!task) return;

    try {
      const updatedTask = task.completed
        ? await api.markIncomplete(task.id)
        : await api.markComplete(task.id);
      setTask(updatedTask);
    } catch (err) {
      alert(`Error: ${err instanceof Error ? err.message : 'Failed to update task'}`);
    }
  };

  const handleDelete = async () => {
    if (!task) return;

    if (!confirm('Are you sure you want to delete this task?')) {
      return;
    }

    try {
      await api.deleteTask(task.id);
      router.push('/dashboard');
    } catch (err) {
      alert(`Error: ${err instanceof Error ? err.message : 'Failed to delete task'}`);
    }
  };

  if (loading || !user) {
    return (
      <div className="flex justify-center items-center min-h-[60vh]">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (taskLoading) {
    return (
      <div className="flex justify-center items-center min-h-[60vh]">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-6">
        <Link href="/dashboard" className="text-blue-600 hover:text-blue-700 text-sm">
          ← Back to Dashboard
        </Link>
      </div>

      <div className="mb-6 flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Edit Task</h1>
        <div className="flex gap-2">
          <button
            onClick={handleToggleComplete}
            disabled={isLoading}
            className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
              task?.completed
                ? 'bg-yellow-100 text-yellow-700 hover:bg-yellow-200'
                : 'bg-green-100 text-green-700 hover:bg-green-200'
            } disabled:opacity-50`}
          >
            {task?.completed ? 'Mark Incomplete' : 'Mark Complete'}
          </button>
          <button
            onClick={handleDelete}
            disabled={isLoading}
            className="px-4 py-2 bg-red-100 text-red-700 rounded-md text-sm font-medium hover:bg-red-200 transition-colors disabled:opacity-50"
          >
            Delete
          </button>
        </div>
      </div>

      <div className="bg-white rounded-lg shadow-md p-6">
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-md mb-6">
            {error}
          </div>
        )}

        <TaskForm
          initialTask={task ? { title: task.title, description: task.description } : undefined}
          onSubmit={handleSubmit}
          isLoading={isLoading}
        />
      </div>
    </div>
  );
}
