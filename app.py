from flask import Flask, render_template, request, redirect, url_for
import json
import os
import random

app = Flask(__name__, template_folder='templates', static_folder='static')
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def generate_recommendations(clothes):
    recommendations = []
    tops = [item for item in clothes if item['type'] == 'top']
    bottoms = [item for item in clothes if item['type'] == 'bottom']
    shoes = [item for item in clothes if item['type'] == 'shoes']

    if tops and bottoms and shoes:
        # Generate a random outfit
        recommendations.append({
            "top": random.choice(tops),
            "bottom": random.choice(bottoms),
            "shoes": random.choice(shoes)
        })
    return recommendations

@app.route('/')
def index():
    db_path = app.config.get('DB_PATH', 'db.json')
    if not os.path.exists(db_path):
        with open(db_path, 'w') as f:
            json.dump({"clothes": []}, f)

    with open(db_path, 'r') as f:
        data = json.load(f)
    clothes = data['clothes']
    recommendations = generate_recommendations(clothes)
    return render_template('index.html', clothes=clothes, recommendations=recommendations)

@app.route('/upload', methods=['POST'])
def upload():
    if 'image' not in request.files:
        return redirect(url_for('index'))

    image = request.files['image']
    if image.filename == '':
        return redirect(url_for('index'))

    if image:
        filename = image.filename
        upload_folder = app.config['UPLOAD_FOLDER']
        os.makedirs(upload_folder, exist_ok=True)
        filepath = os.path.join(upload_folder, filename)
        image.save(filepath)

        # Store a path relative to the static folder for use in url_for
        db_image_path = os.path.join('uploads', filename)

        new_clothing_item = {
            "name": request.form['name'],
            "color": request.form['color'],
            "type": request.form['type'],
            "image_path": db_image_path
        }

        db_path = app.config.get('DB_PATH', 'db.json')
        with open(db_path, 'r+') as f:
            data = json.load(f)
            data['clothes'].append(new_clothing_item)
            f.seek(0)
            json.dump(data, f, indent=4)

    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
