# CampusJobs – On-Campus Job Posting Platform

## Project Description

CampusJobs is a web application designed to connect students seeking part-time or full-time jobs within the university campus with local businesses and employers. Students can easily find jobs that fit their class schedules, while employers can post job openings to reach dynamic and talented METU students for their staffing needs.

This project was developed for the CEIT390 course, using Flask (a Python web framework) and a PostgreSQL database.

## Technologies Used

- **Backend:** Python (Flask)
- **Database:** PostgreSQL
- **Frontend:** HTML, CSS

**Additional Libraries:**
- `psycopg2-binary`: For PostgreSQL connectivity.
- `Werkzeug`: For password hashing (security).

---

## Installation and Running Instructions

This section outlines the steps to set up and run the project locally.

### 1. Prerequisites

- **Python 3.7+**: Ensure Python is installed on your machine. [Download Python](https://www.python.org/downloads/)
- **PostgreSQL**: Make sure the PostgreSQL database server is installed and running. [Download PostgreSQL](https://www.enterprisedb.com/downloads/postgres-postgresql-downloads)
    - During installation, you will be asked to set a username (e.g., `postgres`) and password. You will need these later.
    - If you get error in the installation part, change your systems regional form to United States at windows>system>time and language>regional form
- **pgAdmin**: A database management tool like pgAdmin is recommended for easier database management. You should get this when you download and install PostgreSQL.

### 2. Obtain Project Files

- extract campusjobs-main.zip to a folder that you want.

You will need the following files to run the project:
- `campusjobs.py` &nbsp;&nbsp;&nbsp;*(Python code for the Flask app)*
- `table_creation.txt` &nbsp;&nbsp;&nbsp;*(SQL table definitions)*
- `sample_data.txt` &nbsp;&nbsp;&nbsp;*(Optional: sample records for testing)*

#### **Select the Python Interpreter in VSCode**

> If you are using Visual Studio Code (VSCode), you need to select the correct Python interpreter before running the project.

1. Open `campusjobs.py` in VSCode.
2. Press <kbd>Ctrl</kbd> + <kbd>Shift</kbd> + <kbd>P</kbd> to open the command palette.
3. Type **Python: Select Interpreter** and select it from the list.
4. Choose the Python version you installed (e.g., Python 3.11.x).
5. Now you can run your code with the correct interpreter.

This ensures that VSCode uses the right Python environment when you run the project.

### 3. Install Required Python Libraries

Open a terminal (Command Prompt or PowerShell) and run:
```bash
python -m pip install Flask psycopg2-binary Werkzeug
```

### 4. Set Up the Database

#### 4.1 Open pgAdmin
- Launch pgAdmin on your computer.

#### 4.2 Create a New Database
- Right-click on **Databases** in the left panel.
- Select **Create > Database...**
- Enter a name (e.g., `campusjobs`) and click **Save**.

#### 4.3 Create the Tables
- Select your new database from the left panel.
- Click on **Tools > Query Tool**.
- Open the project folder on your computer and find the file named `table_creation.txt`.
- Copy all the SQL code from `table_creation.txt`.
- Paste the copied code into the Query Tool in pgAdmin.
- Click the **Execute** button to create the tables.

#### 4.4 Insert Sample Data
- Open `sample_data.txt` from the project folder.
- Copy all its content.
- Paste into the Query Tool and execute again to insert sample records.

## IMPORTANT
- Be sure to paste and execute the codes to the correct database, otherwise you might not connect the database at the next step.


### 5. Update Database Connection Settings
Open campusjobs.py in a text editor (VSCode). At the top of the file, update the database connection details according to your PostgreSQL setup:

DB_HOST = "localhost"   # Address of your PostgreSQL server, usually "localhost" or "127.0.0.1"
DB_NAME = "campusjobs"  # Name of the database where you loaded the SQL file
DB_USER = "postgres"    # Your PostgreSQL username
DB_PASS = "1234"        # Password for the above user

IMPORTANT:
DB_HOST: Remains localhost unless your database is on another server.

DB_NAME: Use the name of the database where you imported campusjobs.sql.

DB_USER: Your PostgreSQL user (set during installation).

DB_PASS: Password for the above user.

If these settings are incorrect, the application will not be able to connect to the database.

### 6. Running the Application
In the terminal, navigate to the folder containing campusjobs.py and run:

python campusjobs.py

Or open campusjobs.py in VSCode and run the code.

You should see output like:

 * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
 * Restarting with stat
 * Debugger is active!
 * Debugger PIN: xxx-xxx-xxx

Open a web browser and go to http://127.0.0.1:5000/. The CampusJobs application should appear.

### Usage
Homepage: General information and login/register buttons.

Account Creation:

Students can register using their school email address ending with .edu.tr.

Employers can register with any email address.

Passwords must be at least 8 characters long and include uppercase, lowercase letters, and numbers.

Login: Users log in with their registered email and password.

Student Interface:
View Listings: Filter and sort all active job postings.

Favorites: Add job postings to favorites for easy tracking.

Apply: Use the "Apply via Email" button in job details to contact the employer's email address.

Employer Interface:
Add Job Posting: Create new job listings.

My Listings: View, remove and update job postings they have created.

### Notes
This project was developed for educational purposes. Some advanced security features (e.g., extensive XSS protection, CSRF tokens) and complex features (such as email verification and password reset) are not included.

Passwords are securely hashed in the database using the werkzeug.security library.

The database schema and relationships were designed according to CEIT390 course requirements.

Happy testing!
