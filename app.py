"""
AI Healthcare Analytics - Explainable Multi-Disease Risk Prediction
Flask Web Application Main Module

This application provides:
- User authentication and registration
- Patient data management
- Multi-disease prediction (Diabetes, Heart Disease, Kidney Disease)
- SHAP-based explainability
- Prediction history tracking
- Admin dashboard
- PDF report generation
"""

from flask import Flask, render_template, request, redirect, url_for, session, jsonify, send_file
from werkzeug.security import generate_password_hash, check_password_hash
import os
import sys
import numpy as np
from dotenv import load_dotenv

# Load .env early so app config and imported modules can use it
load_dotenv()
import pandas as pd
import joblib
import shap
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from datetime import datetime
import json

# Import custom modules
from database import Database

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-change-in-production')

# Initialize database
db = Database()

# One-time database initialization flag
_db_initialized = False

def _initialize_database_once():
    """Initialize database connection once on first request"""
    global _db_initialized
    if not _db_initialized:
        if db.connect():
            print('Database initialized successfully')
        else:
            print('Warning: initial database connection failed')
        _db_initialized = True

@app.before_request
def initialize_database():
    """Ensure database is initialized before processing request"""
    _initialize_database_once()

# Base application directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Model paths
MODEL_PATHS = {
    'diabetes': os.path.join(BASE_DIR, 'models', 'diabetes_model.pkl'),
    'heart_disease': os.path.join(BASE_DIR, 'models', 'heart_disease_model.pkl'),
    'kidney_disease': os.path.join(BASE_DIR, 'models', 'kidney_disease_model.pkl')
}

SCALER_PATHS = {
    'diabetes': os.path.join(BASE_DIR, 'scalers', 'diabetes_scaler.pkl'),
    'heart_disease': os.path.join(BASE_DIR, 'scalers', 'heart_disease_scaler.pkl'),
    'kidney_disease': os.path.join(BASE_DIR, 'scalers', 'kidney_disease_scaler.pkl')
}

# Feature names for each disease
FEATURE_NAMES = {
    'diabetes': ['Age', 'BMI', 'Glucose', 'BloodPressure', 'SkinThickness', 'Insulin', 'DiabetesPedigreeFunction', 'Pregnancies'],
    'heart_disease': ['Age', 'Sex', 'ChestPainType', 'RestingBP', 'Cholesterol', 'FastingBS', 'RestingECG', 'MaxHR', 'Oldpeak', 'Slope'],
    'kidney_disease': ['Age', 'BloodPressure', 'SpecificGravity', 'Albumin', 'Sugar', 'Creatinine', 'BloodUrea', 'Hemoglobin', 'WhiteBloodCells', 'RedBloodCells', 'Hypertension', 'Diabetes']
}

