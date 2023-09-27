import threading
import time
import uuid
import logging

class TaskScheduler:
    def __init__(self):
        self.tasks = {}
        self.is_running = False
        self.lock = threading.Lock()
        self.logger = None

    def initialize_logging(self, log_filename='scheduler.log'):
        """
        Initialize logging for the scheduler.

        Args:
            log_filename (str, optional): The name of the log file (default is 'scheduler.log').
        """
        logging.basicConfig(filename=log_filename, level=logging.INFO)
        self.logger = logging.getLogger('SchedulerLogger')

    def _log_event(self, message):
        """
        Log an event to the scheduler's log.

        Args:
            message (str): The message to log.
        """
        if self.logger:
            self.logger.info(message)

    def add_task(self, task, interval, priority=0, dependencies=None, args=(), kwargs={}, name=None, retry=False, max_retries=3, start_time=None, end_time=None, timeout=None, resources=None, scheduling_strategy=None):
        """
        Add a task to the scheduler with various options.

        Args:
            task (callable): The function to execute as a task.
            interval (int): The time interval (in seconds) between task executions.
            priority (int, optional): The task priority (default is 0).
            dependencies (list, optional): A list of task names that this task depends on (default is None).
            args (tuple, optional): Arguments to pass to the task function.
            kwargs (dict, optional): Keyword arguments to pass to the task function.
            name (str, optional): A unique name for the task (auto-generated if not provided).
            retry (bool, optional): Whether to retry the task in case of failure (default is False).
            max_retries (int, optional): Maximum number of retries (default is 3).
            start_time (int, optional): The UNIX timestamp when the task should start (default is None).
            end_time (int, optional): The UNIX timestamp when the task should end (default is None).
            timeout (int, optional): The maximum execution time (in seconds) allowed for the task (default is None).
            resources (dict, optional): Resources required by the task (e.g., {'cpu': 2, 'memory': 1024}).
            scheduling_strategy (callable, optional): A custom scheduling strategy function that determines when to execute the task (default is None).

        Returns:
            str: The name of the added task.
        """
        if name is None:
            name = str(uuid.uuid4())
        with self.lock:
            self.tasks[name] = {
                'task': task,
                'interval': interval,
                'args': args,
                'kwargs': kwargs,
                'last_execution': 0,
                'retry': retry,
                'max_retries': max_retries,
                'retry_count': 0,
                'start_time': start_time,
                'end_time': end_time,
                'priority': priority,
                'dependencies': dependencies if dependencies else [],
                'timeout': timeout,
                'resources': resources,
                'scheduling_strategy': scheduling_strategy
            }
        return name

    def modify_task(self, name, **kwargs):
        """
        Modify an existing task's attributes.

        Args:
            name (str): The name of the task to modify.
            kwargs: Keyword arguments to update task attributes (e.g., interval=10, retry=True).

        Returns:
            bool: True if the task was modified successfully, False otherwise.
        """
        with self.lock:
            task_info = self.tasks.get(name)
            if task_info:
                for key, value in kwargs.items():
                    if key in task_info:
                        task_info[key] = value
                    else:
                        return False
                return True
        return False

    def reschedule_task(self, name, new_interval):
        """
        Reschedule an existing task with a new interval.

        Args:
            name (str): The name of the task to reschedule.
            new_interval (int): The new time interval (in seconds) between task executions.

        Returns:
            bool: True if the task was rescheduled successfully, False otherwise.
        """
        with self.lock:
            task_info = self.tasks.get(name)
            if task_info:
                task_info['interval'] = new_interval
                return True
        return False

    def remove_task(self, name):
        """
        Remove a task from the scheduler.

        Args:
            name (str): The name of the task to remove.

        Returns:
            bool: True if the task was removed successfully, False otherwise.
        """
        with self.lock:
            if name in self.tasks:
                del self.tasks[name]
                return True
        return False

    def _execute_task(self, name):
        while self.is_running:
            with self.lock:
                task_info = self.tasks.get(name)
            if task_info:
                task, interval, args, kwargs, last_execution, retry, max_retries, retry_count, start_time, end_time, timeout, resources, scheduling_strategy = (
                    task_info['task'],
                    task_info['interval'],
                    task_info['args'],
                    task_info['kwargs'],
                    task_info['last_execution'],
                    task_info['retry'],
                    task_info['max_retries'],
                    task_info['retry_count'],
                    task_info['start_time'],
                    task_info['end_time'],
                    task_info['timeout'],
                    task_info['resources'],
                    task_info['scheduling_strategy']
                )
                current_time = time.time()

                if scheduling_strategy:
                    if not scheduling_strategy(task_info):
                        # The scheduling strategy determined not to execute the task.
                        time.sleep(1)  # Sleep for a second and check again.
                        continue
                
                # Check if it's time to execute the task
                if (
                    current_time - last_execution >= interval and
                    (start_time is None or current_time >= start_time) and
                    (end_time is None or current_time <= end_time)
                ):
                    try:
                        # Execute the task with a timeout
                        if timeout:
                            task_thread = threading.Thread(target=task, args=args, kwargs=kwargs)
                            task_thread.start()
                            task_thread.join(timeout=timeout)
                        else:
                            task(*args, **kwargs)

                        task_info['last_execution'] = current_time
                        if not retry:  # Remove the task if retry is False
                            self.remove_task(name)
                        self._log_event(f'Task {name} executed successfully.')
                    except Exception as e:
                        self._log_event(f'Task {name} encountered an error: {e}')
                        if retry and retry_count < max_retries:
                            task_info['retry_count'] += 1
                            task_info['last_execution'] = current_time  # Reset last_execution time for retry
                        else:
                            if not retry:  # Remove the task if retry is False and an error occurred
                                self.remove_task(name)
                            break  # Exit the loop if max retries reached or retry is False
            else:
                break
            time.sleep(1)  # Sleep for a second to avoid busy-waiting

    def _run_tasks(self):
        while self.is_running:
            with self.lock:
                task_names = list(self.tasks.keys())
                executed_tasks = []

            # Sort tasks based on priority (higher priority first)
            task_names.sort(key=lambda name: self.tasks[name]['priority'], reverse=True)

            for name in task_names:
                # Check dependencies
                dependencies = self.tasks[name]['dependencies']
                dependencies_satisfied = all(dep in executed_tasks for dep in dependencies)
                if not dependencies_satisfied:
                    continue

                task_thread = threading.Thread(target=self._execute_task, args=(name,))
                task_thread.start()
                task_thread.join()  # Wait for the task to finish

                executed_tasks.append(name)

    def start(self):
        """
        Start the scheduler and begin executing tasks.
        """
        with self.lock:
            task_names = list(self.tasks.keys())
            current_time = time.time()
            for name in task_names:
                self.tasks[name]['last_execution'] = current_time

        self.is_running = True
        self.thread = threading.Thread(target=self._run_tasks)
        self.thread.start()

    def stop(self):
        """
        Stop the scheduler and wait for all tasks to complete.
        """
        self.is_running = False
        if self.thread:
            self.thread.join()

    def pause(self):
        """
        Pause the scheduler, temporarily stopping task execution.
        """
        self.is_running = False

    def resume(self):
        """
        Resume the scheduler, allowing task execution to continue.
        """
        self.is_running = True

    def get_task_status(self, name):
        """
        Get the status of a task (pending, running, completed, failed).

        Args:
            name (str): The name of the task to query.

        Returns:
            str: The status of the task.
        """
        with self.lock:
            task_info = self.tasks.get(name)
        if task_info:
            if task_info['last_execution'] == 0:
                return 'Pending'
            elif task_info['retry_count'] >= task_info['max_retries']:
                return 'Failed'
            else:
                return 'Running'
        else:
            return 'Not Found'
        
    def get_all_task_names(self):
        """
        Get the names of all tasks currently in the scheduler.

        Returns:
            list: A list of task names.
        """
        with self.lock:
            task_names = list(self.tasks.keys())
        return task_names

