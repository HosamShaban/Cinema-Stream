# Cinema Stream

Cinema Stream is a online movie and TV series streaming web application built with Django that allows users to register, browse, search, save favorites, write reviews, and manage their profile. The platform provides a modern, responsive, Netflix-inspired experience while remaining lightweight and secure. The application demonstrates core Django concepts (authentication, models, class-based views, forms, admin customization, REST API, AJAX, security, and deployment) in a real-world context.
Watch, rate, review, and save your favorite movies & series – all in one beautiful, responsive, and lightning-fast web app!

![Django](https://img.shields.io/badge/Django-5.0+-092E20?style=for-the-badge&logo=django&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=yellow)
![Bootstrap 5](https://img.shields.io/badge/Bootstrap-5-7952B3?style=for-the-badge&logo=bootstrap&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/SQL-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-blue.svg?style=for-the-badge)


<img width="1440" height="723" alt="Screenshot 2025-11-27 at 4 01 30 PM" src="https://github.com/user-attachments/assets/2048b5d0-9a75-42e5-924e-31cca0e87263" />



Live Site: https://cinema-stream-web.fly.dev  
Data provided by [The Movie Database (TMDB)](https://www.themoviedb.org)  
This product uses the TMDB API but is not endorsed or certified by TMDB.

Integrated The Movie Database (TMDB) public API – which is free, legal, and officially allows developers to use it in non-commercial projects with proper attribution.I never scraped any website (which is illegal), and I respected TMDB's rate limits and terms of use.
All API calls go through a dedicated service module with error handling and timeout.
For production or if the app goes public, we can easily switch to cached data, paid API tier, or self-hosted content – the architecture supports both.


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
