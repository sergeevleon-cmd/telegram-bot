import sqlite3
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class Database:
    def __init__(self, db_path="recipes.db"):
        self.db_path = db_path
        self.init_db()
    
    def get_connection(self):
        """Создает подключение к базе данных"""
        return sqlite3.connect(self.db_path)
    
    def init_db(self):
        """Инициализирует базу данных"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS favorites (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    meal_id TEXT NOT NULL,
                    meal_name TEXT,
                    meal_thumb TEXT,
                    rating INTEGER DEFAULT 0,
                    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(user_id, meal_id)
                )
            """)
            
            cursor.execute("""
                SELECT COUNT(*) FROM pragma_table_info('favorites') 
                WHERE name='rating'
            """)
            
            if cursor.fetchone()[0] == 0:
                cursor.execute("""
                    ALTER TABLE favorites ADD COLUMN rating INTEGER DEFAULT 0
                """)
                logger.info("Added rating column to existing table")
            
            conn.commit()
            conn.close()
            logger.info("Database initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            raise
    
    def add_favorite(self, user_id, meal_id, meal_name, meal_thumb):
        """Добавляет рецепт в избранное"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR IGNORE INTO favorites (user_id, meal_id, meal_name, meal_thumb)
                VALUES (?, ?, ?, ?)
            """, (user_id, meal_id, meal_name, meal_thumb))
            
            conn.commit()
            affected = cursor.rowcount
            conn.close()
            
            return affected > 0
        except Exception as e:
            logger.error(f"Error adding favorite: {e}")
            return False
    
    def remove_favorite(self, user_id, meal_id):
        """Удаляет рецепт из избранного"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                DELETE FROM favorites
                WHERE user_id = ? AND meal_id = ?
            """, (user_id, meal_id))
            
            conn.commit()
            affected = cursor.rowcount
            conn.close()
            
            return affected > 0
        except Exception as e:
            logger.error(f"Error removing favorite: {e}")
            return False
    
    def get_favorites(self, user_id):
        """Получает все избранные рецепты пользователя, отсортированные по рейтингу"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT meal_id, meal_name, meal_thumb, added_at, rating
                FROM favorites
                WHERE user_id = ?
                ORDER BY rating DESC, added_at DESC
            """, (user_id,))
            
            results = cursor.fetchall()
            conn.close()
            
            return results
        except Exception as e:
            logger.error(f"Error getting favorites: {e}")
            return []
    
    def is_favorite(self, user_id, meal_id):
        """Проверяет, есть ли рецепт в избранном"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT COUNT(*) FROM favorites
                WHERE user_id = ? AND meal_id = ?
            """, (user_id, meal_id))
            
            count = cursor.fetchone()[0]
            conn.close()
            
            return count > 0
        except Exception as e:
            logger.error(f"Error checking favorite: {e}")
            return False
    
    def set_rating(self, user_id, meal_id, rating):
        """Устанавливает рейтинг для рецепта"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE favorites
                SET rating = ?
                WHERE user_id = ? AND meal_id = ?
            """, (rating, user_id, meal_id))
            
            conn.commit()
            affected = cursor.rowcount
            conn.close()
            
            return affected > 0
        except Exception as e:
            logger.error(f"Error setting rating: {e}")
            return False
    
    def get_rating(self, user_id, meal_id):
        """Получает рейтинг рецепта"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT rating FROM favorites
                WHERE user_id = ? AND meal_id = ?
            """, (user_id, meal_id))
            
            result = cursor.fetchone()
            conn.close()
            
            return result[0] if result else 0
        except Exception as e:
            logger.error(f"Error getting rating: {e}")
            return 0
    
    def clear_favorites(self, user_id):
        """Очищает все избранные рецепты пользователя"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                DELETE FROM favorites
                WHERE user_id = ?
            """, (user_id,))
            
            conn.commit()
            affected = cursor.rowcount
            conn.close()
            
            return affected
        except Exception as e:
            logger.error(f"Error clearing favorites: {e}")
            return 0
