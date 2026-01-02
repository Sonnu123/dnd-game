from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import google.generativeai as genai
import mysql.connector
import os
from dotenv import load_dotenv
import uuid
import json

load_dotenv()

app = FastAPI()

# Get the directory where app.py is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure Gemini API
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
model = genai.GenerativeModel('gemini-pro')

# System prompt for the AI Game Master
SYSTEM_PROMPT = """You are an expert Dungeons & Dragons Game Master. You create immersive,
engaging narratives and respond to player actions with vivid descriptions and exciting scenarios.

Rules:
- Keep responses concise (2-4 paragraphs max)
- Be dramatic and atmospheric
- Present clear choices or ask what the player does next
- Track combat and challenges fairly
- Make the world feel alive and responsive
- Never break character as the GM"""

# Database connection function - CREATE ON DEMAND
def get_db_connection():
    try:
        return mysql.connector.connect(
            host=os.getenv('MYSQL_HOST'),
            user=os.getenv('MYSQL_USER'),
            password=os.getenv('MYSQL_PASSWORD'),
            database=os.getenv('MYSQL_DATABASE')
        )
    except Exception as e:
        print(f"Database connection error: {e}")
        raise

# Create tables on startup
@app.on_event("startup")
async def startup_event():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Create characters table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS characters (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(50) NOT NULL,
                race VARCHAR(20) NOT NULL,
                class VARCHAR(20) NOT NULL,
                strength INT NOT NULL,
                dexterity INT NOT NULL,
                intelligence INT NOT NULL,
                wisdom INT NOT NULL,
                constitution INT NOT NULL,
                charisma INT NOT NULL,
                weapon VARCHAR(50) NOT NULL,
                armor VARCHAR(50) NOT NULL,
                health INT DEFAULT 100,
                max_health INT DEFAULT 100,
                money INT DEFAULT 50,
                level INT DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create game_sessions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS game_sessions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                session_id VARCHAR(100) UNIQUE NOT NULL,
                character_id INT NOT NULL,
                chat_history TEXT,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (character_id) REFERENCES characters(id) ON DELETE CASCADE
            )
        """)
        
        conn.commit()
        cursor.close()
        conn.close()
        print("Database tables created successfully!")
    except Exception as e:
        print(f"Error creating tables: {e}")

# Pydantic models
class PlayerCount(BaseModel):
    players: int

class CharacterCreate(BaseModel):
    name: str
    race: str
    character_class: str

class SessionCreate(BaseModel):
    character_id: int

class GameAction(BaseModel):
    session_id: str
    prompt: str

# Race and class stats
RACE_STATS = {
    "Dwarf": {"STR": 16, "DEX": 12, "CON": 18, "INT": 10, "WIS": 14, "CHA": 8, "weapon": "Warhammer", "armor": "Steel Plate"},
    "Elf": {"STR": 10, "DEX": 18, "CON": 12, "INT": 16, "WIS": 14, "CHA": 12, "weapon": "Longbow", "armor": "Leather Armor"},
    "Human": {"STR": 14, "DEX": 14, "CON": 14, "INT": 14, "WIS": 12, "CHA": 16, "weapon": "Sword", "armor": "Chainmail"},
    "Dragonborn": {"STR": 18, "DEX": 14, "CON": 16, "INT": 10, "WIS": 12, "CHA": 14, "weapon": "Greatsword", "armor": "Dragonhide"},
    "Gnome": {"STR": 8, "DEX": 16, "CON": 12, "INT": 18, "WIS": 14, "CHA": 10, "weapon": "Dagger", "armor": "Robes"},
    "Half-Orc": {"STR": 18, "DEX": 12, "CON": 16, "INT": 8, "WIS": 10, "CHA": 10, "weapon": "Axe", "armor": "Hide Armor"}
}

CLASS_BONUSES = {
    "Knight": "STR",
    "Mage": "INT",
    "Archer": "DEX",
    "Tank": "CON",
    "Charmer": "CHA",
    "Monk": "WIS"
}

# HTML page routes - WITH ABSOLUTE PATHS
@app.get("/")
async def read_root():
    return FileResponse(os.path.join(BASE_DIR, "start.html"))

@app.get("/race")
async def race():
    return FileResponse(os.path.join(BASE_DIR, "Race.html"))

@app.get("/class")
async def class_selection():
    return FileResponse(os.path.join(BASE_DIR, "class.html"))

@app.get("/game")
async def game():
    return FileResponse(os.path.join(BASE_DIR, "game.html"))

# API endpoints
@app.post("/save_players")
async def save_players(player_count: PlayerCount):
    return {"success": True, "players": player_count.players}

@app.post("/create_character")
async def create_character(character: CharacterCreate):
    try:
        # Get base stats for race
        if character.race not in RACE_STATS:
            raise HTTPException(status_code=400, detail="Invalid race")
        
        base_stats = RACE_STATS[character.race].copy()
        weapon = base_stats.pop("weapon")
        armor = base_stats.pop("armor")
        
        # Apply class bonus
        if character.character_class not in CLASS_BONUSES:
            raise HTTPException(status_code=400, detail="Invalid class")
        
        bonus_stat = CLASS_BONUSES[character.character_class]
        base_stats[bonus_stat] += 5
        
        # Calculate health
        max_health = 100 + (base_stats["CON"] - 10) * 5
        
        # Save to database
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO characters (name, race, class, strength, dexterity, intelligence,
                                   wisdom, constitution, charisma, weapon, armor, health, max_health)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            character.name, character.race, character.character_class,
            base_stats["STR"], base_stats["DEX"], base_stats["INT"],
            base_stats["WIS"], base_stats["CON"], base_stats["CHA"],
            weapon, armor, max_health, max_health
        ))
        
        conn.commit()
        character_id = cursor.lastrowid
        
        cursor.close()
        conn.close()
        
        return {
            "success": True,
            "character_id": character_id,
            "stats": base_stats,
            "max_health": max_health,
            "weapon": weapon,
            "armor": armor
        }
    
    except mysql.connector.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/create_session")
async def create_session(session_data: SessionCreate):
    try:
        # Get character details
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("SELECT * FROM characters WHERE id = %s", (session_data.character_id,))
        character = cursor.fetchone()
        
        if not character:
            cursor.close()
            conn.close()
            raise HTTPException(status_code=404, detail="Character not found")
        
        # Create session
        session_id = str(uuid.uuid4())
        
        # Generate initial message from AI
        initial_prompt = f"""Start a D&D adventure for {character['name']}, a {character['race']} {character['class']}.
        Their weapon is {character['weapon']} and they wear {character['armor']}.
        Begin the adventure with an engaging scene. Keep it to 2-3 paragraphs."""
        
        response = model.generate_content(initial_prompt)
        initial_message = response.text
        
        # Create chat history
        chat_history = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "assistant", "content": initial_message}
        ]
        
        # Save session to database
        cursor.execute("""
            INSERT INTO game_sessions (session_id, character_id, chat_history)
            VALUES (%s, %s, %s)
        """, (session_id, session_data.character_id, json.dumps(chat_history)))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return {
            "success": True,
            "session_id": session_id,
            "character": character,
            "initial_message": initial_message
        }
    
    except mysql.connector.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/game_action")
async def game_action(action: GameAction):
    try:
        # Get session from database
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("SELECT * FROM game_sessions WHERE session_id = %s", (action.session_id,))
        session = cursor.fetchone()
        
        if not session:
            cursor.close()
            conn.close()
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Load chat history
        chat_history = json.loads(session['chat_history'])
        
        # Add user message
        chat_history.append({"role": "user", "content": action.prompt})
        
        # Generate AI response
        conversation_text = "\n".join([f"{msg['role']}: {msg['content']}" for msg in chat_history])
        response = model.generate_content(conversation_text + f"\nuser: {action.prompt}\nRespond as the Game Master:")
        ai_response = response.text
        
        # Add AI response to history
        chat_history.append({"role": "assistant", "content": ai_response})
        
        # Update session in database
        cursor.execute("""
            UPDATE game_sessions
            SET chat_history = %s, last_updated = CURRENT_TIMESTAMP
            WHERE session_id = %s
        """, (json.dumps(chat_history), action.session_id))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return {
            "success": True,
            "response": ai_response
        }
    
    except mysql.connector.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/character/{character_id}")
async def get_character(character_id: int):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("SELECT * FROM characters WHERE id = %s", (character_id,))
        character = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        if not character:
            raise HTTPException(status_code=404, detail="Character not found")
        
        return character
    
    except mysql.connector.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
