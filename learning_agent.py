# AI Learning Agent Web App (Flask-based)

from flask import Flask, render_template_string, request, session, redirect
import sqlite3
import uuid
from datetime import datetime
import openai
from web_search import search_web_snippets
import os
from generator import generate_learning_units


app = Flask(__name__)
app.secret_key = 'your-secret-key'

DATABASE = 'learning_agent.db'

# -------------------------- DB Initialization --------------------------
def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
        id TEXT PRIMARY KEY,
        topic TEXT,
        paraphrased_topic TEXT,
        knowledge_level TEXT,
        time_capacity TEXT,
        duration TEXT,
        medium TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS feedback (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT,
        unit_number INTEGER,
        rating INTEGER,
        comment TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    conn.commit()
    conn.close()

# -------------------------- Paraphrasing with OpenAI --------------------------
def paraphrase_topic(topic):
    try:
        openai.api_key = os.environ.get("OPENAI_API_KEY")  # Safer than hardcoding

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an academic assistant."},
                {"role": "user", "content": f"Paraphrase this topic in academic context: {topic}"}
            ]
        )
        return response['choices'][0]['message']['content'].strip()
    except Exception as e:
        print(f"Error in GPT call: {e}")
        return topic

# -------------------------- Helper for learning units --------------------------
def search_google_scholar(query):
    return [
        {'title': f'{query} – Intro Concepts', 'summary': f'Key concepts in {query}.', 'url': f'https://scholar.google.com/scholar?q={query.replace(" ", "+")}'},
        {'title': f'Advanced {query} Topics', 'summary': f'Latest research in {query}.', 'url': f'https://scholar.google.com/scholar?q={query.replace(" ", "+")}'},
    ]

def get_learning_units():
    topic = session.get('paraphrased_topic', 'Artificial Intelligence')
    level = session.get('knowledge_level', 'basic')
    time_per_day = session.get('time_capacity', '1-2 hours')
    duration = session.get('duration', 'one-week')
    medium = session.get('medium', 'text')

    # Rebuild only if medium has changed since last session
    prev_medium = session.get('last_medium_used')
    if 'learning_units' not in session or prev_medium != medium:
        print("❗ Re-generating units due to new medium or no cache")
        feedback = session.get("feedback_action", "great")
        units = generate_learning_units(topic, level, time_per_day, duration, medium=medium, feedback_action=feedback)
        session['learning_units'] = units
        session['last_medium_used'] = medium
        session['feedback_action'] = "great"
    return session['learning_units']

# -------------------------- Routes --------------------------
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        topic = request.form.get('topic', '').strip()
        session['topic'] = topic
        session['paraphrased_topic'] = paraphrase_topic(topic)
        return redirect('/confirm')
    return render_template_string(TEMPLATE, content='''
        <div class="message">
            <h2>Hello, let's bring you on a new level!</h2>
            <form method="POST">
                <input type="text" name="topic" placeholder="Enter your topic (e.g., AI ethics)" required>
                <br><br>
                <button class="btn btn-primary" type="submit">Continue</button>
            </form>
        </div>
    ''')

@app.route('/confirm', methods=['GET'])
def confirm():
    topic = session.get('paraphrased_topic', 'the topic')
    return render_template_string(TEMPLATE, content=f'''
        <div class="message">
            <h2>Ok, let's learn something about: <em>{topic}</em></h2>
            <p>Is this correct?</p>
            <div class="button-group">
                <a href="/knowledge" class="btn btn-primary">Yes, continue</a>
                <a href="/" class="btn btn-secondary">No, change topic</a>
            </div>
        </div>
    ''')

@app.route('/knowledge', methods=['GET', 'POST'])
def knowledge():
    if request.method == 'POST':
        session['knowledge_level'] = request.form['level']
        return redirect('/capacity')
    return render_template_string(TEMPLATE, content='''
        <div class="message">
            <h2>Which level do you want to climb in this learning programme?</h2>
            <form method="POST" style="text-align: center;">
                <button class="btn" name="level" value="basic">Basic Knowledge<br>Gain a foundational understanding of the key facts and core concepts</button><br>
                <button class="btn" name="level" value="broader">Broader Knowledge<br>Connect concepts and adapt learned principles to different scenarios</button><br>
                <button class="btn" name="level" value="profound">Profound Knowledge<br>Gain a profound understanding and the ability to critically evaluate</button>
            </form>
        </div>
    <br><a href="/confirm" class="btn btn-secondary">Go Back</a>
    ''')

@app.route('/capacity', methods=['GET', 'POST'])
def capacity():
    if request.method == 'POST':
        session['time_capacity'] = request.form['capacity']
        return redirect('/duration')
    return render_template_string(TEMPLATE, content='''
        <div class="message">
            <h2>How much time can you dedicate to learning each day?</h2>
            <form method="POST">
                <button class="btn" name="capacity" value="1-2 hours">1-2 hours</button><br><br>
                <button class="btn" name="capacity" value="part-time">Part-time (4h)</button><br><br>
                <button class="btn" name="capacity" value="full-time">Full-time (8h)</button>
            </form>
        </div>
        <br><a href="/knowledge" class="btn btn-secondary">Go Back</a>
    ''')

