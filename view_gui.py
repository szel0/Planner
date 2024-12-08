import tkinter as tk
from tkinter import ttk
from datetime import datetime

class GUI_PlannerApp():
    def __init__(self, controller):
        self.controller = controller
        self.window = tk.Tk()
        self.window.title("Task Planner")
        self.window.geometry("800x400")

        self.sort_index = 0
        self.SORT_TYPES = ["Sort By: Date ASC", "Sort By: Date DESC", "Sort By: Priority ASC", "Sort By: Priority DESC"]

        # Tytul i podtytul
        self.title_label = tk.Label(self.window, text="Task Planner", font=("Halvetica", 16)) 
        self.title_label.pack(pady=10)
        self.sub_title_label = tk.Label(self.window, text="Manage your tasks", font=("Halvetica", 12))
        self.sub_title_label.pack(pady=10)

        # Przyciski
        self.sort_button = tk.Button(self.window, text=self.SORT_TYPES[self.sort_index], command=self.change_sort)
        self.sort_button.pack(fill="x")

        self.filter_button = tk.Button(self.window, text="Filter", command=self.filter_tasks)
        self.filter_button.pack(fill="x")

        self.add_button = tk.Button(self.window, text="Add Task", command=self.add_task)
        self.add_button.pack(fill="x")

        #self.edit_button = tk.Button(self.window, text="Edit Task", command=selfedit_task)
        #self.edit_button.pack(fill="x")

        #self.delete_button = tk.Button(self.window, text="Delete Task", command=self.delete_task)
        #self.delete_button.pack(fill="x")

        # Tabela z zadaniami
        self.tasks_table = ttk.Treeview(self.window, columns=("T", "De", "Da", "P"), show="headings")
        self.tasks_table.heading("T", text="Title")
        self.tasks_table.heading("De", text="Description")
        self.tasks_table.heading("Da", text="Date")
        self.tasks_table.heading("P", text="Priority")


        self.tasks_table.pack(fill="both", expand=True)

        #Wczytanie zadan
        self.load_tasks()

    def load_tasks(self):
        self.tasks_table.delete(*self.tasks_table.get_children())
        self.controller.sort_tasks_by_key()
        tasks = self.controller.get_filtered_tasks()

        for task in tasks:
            self.tasks_table.insert("", "end", values=(task.title, task.description, task.date.strftime("%Y-%m-%d"), task.priority))

    def change_sort(self):
        self.sort_index = (self.sort_index + 1) % len(self.SORT_TYPES)
        self.sort_button.config(text=self.SORT_TYPES[self.sort_index])

        if self.sort_index == 0:
            self.controller.sort_key = "date"
            self.controller.sort_reverse = False
        elif self.sort_index == 1:
            self.controller.sort_key = "date"
            self.controller.sort_reverse = True
        elif self.sort_index == 2:
            self.controller.sort_key = "priority"
            self.controller.sort_reverse = False
        elif self.sort_index == 3:
            self.controller.sort_key = "priority"
            self.controller.sort_reverse = True

        self.load_tasks()

    def filter_tasks(self):
        FilterDialog(self, self.controller)

    def add_task(self):
        AddTaskDialog(self, self.controller)

