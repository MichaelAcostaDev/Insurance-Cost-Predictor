# 🧑‍⚕️ Insurance Cost Predictor

A Machine Learning web application that predicts health insurance costs using a trained regression model built with Python and Flask.

---

## 👀 Overview

Insurance Cost Predictor estimates an individual's insurance premium based on personal information such as age, BMI, smoking status, number of children, sex, and region.

The project demonstrates a complete Machine Learning workflow, from data preprocessing and model training to deploying an interactive web application.

Instead of remaining as a Jupyter Notebook, the trained model is integrated into a production-ready Flask application with a responsive user interface.

---

## 📌 Features

- Machine Learning regression model
- Flask backend
- Responsive modern interface
- English and Spanish support
- Real-time predictions
- Input validation
- CSV prediction logging
- Pre-trained model (.joblib)
- Docker support
- Ready for deployment

---

## ✅ Tech Stack

- Python
- Flask
- Scikit-learn
- Pandas
- NumPy
- Joblib
- HTML5
- CSS3
- JavaScript
- Docker

---

---

## 🤖 Machine Learning

The model was trained using the Insurance dataset with features including:

- Age
- Sex
- BMI
- Children
- Smoker
- Region

Target:

- Insurance Charges

The trained model is serialized with Joblib and loaded by the Flask application to provide instant predictions.

---

## 🚀 Getting Started

Clone the repository

```bash
git clone https://github.com/MichaelAcostaDev/Insurance-Cost-Predictor.git
```

Install dependencies

```bash
pip install -r requirements.txt
```

Run the application

```bash
python app.py
```

Then open:

```
http://localhost:8000
```

---

## 🧑‍💻 Author

Michael Acosta - MichaelAcostaDev

If you found this project useful, consider giving it a ⭐ on GitHub.