class PredictionEngine:
    """Handles disease prediction and explainability"""
    
    def __init__(self):
        """Initialize prediction engine with models"""
        self.models = {}
        self.scalers = {}
        self.explainers = {}
        self.load_models()
    
    def load_models(self):
        """Load trained models and scalers"""
        self.models.clear()
        self.scalers.clear()
        print("\n===== LOADING PREDICTION MODELS =====")
        print(f"BASE_DIR: {BASE_DIR}")
        for disease in MODEL_PATHS.keys():
            model_path = MODEL_PATHS[disease]
            scaler_path = SCALER_PATHS[disease]
            try:
                if os.path.exists(model_path):
                    self.models[disease] = joblib.load(model_path)
                    print(f"Loaded {disease} model from {model_path}")
                else:
                    print(f"Model file missing for {disease}: {model_path}")

                if os.path.exists(scaler_path):
                    self.scalers[disease] = joblib.load(scaler_path)
                    print(f"Loaded {disease} scaler from {scaler_path}")
                else:
                    print(f"Scaler file missing for {disease}: {scaler_path}")
            except Exception as e:
                print(f"Error loading {disease} model or scaler: {e}")

        missing_models = [d for d in MODEL_PATHS.keys() if d not in self.models]
        missing_scalers = [d for d in SCALER_PATHS.keys() if d not in self.scalers]
        print(f"Models loaded: {list(self.models.keys())}")
        print(f"Scalers loaded: {list(self.scalers.keys())}")
        if missing_models: 
            print(f"Missing model entries: {missing_models}")
        if missing_scalers:
            print(f"Missing scaler entries: {missing_scalers}")
        print("===== MODEL LOADING COMPLETE =====\n")

    def ensure_models_loaded(self):
        """Reload models if any expected model is not currently loaded"""
        if len(self.models) != len(MODEL_PATHS) or len(self.scalers) != len(SCALER_PATHS):
            self.load_models()
    
    def preprocess_data(self, data, disease):
        """
        Preprocess input data
        Args:
            data: Dictionary with patient features
            disease: Disease type
        Returns: Scaled numpy array or None
        """
        try:
            if disease not in FEATURE_NAMES:
                print(f"Unknown disease for preprocessing: {disease}")
                return None

            # Create array in correct feature order
            feature_order = FEATURE_NAMES[disease]
            values = [float(data.get(feature, 0) or 0) for feature in feature_order]
            X = np.array([values], dtype=float)

            # Scale data if scaler exists
            if disease in self.scalers:
                X_scaled = self.scalers[disease].transform(X)
                return X_scaled
            return X
        except Exception as e:
            print(f"Preprocessing error for {disease}: {e}")
            return None

    def predict(self, data, disease):
        """
        Make prediction for disease
        Args:
            data: Patient data dictionary
            disease: Disease type
        Returns: Prediction result with confidence
        """
        try:
            self.ensure_models_loaded()

            if disease not in self.models:
                error_msg = f"Model not found for disease '{disease}'"
                print(error_msg)
                return {'error': error_msg}

            # Preprocess data
            X = self.preprocess_data(data, disease)
            if X is None:
                return {'error': 'Data preprocessing failed'}

            # Make prediction
            model = self.models[disease]
            prediction = int(model.predict(X)[0])
            confidence = 0.0
            if hasattr(model, 'predict_proba'):
                confidence = float(max(model.predict_proba(X)[0]) * 100)

            feature_importance = []
            if hasattr(model, 'feature_importances_'):
                feature_importance = model.feature_importances_.tolist()

            return {
                'prediction': prediction,
                'confidence': confidence,
                'feature_importance': feature_importance
            }
        except Exception as e:
            print(f"Prediction error for {disease}: {e}")
            return {'error': str(e)}

    def get_explanation(self, data, disease):
        """
        Generate SHAP explanation
        Args:
            data: Patient data dictionary
            disease: Disease type
        Returns: SHAP explanation dict
        """
        try:
            self.ensure_models_loaded()

            if disease not in self.models:
                print(f"Explanation requested for unknown disease: {disease}")
                return {}

            X = self.preprocess_data(data, disease)
            if X is None:
                return {}

            model = self.models[disease]
            explainer = shap.TreeExplainer(model)
            shap_values_raw = explainer.shap_values(X)

            # Handle SHAP output for binary classification and array/list formats
            if isinstance(shap_values_raw, list):
                if len(shap_values_raw) > 1:
                    shap_values_raw = shap_values_raw[1]
                elif len(shap_values_raw) == 1:
                    shap_values_raw = shap_values_raw[0]

            shap_values_array = np.asarray(shap_values_raw, dtype=object)
            if shap_values_array.ndim == 0:
                shap_values = [float(np.asarray(shap_values_array).item())]
            elif shap_values_array.ndim == 1:
                shap_values = []
                for value in shap_values_array.tolist():
                    if isinstance(value, (list, tuple, np.ndarray)):
                        inner = np.asarray(value, dtype=float)
                        shap_values.append(float(inner.flatten()[0]))
                    else:
                        shap_values.append(float(value))
            else:
                shap_values = []
                for value in np.asarray(shap_values_array[0], dtype=object).tolist():
                    if isinstance(value, (list, tuple, np.ndarray)):
                        inner = np.asarray(value, dtype=float)
                        shap_values.append(float(inner.flatten()[0]))
                    else:
                        shap_values.append(float(value))

            feature_names = FEATURE_NAMES[disease]
            base_value_raw = explainer.expected_value
            if isinstance(base_value_raw, list):
                base_value_raw = base_value_raw[1] if len(base_value_raw) > 1 else base_value_raw[0]

            base_value_array = np.asarray(base_value_raw, dtype=object)
            if base_value_array.ndim == 0:
                base_value = float(base_value_array.item())
            elif base_value_array.size > 1:
                candidate = base_value_array.item(1)
                if isinstance(candidate, (list, tuple, np.ndarray)):
                    candidate = np.asarray(candidate, dtype=float).flatten()[0]
                base_value = float(candidate)
            else:
                candidate = base_value_array.item(0)
                if isinstance(candidate, (list, tuple, np.ndarray)):
                    candidate = np.asarray(candidate, dtype=float).flatten()[0]
                base_value = float(candidate)

            explanation = {
                'feature_names': feature_names,
                'shap_values': shap_values,
                'base_value': base_value
            }
            return explanation
        except Exception as e:
            print(f"Explanation error for {disease}: {e}")
            return {}