class FilterDialog:
    def __init__(self, app, controller):
        self.app = app
        self.controller = controller
        self.dialog = tk.Toplevel()
        self.dialog.title("Filter Tasks")
        self.dialog.geometry("400x450")
        
        # Minimalna i maksymalna data
        min_date, max_date = self.controller.get_min_max_dates()

        min_date_value = self.controller.filtered_date[0].strftime("%Y-%m-%d") if self.controller.filtered_date[0] else min_date.strftime("%Y-%m-%d")
        max_date_value = self.controller.filtered_date[1].strftime("%Y-%m-%d") if self.controller.filtered_date[1] else max_date.strftime("%Y-%m-%d")
        min_priority_value = str(self.controller.filtered_priority[0]) if self.controller.filtered_priority[0] else "1"
        max_priority_value = str(self.controller.filtered_priority[1]) if self.controller.filtered_priority[1] else "5"

        # Tworzenie widgetów
        self.title_label = tk.Label(self.dialog, text="Filter by Minimum Date (YYYY-MM-DD):")
        self.title_label.pack(pady=5)
        self.input_min_date = tk.Entry(self.dialog)
        self.input_min_date.insert(0, min_date_value)
        self.input_min_date.pack(pady=5)

        self.title_label = tk.Label(self.dialog, text="Filter by Maximum Date (YYYY-MM-DD):")
        self.title_label.pack(pady=5)
        self.input_max_date = tk.Entry(self.dialog)
        self.input_max_date.insert(0, max_date_value)
        self.input_max_date.pack(pady=5)

        self.title_label = tk.Label(self.dialog, text="Filter by Minimum Priority (1-5):")
        self.title_label.pack(pady=5)
        self.input_min_priority = tk.Entry(self.dialog)
        self.input_min_priority.insert(0, min_priority_value)
        self.input_min_priority.pack(pady=5)

        self.title_label = tk.Label(self.dialog, text="Filter by Maximum Priority (1-5):")
        self.title_label.pack(pady=5)
        self.input_max_priority = tk.Entry(self.dialog)
        self.input_max_priority.insert(0, max_priority_value)
        self.input_max_priority.pack(pady=5)

        self.title_label = tk.Label(self.dialog, text="Filter by name:")
        self.title_label.pack(pady=5)
        self.input_name = tk.Entry(self.dialog)
        self.input_name.insert(0, self.controller.filtered_name)
        self.input_name.pack(pady=5)

        self.error_label = tk.Label(self.dialog, text="", fg="red")
        self.error_label.pack(pady=5)

        # Przycisk "Apply"
        self.apply_button = tk.Button(self.dialog, text="Apply", command=self.apply_filter)
        self.apply_button.pack(pady=5)

        # Przycisk "Clear Filters"
        self.clear_button = tk.Button(self.dialog, text="Clear Filters", command=self.clear_filters)
        self.clear_button.pack(pady=5)

    def apply_filter(self):
        min_date_input = self.input_min_date.get()
        max_date_input = self.input_max_date.get()
        min_priority_input = self.input_min_priority.get()
        max_priority_input = self.input_max_priority.get()
        name_input = self.input_name.get()

        min_date, max_date = self.controller.get_min_max_dates()

        # Ustawienie filtrów w kontrolerze
        error_message = self.controller.set_filter(
            min_date_input or min_date.strftime("%Y-%m-%d"),
            max_date_input or max_date.strftime("%Y-%m-%d"),
            min_priority_input or "1",
            max_priority_input or "5",
            name_input
        )

        if error_message:
            self.error_label.config(text=error_message)
        else:
            self.dialog.destroy()
            self.app.load_tasks()

    def clear_filters(self):
        self.controller.clear_filters()

        min_date, max_date = self.controller.get_min_max_dates()

        self.input_min_date.delete(0, tk.END)
        self.input_min_date.insert(0, min_date.strftime("%Y-%m-%d"))
        self.input_max_date.delete(0, tk.END)
        self.input_max_date.insert(0, max_date.strftime("%Y-%m-%d"))
        self.input_min_priority.delete(0, tk.END)
        self.input_min_priority.insert(0, "1")
        self.input_max_priority.delete(0, tk.END)
        self.input_max_priority.insert(0, "5")
        self.input_name.delete(0, tk.END)

class AddTaskDialog:
    def __init__(self, app, controller):
        self.app = app
        self.controller = controller
        self.dialog = tk.Toplevel(app.window)
        self.dialog.title("Add Task")
        self.dialog.geometry("400x320")

        today_date = datetime.now().strftime("%Y-%m-%d")

        self.title_label = tk.Label(self.dialog, text="Title:")
        self.title_label.pack(pady=5)
        self.input_title = tk.Entry(self.dialog)
        self.input_title.insert(0, "Task Title")
        self.input_title.pack(pady=5)

        self.description_label = tk.Label(self.dialog, text="Description:")
        self.description_label.pack(pady=5)
        self.input_description = tk.Entry(self.dialog)
        self.input_description.insert(0, "Task Description")
        self.input_description.pack(pady=5)

        self.date_label = tk.Label(self.dialog, text="Date:")
        self.date_label.pack(pady=5)
        self.input_date = tk.Entry(self.dialog)
        self.input_date.insert(0, today_date)
        self.input_date.pack(pady=5)

        self.priority_label = tk.Label(self.dialog, text="Priority:")
        self.priority_label.pack(pady=5)
        self.input_priority = tk.Entry(self.dialog)
        self.input_priority.insert(0, "3")
        self.input_priority.pack(pady=5)

        self.error_label = tk.Label(self.dialog, text="", fg="red")
        self.error_label.pack(pady=5)

        self.cancel_button = tk.Button(self.dialog, text="Cancel", command=self.cancel)
        self.cancel_button.pack(side="right", padx=10, pady=10)

        self.ok_button = tk.Button(self.dialog, text="Submit", command=self.submit)
        self.ok_button.pack(side="left", padx=10, pady=10)

    def submit(self):
        title = self.input_title.get() or "Task Title"
        description = self.input_description.get() or "Task Description"
        date = self.input_date.get() or datetime.now().strftime("%Y-%m-%d")
        priority = self.input_priority.get() or "3"

        error_message = self.controller.add_task(title, description, date, priority)

        if error_message:
            self.error_label.config(text=error_message)
        else:
            self.dialog.destroy()
            self.app.load_tasks()

    def cancel(self):
        self.dialog.destroy()