@app.route('/duration', methods=['GET', 'POST'])
def duration():
    if request.method == 'POST':
        session['duration'] = request.form['duration']
        return redirect('/medium')
    level = session.get('knowledge_level')
    cap = session.get('time_capacity')
    opts = []
    if level == 'profound':
        opts = ['long-term', 'medium-term'] if cap in ['full-time', 'part-time'] else ['long-term']
    elif level == 'broader':
        opts = ['long-term', 'medium-term', 'short-term'] if cap in ['full-time', 'part-time'] else ['long-term', 'medium-term']
    else:
        opts = ['one-week', 'one-month', 'three-months']
    buttons = ''.join([f'<button class="btn" name="duration" value="{o}">{o.replace("-", " ").title()}</button><br><br>' for o in opts])
    return render_template_string(TEMPLATE, content=f'''
        <div class="message">
            <h2>How long should this learning project last?</h2>
            <form method="POST">{buttons}</form>
        </div>
        <br><a href="/capacity" class="btn btn-secondary">Go Back</a>
    ''')

@app.route('/medium', methods=['GET', 'POST'])
def medium():
    if request.method == 'POST':
        session['medium'] = request.form['medium']
        return redirect('/confirm-plan')
    return render_template_string(TEMPLATE, content='''
        <div class="message">
            <h2>Which medium do you prefer to learn with?</h2>
            <form method="POST">
                <button class="btn" name="medium" value="text">Text</button><br><br>
                <button class="btn" name="medium" value="videos">Videos</button>
            </form>
        </div>
        <br><a href="/duration" class="btn btn-secondary">Go Back</a>
    ''')

@app.route('/confirm-plan')
def confirm_plan():
    topic = session.get('paraphrased_topic')
    level = session.get('knowledge_level')
    time = session.get('time_capacity')
    duration = session.get('duration')
    medium = session.get('medium')
    return render_template_string(TEMPLATE, content=f'''
        <div class="message">
            <h2>Let's start learning!</h2>
            <p><strong>Topic:</strong> {topic}</p>
            <p><strong>Level:</strong> {level}</p>
            <p><strong>Time:</strong> {time}</p>
            <p><strong>Duration:</strong> {duration}</p>
            <p><strong>Medium:</strong> {medium}</p>
            <a class="btn btn-primary" href="/learning/1">Start Learning</a>
        </div>
        <br><a href="/medium" class="btn btn-secondary">Go Back</a>
    ''')

