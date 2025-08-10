import React, { useEffect, useState, useCallback } from 'react';
import { getTaskStatus } from '../api';

function QueueList({ tasks, onUpdateTask }) {
  const [localTasks, setLocalTasks] = useState({});
  const [loading, setLoading] = useState(true);
  
  // Инициализация локального состояния задач
  useEffect(() => {
    const initialTasks = {};
    tasks.forEach(task => {
      initialTasks[task.id] = task;
    });
    setLocalTasks(initialTasks);
    setLoading(false);
  }, [tasks]);
  
  // Функция для обновления статуса задачи
  const updateTaskStatus = useCallback(async (taskId) => {
    try {
      const statusData = await getTaskStatus(taskId);
      setLocalTasks(prev => ({
        ...prev,
        [taskId]: { ...prev[taskId], ...statusData }
      }));
      
      if (onUpdateTask) {
        onUpdateTask(taskId, statusData);
      }
    } catch (error) {
      console.error(`Ошибка при обновлении статуса задачи ${taskId}:`, error);
    }
  }, [onUpdateTask]);
  
  // Периодическое обновление статуса активных задач
  useEffect(() => {
    const interval = setInterval(() => {
      Object.values(localTasks).forEach(task => {
        if (task.status === 'queued' || task.status === 'processing') {
          updateTaskStatus(task.id);
        }
      });
    }, 5000); // Обновление каждые 5 секунд
    
    return () => clearInterval(interval);
  }, [localTasks, updateTaskStatus]);
  
  const getStatusText = (status) => {
    switch (status) {
      case 'queued': return 'В очереди';
      case 'processing': return 'Загружается';
      case 'completed': return 'Завершено';
      case 'error': return 'Ошибка';
      case 'cancelled': return 'Отменено';
      default: return status;
    }
  };

  if (loading) return <div>Загрузка...</div>;
  
  const taskItems = Object.values(localTasks);

  return (
    <div className="queue-list">
      <h2>Очередь загрузок</h2>
      
      {taskItems.length === 0 ? (
        <p>Очередь пуста</p>
      ) : (
        <ul>
          {taskItems.map((task) => (
            <li key={task.id} className={`task-item ${task.status}`}>
              <div className="task-header">
                <span className="task-url">{task.url}</span>
                <span className={`task-status ${task.status}`}>
                  {getStatusText(task.status)}
                </span>
              </div>
              {task.status === 'processing' && (
                <div className="task-progress">
                  <div className="progress-bar" style={{ width: `${task.progress || 0}%` }}>
                    {task.progress || 0}%
                  </div>
                </div>
              )}
              {task.result && task.result.error && (
                <div className="task-error">Ошибка: {task.result.error}</div>
              )}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

export default QueueList;