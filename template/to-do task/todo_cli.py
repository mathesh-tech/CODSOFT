import os


def get_storage_path():
    """Return the absolute path to tasks.txt next to this script."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_dir, "tasks.txt")


def load_tasks():
    """Load tasks from tasks.txt, returning a list of task strings."""
    path = get_storage_path()
    if not os.path.exists(path):
        return []
    tasks = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            task = line.rstrip("\n")
            if task:
                tasks.append(task)
    return tasks


def save_tasks(tasks):
    """Persist the list of tasks to tasks.txt."""
    path = get_storage_path()
    with open(path, "w", encoding="utf-8") as f:
        for task in tasks:
            f.write(f"{task}\n")


def print_menu():
    print("\n=== To-Do List ===")
    print("1) View tasks")
    print("2) Add task")
    print("3) Update task")
    print("4) Delete task")
    print("5) Exit")


def prompt_choice():
    choice = input("Select an option (1-5): ").strip()
    if choice not in {"1", "2", "3", "4", "5"}:
        print("Invalid choice. Please enter a number between 1 and 5.")
        return None
    return int(choice)


def view_tasks(tasks):
    if not tasks:
        print("No tasks found.")
        return
    print("\nCurrent tasks:")
    for idx, task in enumerate(tasks, start=1):
        print(f"{idx}. {task}")


def add_task(tasks):
    new_task = input("Enter a new task: ").strip()
    if not new_task:
        print("Task cannot be empty.")
        return tasks
    tasks.append(new_task)
    save_tasks(tasks)
    print("Task added.")
    return tasks


def select_task_index(tasks, action_name):
    if not tasks:
        print("No tasks to select.")
        return None
    view_tasks(tasks)
    raw = input(f"Enter the task number to {action_name}: ").strip()
    if not raw.isdigit():
        print("Invalid input. Please enter a valid task number.")
        return None
    index = int(raw)
    if index < 1 or index > len(tasks):
        print("Task number out of range.")
        return None
    return index - 1


def update_task(tasks):
    idx = select_task_index(tasks, "update")
    if idx is None:
        return tasks
    current = tasks[idx]
    print(f"Current task: {current}")
    updated = input("Enter the updated text (leave empty to cancel): ").strip()
    if not updated:
        print("Update cancelled.")
        return tasks
    tasks[idx] = updated
    save_tasks(tasks)
    print("Task updated.")
    return tasks


def delete_task(tasks):
    idx = select_task_index(tasks, "delete")
    if idx is None:
        return tasks
    to_delete = tasks[idx]
    confirm = input(f"Delete '{to_delete}'? (y/N): ").strip().lower()
    if confirm != "y":
        print("Deletion cancelled.")
        return tasks
    del tasks[idx]
    save_tasks(tasks)
    print("Task deleted.")
    return tasks


def main():
    tasks = load_tasks()
    while True:
        print_menu()
        choice = prompt_choice()
        if choice is None:
            continue
        if choice == 1:
            view_tasks(tasks)
        elif choice == 2:
            tasks = add_task(tasks)
        elif choice == 3:
            tasks = update_task(tasks)
        elif choice == 4:
            tasks = delete_task(tasks)
        elif choice == 5:
            print("Goodbye!")
            break


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nExiting...")


