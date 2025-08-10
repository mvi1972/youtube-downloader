import { useState, useEffect } from 'react';
import './App.css';
import DownloadForm from './components/DownloadForm';
import QueueList from './components/QueueList';
import { getQueue } from './api';

function App() {
  const [queue, setQueue] = useState({ queued: [], active: [] });

  useEffect(() => {
    const fetchQueue = async () => {
      try {
        const data = await getQueue();
        setQueue(data);
      } catch (error) {
        console.error('Error fetching queue:', error);
      }
    };

    fetchQueue();
    const interval = setInterval(fetchQueue, 5000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="App">
      <h1>YouTube Video Downloader</h1>
      <DownloadForm />
      <QueueList queue={queue} />
    </div>
  );
}

export default App;
