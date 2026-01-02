# Medieval Adventures

AI-powered Dungeons & Dragons game with character creation and immersive gameplay.

## Quick Start
```bash
git clone https://github.com/Sonnu123/dnd-game.git
cd dnd-game
pip install -r requirements.txt
python app.py
```

Visit http://localhost:8000 to play!

## Features

- AI Game Master 
- 6 races: Dwarf, Elf, Human, Dragonborn, Gnome, Half-Orc
- 6 classes: Knight, Mage, Archer, Tank, Charmer, Monk
- MySQL database for character persistence
- Medieval-themed interface

## Setup

Create `.env` file:
```
GEMINI_API_KEY=your_api_key_here
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=dandd
```

Get free API key at: https://makersuite.google.com/app/apikey

## Deploy to Railway

1. Go to https://railway.app
2. Connect GitHub repo
3. Add MySQL database
4. Set environment variables
5. Deploy!

## Tech Stack

- Backend: FastAPI + Python
- AI API
- Database: MySQL

## License

MIT License
