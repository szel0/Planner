import uuid


class Priority:
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


class Task:
    def __init__(self, title, description, date, priority, task_id=None):
        self.title = title
        self.description = description
        self.date = date
        self.priority = priority
        self.id = task_id or str(uuid.uuid4())

    def __repr__(self):
        return f"Task(title='{self.title}', description='{self.description}', date='{self.date.strftime('%Y-%m-%d')}')"
