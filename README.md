# Backoffice Reconciliation Hub 📊

A robust, full-stack financial tool designed to automate the reconciliation of Bank Statements against internal General Ledgers. Built with Django, PostgreSQL, and Pandas, this application replaces error-prone manual spreadsheet workflows with an intelligent, automated pipeline.
## Deployed Link:https://backoffice-reconciliation-hub-1.onrender.com

## 🚀 Features

### 1. Project Management Architecture

Multi-User Support: Secure Login/Signup system ensures users only see their own data.

Workspace Isolation: Create distinct projects (e.g., "Dec 2025 Audit", "Q1 Review") to keep financial data organized and separate.

### 2. Intelligent Data Ingestion

File Support: Accepts both .csv and .xlsx (Excel) formats.

Pandas Integration: Uses the Pandas library to clean, normalize, and bulk-insert thousands of transaction rows into the database instantly.

### 3. Reconciliation Engine

Auto-Match Algorithm: Automatically pairs matching transactions between the Bank and Ledger based on amounts and dates.

Status Tracking: Distinguishes between "Auto Reconciled" (system matched) and "Manually Reconciled" (human matched).

### 4. Interactive Dashboard

Two-Column View: Side-by-side comparison of "Bank Breaks" vs "Ledger Breaks".

Manual Matching: Select unmatched items from both sides using checkboxes. The system validates that the Difference is 0.00 before allowing a match.

Live Math: JavaScript-powered calculation updates the selected totals in real-time.

### 5. Reporting & Audit

Excel Export: Generates a professional .xlsx report containing a "Master Register" of all transactions with their status and a "Summary Pivot" table.

Audit Trail: Keeps a history of who matched what and when.

## 🛠️ Tech Stack

Backend: Python 3.12, Django 5.0

Database: PostgreSQL

Data Processing: Pandas, OpenPyXL

Frontend: Bootstrap 5 (Responsive UI), JavaScript

Environment Management: python-dotenv

## ⚙️ Installation & Setup

Follow these steps to run the project locally.

### 1. Clone the Repository

git clone [https://github.com/ShivamxAI/Backoffice-Reconciliation-Hub.git]
cd Backoffice-Reconciliation-Hub


### 2. Create Virtual Environment

### Windows
python -m venv venv
#### Now activate virtual envvironment:
venv\Scripts\activate

### Mac/Linux
python3 -m venv venv
#### Now activate virtual envvironment:
source venv/bin/activate


### 3. Install Dependencies

pip install -r requirements.txt


(Note: If requirements.txt is missing, install the core packages manually):

pip install django pandas psycopg2-binary openpyxl python-dotenv


### 4. Configure Environment Variables

Create a file named .env in the root directory (next to manage.py) and add your database credentials:

SECRET_KEY=your-secret-key-here
DEBUG=True
DB_NAME=reconciliation_db
DB_USER=postgres
DB_PASSWORD=your_db_password


### 5. Setup Database

Make sure PostgreSQL is running and you have created a database named reconciliation_db. Then run:

python manage.py makemigrations
python manage.py migrate


### 6. Run the Server

python manage.py runserver


Visit http://127.0.0.1:8000/ in your browser.

## 📖 Usage Guide

Sign Up/Login: Create a secure account.

Create Project: Click "+ Create New Project" and give it a name (e.g., "January Audit").

Upload Files: Upload your Bank Statement and Internal Ledger.

Auto-Reconcile: Click the "Run Auto-Reconciliation" button to clear obvious matches.

Manual Review:

Select unmatched items from the Left (Bank) and Right (Ledger) tables.

Ensure the difference bar at the bottom turns Green (0.00).

Click "Match Selected".

Export: Download the final result as an Excel file for reporting.

## 📂 Project Structure

<img width="903" height="358" alt="image" src="https://github.com/user-attachments/assets/3c6e4056-6491-4053-af64-31b52156f602" />



## 🛡️ Security

CSRF Protection: All forms are protected against Cross-Site Request Forgery.

Authentication: Pages are protected with @login_required decorators.

Data Isolation: Queries are scoped to request.user to prevent data leakage between users.

