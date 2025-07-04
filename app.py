# backend/app.py
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
from bson import ObjectId
from datetime import datetime
from flask_cors import CORS
import requests

app = Flask(__name__)
app.secret_key = 'supersecretkey'
CORS(app)

# MongoDB setup
client = MongoClient('mongodb://localhost:27017/')
db = client.infinityDB
users = db.users
projects = db.projects
comments = db.comments
notifications = db.notifications
likes = db.likes
microcollabs = db.microcollabs

# ================= USER AUTH =================
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/signup', methods=['POST'])
def signup():
    email = request.form['email']
    password = request.form['password']
    confirm = request.form['confirm']

    if password != confirm:
        return jsonify({'status': 'error', 'message': 'Passwords do not match'})

    if users.find_one({'email': email}):
        return jsonify({'status': 'error', 'message': 'User already exists'})

    users.insert_one({
        'email': email,
        'password': generate_password_hash(password)
    })
    return jsonify({'status': 'success', 'message': 'Signup successful'})

@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    password = request.form['password']
    user = users.find_one({'email': email})
    if user and check_password_hash(user['password'], password):
        session['user_email'] = email
        return jsonify({'status': 'success', 'redirect': '/home'})
    return jsonify({'status': 'error', 'message': 'Invalid credentials'})

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

# ================= PROJECT ROUTES =================
@app.route('/home')
def home():
    if 'user_email' not in session:
        return redirect('/')
    return render_template('home.html')

@app.route('/project')
def project():
    if 'user_email' not in session:
        return redirect('/')
    return render_template('project.html')

@app.route('/add_project', methods=['POST'])
def add_project():
    if 'user_email' not in session:
        return jsonify({'status': 'error', 'message': 'Login required'})

    data = request.get_json()
    project = {
        'user_id': session['user_email'],
        'title': data['title'],
        'description': data['description'],
        'stage': data['stage'],
        'tags': data['tags'],
        'link': data['link'],
        'created_at': datetime.utcnow()
    }
    result = projects.insert_one(project)
    return jsonify({'status': 'success', 'id': str(result.inserted_id)})

@app.route('/get_projects')
def get_user_projects():
    if 'user_email' not in session:
        return jsonify([])
    user_projects = list(projects.find({'user_id': session['user_email']}))
    for proj in user_projects:
        proj['_id'] = str(proj['_id'])
    return jsonify(user_projects)

@app.route('/get_all_projects')
def get_all_projects():
    all_projects = list(projects.find().sort('created_at', -1))
    for proj in all_projects:
        proj['_id'] = str(proj['_id'])
    return jsonify(all_projects)

@app.route('/get_project/<project_id>')
def get_project(project_id):
    project = projects.find_one({'_id': ObjectId(project_id)})
    if project:
        project['_id'] = str(project['_id'])
        return jsonify(project)
    return jsonify({'error': 'Project not found'})

@app.route('/edit_project/<project_id>', methods=['POST'])
def edit_project(project_id):
    data = request.get_json()
    projects.update_one({'_id': ObjectId(project_id)}, {'$set': data})
    return jsonify({'status': 'success'})

@app.route('/toggle_like', methods=['POST'])
def toggle_like():
    if 'user_email' not in session:
        return jsonify({'status': 'error', 'message': 'Login required'})

    data = request.get_json()
    project_id = data['project_id']
    user_email = session['user_email']

    existing = likes.find_one({'project_id': project_id, 'user_id': user_email})

    if existing:
        likes.delete_one({'_id': existing['_id']})
    else:
        likes.insert_one({'project_id': project_id, 'user_id': user_email})

        project = projects.find_one({'_id': ObjectId(project_id)})
        if project and project['user_id'] != user_email:
            notifications.insert_one({
                'type': 'like',
                'from': user_email,
                'to': project['user_id'],
                'project_id': project_id,
                'message': f"{user_email} liked your project.",
                'timestamp': datetime.utcnow()
            })

    like_count = likes.count_documents({'project_id': project_id})
    return jsonify({'status': 'success', 'count': like_count})

