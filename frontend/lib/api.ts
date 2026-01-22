const API_BASE_URL = 'http://localhost:8000';

export interface Task {
  id: number;
  title: string;
  description: string;
  completed: boolean;
  userId?: string;
}

export interface TaskCreate {
  title: string;
  description?: string;
}

export interface TaskUpdate {
  title?: string;
  description?: string;
}

export interface MessageResponse {
  message: string;
}

async function handleResponse(response: Response) {
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'An error occurred' }));
    throw new Error(error.detail || 'An error occurred');
  }
  return response.json();
}

export async function fetchWithAuth(
  input: RequestInfo | URL,
  init: RequestInit = {}
): Promise<Response> {
  const token = typeof window !== 'undefined'
    ? localStorage.getItem('auth-token')
    : null;

  const headers = {
    ...(init.headers || {}),
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    'Content-Type': 'application/json',
  };

  return fetch(`${API_BASE_URL}${input}`, {
    ...init,
    headers,
  });
}

export const api = {
  // Get all tasks
  async getTasks(): Promise<Task[]> {
    const response = await fetchWithAuth('/tasks');
    return handleResponse(response);
  },

  // Get a single task
  async getTask(id: number): Promise<Task> {
    const response = await fetchWithAuth(`/tasks/${id}`);
    return handleResponse(response);
  },

  // Create a new task
  async createTask(data: TaskCreate): Promise<Task> {
    const response = await fetchWithAuth('/tasks', {
      method: 'POST',
      body: JSON.stringify(data),
    });
    return handleResponse(response);
  },

  // Update a task
  async updateTask(id: number, data: TaskUpdate): Promise<Task> {
    const response = await fetchWithAuth(`/tasks/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
    return handleResponse(response);
  },

  // Delete a task
  async deleteTask(id: number): Promise<MessageResponse> {
    const response = await fetchWithAuth(`/tasks/${id}`, {
      method: 'DELETE',
    });
    return handleResponse(response);
  },

  // Mark task as complete
  async markComplete(id: number): Promise<Task> {
    const response = await fetchWithAuth(`/tasks/${id}/complete`, {
      method: 'POST',
    });
    return handleResponse(response);
  },

  // Mark task as incomplete
  async markIncomplete(id: number): Promise<Task> {
    const response = await fetchWithAuth(`/tasks/${id}/incomplete`, {
      method: 'POST',
    });
    return handleResponse(response);
  },
};
