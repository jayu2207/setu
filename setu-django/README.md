# Setu — Student–Alumni Connection Platform (Django Version)

हे मूळ **Node.js + Express** backend चं पूर्ण **Python + Django** मध्ये rewrite आहे.
Frontend (HTML/CSS/JS) जसंच्या तसं ठेवलं आहे — त्यामुळे दिसायला आणि वापरायला दोन्ही
versions मध्ये काहीही फरक नाही, फक्त backend आता Node.js ऐवजी Python/Django वर चालतो.

---

## 🧩 Tech Stack

| भाग | Technology |
|---|---|
| Backend | Python + Django |
| Database | SQLite (Django ORM) — फाइल-based, वेगळा DB server लागत नाही |
| Authentication | JWT (PyJWT) + Django चं password hashing |
| Frontend | तेच जुनं Plain HTML + CSS + JavaScript (कुठलाही बदल नाही) |

---

## ✅ आधी काय Install असणं गरजेचं आहे

**Python 3.10+** — नसेल तर [python.org](https://www.python.org/downloads/) वरून install करा.
Terminal मध्ये check करा:
```bash
python --version
pip --version
```
(Windows वर कधी कधी `python` ऐवजी `py` वापरावं लागतं.)

---

## 🚀 Step by Step — Project कसा Run करायचा

### Step 1 — Project Folder उघडा
`setu-django` हा folder VS Code मध्ये उघडा (`File → Open Folder...`), किंवा
terminal मध्ये त्या folder मध्ये जा:
```bash
cd setu-django
```

### Step 2 — Virtual Environment बनवा (recommended)
```bash
python -m venv venv
```
Activate करा:
- **Windows:** `venv\Scripts\activate`
- **Mac/Linux:** `source venv/bin/activate`

### Step 3 — Dependencies Install करा
```bash
pip install -r requirements.txt
```

### Step 4 — Database तयार करा (Migrations)
```bash
python manage.py migrate
```
यामुळे SQLite database तयार होईल आणि आपोआप एक admin account सुद्धा बनेल:
```
✔ Default admin created -> email: admin@campus.edu  password: Admin@123
```

### Step 5 — Server Start करा
```bash
python manage.py runserver 0.0.0.0:5000
```
Terminal मध्ये असं दिसेल:
```
Starting WSGI development server at http://0.0.0.0:5000/
```

### Step 6 — Browser मध्ये उघडा
[http://localhost:5000](http://localhost:5000) या link वर जा.
इथून तुम्हाला पूर्ण website दिसेल — Landing page, Register, Login, सगळं
(Node.js version सारखंच दिसेल, कारण frontend तेच आहे).

> Server बंद करायला terminal मध्ये `Ctrl + C` दाबा.

**Shortcut:** वरच्या सगळ्या steps एकत्र run करण्यासाठी `start_windows.bat`
(Windows) किंवा `start_mac_linux.sh` (Mac/Linux) वापरू शकता.

---

## 🔑 Default Login (Admin)

- **Email:** `admin@campus.edu`
- **Password:** `Admin@123`

Student आणि Alumni accounts तुम्ही स्वतः **Register** page वरून बनवू शकता.

---

## 👥 तीन Roles आणि त्यांचं काम

### 🧑‍🎓 Student
- Profile बनवणे (branch, year, skills, bio)
- Opportunities (jobs/internships) बघणे आणि apply करणे
- आपल्या applications चा status track करणे
- Alumni list बघून mentorship request पाठवणे
- College events बघणे

### 🧑‍💼 Alumni
- Professional profile बनवणे (company, position, experience, skills)
- Job/internship opportunities post करणे
- कोणी apply केलं ते बघणे आणि त्यांचा status update करणे (Shortlisted/Selected/Rejected)
- Students कडून आलेल्या mentorship requests accept/reject करणे
- College events add करणे

### 🛡️ Admin
- सगळे users बघणे, block/unblock करणे, delete करणे
- सगळ्या opportunities, mentorship requests, events चा overview बघणे
- Platform चे stats बघणे (total students, alumni, opportunities वगैरे)

---

## 📂 Project Structure

```
setu-django/
├── manage.py
├── .env                    ← PORT, JWT_SECRET, ADMIN_EMAIL, ADMIN_PASSWORD
├── requirements.txt
├── setu_backend/           ← Django project settings + urls.py
├── api/                    ← सगळं backend logic इथे
│   ├── models.py           ← Database tables (users, opportunities, events...)
│   ├── auth_utils.py       ← JWT + login-required decorators
│   ├── views_auth.py       ← /api/auth/register, /api/auth/login
│   ├── views_profile.py    ← /api/profile/...
│   ├── views_opportunities.py
│   ├── views_mentorship.py
│   ├── views_events.py
│   ├── views_admin.py
│   ├── views_frontend.py   ← public/ folder serve करतो
│   └── urls.py
└── public/                 ← तेच जुनं frontend (HTML/CSS/JS), काहीही बदल नाही
```

## ⚙️ .env मधले Settings बदलायचे असतील तर

`.env` file मध्ये हे आहे (गरज पडल्यास बदला):
```
PORT=5000
JWT_SECRET=studentAlumniSuperSecretKey_ChangeThisInProduction_2026
ADMIN_EMAIL=admin@campus.edu
ADMIN_PASSWORD=Admin@123
```

---

## 🔁 Node.js Version शी Comparison

| | Node.js Version | Django Version |
|---|---|---|
| Backend | Express + better-sqlite3 | Django + Django ORM (SQLite) |
| Auth | jsonwebtoken + bcryptjs | PyJWT + Django password hashing |
| API endpoints | तेच | तेच (एकसारखे — frontend ला फरक जाणवत नाही) |
| Frontend | HTML/CSS/JS | तेच HTML/CSS/JS (जशाच्या तसं) |
| Run command | `npm start` | `python manage.py runserver 0.0.0.0:5000` |
