# Cinema Stream

A Netflix-inspired movie & TV series streaming platform built with Django

Watch, rate, review, and save your favorite movies & series – all in one beautiful, responsive, and lightning-fast web app!

![Django](https://img.shields.io/badge/Django-5.0+-092E20?style=for-the-badge&logo=django&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=yellow)
![Bootstrap 5](https://img.shields.io/badge/Bootstrap-5-7952B3?style=for-the-badge&logo=bootstrap&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Ready-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-blue.svg?style=for-the-badge)

> "Where Stories Come to Life"

![Cinema Stream Preview](https://via.placeholder.com/1200x600/111/eee?text=Cinema+Stream+Preview)  
*(Replace with your actual screenshot)*


## Features

| Feature                            | Status       | Emoji |
|------------------------------------|--------------|-------|
| User Registration & Login          | Completed     | Done |
| Combined Login/Register Tabs       | Completed     | Done |
| User Profile + Avatar & Bio        | Completed     | Done |
| Favorites / Watchlist (AJAX)       | Completed     | Done |
| Movie & Series Detail Pages        | Completed     | Done |
| Star Rating + Reviews System       | Completed     | Done |
| Edit/Delete Own Reviews            | Completed     | Done |
| Real-time Search & Filters (AJAX)  | Completed     | Done |
| Responsive Design (Mobile-First)   | Completed     | Done |
| Trailer Modal (YouTube/Vimeo)      | In Progress   | Building |
| Password Reset via Email           | In Progress   | Building |
| Advanced Admin Statistics          | Planned       | Planning |

---

## Tech Stack

### Backend
- Django 5.0+– Full-featured Python web framework
- Django REST Framework – For AJAX endpoints
- PostgreSQL / SQLite** – Production-ready database
- Pillow – Image processing (avatars, posters)

### Frontend
- Bootstrap 5 – Responsive, sleek UI
- JavaScript + AJAX** – Smooth interactions
- Font Awesome – Beautiful icons
- Django Templates– Server-side rendering

### Deployment Ready
- WhiteNoise – Serve static files in production
- Gunicorn + Django – Production server
- Ready for AWS, Heroku, Render, Railway, or DigitalOcean

---

## Project Structure
cinema_stream/
├── accounts/          # Authentication & profiles
├── movies/            # Movie models, views, templates
├── series/            # TV series management
├── reviews/           # Rating & review system
├── static/
│   ├── css/           # Custom styles
│   ├── js/            # AJAX & interactions
│   └── images/
├── templates/         # Base + all pages
└── media/             # User avatars & uploads
text---

## Key Pages

- Home – Hero banner, trending, genre rows
- Browse – Movies & series with live filters
- Movie / Series Detail – Trailer, cast, reviews, favorite button
- Profile*– Favorites, reviews, edit profile
- Login / Register – Beautiful tabbed interface

---

## Security

- CSRF protection on all forms
- Secure password hashing (PBKDF2)
- Input validation & sanitization
- Login required for reviews & favorites
- Only owners can edit/delete their reviews

---

## Future Roadmap

- Trailer modal with YouTube embed
- Watch history & "Continue Watching"
- Personalized recommendations
- Actor / Director dedicated pages
- Dark/Light mode toggle
- Mobile app (Flutter)
- Multi-language support (i18n)
- Premium subscription features

---

## Screenshots

Home
Movie Detail
Profile

## Installation (Local Development)

```bash
git clone https://github.com/yourusername/cinema-stream.git
cd cinema-stream
python -m venv venv
source venv/bin/activate    # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
Then visit: http://127.0.0.1:8000

Contributing
Contributions are welcome! Feel free to:

Open issues
Submit pull requests
Suggest new features
Improve UI/UX


License
This project is licensed under the MIT License – see the LICENSE file for details.

Cinema Stream – Watch Like Never Before