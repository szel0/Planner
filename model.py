from datetime import datetime

class Priority:
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4

class Task:
    def __init__(self, title, description, date, priority=Priority.MEDIUM):
        self.title = title
        self.description = description
        self.date = datetime.strptime(date, "%Y-%m-%d")
        self.priority = priority

    def __repr__(self):
        return f"Task(title='{self.title}', description='{self.description}', date='{self.date.strftime('%Y-%m-%d')}')"

class Calendar:
    def __init__(self):
        self.tasks = {}

    def add_task(self, task):
        # Konwertujemy datę na string w formacie "YYYY-MM-DD"
        date_key = task.date.strftime("%Y-%m-%d")
        if date_key not in self.tasks:
            self.tasks[date_key] = []
        self.tasks[date_key].append(task)

    def get_tasks_for_day(self, date):
        # Zakładamy, że 'date' jest stringiem w formacie "YYYY-MM-DD"
        return self.tasks.get(date, [])

