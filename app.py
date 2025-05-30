from flask import Flask, request, render_template, jsonify
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import shap
import hashlib
import json

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///rtms.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    role = db.Column(db.String(20), nullable=False)

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    worker_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    client_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    rating = db.Column(db.Float, nullable=False)
    comment = db.Column(db.Text)
    bias_flag = db.Column(db.Boolean, default=False)
    seller_gender = db.Column(db.String(20))
    seller_nationality = db.Column(db.String(50))

class ReputationLedger(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    worker_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    reputation_score = db.Column(db.Float, nullable=False)
    hash = db.Column(db.String(64), nullable=False)
    prev_hash = db.Column(db.String(64))

# Bias Detector
class BiasDetector:
    def __init__(self):
        self.model = RandomForestClassifier(random_state=42)
        self.is_trained = False
        self.feature_order = ['Average Rating', 'seller_gender', 'seller_nationality']
        self.gender_mapping = {'female': 0, 'male': 1, 'unknown': 2}
        self.nationality_mapping = {'India': 0, 'Nigeria': 1, 'Pakistan': 2, 'UK': 3, 'USA': 4}

    def train(self, data_path):
        try:
            df = pd.read_csv(data_path)
            if not all(col in df.columns for col in self.feature_order + ['bias_flag']):
                missing = [col for col in self.feature_order + ['bias_flag'] if col not in df.columns]
                raise ValueError(f"Missing columns: {missing}")
            X = df[self.feature_order]
            y = df['bias_flag']
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            self.model.fit(X_train, y_train)
            self.is_trained = True
            print("Bias detector trained successfully")
            return self.model
        except Exception as e:
            print(f"Training error: {str(e)}")
            raise

    def predict(self, review_data):
        if not self.is_trained:
            raise ValueError("Model not trained")
        if not all(key in review_data for key in self.feature_order):
            raise ValueError(f"Missing required keys: {self.feature_order}")
        if not isinstance(review_data['Average Rating'], (int, float)) or review_data['Average Rating'] < 1 or review_data['Average Rating'] > 5:
            raise ValueError("Average Rating must be a number between 1 and 5")
        try:
            review_data = review_data.copy()
            seller_gender = review_data['seller_gender']
            seller_nationality = review_data['seller_nationality']
            if seller_gender not in self.gender_mapping:
                raise ValueError(f"Invalid seller_gender: {seller_gender}. Expected one of {list(self.gender_mapping.keys())}")
            if seller_nationality not in self.nationality_mapping:
                raise ValueError(f"Invalid seller_nationality: {seller_nationality}. Expected one of {list(self.nationality_mapping.keys())}")
            review_data['seller_gender'] = self.gender_mapping[seller_gender]
            review_data['seller_nationality'] = self.nationality_mapping[seller_nationality]
        except KeyError as e:
            raise ValueError(f"Missing categorical field: {str(e)}")
        X = pd.DataFrame([review_data], columns=self.feature_order)
        return self.model.predict(X)[0]

# Explainable AI
class ReputationExplainer:
    def __init__(self, model):
        self.model = model
        self.explainer = shap.TreeExplainer(model)

    def explain(self, data):
        X = pd.DataFrame([data], columns=['Average Rating', 'seller_gender', 'seller_nationality'])
        shap_values = self.explainer.shap_values(X)
        return shap_values

# Blockchain-inspired Ledger
class ReputationBlockchain:
    def __init__(self):
        self.chain = []

    def add_block(self, worker_id, reputation_score, prev_hash=''):
        block = {
            'worker_id': worker_id,
            'reputation_score': reputation_score,
            'prev_hash': prev_hash,
            'hash': self.calculate_hash(worker_id, reputation_score, prev_hash)
        }
        self.chain.append(block)
        return block

    def calculate_hash(self, worker_id, reputation_score, prev_hash):
        block_string = json.dumps({'worker_id': worker_id, 'reputation_score': reputation_score, 'prev_hash': prev_hash}, sort_keys=True)
        return hashlib.sha256(block_string.encode()).hexdigest()

# Initialize Components
bias_detector = BiasDetector()
reputation_blockchain = ReputationBlockchain()

# Train Bias Detector on Startup
with app.app_context():
    try:
        bias_detector.train('data/processed_fiverr_data.csv')
    except Exception as e:
        print(f"Failed to train bias detector: {str(e)}")

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit_review', methods=['POST'])
def submit_review():
    data = request.form
    print(f"Received form data: {dict(data)}")
    try:
        worker_id = int(data['worker_id'])
        client_id = int(data['client_id'])
        rating = float(data['rating'])
        if not (1 <= rating <= 5):
            return jsonify({'status': 'error', 'message': 'Rating must be between 1 and 5'}), 400
        comment = data.get('comment', '')
        seller_gender = data.get('seller_gender', 'unknown')
        seller_nationality = data.get('seller_nationality', 'unknown')

        # Bias Detection
        review_data = {
            'Average Rating': rating,
            'seller_gender': seller_gender,
            'seller_nationality': seller_nationality
        }
        bias_flag = bias_detector.predict(review_data)

        # Store Review
        review = Review(
            worker_id=worker_id,
            client_id=client_id,
            rating=rating,
            comment=comment,
            bias_flag=bias_flag,
            seller_gender=seller_gender,
            seller_nationality=seller_nationality
        )
        db.session.add(review)
        db.session.commit()

        # Update Reputation
        reviews = Review.query.filter_by(worker_id=worker_id).all()
        non_biased_reviews = [r for r in reviews if not r.bias_flag]
        reputation_score = sum(r.rating for r in non_biased_reviews) / len(non_biased_reviews) if non_biased_reviews else 0
        prev_block = ReputationLedger.query.filter_by(worker_id=worker_id).order_by(ReputationLedger.id.desc()).first()
        prev_hash = prev_block.hash if prev_block else ''
        block = reputation_blockchain.add_block(worker_id, reputation_score, prev_hash)

        # Store in Ledger
        ledger_entry = ReputationLedger(worker_id=worker_id, reputation_score=reputation_score, hash=block['hash'], prev_hash=prev_hash)
        db.session.add(ledger_entry)
        db.session.commit()

        # Explain Reputation
        explainer = ReputationExplainer(bias_detector.model)
        shap_data = {
            'Average Rating': rating,
            'seller_gender': bias_detector.gender_mapping[seller_gender],
            'seller_nationality': bias_detector.nationality_mapping[seller_nationality]
        }
        explanation = explainer.explain(shap_data)

        return jsonify({
            'status': 'success',
            'reputation_score': reputation_score,
            'bias_detected': bool(bias_flag),  # Ensure JSON-serializable
            'explanation': str(explanation)  # Ensure JSON-serializable
        })
    except ValueError as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400
    except Exception as e:
        print(f"Server error in submit_review: {str(e)}")
        return jsonify({'status': 'error', 'message': f'Server error: {str(e)}'}), 500

@app.route('/user/<int:user_id>')
def user_profile(user_id):
    user = User.query.get_or_404(user_id)
    reviews = Review.query.filter_by(worker_id=user_id).all()
    ledger = ReputationLedger.query.filter_by(worker_id=user_id).order_by(ReputationLedger.id.desc()).first()
    return render_template('profile.html', user=user, reviews=reviews, reputation_score=ledger.reputation_score if ledger else 0)

# Database Initialization
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)