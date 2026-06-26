Hospital Management System

A full-stack database-driven web application developed using Flask and MySQL to streamline hospital operations, including patient records, doctor management, appointments, departments, and medical records through an intuitive web interface.

Features

* Secure CRUD operations for Patients, Doctors, Departments, Appointments, and Medical Records
* Relational database design with normalized MySQL schema
* Appointment scheduling and management
* Doctor-to-department mapping
* Medical history and diagnosis management
* Data validation and referential integrity using foreign key constraints
* Responsive web interface built with HTML and CSS

Tech Stack

* Python (Flask)
* MySQL
* HTML
* CSS

Database Design

The system follows a normalized relational schema consisting of:

* Department
* Doctor
* Patient
* Appointment
* Medical Record

Relationships are maintained using primary and foreign key constraints to ensure data consistency and integrity.

Project Structure

hospital-management-system/
├── app.py
├── templates/
├── static/
│   └── css/
├── hospital_db.sql
└── README.md

Installation

1. Clone the repository

git clone https://github.com/anandanshu07/dbms-project.git

2. Navigate to the project directory

cd dbms-project

3. Install the required dependencies

pip install -r requirements.txt

4. Configure MySQL credentials in app.py.
5. Import the SQL database.
6. Run the application

python app.py

Learning Outcomes

* Relational database design and normalization
* SQL query optimization
* CRUD application development using Flask
* Backend integration with MySQL
* Database constraint management
* Full-stack web application development

Author

Anshu Anand
