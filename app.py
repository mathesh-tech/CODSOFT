from flask import Flask, render_template, request, session
import re

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Change this to a random secret key

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

@app.route("/", methods=["GET", "POST"])
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

if __name__ == "__main__":
    app.run(debug=True)
