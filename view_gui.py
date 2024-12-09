import tkinter as tk
from tkinter import ttk
from datetime import datetime

class GUI_PlannerApp():
    def __init__(self, controller):
        self.controller = controller
        self.window = tk.Tk()
        self.window.title("Task Planner")
        self.window.geometry("1050x500")
        self.window.config(bg="gray")

        self.sort_index = 0
        self.SORT_TYPES = ["Sort By: Date ASC", "Sort By: Date DESC", "Sort By: Priority ASC", "Sort By: Priority DESC"]

        header_frame = tk.Frame(self.window, bg="gray")
        header_frame.pack(side="top", pady=10)

        self.title_label = tk.Label(header_frame, text="Task Planner - Manage your tasks", font=("Noto Sans", 8), fg="white", bg="gray") 
        self.title_label.pack()

        left_frame = tk.Frame(self.window, bg="gray", width=200)
        left_frame.pack(side="left", fill="y", padx=10)

        self.sort_button = tk.Button(left_frame, text=self.SORT_TYPES[self.sort_index], command=self.change_sort, font=("Noto Sans", 9), width=30, height=1, fg="white", bg="gray")
        self.sort_button.pack(fill="x", pady=5)

        self.filter_button = tk.Button(left_frame, text="Filter", command=self.filter_tasks, font=("Noto Sans", 9), width=30, height=1, fg="white",  bg="gray")
        self.filter_button.pack(fill="x", pady=5)

        self.add_button = tk.Button(left_frame, text="Add Task", command=self.add_task, font=("Noto Sans", 9), width=30, height=1, fg="white",  bg="green")
        self.add_button.pack(fill="x", pady=5)

        self.edit_button = tk.Button(left_frame, text="Edit Task", command=self.edit_task, font=("Noto Sans", 9), width=30, height=1, fg="white",  bg="blue")
        self.edit_button.pack(fill="x", pady=5)

        self.delete_button = tk.Button(left_frame, text="Delete Task", command=self.delete_task, font=("Noto Sans", 9), width=30, height=1, fg="white",  bg="red")
        self.delete_button.pack(fill="x", pady=5)

        style = ttk.Style()

        style.theme_use("clam")

        style.configure("Treeview", 
                        background="gray",
                        foreground="black",
                        rowheight=25,
                        fieldbackground="silver",
                        font=("Noto Sans", 8))
        
        style.map('Treeview',
                 background=[('selected', 'red')])

        right_frame = tk.Frame(self.window, bg="gray", width=780)
        right_frame.pack(side="left", fill="y", padx=10)

        self.tasks_table = ttk.Treeview(right_frame, 
                                        columns=("T", 
                                                 "De", 
                                                 "Da", 
                                                 "P", 
                                                 "ID"), 
                                        show="headings")
        
        self.tasks_table.column("T", width=140, stretch=True)
        self.tasks_table.column("De", width=500, stretch=True)
        self.tasks_table.column("Da", width=80, stretch=True, anchor="center")
        self.tasks_table.column("P", width=60, stretch=True, anchor="center")
        self.tasks_table.column("ID", width=0, stretch=False)

        self.tasks_table.heading("T", text="Title")
        self.tasks_table.heading("De", text="Description")
        self.tasks_table.heading("Da", text="Date")
        self.tasks_table.heading("P", text="Priority")
        self.tasks_table.heading("ID", text="")

        self.tasks_table.tag_configure('oddrow', background="lightblue")
        self.tasks_table.tag_configure('evenrow', background="silver")

        self.tasks_table.pack(fill="both", expand=True)

        self.load_tasks()

    def load_tasks(self):
        self.tasks_table.delete(*self.tasks_table.get_children())
        self.controller.sort_tasks_by_key()
        tasks = self.controller.get_filtered_tasks()
        count=0

        for task in tasks:
            if count % 2 == 0: 
                self.tasks_table.insert(
                    "", 
                    "end", 
                    values=(
                        task.title, 
                        task.description, 
                        task.date.strftime("%Y-%m-%d"), 
                        task.priority, 
                        task.id
                    ),
                    tags=('evenrow',)
                )
            else:
                self.tasks_table.insert(
                    "", 
                    "end", 
                    values=(
                        task.title, 
                        task.description, 
                        task.date.strftime("%Y-%m-%d"), 
                        task.priority, 
                        task.id
                    ),
                    tags=('oddrow',)
                )                
            count += 1

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

    def edit_task(self):
        if not self.tasks_table.get_children():
            self.show_message_window("No tasks available to delete", fg="red")
            return
            
        selected_task = self.tasks_table.selection()

        if not selected_task:
            self.show_message_window("No task selected", fg="red")
            return
        
        EditTaskDialog(self, self.controller, selected_task)

    def delete_task(self):
        if not self.tasks_table.get_children():
            self.show_message_window("No tasks available to delete", fg="red")
            return
            
        selected_task = self.tasks_table.selection()

        if not selected_task:
            self.show_message_window("No task selected", fg="red")
            return
        
        DeleteConfirm(self, self.controller, selected_task)


    def show_message_window(self, message, fg="black"):
        message_window = tk.Toplevel(self.window)
        message_window.title("Information")
        message_window.geometry("300x100")

        label = tk.Label(message_window, text=message, fg=fg, wraplength=250, justify="center")
        label.pack(pady=20)

        close_button = tk.Button(message_window, text="OK", command=message_window.destroy)
        close_button.pack(pady=10)

