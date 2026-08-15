# 🏥 AI Healthcare Analytics - Quick Start Guide

> **AI-Driven Healthcare Analytics for Explainable Multi-Disease Risk Prediction**

A comprehensive full-stack web application that uses machine learning and explainable AI to predict health risks.

## 🚀 Quick Start (5 Minutes)

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Database
```bash
# Create MySQL database
mysql -u root -p < healthcare_schema.sql
```

### 3. Create .env File
```bash
cp .env.example .env
# Edit .env with your MySQL credentials
```

### 4. Train Models
```bash
python train_models/train_models.py
```

### 5. Run Application
```bash
python app.py
# Visit http://localhost:5000
```

---

## 📋 Features

✅ **Multi-Disease Prediction**
- Diabetes Risk Assessment
- Heart Disease Detection  
- Chronic Kidney Disease Screening

✅ **Explainable AI**
- SHAP feature importance analysis
- Transparent model decisions
- Easy-to-understand explanations

✅ **User Management**
- Secure registration & login
- Password hashing with Werkzeug
- Session management

✅ **Data Management**
- Patient information storage
- Prediction history tracking
- Medical data privacy

✅ **Reports & Export**
- PDF report generation
- Prediction history download
- Admin analytics

✅ **Admin Dashboard**
- User management
- Prediction statistics
- System monitoring

---

## 🔑 Default Admin Account

```
Email: admin@healthcare.com
Password: admin123
```

---

## 📁 Project Structure

```
├── app.py                    # Main Flask application
├── database.py               # Database operations
├── requirements.txt          # Python dependencies
├── healthcare_schema.sql     # MySQL database schema
│
├── train_models/
│   └── train_models.py      # ML model training script
│
├── models/                   # Trained model files (.pkl)
├── templates/                # HTML templates (13 files)
└── static/
    ├── css/                  # Stylesheets
    └── js/                   # JavaScript files
```

---

## 🔧 Technology Stack

| Component | Technology |
|-----------|-----------|
| **Frontend** | HTML5, CSS3, JavaScript (ES6+) |
| **Backend** | Python, Flask |
| **Database** | MySQL |
| **ML Framework** | Scikit-learn, SHAP |
| **Data Science** | Pandas, NumPy |

---

## 📊 Disease Models

### Diabetes Prediction
- **Algorithm**: Random Forest (100 estimators)
- **Input Features**: 8 parameters
- **Accuracy**: ~78-82%
- **Key Factors**: Glucose, BMI, Age, Family History

### Heart Disease Prediction
- **Algorithm**: Random Forest (100 estimators)
- **Input Features**: 10 parameters
- **Accuracy**: ~80-85%
- **Key Factors**: Age, Cholesterol, Blood Pressure

### Kidney Disease Prediction
- **Algorithm**: Random Forest (100 estimators)
- **Input Features**: 12 parameters
- **Accuracy**: ~78-82%
- **Key Factors**: Creatinine, Blood Urea, Hemoglobin

---

## 🔒 Security Features

- ✅ Password hashing (Werkzeug)
- ✅ SQL injection prevention (Parameterized queries)
- ✅ CSRF protection (Flask sessions)
- ✅ Input validation (Client & server-side)
- ✅ Authentication & authorization

---

## 📱 Pages & Routes

| Page | Route | Description |
|------|-------|-------------|
| Login | `/login` | User authentication |
| Register | `/register` | New user registration |
| Dashboard | `/dashboard` | Main user dashboard |
| Patient Info | `/patient-info` | Manage patient data |
| Prediction | `/predict/<disease>` | Make predictions |
| History | `/prediction-history` | View past predictions |
| Admin Panel | `/admin/dashboard` | Admin management |
| Report | `/download-report/<id>` | Download PDF report |

---

## ⚙️ Troubleshooting

### MySQL Connection Error
```bash
# Check MySQL is running and credentials are correct
mysql -u root -p
```

### Models Not Found
```bash
# Retrain models
python train_models/train_models.py
```

### Port 5000 Already in Use
```bash
# Kill process using port 5000
# Windows: netstat -ano | findstr :5000 → taskkill /PID <PID> /F
# Mac/Linux: lsof -ti:5000 | xargs kill -9
```

### Module Import Errors
```bash
# Reinstall all packages
pip install --force-reinstall -r requirements.txt
```

---

## 📚 Documentation

For detailed documentation, see:
- **SETUP_INSTRUCTIONS.md** - Complete installation guide
- **Code comments** - Inline documentation
- **Docstrings** - Function documentation

---

## ⚠️ Medical Disclaimer

This application is for **educational and informational purposes only**:

- ❌ NOT a medical device
- ❌ NOT a substitute for professional medical advice
- ❌ Should NOT be used for medical diagnosis or treatment
- ✅ Always consult qualified healthcare professionals

**Use responsibly. Your health matters.** 🏥

---

## 🚀 Next Steps

1. ✅ Install dependencies (`pip install -r requirements.txt`)
2. ✅ Setup MySQL database (`mysql -u root -p < healthcare_schema.sql`)
3. ✅ Configure `.env` file (copy and edit `.env.example`)
4. ✅ Train ML models (`python train_models/train_models.py`)
5. ✅ Run application (`python app.py`)
6. ✅ Visit http://localhost:5000

---

## 💡 Features To Try

1. **Register** a new account
2. **Add** patient information
3. **Make** a disease prediction
4. **View** SHAP explanation
5. **Download** PDF report
6. **Check** prediction history
7. **Login as admin** (email: admin@healthcare.com)
8. **View** admin dashboard

---

## 🎯 System Requirements

- **Python**: 3.8+
- **MySQL**: 5.7+
- **RAM**: 2GB+
- **Disk**: 500MB+
- **Browser**: Modern (Chrome, Firefox, Safari, Edge)

---

## 📞 Support

For issues or questions:
1. Check SETUP_INSTRUCTIONS.md
2. Review code comments
3. Check error messages in console
4. Verify all dependencies installed

---

## 📄 License

This project is provided as-is for educational purposes.

---

## 🙏 Acknowledgments

- Scikit-learn team for ML algorithms
- SHAP developers for explainability
- Flask team for the web framework
- ReportLab for PDF generation

---

**Ready to get started? Run `python app.py` and visit http://localhost:5000!** 🚀

---

*Last Updated: June 18, 2024*
