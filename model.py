class Task:
    def __init__(self, title, description, date, priority, task_id):
        self.title = title
        self.description = description
        self.date = date
        self.priority = priority
        self.id = task_id

    def __repr__(self):
        return f"Task(title='{self.title}', description='{self.description}', date='{self.date.strftime('%Y-%m-%d')}')"
