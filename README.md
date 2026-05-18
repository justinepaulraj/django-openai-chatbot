# Django OpenAI Chatbot

An AI chatbot built with Django and OpenAI where you can have text conversations or upload a document and ask questions about it.

## Features

- **User Authentication:** secure sign-up, login, and logout functionality
- **Chat History Sidebar:** user-specific conversation history displayed in a sidebar; users can start a new one, delete old ones, or pick up where you left off
- **Conversational Memory:** the chatbot keeps track of your previous messages so you can have natural, flowing conversations
- **Flexible Input Modes:** three interaction modes supported
  - **Text only:** type a message and chat normally
  - **Text + Document:** send a message along with a document for context-aware responses
  - **Document only:** upload a document and let the AI summarize or answer questions about it
- **OpenAI API Integration:** powered by GPT-3.5 Turbo for intelligent responses

## Built With

![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=fff)
![Django](https://img.shields.io/badge/Django-%23092E20.svg?logo=django&logoColor=white)
![OpenAI](https://custom-icon-badges.demolab.com/badge/OpenAI-black?logo=openai&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-%2307405e.svg?logo=sqlite&logoColor=white)
![LangChain](https://img.shields.io/badge/LangChain-1c3c3c.svg?logo=langchain&logoColor=white)
![ChromaDB](https://custom-icon-badges.demolab.com/badge/ChromaDB-white.svg?logoColor=bg-light&logo=chroma-svg-logo)
![PyPDF](https://img.shields.io/badge/PyPDF-3776AB?logo=python&logoColor=fff)
![Bootstrap](https://img.shields.io/badge/Bootstrap-7952B3?logo=bootstrap&logoColor=fff)
![HTMX](https://img.shields.io/badge/HTMX-36C?logo=htmx&logoColor=fff)

## Getting Started

### Prerequisites

- Python 3.12+
- Git
- An OpenAI API key — get one at [platform.openai.com](https://platform.openai.com)

### Installation

1. Clone the repository
  ```bash
  git clone https://github.com/justinepaulraj/django-openai-chatbot.git
  cd django-openai-chatbot
  ```

2. Create and activate a virtual environment
  ```bash
  python -m venv .venv
  # Windows
  .venv\Scripts\activate
  # Mac/Linux
  source .venv/bin/activate
  ```

3. Install dependencies
  ```bash
  pip install -r requirements.txt
  ```

### Environment Variables

Create a `.env` file at the project root and add:

```env
OPENAI_API_KEY=your-openai-api-key
SECRET_KEY=your-django-secret-key
```

### Run

```bash
python manage.py migrate
python manage.py runserver
```

Visit `http://127.0.0.1:8000`

## Project Structure

```
django-openai-chatbot/
├── chatbot/                         # Main application
│   ├── templates/
│   │   └── chatbot/
│   │       ├── base.html            # Base template
│   │       ├── login.html           # Login page
│   │       ├── signup.html          # Signup page
│   │       ├── chat.html            # Main chat interface
│   │       └── chat_partial.html    # Sidebar partial
│   ├── admin.py                     # Admin configuration
│   ├── apps.py                      # App configuration
│   ├── forms.py                     # Django forms
│   ├── models.py                    # Database models
│   ├── tests.py                     # Unit tests
│   ├── urls.py                      # App URL configuration
│   └── views.py                     # View logic
├── config/                          # Django project configuration
│   ├── settings.py                  # Project settings
│   ├── urls.py                      # Root URL configuration
│   ├── wsgi.py                      # WSGI entry point
│   └── asgi.py                      # ASGI entry point
├── .env                             # Environment variables (not tracked)
├── .gitignore
├── manage.py                        # Django management script
├── README.md
└── requirements.txt                 # Python dependencies
```

## Contact

**Justine Paulraj**
- Email: [justine.paulraj@outlook.com](mailto:justine.paulraj@outlook.com)
- LinkedIn: [linkedin.com/in/justinepaulraj](https://linkedin.com/in/justinepaulraj)