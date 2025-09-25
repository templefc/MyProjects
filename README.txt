Flask Web Application Project

Overview
This project is a mobile-friendly web application built using Python and Flask. It includes user authentication, dynamic database interactions, and additional personal features. The project demonstrates the use of Flask to create a responsive, database-driven web application suitable for various use cases.

Features
User Authentication:

Users can sign up with a unique email and password.
Passwords are securely hashed using werkzeug.security.
Users can log in and out of their accounts.
User Profiles:

Each user has a profile that includes their username, email, and posts.
Logged-in users can view their data and interact with their content.

Contact Form:

A form for users to submit inquiries or feedback.
Includes validation for email addresses and required fields.
Stores messages in the database.

Trip Planner:

Allows users to plan trips with fields for location, date, budget, and duration.
Calculates and displays the total cost based on user inputs.
Saves trip plans in the database.

Product Reviews:

Enables users to submit reviews and ratings for products.
Validates the rating to be between 1 and 5.
Displays all reviews dynamically.

Post Creation:

Users can create posts with a title and message.
Posts are linked to the user and stored in the database.

Responsive Design:

Designed to adapt to various screen sizes.
Uses a consistent layout for all pages.

Setup Instructions
Clone the repository or extract the project files.
Navigate to the project directory and create a virtual environment:
python -m venv venv
Activate the virtual environment:
On Windows:
venv\Scripts\activate
On macOS/Linux:
source venv/bin/activate
Install the required dependencies:
pip install -r requirements.txt
Apply database migrations:
flask db upgrade
Run the Flask application:
flask run


Testing the Application
Open a browser and navigate to http://127.0.0.1:5000.
Test functionalities including user sign-up, login, contact form, trip planner, product reviews, and post creation.