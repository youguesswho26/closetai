from flask import Flask, render_template, request, redirect, url_for
import json
import os

app = Flask(__name__)
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def generate_recommendations(clothes):
    recommendations = []
    tops = [item for item in clothes if item['type'] == 'top']
    bottoms = [item for item in clothes if item['type'] == 'bottom']
    shoes = [item for item in clothes if item['type'] == 'shoes']

    if tops and bottoms and shoes:
        # For simplicity, we'll just recommend the first of each type.
        # A more advanced version could create more combinations.
        recommendations.append({
            "top": tops[0],
            "bottom": bottoms[0],
            "shoes": shoes[0]
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
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        image.save(filepath)

        new_clothing_item = {
            "name": request.form['name'],
            "color": request.form['color'],
            "type": request.form['type'],
            "image_path": filepath
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
