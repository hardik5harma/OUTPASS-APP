# Hostel Outpass Management System

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-2.3.2-green)](https://flask.palletsprojects.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15%2B-blue)](https://www.postgresql.org/)

A web-based outpass management system for hostels, built with Flask and PostgreSQL. Streamline student movement tracking with digital outpass requests and approvals.

## Features

- **Role-Based Access Control**
  - Student: Request outpasses with time windows
  - Warden: Review and approve/reject requests
  - Guard: Verify approved outpasses
- **Email Notifications**: Automatic status updates
- **Database Management**: SQLAlchemy ORM with PostgreSQL
- **Web Interface**: Simple and intuitive UI with Bootstrap

## Prerequisites

- Python 3.10+
- PostgreSQL 15+
- SMTP Email Service (Gmail recommended)

## Installation
```bash
#Clone Repository

git clone https://github.com/<your-username>/hostel-outpass-system.git
cd hostel-outpass-system

#Set Up Virtual Environment

python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate    # Windows

#Install Dependencies

pip install -r requirements.txt

#Database Setup
sql
CREATE DATABASE outpass_db;
CREATE USER op_user WITH PASSWORD 'op_password';
GRANT ALL PRIVILEGES ON DATABASE outpass_db TO op_user;

#Configuration
Create .env file:

#env
SECRET_KEY=your-secret-key-here
DATABASE_URL=postgresql://op_user:op_password@localhost/outpass_db
EMAIL_USER=your-email@example.com
EMAIL_PASSWORD=your-email-password

#Initialize Database

flask shell
>>> from app import db
>>> db.create_all()
>>> exit()

#Add Test Users

Run in PostgreSQL:
INSERT INTO "user" (username, password, role, email) VALUES
('student1', 'pass123', 'student', 'student@example.com'),
('warden1', 'wardenpass', 'warden', NULL),
('guard1', 'guardpass', 'guard', NULL);

#Start Application

python app.py