# Initialize prediction engine
prediction_engine = PredictionEngine()

# ==================== Authentication Routes ====================

@app.route('/')
def index():
    """Home page"""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Validation
        if not username or not email or not password:
            return render_template('register.html', error='All fields required')
        
        if password != confirm_password:
            return render_template('register.html', error='Passwords do not match')
        
        if len(password) < 6:
            return render_template('register.html', error='Password must be at least 6 characters')
        
        try:
            print(f'\n=== REGISTRATION ATTEMPT ===')
            print(f'Username: {username}, Email: {email}')
            
            # Attempt database connection
            print('Step 1: Connecting to database...')
            conn = db.connect()
            if not conn:
                error_msg = 'Failed to connect to database. Check Flask console for detailed error.'
                print(f'✗ {error_msg}')
                return render_template('register.html', error=error_msg)
            print('✓ Database connection successful')

            # Check if email exists
            print('Step 2: Checking if email already exists...')
            existing_user = db.get_user(email)
            if existing_user:
                print(f'✗ Email already exists: {email}')
                return render_template('register.html', error='Email already exists')
            print(f'✓ Email is available: {email}')

            # Hash password
            print('Step 3: Hashing password...')
            hashed_password = generate_password_hash(password)
            print('✓ Password hashed')
            
            # Insert user
            print('Step 4: Inserting user into database...')
            if db.insert_user(username, email, hashed_password):
                print(f'✓ User registered successfully: {email}')
                print('=== REGISTRATION COMPLETE ===\n')
                return redirect(url_for('login'))
            else:
                error_msg = 'Failed to insert user. Check Flask console for SQL error details.'
                print(f'✗ {error_msg}')
                return render_template('register.html', error=error_msg)
                
        except Exception as e:
            error_msg = f'Unexpected error: {str(e)}'
            print(f'✗ Exception during registration: {error_msg}')
            print(f'Exception type: {type(e).__name__}')
            print('=== REGISTRATION FAILED ===\n')
            return render_template('register.html', error=error_msg)
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        if not email or not password:
            return render_template('login.html', error='Email and password required')
        
        conn = db.connect()
        if not conn:
            return render_template('login.html', error='Database connection failed')

        user = db.get_user(email)

        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['is_admin'] = user['is_admin']
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error='Invalid email or password')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """User logout"""
    session.clear()
    return redirect(url_for('login'))

# ==================== Main Application Routes ====================

@app.route('/dashboard')
def dashboard():
    """User dashboard"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if not db.connect():
        return redirect(url_for('login'))
    user = db.get_user_by_id(session['user_id']) or {}
    patient = db.get_patient(session['user_id']) or {}
    predictions = db.get_predictions(session['user_id']) or []
    
    return render_template('dashboard.html', 
                         user=user, 
                         patient=patient, 
                         predictions=predictions)

@app.route('/patient-info', methods=['GET', 'POST'])
def patient_info():
    """Manage patient information"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if not db.connect():
        return redirect(url_for('login'))

    if request.method == 'POST':
        age = request.form.get('age')
        gender = request.form.get('gender')
        blood_type = request.form.get('blood_type')
        medical_history = request.form.get('medical_history', '')
        
        # Check if patient record exists
        patient = db.get_patient(session['user_id'])
        
        if patient:
            # Update existing patient record
            db.update_patient(session['user_id'], age, gender, blood_type)
        else:
            # Create new patient record
            db.insert_patient(session['user_id'], age, gender, blood_type)
        
        return redirect(url_for('dashboard'))
    
    patient = db.get_patient(session['user_id'])
    
    return render_template('patient_info.html', patient=patient)

