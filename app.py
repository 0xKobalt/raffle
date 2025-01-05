from flask import Flask, render_template_string, request, redirect, url_for, session
import random

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Store previous numbers, custom text, and history
generated_numbers = set()
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
        body {
            background-color: darkred;
            color: #FFCC66;
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
        }
        h1 {
            color: #FFCC66;
        }
        table {
            border-collapse: collapse;
            width: 100%;
            max-width: 1200px;
            margin: auto;
        }
        td {
            border: 1px solid #FFCC66;
            text-align: center;
            width: 25px;
            height: 25px;
            background-color: darkred;
            color: #FFCC66;
        }
        td.highlight {
            background-color: #FFCC66;
            color: darkred;
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
            color: #FF6666;
            text-align: center;
        }
        .history {
            text-align: center;
            margin-top: 20px;
        }
        .history p {
            font-size: 1em;
        }
        button {
            background-color: #FFCC66;
            color: darkred;
            border: none;
            padding: 10px 20px;
            cursor: pointer;
            font-size: 1em;
        }
        button:hover {
            background-color: #FFA500;
        }
        input {
            border: 1px solid #FFCC66;
            padding: 5px;
            background-color: darkred;
            color: #FFCC66;
        }
        input::placeholder {
            color: #FFCC66;
        }
        input[type="number"] {
            width: 60px;
        }
    </style>
</head>
<body>
    <h1 style="text-align: center;">CSA-EUR Give Fortune Get Fortune Raffle</h1>

    <form method="post">
        <label for="custom_text">Prize:</label>
        <input type="text" id="custom_text" name="custom_text" placeholder="Enter prize" >
        <br><br>
        <label for="count">Enter the number of unique random numbers:</label>
        <input type="number" id="count" name="count" min="1" max="{{ max_count }}" >
        <br><br>
        <button type="submit">Generate Numbers</button>
        <br>
        <br>
        <button type="submit" formaction="/generate-single">Generate Single Number</button>
    </form>

    <div class="last-drawn">
        {% if error_message %}
            <p class="error">{{ error_message }}</p>
        {% elif single_number %}
            <p>{{ single_custom_text }}: {{ single_number }}</p>
            <form method="post" action="/confirm">
                <button type="submit">Confirm Number</button>
            </form>
        {% elif numbers %}
            <p>{{ custom_text }}: {{ numbers | join(', ') }}</p>
        {% endif %}
    </div>

    <div class="history">
        <h3>History of Drawn Numbers:</h3>
        {% for entry in history[::-1] %}
        <p>{{ entry.custom_text }}: {{ entry.numbers | join(', ') }}</p>
        {% endfor %}
    </div>

    <form method="post" action="/reset">
        <button type="submit">Reset Drawn Numbers</button>
    </form>

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
</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def generate_number():
    global generated_numbers, history

    print(session)

    numbers = None
    single_number = session.get('single_number', None)
    single_custom_text = session.get('single_custom_text', "")
    error_message = session.pop('error_message', None)
    custom_text = session.get('custom_text', "")

    if request.method == 'POST' and 'count' in request.form:
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
                    session['numbers'] = numbers
                    session['error_message'] = None
        except ValueError:
            session['error_message'] = "Invalid input. Please enter a valid number."

        if 'custom_text' in request.form:
            custom_text = request.form.get('custom_text')
            session['custom_text'] = custom_text
            if numbers:
                history.append({'custom_text': custom_text, 'numbers': numbers})
                session['history'] = history

        return redirect(url_for('generate_number'))

    return render_template_string(
        HTML_TEMPLATE,
        numbers=session.get('numbers'),
        previous_numbers=generated_numbers,
        custom_text=custom_text,
        single_custom_text=single_custom_text,
        single_number=single_number,
        history=history,
        max_count=MAX_COUNT,
        error_message=error_message
    )

@app.route('/generate-single', methods=['POST'])
def generate_single_number():
    global generated_numbers
    session.pop('numbers', None)
    available_numbers = set(range(1, MAX_COUNT + 1)) - generated_numbers
    single_custom_text = request.form.get('custom_text')
    if single_custom_text != None:
        single_custom_text = session.get('single_custom_text', "Single Number")
    print(session)
    if available_numbers:
        single_number = random.choice(list(available_numbers))
        session['single_number'] = single_number
        session['single_custom_text'] = single_custom_text
    else:
        session['error_message'] = "No numbers available to generate."
    return redirect(url_for('generate_number'))

@app.route('/confirm', methods=['POST'])
def confirm_single_number():
    global generated_numbers, history
    single_number = session.pop('single_number', None)
    single_custom_text = session.pop('single_custom_text', "Single Number")
    if single_number:
        generated_numbers.add(single_number)
        history.append({'custom_text': single_custom_text, 'numbers': [single_number]})
        session['history'] = history
    return redirect(url_for('generate_number'))

@app.route('/reset', methods=['POST'])
def reset_numbers():
    global generated_numbers, history
    generated_numbers = set()
    history = []
    session.clear()
    return redirect(url_for('generate_number'))

if __name__ == '__main__':
    app.run(debug=True)
