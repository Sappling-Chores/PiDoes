"""
manage_task.py
--------------
Legacy wrapper delegating to task_manager.py.
"""

try:
    import task_manager
except ImportError:
    import APP.task_manager as task_manager

fetch_task = task_manager.load_task_data
write_task = task_manager.save_task_data
manage_old_task = task_manager.manage_old_task
manage_task = task_manager.manage_task

if __name__ == "__main__":
    manage_task()