class FilterDialog:
    def __init__(self, app, controller):
        self.app = app
        self.controller = controller
        self.dialog = tk.Toplevel()
        self.dialog.title("Filter Tasks")
        self.dialog.geometry("400x450")
        self.dialog.config(bg="gray")
        
        # Minimalna i maksymalna data
        min_date, max_date = self.controller.get_min_max_dates()

        min_date_value = self.controller.filtered_date[0].strftime("%Y-%m-%d") if self.controller.filtered_date[0] else min_date.strftime("%Y-%m-%d")
        max_date_value = self.controller.filtered_date[1].strftime("%Y-%m-%d") if self.controller.filtered_date[1] else max_date.strftime("%Y-%m-%d")
        min_priority_value = str(self.controller.filtered_priority[0]) if self.controller.filtered_priority[0] else "1"
        max_priority_value = str(self.controller.filtered_priority[1]) if self.controller.filtered_priority[1] else "5"

        # Tworzenie widgetów
        self.title_label = tk.Label(self.dialog, text="Filter by Minimum Date (YYYY-MM-DD):", font=("Noto Sans", 9), bg="gray", fg="white")
        self.title_label.pack(pady=5)
        self.input_min_date = tk.Entry(self.dialog, font=("Noto Sans", 9))
        self.input_min_date.insert(0, min_date_value)
        self.input_min_date.pack(pady=5)

        self.title_label = tk.Label(self.dialog, text="Filter by Maximum Date (YYYY-MM-DD):", font=("Noto Sans", 9), bg="gray", fg="white")
        self.title_label.pack(pady=5)
        self.input_max_date = tk.Entry(self.dialog, font=("Noto Sans", 9))
        self.input_max_date.insert(0, max_date_value)
        self.input_max_date.pack(pady=5)

        self.title_label = tk.Label(self.dialog, text="Filter by Minimum Priority (1-5):", font=("Noto Sans", 9), bg="gray", fg="white")
        self.title_label.pack(pady=5)
        self.input_min_priority = tk.Entry(self.dialog, font=("Noto Sans", 9))
        self.input_min_priority.insert(0, min_priority_value)
        self.input_min_priority.pack(pady=5)

        self.title_label = tk.Label(self.dialog, text="Filter by Maximum Priority (1-5):", font=("Noto Sans", 9), bg="gray", fg="white")
        self.title_label.pack(pady=5)
        self.input_max_priority = tk.Entry(self.dialog, font=("Noto Sans", 9))
        self.input_max_priority.insert(0, max_priority_value)
        self.input_max_priority.pack(pady=5)

        self.title_label = tk.Label(self.dialog, text="Filter by name:", font=("Noto Sans", 9), bg="gray", fg="white")
        self.title_label.pack(pady=5)
        self.input_name = tk.Entry(self.dialog, font=("Noto Sans", 9))
        self.input_name.insert(0, self.controller.filtered_name)
        self.input_name.pack(pady=5)

        self.error_label = tk.Label(self.dialog, text="", font=("Noto Sans", 12), fg="pink", bg="gray")
        self.error_label.pack(pady=5)

        # Przycisk "Apply"
        self.apply_button = tk.Button(self.dialog, text="Apply", command=self.apply_filter, font=("Noto Sans", 9), width=30, height=1, fg="white",  bg="green")
        self.apply_button.pack(pady=5)

        # Przycisk "Clear Filters"
        self.clear_button = tk.Button(self.dialog, text="Clear Filters", command=self.clear_filters, font=("Noto Sans", 9), width=30, height=1, fg="white",  bg="red")
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
        self.dialog.geometry("400x450")
        self.dialog.config(bg="gray")

        today_date = datetime.now().strftime("%Y-%m-%d")

        self.title_label = tk.Label(self.dialog, text="Title:", font=("Noto Sans", 9), bg="gray", fg="white")
        self.title_label.pack(pady=5)
        self.input_title = tk.Entry(self.dialog, font=("Noto Sans", 9))
        self.input_title.insert(0, "Task Title")
        self.input_title.pack(pady=5)

        self.description_label = tk.Label(self.dialog, text="Description:", font=("Noto Sans", 9), bg="gray", fg="white")
        self.description_label.pack(pady=5)
        self.input_description = tk.Text(self.dialog, width=40, height=5, wrap="word", font=("Noto Sans", 9))
        self.input_description.insert("1.0", "Task Description")
        self.input_description.pack(pady=5)

        self.date_label = tk.Label(self.dialog, text="Date:", font=("Noto Sans", 9), bg="gray", fg="white")
        self.date_label.pack(pady=5)
        self.input_date = tk.Entry(self.dialog, font=("Noto Sans", 9))
        self.input_date.insert(0, today_date)
        self.input_date.pack(pady=5)

        self.priority_label = tk.Label(self.dialog, text="Priority:", font=("Noto Sans", 9), bg="gray", fg="white")
        self.priority_label.pack(pady=5)
        self.input_priority = tk.Entry(self.dialog, font=("Noto Sans", 9))
        self.input_priority.insert(0, "3")
        self.input_priority.pack(pady=5)

        self.error_label = tk.Label(self.dialog, text="", fg="pink", font=("Noto Sans", 12), bg="gray")
        self.error_label.pack(pady=5)

        self.ok_button = tk.Button(self.dialog, text="Submit", command=self.submit, font=("Noto Sans", 9), width=30, height=1, fg="white",  bg="green")
        self.ok_button.pack(pady=5)

        self.cancel_button = tk.Button(self.dialog, text="Cancel", command=self.cancel, font=("Noto Sans", 9), width=30, height=1, fg="white",  bg="red")
        self.cancel_button.pack(pady=5)


    def submit(self):
        title = self.input_title.get() or "Task Title"
        description = self.input_description.get("1.0", "end-1c") or "Task Description"
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

