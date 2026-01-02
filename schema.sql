-- Medieval Adventures Database Schema

-- Characters table (stores player characters)
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Game sessions table (stores ongoing games)
CREATE TABLE IF NOT EXISTS game_sessions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    session_id VARCHAR(100) UNIQUE NOT NULL,
    character_id INT NOT NULL,
    chat_history TEXT,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (character_id) REFERENCES characters(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