@app.route('/feedback', methods=['POST'])
def feedback():
    user_id = session.get('user_id', str(uuid.uuid4()))
    unit_number = int(request.form['unit_number'])
    rating = int(request.form['rating'])
    comment = request.form.get('comment', '')
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO feedback (user_id, unit_number, rating, comment) VALUES (?, ?, ?, ?)''',
                   (user_id, unit_number, rating, comment))
    conn.commit()
    conn.close()
    return redirect(f'/learning/{unit_number}')

@app.route('/feedback-action', methods=['POST'])
def feedback_action():
    session['feedback_action'] = request.form.get('feedback_action', 'great')
    unit_number = int(request.form.get('unit_number', 1))
    
    if session['feedback_action'] == 'refine':
        return redirect('/')
    return redirect(f'/learning/{unit_number + 1}')

@app.route('/learning/<int:unit_number>')
def learning(unit_number):
    session.setdefault('user_id', str(uuid.uuid4()))
    units = get_learning_units()

    if unit_number < 1 or unit_number > len(units):
        return redirect('/learning/1')

    unit = units[unit_number - 1]

    # ✅ DEBUG: Confirm medium and content
    print(f"Rendering medium: {session.get('medium')}")
    print(f"Unit content preview: {unit['content'][:100]}")

    # Navigation buttons
    buttons = '<div class="button-row" style="display: flex; justify-content: center; gap: 10px;">'
    if unit_number > 1:
        buttons += f'<a class="btn" href="/learning/{unit_number - 1}">Previous Learning Unit</a>'
    if unit_number < len(units):
        buttons += f'<a class="btn" href="/learning/{unit_number + 1}">Next Learning Unit</a>'
    buttons += '</div>'



# -------- CONTENT BLOCK --------
    medium = session.get("medium", "text")
    is_video = medium in ["video", "videos"]

    # fallback if no sections available
    if 'sections' not in unit or not unit['sections']:
        unit['sections'] = [unit.get("content", "No content available.")]

    # Unified rendering with segment navigation + feedback at the end of text unit
    content = f"""
    <div class="message">
        <h2>Unit {unit['unit_number']}: {unit['title']}</h2>
        {'<h3> </h3>' if is_video else ''}

        <section id="section-display">
            <div id="section-text"></div>
        </section>


        {'<div class="button-group">'f'<button class="btn" style="font-size: 0.8em; padding: 5px 10px; margin-right: 10px;" onclick="prevSection()"> ⇠ </button>'f'<button class="btn" style="font-size: 0.8em; padding: 5px 10px;" onclick="nextSection()"> ⇢ </button>''</div>' if not is_video else ''}


        <form id="feedback-form" method="POST" action="/feedback-action" style="display: none; margin-top: 5px;">
            <input type="hidden" name="unit_number" value="{unit['unit_number']}">
            <h3>How have you experienced this learning unit?</h3>
            <button class="btn" name="feedback_action" value="great" style="margin-right: 5px;"> Great, go ahead</button><br><br>
            <button class="btn" name="feedback_action" value="harder" style="margin-right: 5px;"> Make it more complex</button><br><br>
            <button class="btn" name="feedback_action" value="easier"style="margin-right: 5px;"> Make it easier to understand</button><br><br>
            <button class="btn btn-secondary" name="feedback_action" value="refine"style="margin-right: 5px;"> Let’s refine the topic: go back to start</button>
        </form>

        <script>
                const sections = {unit['sections']};
                let index = 0;

                function updateSection() {{
                    document.getElementById("section-text").innerHTML = sections[index];

                    // Show feedback only at last section if medium is "text"
                    if ("{medium}" === "text" && index === sections.length - 1) {{
                        document.getElementById("feedback-form").style.display = "block";
                    }} else {{
                        document.getElementById("feedback-form").style.display = "none";
                    }}
                }}

                function nextSection() {{
                    if (index < sections.length - 1) {{
                        index++;
                        updateSection();
                    }}
                }}

                function prevSection() {{
                    if (index > 0) {{
                        index--;
                        updateSection();
                    }}
                }}

                updateSection(); // Initial call
            </script>
        </div>
        """
# -------- END CONTENT BLOCK --------
#a

    # Feedback form and navigation
    content += f'''
    <form method="POST" action="/feedback">
        <input type="hidden" name="unit_number" value="{unit['unit_number']}">

        <style>
            .tooltip {{
                visibility: hidden;
                background-color: black;
                color: #fff;
                text-align: center;
                border-radius: 5px;
                padding: 2px 8px;
                position: absolute;
                top: -30px;
                left: 50%;
                transform: translateX(-50%);
                white-space: nowrap;
                font-size: 12px;
                z-index: 1;
            }}
            .button-row {{
                text-align: center;
                margin-top: 20px;
                margin-right: 20px;
            }}
        </style>

    </form>

    <div class="button-group">{buttons}</div>

    <script>
        const circles = document.querySelectorAll('.circle');
        const ratingLabel = document.getElementById('rating-label');
        const ratingInput = document.getElementById('rating');

        circles.forEach((circle, index) => {{
            circle.addEventListener('click', () => {{
                const value = parseInt(circle.getAttribute('data-value'));
                const label = circle.getAttribute('data-label');
                ratingInput.value = value;
                ratingLabel.innerText = label;
                circles.forEach((c, i) => {{
                    c.classList.toggle('selected', i < value);
                }});
            }});
        }});
    </script>
    '''
    if session.get("medium") in ["video", "videos"]:
        print("⚠️ DEBUG VIDEO HTML BLOCK:")
        print(unit["content"])  # Print actual HTML string that will be rendered
    # Safe render
    return render_template_string(TEMPLATE, content=content)


# -------------------------- Template --------------------------
TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>AI Learning Agent</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body { font-family: Consolas; background: #F0F0F0; padding: 2rem; }
        .message { background: white; padding: 1.5rem; border-radius: 8px; max-width: 800px; margin: auto; box-shadow: 0 4px 10px rgba(0,0,0,0.1); }
        .btn { background: #FFD300; color: #000000; font-family: Consolas; border: none; padding: 10px 20px; margin-top: 10px; cursor: pointer; border-radius: 5px; font-weight: bold; text-decoration: none; display: inline-block; }
        .btn-primary { background-color: #FFD300; }
        .btn-secondary { background-color: #FFD300; }
        input[type=text], input[type=number] { padding: 10px; width: 100%; margin-top: 10px; }
        .button-group { margin-top: 20px; }
        .video-list ul {
            padding-left: 1.2rem;
        }
        .video-list li {
            margin-bottom: 0.6rem;
        }
        .video-list a {
            color: #FFD300;
            text-decoration: underline;
        }
        .section {
            margin-bottom: 1.5rem;
            line-height: 1.6;
        }
        .section h3, .section h2 {
            color: #333;
        }
        .text-sections {
            margin-top: 1rem;
        }
        .video-entry {
            margin-bottom: 1.5rem;
        }
        .thumbnail {
            display: none;
        }
        .video-entry {
            text-decoration: none;
            color: #000;
            font-weight: bold;
            margin-bottom: 1.5rem;
        }
    </style>
</head>
<body>
    {{ content|safe }}
</body>
</html>
'''

if __name__ == '__main__':
    init_db()
    app.run(debug=True)      