@app.route('/predict/<disease>', methods=['GET', 'POST'])
def predict(disease):
    """Disease prediction form and result"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if disease not in FEATURE_NAMES:
        return "Invalid disease", 400
    
    if request.method == 'POST':
        # Get form data
        data = {}
        for feature in FEATURE_NAMES[disease]:
            data[feature] = request.form.get(feature, 0)
        
        # Make prediction
        result = prediction_engine.predict(data, disease)
        
        if 'error' in result:
            return render_template(f'predict_{disease}.html', 
                                 error=result['error'],
                                 disease=disease,
                                 features=FEATURE_NAMES[disease])
        
        # Get explanation
        explanation = prediction_engine.get_explanation(data, disease)
        
        # Store in database (best-effort)
        if db.connect():
            patient = db.get_patient(session['user_id'])
            patient_id = patient['id'] if patient else None
            explanation_text = json.dumps(explanation)
            db.insert_prediction(
                session['user_id'],
                patient_id,
                disease,
                "Positive" if result['prediction'] == 1 else "Negative",
                result['confidence'],
                explanation_text
            )
        else:
            print('Warning: DB connection failed; skipping saving prediction')
        
        return render_template(f'result_{disease}.html',
                             disease=disease,
                             prediction=result['prediction'],
                             confidence=result['confidence'],
                             explanation=explanation,
                             data=data)
    
    return render_template(f'predict_{disease}.html',
                         disease=disease,
                         features=FEATURE_NAMES[disease])

@app.route('/prediction-history')
def prediction_history():
    """View prediction history"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if not db.connect():
        return redirect(url_for('login'))
    predictions = db.get_predictions(session['user_id'])
    
    return render_template('prediction_history.html', predictions=predictions)

@app.route('/download-report/<int:prediction_id>')
def download_report(prediction_id):
    """Download prediction report as PDF"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if not db.connect():
        return redirect(url_for('login'))
    predictions = db.get_predictions(session['user_id'])
    prediction = next((p for p in predictions if p['id'] == prediction_id), None)
    
    if not prediction:
        return "Report not found", 404
    
    # Create PDF
    pdf_buffer = BytesIO()
    doc = SimpleDocTemplate(pdf_buffer, pagesize=letter)
    story = []
    styles = getSampleStyleSheet()
    
    # Add title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1F4788'),
        spaceAfter=30
    )
    story.append(Paragraph("Healthcare Prediction Report", title_style))
    story.append(Spacer(1, 12))
    
    # Add patient and prediction info
    info_data = [
        ['Report Date:', datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
        ['Disease:', prediction['disease']],
        ['Prediction:', prediction['prediction']],
        ['Confidence:', f"{prediction['confidence']:.2f}%"],
        ['Prediction Date:', prediction['prediction_date']]
    ]
    
    info_table = Table(info_data, colWidths=[2*72, 4*72])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#E8F1FF')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey)
    ]))
    story.append(info_table)
    story.append(Spacer(1, 20))
    
    # Add explanation if available
    if prediction['explanation']:
        try:
            explanation = json.loads(prediction['explanation'])
            story.append(Paragraph("Explanation (SHAP)", styles['Heading2']))
            story.append(Spacer(1, 10))
            
            explanation_text = "This prediction is based on the following feature contributions:"
            story.append(Paragraph(explanation_text, styles['Normal']))
            story.append(Spacer(1, 10))
        except:
            pass
    
    # Add disclaimer
    story.append(Spacer(1, 20))
    disclaimer_style = ParagraphStyle(
        'Disclaimer',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.grey
    )
    disclaimer_text = "Disclaimer: This report is generated by an AI system and should not be used as a substitute for professional medical advice. Please consult with a healthcare professional for accurate diagnosis."
    story.append(Paragraph(disclaimer_text, disclaimer_style))
    
    # Build PDF
    doc.build(story)
    pdf_buffer.seek(0)
    
    return send_file(
        pdf_buffer,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f'prediction_{prediction_id}.pdf'
    )

# ==================== Admin Routes ====================

@app.route('/admin/dashboard')
def admin_dashboard():
    """Admin dashboard"""
    if 'user_id' not in session or not session.get('is_admin'):
        return redirect(url_for('login'))
    
    if not db.connect():
        return redirect(url_for('login'))
    all_users = db.get_all_users()
    all_predictions = db.get_all_predictions()
    
    # Calculate statistics
    total_users = len(all_users) if all_users else 0
    total_predictions = len(all_predictions) if all_predictions else 0
    
    return render_template('admin_dashboard.html',
                         users=all_users,
                         predictions=all_predictions,
                         total_users=total_users,
                         total_predictions=total_predictions)

# ==================== Error Handlers ====================

@app.errorhandler(404)
def page_not_found(error):
    """Handle 404 errors"""
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return render_template('500.html'), 500

if __name__ == '__main__':
    try:
        print("Healthcare Analytics Application Started")
        print("Access the application at http://localhost:5000")
        app.run(debug=True, host='localhost', port=5000)
    finally:
        # Ensure database connection is closed on shutdown
        db.disconnect()
        print("Application shutdown complete")