@app.route('/get_likes/<project_id>')
def get_likes(project_id):
    count = likes.count_documents({'project_id': project_id})
    return jsonify({'count': count})

@app.route('/add_comment', methods=['POST'])
def add_comment():
    if 'user_email' not in session:
        return jsonify({'status': 'error', 'message': 'Login required'})

    data = request.get_json()
    comment = {
        'project_id': data['project_id'],
        'user_id': session['user_email'],
        'text': data['text'],
        'timestamp': datetime.utcnow(),
        'replies': []
    }
    comments.insert_one(comment)

    project = projects.find_one({'_id': ObjectId(data['project_id'])})
    if project and project['user_id'] != session['user_email']:
        notifications.insert_one({
            'type': 'comment',
            'from': session['user_email'],
            'to': project['user_id'],
            'project_id': data['project_id'],
            'message': f"{session['user_email']} commented on your project.",
            'timestamp': datetime.utcnow()
        })

    return jsonify({'status': 'success'})

@app.route('/get_comments/<project_id>')
def get_comments(project_id):
    all_comments = list(comments.find({'project_id': project_id}).sort('timestamp', 1))
    for c in all_comments:
        c['_id'] = str(c['_id'])
    return jsonify(all_comments)

@app.route('/get_notifications')
def get_notifications():
    if 'user_email' not in session:
        return jsonify([])

    notif = list(notifications.find({'to': session['user_email']}).sort('timestamp', -1))
    for n in notif:
        n['_id'] = str(n['_id'])
    return jsonify(notif)

@app.route('/dismiss_notification/<notif_id>', methods=['DELETE'])
def dismiss_notification(notif_id):
    notifications.delete_one({'_id': ObjectId(notif_id)})
    return jsonify({'status': 'success'})

@app.route('/search_projects')
def search_projects():
    query = request.args.get('q', '').lower()
    results = list(projects.find({
        '$or': [
            {'title': {'$regex': query, '$options': 'i'}},
            {'description': {'$regex': query, '$options': 'i'}},
            {'tags': {'$regex': query, '$options': 'i'}},
            {'user_id': {'$regex': query, '$options': 'i'}}
        ]
    }).sort('created_at', -1))

    for p in results:
        p['_id'] = str(p['_id'])
    return jsonify(results)

@app.route('/review')
def review():
    if 'user_email' not in session:
        return redirect('/')
    return render_template('review.html')

@app.route('/get_reviews')
def get_reviews():
    if 'user_email' not in session:
        return jsonify([])

    user_email = session['user_email']
    user_projects = list(projects.find({'user_id': user_email}))
    review_data = []

    for proj in user_projects:
        proj_id = str(proj['_id'])
        proj_comments = list(comments.find({'project_id': proj_id}))
        for c in proj_comments:
            c['_id'] = str(c['_id'])
            c['timestamp'] = c['timestamp'].isoformat()

        review_data.append({
            'project_id': proj_id,
            'project_title': proj['title'],
            'project_desc': proj['description'],
            'tags': proj.get('tags', ''),
            'comments': proj_comments
        })

    return jsonify(review_data)

@app.route('/summarize_feedback', methods=['POST'])
def summarize_feedback():
    data = request.get_json()
    project_desc = data.get('project_desc', '')
    comments = data.get('comments', [])

    prompt = f"Project Description:\n{project_desc}\n\n"
    prompt += "Reviewer Comments:\n"
    for comment in comments:
        prompt += f"- {comment}\n"
    prompt += "\nGive a short 3-4 sentence summary of the feedback. Highlight positives and suggestions for improvement."

    headers = {
        'Content-Type': 'application/json',
        'X-goog-api-key': 'your Gemini API key'
    }

    body = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ]
    }

    try:
        response = requests.post(
            "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent",
            headers=headers,
            json=body
        )

        if response.status_code == 200:
            response_data = response.json()
            summary = response_data['candidates'][0]['content']['parts'][0]['text']
            return jsonify({'summary': summary})
        else:
            return jsonify({'error': response.text}), response.status_code

    except Exception as e:
        return jsonify({'error': str(e)}), 500



