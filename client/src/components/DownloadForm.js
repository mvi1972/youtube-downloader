import React, { useState } from 'react';
import { startDownload } from '../api';

function DownloadForm({ onNewTask }) {
  const [url, setUrl] = useState('');
  const [priority, setPriority] = useState(2); // PRIORITY_NORMAL
  const [cookiesFile, setCookiesFile] = useState(null);
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    try {
      const result = await startDownload(url, priority, cookiesFile);
      if (result.error) {
        alert(`Ошибка: ${result.error}`);
      } else {
        onNewTask({
          id: result.task_id,
          url,
          priority,
          status: 'queued',
          progress: 0
        });
      }

      // Сбрасываем форму
      setUrl('');
      setPriority(2);
      setCookiesFile(null);
    } catch (error) {
      alert('Ошибка при запуске загрузки');
      console.error(error);
    }
  };

  const handleFileChange = (e) => {
    if (e.target.files.length > 0) {
      setCookiesFile(e.target.files[0]);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="download-form">
      <div className="form-group">
        <label>YouTube URL:</label>
        <input 
          type="text" 
          value={url} 
          onChange={(e) => setUrl(e.target.value)} 
          placeholder="https://www.youtube.com/watch?v=..." 
          required 
        />
      </div>
      
      <div className="form-group">
        <label>Приоритет:</label>
        <select value={priority} onChange={(e) => setPriority(Number(e.target.value))}>
          <option value={1}>Высокий</option>
          <option value={2}>Обычный</option>
          <option value={3}>Низкий</option>
        </select>
      </div>
      
      <div className="form-group">
        <label>Cookies файл (опционально):</label>
        <input 
          type="file" 
          accept=".txt" 
          onChange={handleFileChange}
        />
      </div>
      
      <button type="submit" className="btn-download">Начать загрузку</button>
    </form>
  );
}

export default DownloadForm;