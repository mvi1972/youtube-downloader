const API_BASE = 'http://localhost:5000/api';

export async function startDownload(url, priority, cookiesFile) {
  const formData = new FormData();
  formData.append('url', url);
  formData.append('priority', priority);
  if (cookiesFile) {
    formData.append('file', cookiesFile);
  }

  try {
    // Загрузка cookies (если есть)
    let cookiesPath = null;
    if (cookiesFile) {
      const uploadResponse = await fetch(`${API_BASE}/upload_cookies`, {
        method: 'POST',
        body: formData
      });
      const uploadData = await uploadResponse.json();
      cookiesPath = uploadData.filename;
    }

    // Запуск скачивания
    const response = await fetch(`${API_BASE}/download`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        url,
        priority,
        cookies_file: cookiesPath
      })
    });
    
    return await response.json();
  } catch (error) {
    console.error('Download start error:', error);
    return { error: 'Connection error' };
  }
}

export async function getTaskStatus(taskId) {
  try {
    const response = await fetch(`${API_BASE}/task/${taskId}`);
    return await response.json();
  } catch (error) {
    console.error('Status check error:', error);
    return { status: 'error', error: 'Connection error' };
  }
}

export async function getQueue() {
  try {
    const response = await fetch(`${API_BASE}/queue`);
    return await response.json();
  } catch (error) {
    console.error('Queue fetch error:', error);
    return { queued: [], active: [] };
  }
}