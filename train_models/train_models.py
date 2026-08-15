"""
Machine Learning Model Training Script
Trains models for Diabetes, Heart Disease, and Chronic Kidney Disease prediction

This script:
1. Loads sample datasets
2. Preprocesses data
3. Trains Random Forest models
4. Calculates accuracy metrics
5. Saves models as pickle files
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
import joblib
import os
from datetime import datetime

# Set random seed for reproducibility
np.random.seed(42)

class MLModelTrainer:
    """Class to train and save ML models for disease prediction"""
    
    def __init__(self, models_path='models', scalers_path='scalers', datasets_path='datasets'):
        """Initialize trainer with paths for models, scalers, and datasets"""
        self.models_path = models_path
        self.scalers_path = scalers_path
        self.datasets_path = datasets_path

        os.makedirs(self.models_path, exist_ok=True)
        os.makedirs(self.scalers_path, exist_ok=True)
        os.makedirs(self.datasets_path, exist_ok=True)

        self.models = {}
        self.accuracies = {}
    
    def create_diabetes_dataset(self, n_samples=500):
        """
        Create or load diabetes dataset
        Expected features: Age, BMI, Glucose, BloodPressure, SkinThickness, Insulin, DiabetesPedigreeFunction, Pregnancies
        """
        diabetes_path = os.path.join(self.datasets_path, 'diabetes.csv')
        if os.path.exists(diabetes_path):
            print(f"Loading diabetes dataset from {diabetes_path}")
            df = pd.read_csv(diabetes_path)
            if 'Outcome' in df.columns:
                df = df.rename(columns={'Outcome': 'Diabetes'})
            required_columns = [
                'Age', 'BMI', 'Glucose', 'BloodPressure', 'SkinThickness',
                'Insulin', 'DiabetesPedigreeFunction', 'Pregnancies', 'Diabetes'
            ]
            missing = [col for col in required_columns if col not in df.columns]
            if not missing:
                return df[required_columns]
            print(f"Diabetes dataset missing columns: {missing}")

        np.random.seed(42)
        data = {
            'Age': np.random.randint(20, 80, n_samples),
            'BMI': np.random.uniform(18, 40, n_samples),
            'Glucose': np.random.uniform(70, 200, n_samples),
            'BloodPressure': np.random.uniform(60, 140, n_samples),
            'SkinThickness': np.random.uniform(0, 100, n_samples),
            'Insulin': np.random.uniform(0, 300, n_samples),
            'DiabetesPedigreeFunction': np.random.uniform(0, 2.5, n_samples),
            'Pregnancies': np.random.randint(0, 15, n_samples)
        }
        target = (
            (data['Glucose'] > 125).astype(int) * 0.4 +
            (data['BMI'] > 30).astype(int) * 0.3 +
            (data['Age'] > 50).astype(int) * 0.2 +
            np.random.randint(0, 2, n_samples) * 0.1
        ) > 0.5
        
        df = pd.DataFrame(data)
        df['Diabetes'] = target.astype(int)
        return df
    
    def create_heart_disease_dataset(self, n_samples=500):
        """
        Create or load heart disease dataset
        Expected features: Age, Sex, ChestPainType, RestingBP, Cholesterol, FastingBS,
        RestingECG, MaxHR, Oldpeak, Slope
        """
        heart_path = os.path.join(self.datasets_path, 'heart.csv')
        if os.path.exists(heart_path):
            print(f"Loading heart disease dataset from {heart_path}")
            df = pd.read_csv(heart_path)
            if 'Target' in df.columns:
                df = df.rename(columns={'Target': 'HeartDisease'})
                df['HeartDisease'] = (df['HeartDisease'] > 0).astype(int)
            required_columns = [
                'Age', 'Sex', 'ChestPainType', 'RestingBP', 'Cholesterol',
                'FastingBS', 'RestingECG', 'MaxHR', 'Oldpeak', 'Slope', 'HeartDisease'
            ]
            missing = [col for col in required_columns if col not in df.columns]
            if not missing:
                return df[required_columns]
            print(f"Heart disease dataset missing columns: {missing}")

        np.random.seed(42)
        data = {
            'Age': np.random.randint(30, 80, n_samples),
            'Sex': np.random.choice([0, 1], n_samples),
            'ChestPainType': np.random.choice([1, 2, 3, 4], n_samples),
            'RestingBP': np.random.uniform(90, 180, n_samples),
            'Cholesterol': np.random.uniform(150, 400, n_samples),
            'FastingBS': np.random.choice([0, 1], n_samples),
            'RestingECG': np.random.choice([0, 1, 2], n_samples),
            'MaxHR': np.random.randint(60, 200, n_samples),
            'Oldpeak': np.random.uniform(0, 6, n_samples),
            'Slope': np.random.choice([1, 2, 3], n_samples)
        }
        target = (
            (data['Age'] > 50).astype(int) * 0.3 +
            (data['Cholesterol'] > 240).astype(int) * 0.3 +
            (data['RestingBP'] > 140).astype(int) * 0.2 +
            (data['MaxHR'] < 100).astype(int) * 0.2
        ) > 0.5
        
        df = pd.DataFrame(data)
        df['HeartDisease'] = target.astype(int)
        return df
    
    def create_kidney_disease_dataset(self, n_samples=500):
        """
        Create or load chronic kidney disease dataset
        Expected features: Age, BloodPressure, SpecificGravity, Albumin, Sugar,
        Creatinine, BloodUrea, Hemoglobin, WhiteBloodCells, RedBloodCells,
        Hypertension, Diabetes
        """
        kidney_path = os.path.join(self.datasets_path, 'kidney.csv')
        if os.path.exists(kidney_path):
            print(f"Loading kidney disease dataset from {kidney_path}")
            df = pd.read_csv(kidney_path)
            if 'KidneyDisease' in df.columns:
                required_columns = [
                    'Age', 'BloodPressure', 'SpecificGravity', 'Albumin', 'Sugar',
                    'Creatinine', 'BloodUrea', 'Hemoglobin', 'WhiteBloodCells',
                    'RedBloodCells', 'Hypertension', 'Diabetes', 'KidneyDisease'
                ]
                missing = [col for col in required_columns if col not in df.columns]
                if not missing:
                    return df[required_columns]
                print(f"Kidney disease dataset missing columns: {missing}")

        np.random.seed(42)
        data = {
            'Age': np.random.randint(20, 85, n_samples),
            'BloodPressure': np.random.uniform(70, 180, n_samples),
            'SpecificGravity': np.random.choice([1.005, 1.010, 1.015, 1.020, 1.025, 1.030], n_samples),
            'Albumin': np.random.choice([0, 1, 2, 3, 4, 5], n_samples),
            'Sugar': np.random.choice([0, 1, 2, 3, 4, 5], n_samples),
            'Creatinine': np.random.uniform(0.5, 8.0, n_samples),
            'BloodUrea': np.random.uniform(20, 150, n_samples),
            'Hemoglobin': np.random.uniform(7, 17, n_samples),
            'WhiteBloodCells': np.random.uniform(3000, 20000, n_samples),
            'RedBloodCells': np.random.uniform(2, 6, n_samples),
            'Hypertension': np.random.choice([0, 1], n_samples),
            'Diabetes': np.random.choice([0, 1], n_samples)
        }
        target = (
            (data['Creatinine'] > 1.5).astype(int) * 0.35 +
            (data['BloodUrea'] > 100).astype(int) * 0.25 +
            (data['Hemoglobin'] < 10).astype(int) * 0.2 +
            (data['Hypertension'] == 1).astype(int) * 0.1 +
            (data['Diabetes'] == 1).astype(int) * 0.1 +
            np.random.rand(n_samples) * 0.05
        ) > 0.5
        df = pd.DataFrame(data)
        df['KidneyDisease'] = target.astype(int)
        return df
    
    def train_model(self, X, y, disease_name, test_size=0.2):
        """
        Train Random Forest model
        Args:
            X: Features dataframe
            y: Target variable
            disease_name: Name of disease (for identification)
            test_size: Test set proportion
        Returns: Trained model, scaler, and metrics
        """
        print(f"\nTraining {disease_name} model...")
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42
        )
        
        # Scale features with a fresh scaler per disease
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Train Random Forest model
        model = RandomForestClassifier(
            n_estimators=100,
            max_depth=15,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42,
            n_jobs=-1
        )
        model.fit(X_train_scaled, y_train)
        
        # Make predictions
        y_pred = model.predict(X_test_scaled)
        
        # Calculate metrics
        accuracy = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred, average='weighted')
        recall = recall_score(y_test, y_pred, average='weighted')
        f1 = f1_score(y_test, y_pred, average='weighted')
        
        # Print metrics
        print(f"Accuracy: {accuracy:.4f}")
        print(f"Precision: {precision:.4f}")
        print(f"Recall: {recall:.4f}")
        print(f"F1 Score: {f1:.4f}")
        
        metrics = {
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'f1': f1
        }
        
        return model, scaler, metrics
    
    def save_model(self, model, scaler, disease_name):
        """Save trained model and scaler"""
        name = disease_name.lower().replace(' ', '_')
        model_filename = os.path.join(self.models_path, f'{name}_model.pkl')
        scaler_filename = os.path.join(self.scalers_path, f'{name}_scaler.pkl')
        
        joblib.dump(model, model_filename)
        joblib.dump(scaler, scaler_filename)
        
        print(f"Model saved: {model_filename}")
        print(f"Scaler saved: {scaler_filename}")
        
        self.models[disease_name] = model
        self.accuracies[disease_name] = {}
    
    def train_all_models(self):
        """Train all three disease prediction models"""
        print("=" * 60)
        print("AI Healthcare Analytics - Model Training")
        print("=" * 60)
        print(f"Start Time: {datetime.now()}")
        
        # Train Diabetes Model
        print("\n--- DIABETES PREDICTION MODEL ---")
        diabetes_df = self.create_diabetes_dataset()
        X_diabetes = diabetes_df.drop('Diabetes', axis=1)
        y_diabetes = diabetes_df['Diabetes']
        diabetes_model, diabetes_scaler, diabetes_metrics = self.train_model(
            X_diabetes, y_diabetes, 'Diabetes'
        )
        self.save_model(diabetes_model, diabetes_scaler, 'Diabetes')
        self.accuracies['Diabetes'] = diabetes_metrics
        
        # Train Heart Disease Model
        print("\n--- HEART DISEASE PREDICTION MODEL ---")
        heart_df = self.create_heart_disease_dataset()
        X_heart = heart_df.drop('HeartDisease', axis=1)
        y_heart = heart_df['HeartDisease']
        heart_model, heart_scaler, heart_metrics = self.train_model(
            X_heart, y_heart, 'Heart Disease'
        )
        self.save_model(heart_model, heart_scaler, 'Heart Disease')
        self.accuracies['Heart Disease'] = heart_metrics
        
        # Train Kidney Disease Model
        print("\n--- CHRONIC KIDNEY DISEASE PREDICTION MODEL ---")
        kidney_df = self.create_kidney_disease_dataset()
        X_kidney = kidney_df.drop('KidneyDisease', axis=1)
        y_kidney = kidney_df['KidneyDisease']
        kidney_model, kidney_scaler, kidney_metrics = self.train_model(
            X_kidney, y_kidney, 'Kidney Disease'
        )
        self.save_model(kidney_model, kidney_scaler, 'Kidney Disease')
        self.accuracies['Kidney Disease'] = kidney_metrics
        
        # Print summary
        print("\n" + "=" * 60)
        print("TRAINING SUMMARY")
        print("=" * 60)
        for disease, metrics in self.accuracies.items():
            print(f"\n{disease}:")
            print(f"  Accuracy:  {metrics['accuracy']:.4f}")
            print(f"  Precision: {metrics['precision']:.4f}")
            print(f"  Recall:    {metrics['recall']:.4f}")
            print(f"  F1 Score:  {metrics['f1']:.4f}")
        
        print(f"\nEnd Time: {datetime.now()}")
        print("=" * 60)
        print("All models trained and saved successfully!")

if __name__ == "__main__":
    # Create trainer instance and train models
    trainer = MLModelTrainer(models_path='models', scalers_path='scalers', datasets_path='datasets')
    trainer.train_all_models()
