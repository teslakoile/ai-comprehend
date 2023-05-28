# AI Comprehend

AI Comprehend is a web application developed as part of an undergraduate research project at the Ubiquitous Computing Laboratory in the Electrical and Electronics Engineering Institute (EEEI), University of the Philippines Diliman. The project aims to help users improve their comprehension skills using an adaptive learning system. The system provides questions based on the user's performance and learning progress to help them master various knowledge components.

This project is supervised by Dr. Nestor Tiglao, with team members Kyle Nathan Naranjo, Dominic Mondia, and Stephen Galamay.

## Acknowledgements

The group would like to acknowledge the contributions of Dr. Nilda Ginete for her assistance with English and reading comprehension-related matters. Her expertise has been invaluable in the development of the application's reading materials and comprehension tests.

## Features

- User registration and authentication
- Adaptive learning system based on the Performance Factors Analysis (PFA) model
- Real-time user progress tracking
- Admin dashboard for managing users and questions
- Text highlighting and explanations for improved comprehension

## Installation

1. Clone the repository:
git clone https://github.com/your-username/ai-comprehend.git


2. Install the required dependencies:
cd ai-comprehend
pip install -r requirements.txt


3. Set up the database:
python manage.py makemigrations
python manage.py migrate


4. Start the development server:
python manage.py runserver


The application should now be accessible at http://127.0.0.1:8000.

## Usage

1. Register a new user or log in with an existing account.
2. Start the comprehension test and answer questions.
3. Monitor your progress and see real-time feedback.