# 📊 BYS Dashboard

This is a Streamlit-based dashboard for analyzing training program data. It includes authentication, multiple dashboard views, and Excel file integration.

---

## 🔧 Features

- 🔐 **Login System** for multiple users (admin, user1, etc.)
- 📁 **Project Dashboard** — Analyze SPOC-wise, project-wise, and batch type data
- 📌 **Active Batches Dashboard** — Filter active batches by SPOC, project, and course
- 💰 **SPOC Payout** — Calculate and display payouts based on certifications

---

## 📁 Files Included

- `bys_dashboard.py` – Main Streamlit app script
- `master_data.xlsx` – Source Excel file with batch and SPOC data
- `requirements.txt` – Python package requirements

---

## ▶️ How to Run Locally

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Run the app:

```bash
streamlit run bys_dashboard.py
```

---

## 🛠️ Sample Users

| Username | Password   |
|----------|------------|
| user    | password   |
| user2    | password2  |

---

## ☁️ Deploy on Streamlit Cloud

1. Upload all files (`bys_dashboard.py`, `Master Data for App_updated.csv.xlsx`, `requirements.txt`, `README.md`) to a **public GitHub repository**
2. Go to [https://streamlit.io/cloud](https://streamlit.io/cloud)
3. Sign in with GitHub and deploy the app using `bys_dashboard.py` as the entry file

---

## 📦 requirements.txt (for reference)

```
streamlit
pandas
openpyxl
```

---

## 📬 Contact

For issues or suggestions, feel free to open an issue or contact the maintainer.