@app.route('/microcollab')
def microcollab():
    if 'user_email' not in session:
        return redirect('/')
    return render_template('microCollab.html')


# ================= MICROCOSMOS COLLABORATION =================

@app.route('/create_microcollab', methods=['POST'])
def create_microcollab():
    if 'user_email' not in session:
        return jsonify({'status': 'error', 'message': 'Login required'}), 401

    data = request.get_json()
    microcollabs.insert_one({
        'owner': session['user_email'],
        'projectName': data['projectName'],
        'taskTitle': data['taskTitle'],
        'description': data['description'],
        'workDescription': data['workDescription'],
        'tags': data['tags'],
        'deadline': data['deadline'],
        'accepted_by': None,
        'completed': False,
        'messages': []
    })
    return jsonify({'status': 'success'})

@app.route('/get_discover_collabs')
def get_discover_collabs():
    if 'user_email' not in session:
        return jsonify([])

    discover = list(microcollabs.find({
        'owner': {'$ne': session['user_email']},
        'accepted_by': None
    }))
    for c in discover:
        c['_id'] = str(c['_id'])
    return jsonify(discover)

@app.route('/get_my_collabs')
def get_my_collabs():
    if 'user_email' not in session:
        return jsonify([])

    mine = list(microcollabs.find({'owner': session['user_email']}))
    for c in mine:
        c['_id'] = str(c['_id'])
    return jsonify(mine)

@app.route('/get_accepted_collabs')
def get_accepted_collabs():
    if 'user_email' not in session:
        return jsonify([])

    accepted = list(microcollabs.find({'accepted_by': session['user_email']}))
    for c in accepted:
        c['_id'] = str(c['_id'])
    return jsonify(accepted)

@app.route('/accept_microcollab', methods=['POST'])
def accept_microcollab():
    if 'user_email' not in session:
        return jsonify({'status': 'error'})

    data = request.get_json()
    microcollabs.update_one(
        {'_id': ObjectId(data['collab_id'])},
        {'$set': {'accepted_by': session['user_email']}}
    )
    return jsonify({'status': 'success'})

@app.route('/decline_microcollab', methods=['POST'])
def decline_microcollab():
    if 'user_email' not in session:
        return jsonify({'status': 'error'})

    data = request.get_json()
    microcollabs.update_one(
        {'_id': ObjectId(data['collab_id'])},
        {'$set': {'accepted_by': None}}
    )
    return jsonify({'status': 'success'})

@app.route('/complete_microcollab', methods=['POST'])
def complete_microcollab():
    if 'user_email' not in session:
        return jsonify({'status': 'error'})

    data = request.get_json()
    microcollabs.update_one(
        {'_id': ObjectId(data['collab_id'])},
        {'$set': {'completed': True}}
    )
    return jsonify({'status': 'success'})

@app.route('/send_message', methods=['POST'])
def send_message():
    if 'user_email' not in session:
        return jsonify({'status': 'error'})

    data = request.get_json()
    message = {
        'sender': session['user_email'],
        'message': data['message'],
        'timestamp': datetime.utcnow().isoformat()
    }

    microcollabs.update_one(
        {'_id': ObjectId(data['collab_id'])},
        {'$push': {'messages': message}}
    )

    return jsonify({'status': 'success'})

@app.route('/get_messages/<collab_id>')
def get_messages(collab_id):
    collab = microcollabs.find_one({'_id': ObjectId(collab_id)})
    if not collab:
        return jsonify([])

    return jsonify(collab.get('messages', []))


if __name__ == '__main__':
    app.run(debug=True)
