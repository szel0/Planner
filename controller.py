from model import Task, Priority
from datetime import datetime


class PlannerController:
    def __init__(self):
        self.tasks = []
        self.task_id = 1

    def add_task(self, title, description, date, priority=Priority.MEDIUM):
        if not date:
            return datetime.now().strftime("%Y-%m-%d")
        try:
            task_date = datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            return "Error: Invalid date format. Please use 'YYYY-MM-DD'."

        if priority < 1 or priority > 4:
            return "Error: Priority must be between 1 and 4."

        task = Task(title, description, task_date, priority, self.task_id)
        self.tasks.append(task)
        self.task_id += 1
        return None

    def get_task_by_id(self, task_id):
        for task in self.tasks:
            if task.id == task_id:
                return task
        return None

    def get_all_tasks(self):
        return self.tasks

    @staticmethod
    def edit_task(task, new_title=None, new_description=None, new_date=None, new_priority=None):
        if new_title:
            task.title = new_title
        if new_description:
            task.description = new_description
        if new_date:
            task.date = new_date
        if new_priority:
            task.priority = new_priority

    def delete_task(self, task):
        if task in self.tasks:
            self.tasks.remove(task)
