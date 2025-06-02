project:
  name: CampusJobs – On-Campus Job Posting Platform
  description: |
    CampusJobs is a web application designed to connect students seeking part-time or full-time jobs within the university campus with local businesses and employers. Students can easily find jobs that fit their class schedules, while employers can post job openings to reach dynamic and talented METU students for their staffing needs.
    This project was developed for the CEIT390 course, using Flask (a Python web framework) and a PostgreSQL database.
  technologies:
    backend: Python (Flask)
    database: PostgreSQL
    frontend: HTML, CSS
    libraries:
      - psycopg2-binary (PostgreSQL connectivity)
      - Werkzeug (password hashing / security)

installation_and_run:
  prerequisites:
    - Python 3.7+ (https://www.python.org/downloads/)
    - PostgreSQL (https://www.enterprisedb.com/downloads/postgres-postgresql-downloads)
    - pgAdmin (included with PostgreSQL installer)
  files_needed:
    - campusjobs.py
    - table_creation.txt
    - sample_data.txt
  steps:
    - step: Extract the campusjobs.zip file to your desired location.
    - step: Install required Python libraries
      code: |
        pip install Flask psycopg2-binary Werkzeug
    - step: Open pgAdmin and create a new database (e.g., campusjobs).
    - step: In the new database, open Query Tool.
    - step: Copy all SQL code from table_creation.txt and execute in Query Tool to create tables.
    - step: (Optional) Copy and execute all code from sample_data.txt to insert sample data.
    - step: Update DB connection settings in campusjobs.py
      details: |
        DB_HOST = "localhost"
        DB_NAME = "campusjobs"
        DB_USER = "postgres"
        DB_PASS = "your_password"
    - step: Run the application
      code: |
        python campusjobs.py
    - step: Open browser at http://127.0.0.1:5000/

usage:
  homepage: General info, login/register buttons
  students:
    - Register with school email ending with .edu.tr
    - View, filter, and favorite job postings
    - Apply to jobs via email
  employers:
    - Register with any email
    - Add, update, and remove job postings
  password_policy: Passwords must be at least 8 characters, with uppercase, lowercase, and numbers

notes:
  - Project is for educational purposes; some security features are not included.
  - Passwords are hashed using werkzeug.security.
  - Database schema follows CEIT390 requirements.
