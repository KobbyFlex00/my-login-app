# Secure User Authentication System

![Deployment](https://img.shields.io/badge/Deployment-PythonAnywhere-green)

A full-stack, responsive web application providing a secure foundation for user registration, login, and management. This project is built with Flask and demonstrates best practices for security, a responsive frontend, and deployment.

## 🌐 Live Demo

The application is deployed and live on PythonAnywhere.

**URL:** [https://KobbyFlex.pythonanywhere.com](https://KobbyFlex.pythonanywhere.com)

---

## 📸 Screenshots

Here is a preview of the application's interface.


*Login Page (Light & Dark Mode)*


*Admin Dashboard (Viewing Users)*

---

## 🚀 Core Features

* **Secure Authentication:** Full user lifecycle including sign-up, login, and logout.
* **Advanced Password Hashing:** User passwords are **never** stored in plain text. We use `werkzeug.security`'s `generate_password_hash` (salting + hashing) and `check_password_hash` for verification.
* **Role-Based Access Control:**
    * **User:** Can register, log in, and change their own password.
    * **Admin:** Has all user privileges and can also access a special dashboard to view all registered users in the database.
* **Account Management:** Logged-in users can change their own password after verifying their old one.
* **Responsive UI/UX:** A clean, modern two-column layout that adapts to all screen sizes, from mobile phones to desktops.
* **Light/Dark Mode:** A theme toggle button that saves the user's preference in their browser's `localStorage` for future visits.
* **Session Management:** Uses Flask's secure cookie-based sessions to keep users logged in.

---

## 🛠️ Technology Stack

### Backend
* **Python:** The core programming language.
* **Flask:** A lightweight web framework for handling routing and backend logic.
* **SQLite:** The database used to store user information.
* **Werkzeug:** Used for its powerful and secure password hashing utilities.

### Frontend
* **HTML5:** The structure of all web pages.
* **CSS3 (with CSS Variables):** Used for custom styling and to implement the light/dark mode theme.
* **Bootstrap 5:** A professional framework for responsive layout (the two-column grid) and clean components (forms, buttons, tables).
* **JavaScript:** Powers the light/dark mode toggle and saves the user's preference.

### Deployment
* **Git / GitHub:** For version control.
* **PythonAnywhere:** The hosting platform for the live application.

---

## 🔧 Getting Started (Running Locally)

To run this project on your local machine, follow these steps:

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/KobbyFlex00/my-login-app.git](https://github.com/KobbyFlex00/my-login-app.git)
    cd my-login-app
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    # Create the environment
    python -m venv venv
    
    # Activate on Windows (CMD)
    .\venv\Scripts\activate.bat
    
    # Activate on Mac/Linux (Bash)
    source venv/bin/activate
    ```

3.  **Install the dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Initialize the database:**
    This is a crucial one-time step to create the `users.db` file and the `users1` table.
    ```bash
    # Open the Python shell
    python
    
    # Run these commands inside the shell
    >>> from app import init_db
    >>> init_db()
    >>> exit()
    ```

5.  **Run the application:**
    ```bash
    python app.py
    ```

6.  Open your browser and navigate to `http://127.0.0.1:5000`.

---

## 🔒 Security Practices

* **Password Hashing:** Passwords are never stored directly. They are processed with a **salt and hash** algorithm, making it infeasible to reverse-engineer them.
* **Secret Key:** The Flask app uses a random, hardcoded `secret_key` to sign user sessions, preventing session hijacking.
* **Debug Mode Off:** `debug=False` is set in the `app.py` file, ensuring that no sensitive error information is ever leaked to a public user.
* **`.gitignore`:** The `venv` virtual environment, `.pycache` files, and the local `users.db` are all included in the `.gitignore` file to prevent sensitive data or unnecessary files from being committed to GitHub.
