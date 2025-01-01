from flask import Flask, render_template_string, request, redirect, url_for, session
import random

app = Flask(__name__)

app.secret_key = 'your_secret_key'  # Necessary for using sessions

# Store previous numbers, custom text, and history
generated_numbers = set()  # Store all drawn numbers from previous sessions
custom_text = ""
history = []

# Max count for number generation
MAX_COUNT = 3000

# HTML Template
HTML_TEMPLATE = """
<!doctype html>
<html>
<head>
    <title>CSA-EUR Give Fortune Get Fortune Raffle</title>
    <style>
        table {
            border-collapse: collapse;
            width: 100%;
            max-width: 1200px;
            margin: auto;
        }
        td {
            border: 1px solid black;
            text-align: center;
            width: 25px;
            height: 25px;
            background-color: white;
        }
        td.highlight {
            background-color: teal;
            color: white;
        }
        form {
            text-align: center;
            margin-top: 20px;
            margin-bottom: 20px;
        }
        .last-drawn {
            text-align: center;
            margin-top: 20px;
            font-size: 1.2em;
        }
        .error {
            color: red;
            text-align: center;
        }
        .history {
            text-align: center;
            margin-top: 20px;
        }
        .history p {
            font-size: 1em;
        }
    </style>
</head>
<body>
    <h1 style="text-align: center;">CSA-EUR Give Fortune Get Fortune Raffle</h1>

    <form method="post">
        <label for="custom_text">Prize:</label>
        <input type="text" id="custom_text" name="custom_text" placeholder="Enter prize" required>
        <br><br>
        <label for="count">Enter the number of unique random numbers:</label>
        <input type="number" id="count" name="count" min="1" max="{{ max_count }}" required>
        <br><br>
        <button type="submit">Generate Numbers</button>
    </form>

    <form method="post" action="/reset">
        <button type="submit">Reset Drawn Numbers</button>
    </form>

    <div class="last-drawn">
        {% if error_message %}
            <p class="error">{{ error_message }}</p>
        {% elif numbers %}
            <p>{{ custom_text }}: {{ numbers | join(', ') }}</p>
        {% endif %}
    </div>

    <table>
        {% for i in range(1, 3001, 40) %}
        <tr>
            {% for j in range(40) %}
            <td class="{% if (i + j) in previous_numbers %}highlight{% endif %}">
                {{ i + j }}
            </td>
            {% endfor %}
        </tr>
        {% endfor %}
    </table>

    <div class="history">
        <h3>History of Drawn Numbers:</h3>
        {% for entry in history %}
        <p>{{ entry.custom_text }}: {{ entry.numbers | join(', ') }}</p>
        {% endfor %}
    </div>

</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def generate_number():
    global generated_numbers, custom_text, history

    numbers = None  # Initialize to None

    if request.method == 'POST':
        if 'count' in request.form:
            try:
                count = int(request.form.get('count', 1))
                if count > MAX_COUNT:
                    session['error_message'] = "Not enough unique numbers available."
                else:
                    available_numbers = set(range(1, MAX_COUNT + 1)) - generated_numbers
                    if len(available_numbers) < count:
                        session['error_message'] = "Not enough unique numbers available."
                    else:
                        numbers = sorted(random.sample(list(available_numbers), count))
                        generated_numbers.update(numbers)
                        session['numbers'] = numbers  # Store numbers in session
                        session['error_message'] = None
            except ValueError:
                session['error_message'] = "Invalid input. Please enter a valid number."

        if 'custom_text' in request.form:
            custom_text = request.form.get('custom_text')
            session['custom_text'] = custom_text  # Store custom text in session
            if numbers:
                history.append({'custom_text': custom_text, 'numbers': numbers})
                session['history'] = history

        return redirect(url_for('generate_number'))

    # For GET requests, retrieve numbers and error message from session
    numbers = session.get('numbers')
    error_message = session.pop('error_message', None)  # Pop to clear after display
    custom_text = session.get('custom_text', "")

    return render_template_string(
        HTML_TEMPLATE,
        numbers=numbers,
        previous_numbers=generated_numbers,
        custom_text=custom_text,
        history=history,
        max_count=MAX_COUNT,
        error_message=error_message
    )

@app.route('/reset', methods=['POST'])
def reset_numbers():
    global generated_numbers, custom_text, history
    generated_numbers = set()  # Reset the generated numbers set
    custom_text = ""  # Reset custom text
    history = []  # Clear history
    session.clear()  # Clear session data
    return redirect(url_for('generate_number'))  # Redirect back to the main page with the reset state

if __name__ == '__main__':
    app.run(debug=True)
