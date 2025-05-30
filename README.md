---

# Reputation and Trust Management System (RTMS)

The **Reputation and Trust Management System (RTMS)** is a web-based application designed to evaluate and manage reviews for gig workers on freelance platforms like Fiverr. It integrates machine learning for bias detection, a blockchain-inspired reputation ledger, and explainable AI (XAI) using SHAP for transparency in reputation scoring.

Developed as part of a startup initiative, RTMS promotes fairness and accountability in gig economies. The system detects biased reviews with \~92% accuracy, supports up to 150 automated review submissions, and responds in under 0.75 seconds on average.

---

## 📌 Table of Contents

* [Features](#features)
* [Technologies](#technologies)
* [Project Structure](#project-structure)
* [Setup Instructions](#setup-instructions)
* [Usage](#usage)
* [Testing](#testing)
* [Contributing](#contributing)
* [License](#license)
* [Contact](#contact)

---

## 🚀 Features

* **Bias Detection**
  Uses a Random Forest Classifier to detect biased reviews based on average rating, seller gender, and nationality (\~92% accuracy).

* **Reputation Ledger**
  Implements a blockchain-like ledger to securely store and track reputation scores.

* **Explainable AI**
  Integrates SHAP to provide insights into how decisions (bias detection and reputation scores) are made.

* **User-Friendly Web Interface**
  Built with Flask and Bootstrap, offering forms for submitting reviews and viewing user profiles.

* **Automated Testing**
  Includes `automated.py` to simulate 150 reviews for performance testing.

* **Scalable Performance**
  Processes 150 review submissions with an average response time of 0.75 seconds and flags \~15% as biased.

---

## 🛠 Technologies

| Component    | Version | Purpose                          |
| ------------ | ------- | -------------------------------- |
| Python       | 3.12    | Core language                    |
| Flask        | 2.3.2   | Web framework                    |
| scikit-learn | 1.3.0   | Machine learning (Random Forest) |
| pandas       | 2.0.3   | Data manipulation                |
| numpy        | 1.25.0  | Numerical operations             |
| SHAP         | 0.42.1  | Explainable AI                   |
| SQLAlchemy   | 2.0.19  | ORM for SQLite database          |
| SQLite       | -       | Lightweight database             |
| Bootstrap    | 5.3.0   | Front-end styling                |

---

## 📁 Project Structure

```
Reputation-and-Trust-Management-System/
├── app.py                  # Flask app with routes and main logic
├── preprocess.py           # Data cleaning and preprocessing script
├── automated.py            # Automation script to simulate reviews
├── bias_detector.py        # Bias detection model training logic
├── data/
│   ├── fiverr_data.csv     # Raw input dataset
│   └── processed_fiverr_data.csv  # Preprocessed dataset
├── templates/
│   ├── index.html          # Review submission page
│   └── profile.html        # User profile display
├── rtms.db                 # SQLite database (auto-generated)
├── training_metrics.txt    # Bias model training results
└── README.md               # Project documentation
```

---

## ⚙️ Setup Instructions

### ✅ Prerequisites

* Python 3.12
* Git
* Windows OS (tested on Windows 10/11)

### 🔧 Steps

1. **Clone the Repository**

   ```bash
   git clone https://github.com/Akobabs/Reputation-and-Trust-Management-System.git
   cd Reputation-and-Trust-Management-System
   ```

2. **Set Up Virtual Environment**

   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

3. **Install Dependencies**

   ```bash
   pip install flask==2.3.2 scikit-learn==1.3.0 pandas==2.0.3 numpy==1.25.0 shap==0.42.1 sqlalchemy==2.0.19
   ```

4. **Preprocess Dataset**

   * Ensure `data/fiverr_data.csv` contains the expected columns:

     > `Title`, `Seller Level`, `Average Rating`, `Number of Reviewers`, `Price (USD)`
   * Run preprocessing:

     ```bash
     python preprocess.py
     ```

5. **Initialize the Database**

   ```bash
   python app.py
   ```

   Press `Ctrl + C` to stop the server once `rtms.db` is generated.

6. **Add Sample Users**

   ```python
   from app import db, User
   with app.app_context():
       db.session.add(User(username="worker1", role="worker"))
       db.session.add(User(username="client1", role="client"))
       db.session.commit()
   ```

---

## 💡 Usage

### 🖥️ Start the Application

```bash
python app.py
```

Open your browser to: [http://127.0.0.1:5000](http://127.0.0.1:5000)

### 📝 Submit a Review

* Enter details like Worker ID, Client ID, Rating, Gender, Nationality, and Comment.
* Receive:

  * Reputation score
  * Bias flag (if any)
  * SHAP-based explanation

### 🤖 Run Automation Script

```bash
python automated.py
```

Simulates 150 reviews with test data and prints server responses.

### 👤 View User Profiles

Visit:

```
http://127.0.0.1:5000/user/1
```

To view all reviews and reputation history for `worker1`.

---

## ✅ Testing

### 📊 Model Accuracy

* View `training_metrics.txt` for \~92% bias detection accuracy.

### 🧪 Database Queries

* **Review Bias Check**

  ```bash
  sqlite3 rtms.db "SELECT rating, bias_flag FROM review;"
  ```
* **Reputation Scores**

  ```bash
  sqlite3 rtms.db "SELECT worker_id, reputation_score FROM reputation_ledger;"
  ```

### ⏱️ Performance

* Expect \~0.75s average response time per request in `automated.py`.

---

## 🤝 Contributing

Contributions are welcome!

1. Fork the repo
2. Create your feature branch:
   `git checkout -b feature/your-feature`
3. Commit changes:
   `git commit -m "Add your feature"`
4. Push to GitHub:
   `git push origin feature/your-feature`
5. Open a Pull Request 🚀

---

## 📜 License

This project is licensed under the [MIT License](LICENSE).

---

## 📬 Contact

* GitHub: [Akobabs](https://github.com/Akobabs)
* For questions, open an issue on the GitHub repo.

---