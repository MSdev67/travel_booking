# Travel Booking Application

A Django-based web application for booking travel options (flights, trains, buses).

## Features

- User registration, login, and profile management
- Browse available travel options with filtering
- Book travel options with seat selection
- View and manage bookings
- Cancel bookings

## Setup Instructions

1. Clone the repository
2. Create a virtual environment: `python3 -m venv venv`
3. Activate the virtual environment: `source venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Configure MySQL database in settings.py
6. Run migrations: `python manage.py migrate`
7. Create superuser: `python manage.py createsuperuser`
8. Run development server: `python manage.py runserver`

## Deployment

The application can be deployed to PythonAnywhere or AWS following their respective Django deployment guides.# travel_booking
