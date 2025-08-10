from flask import Flask, request, jsonify, send_from_directory, Blueprint
from download_service import DownloadService
import uuid
import threading
import time
import os
import re
import heapq
from collections import deque
from typing import Dict, Any, List
from werkzeug.utils import secure_filename

# Создаем Blueprint
api = Blueprint('api', __name__)

app = Flask(__name__)
UPLOAD_FOLDER = './cookies'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
ALLOWED_EXTENSIONS = {'txt'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def validate_cookies_file(filepath):
    """Проверка формата файла cookies"""
    try:
        with open(filepath, 'r') as f:
            first_line = f.readline().strip()
            # Проверка формата Netscape
            if first_line.startswith("# Netscape HTTP Cookie File"):
                return True
            # Проверка формата JSON
            if first_line.startswith("["):
                try:
                    json.load(f)
                    return True
                except:
                    pass
        return False
    except:
        return False

# Конфигурация очереди
MAX_CONCURRENT_TASKS = 3
PRIORITY_HIGH = 1
PRIORITY_NORMAL = 2
PRIORITY_LOW = 3

# Глобальные структуры данных
tasks: Dict[str, Dict] = {}
task_queue = deque()
active_tasks: List[str] = []
MAX_CONCURRENT_TASKS = 3

class QueueManager:
    """Менеджер очереди задач"""
    
    @staticmethod
    def add_task(**kwargs) -> str:
        """Добавление задачи в очередь"""
        task_id = str(uuid.uuid4())
        task = {
            'id': task_id,
            'status': 'queued',
            'progress': 0,
            'result': None,
            'service': None,
            'thread': None,
            'kwargs': kwargs
        }
        tasks[task_id] = task
        task_queue.append(task_id)
        QueueManager._process_queue()
        return task_id

    @staticmethod
    def _process_queue():
        """Обработка очереди задач"""
        while len(active_tasks) < MAX_CONCURRENT_TASKS and task_queue:
            task_id = task_queue.popleft()
            active_tasks.append(task_id)
            task = tasks[task_id]
            task['status'] = 'starting'
            # Запуск задачи через TaskManager
            # Удаляем параметры, не используемые в DownloadService
            service_kwargs = task['kwargs'].copy()
            for key in ['priority']:
                if key in service_kwargs:
                    del service_kwargs[key]
                    
            service = DownloadService(
                progress_callback=lambda d: TaskManager._update_progress(task_id, d),
                **service_kwargs
            )
            thread = threading.Thread(target=TaskManager._run_task_wrapper, args=(task_id, service))
            thread.start()
            task['service'] = service
            task['thread'] = thread

class TaskManager:
    """Менеджер для управления задачами скачивания"""
    
    @staticmethod
    def _run_task_wrapper(task_id: str, service: DownloadService):
        """Обертка для запуска задачи с последующим обновлением очереди"""
        try:
            result = service.run()
            tasks[task_id]['result'] = result
            tasks[task_id]['status'] = result['status']
        except Exception as e:
            tasks[task_id]['status'] = 'error'
            tasks[task_id]['result'] = {'error': str(e)}
        finally:
            # Удаляем задачу из активных и обрабатываем очередь
            if task_id in active_tasks:
                active_tasks.remove(task_id)
            QueueManager._process_queue()
    
    @staticmethod
    def create_task(url: str, save_path: str, **kwargs) -> str:
        """Создание новой задачи скачивания"""
        task_id = str(uuid.uuid4())
        task = {
            'id': task_id,
            'url': url,
            'status': 'queued',
            'progress': 0,
            'result': None,
            'service': None,
            'thread': None
        }
        
        # Создаем экземпляр сервиса
        service = DownloadService(
            url=url,
            save_path=save_path,
            progress_callback=lambda d: TaskManager._update_progress(task_id, d),
            **kwargs
        )
        
        # Сохраняем ссылку на сервис
        task['service'] = service
        
        # Запускаем в отдельном потоке
        thread = threading.Thread(target=TaskManager._run_task, args=(task_id,))
        thread.start()
        task['thread'] = thread
        
        tasks[task_id] = task
        return task_id
    
    @staticmethod
    def _run_task(task_id: str):
        """Выполнение задачи в фоновом потоке"""
        task = tasks.get(task_id)
        if not task:
            return
            
        try:
            task['status'] = 'processing'
            result = task['service'].run()
            task['result'] = result
            task['status'] = result['status']
        except Exception as e:
            task['status'] = 'error'
            task['result'] = {'error': str(e)}
    
    @staticmethod
    def _update_progress(task_id: str, progress_data: dict):
        """Обновление прогресса задачи"""
        task = tasks.get(task_id)
        if task:
            task['progress'] = progress_data.get('percent', 0)
            # Для простоты сохраняем последние данные прогресса
            task['progress_data'] = progress_data
    
    @staticmethod
    def get_task(task_id: str) -> dict:
        """Получение информации о задаче"""
        return tasks.get(task_id, {})
    
    @staticmethod
    def cancel_task(task_id: str):
        """Отмена задачи"""
        task = tasks.get(task_id)
        if task and task['service']:
            task['service'].cancel()
            task['status'] = 'cancelling'

@app.route('/upload_cookies', methods=['POST'])
def upload_cookies():
    """Загрузка файла cookies или данных для авторизации"""
    if 'file' in request.files:
        # Обработка файла cookies
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
            
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)
            
            # Валидация файла
            if not validate_cookies_file(filepath):
                os.remove(filepath)
                return jsonify({'error': 'Invalid cookies file format'}), 400
                
            return jsonify({
                'status': 'success',
                'filename': filename,
                'path': filepath
            }), 200
        else:
            return jsonify({'error': 'Invalid file type'}), 400
            
    elif request.json:
        # Обработка ручного ввода данных
        data = request.json
        cookies_data = data.get('cookies')
        login = data.get('login')
        password = data.get('password')
        
        if cookies_data:
            # Сохраняем cookies как файл
            filename = "manual_cookies.txt"
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            with open(filepath, 'w') as f:
                f.write(cookies_data)
                
            return jsonify({
                'status': 'success',
                'filename': filename,
                'path': filepath
            }), 200
            
        elif login and password:
            # Здесь должна быть логика авторизации
            # Пока просто возвращаем заглушку
            return jsonify({
                'status': 'success',
                'message': 'Manual auth not implemented yet'
            }), 200
            
        else:
            return jsonify({'error': 'Missing auth data'}), 400
            
    else:
        return jsonify({'error': 'No file or data provided'}), 400

