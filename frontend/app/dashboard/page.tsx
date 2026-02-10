'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { useAuth } from '@/components/AuthProvider';
import TaskList from '@/components/TaskList';
import { api, Task } from '@/lib/api';

export default function DashboardPage() {
  const { user, loading } = useAuth();
  const router = useRouter();
  const [tasks, setTasks] = useState<Task[]>([]);
  const [tasksLoading, setTasksLoading] = useState(true);
  const [error, setError] = useState('');
  const [deletingId, setDeletingId] = useState<number | null>(null);

  useEffect(() => {
    if (!loading && !user) {
      router.push('/login');
    }
  }, [user, loading, router]);

  const fetchTasks = async () => {
    try {
      const data = await api.getTasks();
      setTasks(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch tasks');
    } finally {
      setTasksLoading(false);
    }
  };

  useEffect(() => {
    if (user) {
      fetchTasks();
    }
  }, [user]);

  const handleToggleComplete = async (task: Task) => {
    try {
      const updatedTask = task.completed
        ? await api.markIncomplete(task.id)
        : await api.markComplete(task.id);

      setTasks((prev) =>
        prev.map((t) => (t.id === task.id ? updatedTask : t))
      );
    } catch (err) {
      alert(`Error: ${err instanceof Error ? err.message : 'Failed to update task'}`);
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm('Are you sure you want to delete this task?')) {
      return;
    }

    setDeletingId(id);
    try {
      await api.deleteTask(id);
      setTasks((prev) => prev.filter((t) => t.id !== id));
    } catch (err) {
      alert(`Error: ${err instanceof Error ? err.message : 'Failed to delete task'}`);
    } finally {
      setDeletingId(null);
    }
  };

  const handleRefresh = () => {
    setTasksLoading(true);
    fetchTasks();
  };

  if (loading || !user) {
    return (
      <div className="flex justify-center items-center min-h-[60vh]">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">My Tasks</h1>
          <p className="text-gray-500">Welcome back, {user.name || user.email}!</p>
        </div>
        <Link
          href="/dashboard/create"
          className="bg-blue-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-blue-700 transition-colors"
        >
          Create Task
        </Link>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-md mb-6">
          <strong>Error: </strong>
          {error}. Make sure the backend server is running at http://localhost:8000
        </div>
      )}

      <TaskList
        tasks={tasks}
        loading={tasksLoading}
        onToggleComplete={handleToggleComplete}
        onDelete={handleDelete}
        deletingId={deletingId}
      />
    </div>
  );
}
