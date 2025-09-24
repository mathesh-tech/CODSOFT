from flask import Flask, render_template, request, session, redirect, url_for
import re
import os
import json
import uuid
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


# ---------------------------------
# Contact List (HTML + JSON storage)
# ---------------------------------

CONTACTS_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "template",
    "contact list",
    "contacts.json",
)


def ensure_contacts_file():
    directory = os.path.dirname(CONTACTS_FILE)
    if not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)
    if not os.path.exists(CONTACTS_FILE):
        with open(CONTACTS_FILE, "w", encoding="utf-8") as f:
            json.dump([], f)


def load_contacts():
    ensure_contacts_file()
    try:
        with open(CONTACTS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except Exception:
        return []


def save_contacts(contacts):
    ensure_contacts_file()
    with open(CONTACTS_FILE, "w", encoding="utf-8") as f:
        json.dump(contacts, f, ensure_ascii=False, indent=2)


def validate_contact_payload(name, phone, email, address):
    errors = {}
    name = (name or "").strip()
    phone = (phone or "").strip()
    email = (email or "").strip()
    address = (address or "").strip()

    if not name:
        errors["name"] = "Name is required."
    phone_clean = re.sub(r"[^0-9+()\-\s]", "", phone)
    if not phone_clean:
        errors["phone"] = "Phone is required."
    if email and not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email):
        errors["email"] = "Invalid email format."
    return errors, {"name": name, "phone": phone, "email": email, "address": address}


@app.route("/contacts", methods=["GET"])
def contacts_list():
    q = (request.args.get("q") or "").strip().lower()
    contacts = load_contacts()
    if q:
        def norm_phone(p):
            return re.sub(r"\s", "", p or "")
        contacts = [c for c in contacts if q in (c.get("name", "").lower()) or q in norm_phone(c.get("phone", ""))]
    return render_template("contact list/list.html", contacts=contacts, q=q)


@app.route("/contacts/new", methods=["GET"])
def contacts_new():
    return render_template("contact list/form.html", mode="create", values={"name": "", "phone": "", "email": "", "address": ""}, errors={})


@app.route("/contacts", methods=["POST"])
def contacts_create():
    errors, values = validate_contact_payload(
        request.form.get("name"), request.form.get("phone"), request.form.get("email"), request.form.get("address")
    )
    if errors:
        return render_template("contact list/form.html", mode="create", values=values, errors=errors)
    contacts = load_contacts()
    values["id"] = uuid.uuid4().hex
    contacts.append(values)
    save_contacts(contacts)
    return redirect(url_for("contacts_list"))


def find_contact(contact_id):
    for c in load_contacts():
        if c.get("id") == contact_id:
            return c
    return None


@app.route("/contacts/<contact_id>", methods=["GET"])
def contacts_view(contact_id):
    contact = find_contact(contact_id)
    if not contact:
        return redirect(url_for("contacts_list"))
    return render_template("contact list/view.html", contact=contact)


@app.route("/contacts/<contact_id>/edit", methods=["GET"])
def contacts_edit(contact_id):
    contact = find_contact(contact_id)
    if not contact:
        return redirect(url_for("contacts_list"))
    return render_template("contact list/form.html", mode="edit", values=contact, errors={})


@app.route("/contacts/<contact_id>/update", methods=["POST"])
def contacts_update(contact_id):
    contacts = load_contacts()
    errors, values = validate_contact_payload(
        request.form.get("name"), request.form.get("phone"), request.form.get("email"), request.form.get("address")
    )
    if errors:
        values["id"] = contact_id
        return render_template("contact list/form.html", mode="edit", values=values, errors=errors)
    updated = False
    for c in contacts:
        if c.get("id") == contact_id:
            c.update(values)
            updated = True
            break
    if updated:
        save_contacts(contacts)
    return redirect(url_for("contacts_list"))


@app.route("/contacts/<contact_id>/delete", methods=["POST"])
def contacts_delete(contact_id):
    contacts = load_contacts()
    contacts = [c for c in contacts if c.get("id") != contact_id]
    save_contacts(contacts)
    return redirect(url_for("contacts_list"))

if __name__ == "__main__":
    app.run(debug=True)