# Пример конфигурации
DEFAULT_CONFIG = {
    'save_path': './downloads',
    'threads': 4,
    'max_retries': 3,
    'socks_proxy': None
}

@app.route('/download', methods=['POST'])
def start_download():
    """Запуск процесса скачивания"""
    data = request.json
    if not data or 'url' not in data:
        return jsonify({'error': 'Missing URL parameter'}), 400
    
    # Параметры скачивания
    params = {**DEFAULT_CONFIG, **data}
    priority = data.get('priority', PRIORITY_NORMAL)
    
    try:
        cookies_file = data.get('cookies_file')
        # Формируем параметры для задачи
        task_params = {
            'url': data['url'],
            'save_path': params['save_path'],
            'cookies_path': cookies_file,
            'priority': priority,
            'username': data.get('username'),
            'password': data.get('password')
        }
        task_params.update(params)
        
        task_id = QueueManager.add_task(**task_params)
        return jsonify({'task_id': task_id}), 202
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/queue', methods=['GET'])
def get_queue():
    """Получение состояния очереди"""
    def format_task(task):
        """Форматирование задачи для JSON сериализации"""
        return {
            'id': task['id'],
            'status': task['status'],
            'progress': task['progress'],
            'result': task['result'],
            'progress_data': task.get('progress_data', {}),
            'kwargs': task.get('kwargs', {})
        }
    
    queued_tasks = [format_task(tasks[tid]) for tid in task_queue]
    active_tasks_list = [format_task(tasks[tid]) for tid in active_tasks]
    
    response = {
        'queued': queued_tasks,
        'active': active_tasks_list,
        'max_concurrent': MAX_CONCURRENT_TASKS
    }
    return jsonify(response)

@api.route('/tasks', methods=['GET'])
def list_tasks():
    """Получение списка всех задач"""
    # Форматируем задачи для JSON сериализации
    formatted_tasks = []
    for task in tasks.values():
        formatted_task = {
            'id': task['id'],
            'status': task['status'],
            'progress': task['progress'],
            'result': task['result'],
            'progress_data': task.get('progress_data', {}),
            'kwargs': task.get('kwargs', {})
        }
        # Исключаем несериализуемые объекты
        formatted_tasks.append(formatted_task)
    return jsonify(formatted_tasks)

@api.route('/task/<task_id>', methods=['GET'])
def get_task(task_id):
    """Получение информации о конкретной задаче"""
    task = tasks.get(task_id)
    if not task:
        return jsonify({'error': 'Task not found'}), 404
    
    # Форматируем ответ для клиента
    response = {
        'id': task['id'],
        'status': task['status'],
        'progress': task['progress'],
        'result': task['result'],
        'progress_data': task.get('progress_data', {})
    }
    return jsonify(response)

@api.route('/cancel/<task_id>', methods=['POST'])
def cancel_task(task_id):
    """Отмена задачи скачивания"""
    task = tasks.get(task_id)
    if not task:
        return jsonify({'error': 'Task not found'}), 404
    
    try:
        if task['service']:
            task['service'].cancel()
            task['status'] = 'cancelled'
            return jsonify({'status': 'cancelled'}), 200
        else:
            return jsonify({'error': 'Task service not available'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Регистрируем Blueprint после определения всех маршрутов
app.register_blueprint(api, url_prefix='/api')

if __name__ == '__main__':
    app.run(debug=True)