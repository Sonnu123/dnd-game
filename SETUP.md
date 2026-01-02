# Setup Guide for Medieval Adventures

This guide will help you get the game running on your local machine or deploy it to a server.

## Prerequisites

1. Python 3.8 or higher
2. MySQL 8.0 or higher
3. Gemini API key (already configured in your .env file)

## Step-by-Step Setup

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up MySQL Database

Start your MySQL server, then create the database and tables:

```bash
# Login to MySQL
mysql -u root -p

# In MySQL prompt:
CREATE DATABASE dandd;
exit;

# Run the schema file
mysql -u root -p dandd < schema.sql
```

Alternatively, you can run the schema manually in MySQL Workbench or phpMyAdmin.

### 3. Configure Environment Variables

Your `.env` file is already set up with:
- Your Gemini API key
- MySQL connection details (localhost, root, password: ayush, database: dandd)

**IMPORTANT SECURITY NOTE:** 
- Never commit the `.env` file to GitHub
- The `.gitignore` file is already configured to exclude it
- If you share this code, use `.env.example` as a template

### 4. Add Your Image Files

Make sure these image files are in the same directory as your HTML files:
- Dwarf.png
- Elf.png
- Human.png
- DragonBorn.png
- Gnome.png
- HalfOrc.png
- knight.jpg
- mage.jpg
- archer.jpg
- tank.jpg
- charmer.jpg
- monk.jpg

### 5. Run the Application

```bash
python app.py
```

Or using uvicorn directly:

```bash
uvicorn app:app --reload
```

The application will start on http://localhost:8000

### 6. Test the Application

1. Open your browser and go to http://localhost:8000
2. Click "New Game"
3. Select number of players
4. Choose a race
5. Choose a class
6. Name your character
7. Start your adventure!

## Project Structure

```
medieval-adventures/
├── app.py              # Main FastAPI application
├── start.html          # Main menu
├── Race.html           # Race selection
├── class.html          # Class selection with character creation
├── game.html           # Game interface
├── schema.sql          # Database schema
├── requirements.txt    # Python dependencies
├── .env               # Environment variables (DO NOT COMMIT)
├── .env.example       # Template for environment variables
├── .gitignore         # Git ignore file
└── README.md          # Project documentation
```

## How It Works

### Flow
1. **Start Screen** → Select number of players
2. **Race Selection** → Choose character race (affects base stats)
3. **Class Selection** → Choose character class (adds +5 to specific stat)
4. **Character Creation** → Name your character, saves to database
5. **Game Session** → Session created, initial adventure begins
6. **Gameplay** → Interact with AI Game Master via text

### Database Tables

**characters**
- Stores all character data (name, race, class, stats, equipment)
- Each character gets unique ID

**game_sessions**
- Stores active game sessions
- Links to character_id
- Saves chat history as JSON
- Tracks when session was last updated

### API Endpoints

- `GET /` - Main menu
- `GET /race` - Race selection page
- `GET /class` - Class selection page
- `GET /game` - Game interface
- `POST /save_players` - Save player count
- `POST /create_character` - Create new character in database
- `POST /create_session` - Create new game session
- `POST /game_action` - Send player action to AI
- `GET /character/{id}` - Get character details

## Troubleshooting

### Database Connection Issues

If you get a database connection error:
1. Make sure MySQL is running
2. Verify your password in `.env` matches your MySQL root password
3. Ensure the `dandd` database exists
4. Check that the schema tables are created

```bash
# Check if MySQL is running
sudo systemctl status mysql  # Linux
# or
brew services list | grep mysql  # macOS

# Test connection
mysql -u root -p -e "SHOW DATABASES;"
```

### Gemini API Issues

If the AI isn't responding:
1. Check that your API key is correct in `.env`
2. Verify you have API quota remaining
3. Check the console for error messages

### Port Already in Use

If port 8000 is already in use:
```bash
# Use a different port
uvicorn app:app --port 8080
```

### Images Not Loading

Make sure all image files are in the same directory as the HTML files. If images are in a subdirectory:
1. Create a `static` folder
2. Move images there
3. Update image paths in HTML files to `static/Dwarf.png` etc.

## Deployment Options

### Option 1: Railway.app (Recommended)
1. Create account on railway.app
2. Add MySQL plugin
3. Update .env with Railway database credentials
4. Deploy from GitHub

### Option 2: Heroku
1. Add ClearDB MySQL add-on
2. Update .env with Heroku database credentials
3. Create Procfile: `web: uvicorn app:app --host 0.0.0.0 --port $PORT`

### Option 3: DigitalOcean
1. Create a Droplet
2. Install MySQL
3. Clone repository
4. Set up systemd service
5. Configure nginx as reverse proxy

## Next Steps

Want to enhance the game? Here are some ideas:
- Add inventory system
- Implement combat mechanics with dice rolls
- Create multiple save slots
- Add multiplayer turn-based gameplay
- Implement character leveling
- Add more races and classes
- Create a dungeon map system

## Support

If you run into issues:
1. Check the console output for error messages
2. Verify all environment variables are set
3. Ensure database is properly configured
4. Check that all image files are present

Good luck on your adventures!
