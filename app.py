from flask import Flask, render_template, request, session, redirect, url_for
import re
import os
from jinja2 import ChoiceLoader, FileSystemLoader

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Change this to a random secret key

# Allow templates to be loaded from both 'templates' and 'template' directories
app.jinja_loader = ChoiceLoader([
    app.jinja_loader,
    FileSystemLoader(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'template')),
])

def safe_eval(expression):
    """Safely evaluate mathematical expressions"""
    # Remove any characters that aren't numbers, operators, or parentheses
    cleaned = re.sub(r'[^0-9+\-*/().]', '', expression)
    
    # Check if expression contains only allowed characters
    if not re.match(r'^[0-9+\-*/().\s]+$', expression):
        return "Invalid characters"
    
    try:
        # Use a safer evaluation method
        result = eval(cleaned, {"__builtins__": {}}, {})
        return str(result)
    except ZeroDivisionError:
        return "Division by zero"
    except Exception:
        return "Error"

@app.route("/calc", methods=["GET", "POST"])
def calculator():
    if 'expression' not in session:
        session['expression'] = ""
    
    display_text = session['expression']
    
    if request.method == "POST":
        action = request.form.get("action")
        
        if action == "clear":
            session['expression'] = ""
            display_text = ""
        elif action == "equals":
            if session['expression']:
                result = safe_eval(session['expression'])
                display_text = result
                session['expression'] = ""
        else:
            # Add the action to the expression
            session['expression'] += action
            display_text = session['expression']
    
    return render_template("index.html", display_text=display_text)


@app.route("/")
def home():
    return redirect(url_for("todo_page"))


# -----------------------------
# To-Do List (HTML frontend)
# -----------------------------

TASKS_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "template",
    "to-do task",
    "tasks.txt",
)


def load_tasks():
    """Load tasks with done status. Supports legacy plain-text lines."""
    if not os.path.exists(TASKS_FILE):
        return []
    tasks = []
    with open(TASKS_FILE, "r", encoding="utf-8") as f:
        for line in f:
            raw = line.rstrip("\n")
            if not raw:
                continue
            # New format: "0|Task" or "1|Task"; Legacy: "Task"
            if "|" in raw and raw.split("|", 1)[0] in {"0", "1"}:
                done_flag, text = raw.split("|", 1)
                tasks.append({"text": text, "done": done_flag == "1"})
            else:
                tasks.append({"text": raw, "done": False})
    return tasks


def save_tasks(tasks):
    with open(TASKS_FILE, "w", encoding="utf-8") as f:
        for task in tasks:
            done_flag = "1" if task.get("done") else "0"
            text = task.get("text", "").replace("\n", " ")
            f.write(f"{done_flag}|{text}\n")


@app.route("/todo", methods=["GET"])
def todo_page():
    tasks = load_tasks()
    return render_template("to-do task/index.html", tasks=tasks)


@app.route("/todo/add", methods=["POST"])
def todo_add():
    tasks = load_tasks()
    new_task = (request.form.get("task") or "").strip()
    if not new_task:
        return redirect(url_for("todo_page"))
    tasks.append({"text": new_task, "done": False})
    save_tasks(tasks)
    return redirect(url_for("todo_page"))


@app.route("/todo/update/<int:index>", methods=["POST"])
def todo_update(index):
    tasks = load_tasks()
    if 0 <= index < len(tasks):
        updated = (request.form.get("task") or "").strip()
        if updated:
            tasks[index]["text"] = updated
            save_tasks(tasks)
    return redirect(url_for("todo_page"))


@app.route("/todo/delete/<int:index>", methods=["POST"])
def todo_delete(index):
    tasks = load_tasks()
    if 0 <= index < len(tasks):
        del tasks[index]
        save_tasks(tasks)
    return redirect(url_for("todo_page"))


@app.route("/todo/toggle/<int:index>", methods=["POST"])
def todo_toggle(index):
    tasks = load_tasks()
    if 0 <= index < len(tasks):
        tasks[index]["done"] = not tasks[index].get("done", False)
        save_tasks(tasks)
    return redirect(url_for("todo_page"))

if __name__ == "__main__":
    app.run(debug=True)