class EditTaskDialog:
    def __init__(self, app, controller, selected_task):
        self.app = app
        self.controller = controller
        self.selected_task = selected_task
        self.dialog = tk.Toplevel(app.window)
        self.dialog.title("Edit Task")
        self.dialog.geometry("400x450")
        self.dialog.config(bg="gray")

        self.title_label = tk.Label(self.dialog, text="Title:", font=("Noto Sans", 9), bg="gray", fg="white")
        self.title_label.pack(pady=5)
        self.input_title = tk.Entry(self.dialog, font=("Noto Sans", 9))
        self.input_title.insert(0, self.app.tasks_table.item(self.selected_task)["values"][0])
        self.input_title.pack(pady=5)

        self.description_label = tk.Label(self.dialog, text="Description:", font=("Noto Sans", 9), bg="gray", fg="white")
        self.description_label.pack(pady=5)
        self.input_description = tk.Text(self.dialog, width=40, height=5, wrap="word", font=("Noto Sans", 9))
        self.input_description.insert("1.0", self.app.tasks_table.item(self.selected_task)["values"][1])
        self.input_description.pack(pady=5)

        self.date_label = tk.Label(self.dialog, text="Date:", font=("Noto Sans", 9), bg="gray", fg="white")
        self.date_label.pack(pady=5)
        self.input_date = tk.Entry(self.dialog, font=("Noto Sans", 9))
        self.input_date.insert(0, self.app.tasks_table.item(self.selected_task)["values"][2])
        self.input_date.pack(pady=5)

        self.priority_label = tk.Label(self.dialog, text="Priority:", font=("Noto Sans", 9), bg="gray", fg="white")
        self.priority_label.pack(pady=5)
        self.input_priority = tk.Entry(self.dialog, font=("Noto Sans", 9))
        self.input_priority.insert(0, self.app.tasks_table.item(self.selected_task)["values"][3])
        self.input_priority.pack(pady=5)

        self.error_label = tk.Label(self.dialog, text="", fg="pink", font=("Noto Sans", 12), bg="gray")
        self.error_label.pack(pady=5)

        self.ok_button = tk.Button(self.dialog, text="Confirm", command=self.submit, width=30, height=1, fg="white",  bg="green")
        self.ok_button.pack(pady=5)
        
        self.cancel_button = tk.Button(self.dialog, text="Cancel", command=self.cancel, width=30, height=1, fg="white",  bg="red")
        self.cancel_button.pack(pady=5)

    def submit(self):
        new_title = self.input_title.get()
        new_description = self.input_description.get("1.0", "end-1c")
        new_date = self.input_date.get()
        new_priority = self.input_priority.get()
        current_task = self.controller.get_task_by_id(self.app.tasks_table.item(self.selected_task)["values"][4])

        error_message = self.controller.edit_task(
            current_task,
            new_title,
            new_description,
            new_date,
            new_priority
        )

        if error_message:
            self.error_label.config(text=error_message)
        else:
            self.dialog.destroy()
            self.app.load_tasks()

    def cancel(self):
        self.dialog.destroy()

class DeleteConfirm:
    def __init__(self, app, controller, selected_task):
        self.app = app
        self.controller = controller
        self.selected_task = selected_task

        self.dialog = tk.Toplevel(app.window)
        self.dialog.title("Confirm Deletion")
        self.dialog.geometry("300x100")
        self.dialog.config(bg="gray")

        self.confirm_label = tk.Label(self.dialog, text=f"Are you sure you want to delete '{self.app.tasks_table.item(self.selected_task)['values'][0]}'?", bg="gray", fg="white", font=("Noto Sans", 9))
        self.confirm_label.pack(pady=10)

        self.cancel_button = tk.Button(self.dialog, text="Cancel", command=self.cancel, bg="blue", fg="white",  font=("Noto Sans", 9))
        self.cancel_button.pack(side="right", padx=10, pady=10)

        self.delete_button = tk.Button(self.dialog, text="Delete", command=self.delete, bg="red", fg="white",   font=("Noto Sans", 9))
        self.delete_button.pack(side="left", padx=10, pady=10)

    def delete(self):
        self.controller.delete_task(self.app.tasks_table.item(self.selected_task)["values"][4])
        self.dialog.destroy()
        self.app.load_tasks()

    def cancel(self):
        self.dialog.destroy()
