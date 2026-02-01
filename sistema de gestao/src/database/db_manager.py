import sqlite3
import os
from pathlib import Path
from datetime import datetime

class PharmacyDatabaseManager:
    def __init__(self, db_path: str = None):
        """Initialize database manager with path to database file"""
        if db_path is None:
            # Create db in assets folder
            db_path = os.path.join(
                os.path.dirname(__file__),
                '../../assets/pharmacy.db'
            )
        
        self.db_path = db_path
        self._ensure_db_exists()
    
    def _ensure_db_exists(self):
        """Create database and tables if they don't exist"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Criar tabela de proprietários
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pharmacy_owners (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                phone TEXT NOT NULL,
                cpf TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Criar tabela de farmácias
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pharmacies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                owner_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                cnpj TEXT UNIQUE NOT NULL,
                address TEXT NOT NULL,
                city TEXT NOT NULL,
                state TEXT NOT NULL,
                zip_code TEXT NOT NULL,
                phone TEXT NOT NULL,
                email TEXT NOT NULL,
                latitude REAL,
                longitude REAL,
                logo_path TEXT,
                pharmacy_photo_path TEXT,
                description TEXT,
                status TEXT DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (owner_id) REFERENCES pharmacy_owners(id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def create_owner(self, full_name: str, email: str, phone: str, cpf: str, password: str) -> int:
        """Create a new pharmacy owner"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO pharmacy_owners (full_name, email, phone, cpf, password)
                VALUES (?, ?, ?, ?, ?)
            ''', (full_name, email, phone, cpf, password))
            
            conn.commit()
            owner_id = cursor.lastrowid
            conn.close()
            return owner_id
        except sqlite3.IntegrityError as e:
            raise ValueError(f"Error creating owner: {str(e)}")
    
    def create_pharmacy(self, owner_id: int, name: str, cnpj: str, address: str,
                       city: str, state: str, zip_code: str, phone: str,
                       email: str, latitude: float = None, longitude: float = None,
                       logo_path: str = None, pharmacy_photo_path: str = None,
                       description: str = None) -> int:
        """Create a new pharmacy"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO pharmacies 
                (owner_id, name, cnpj, address, city, state, zip_code, phone, 
                 email, latitude, longitude, logo_path, pharmacy_photo_path, description)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (owner_id, name, cnpj, address, city, state, zip_code, phone,
                  email, latitude, longitude, logo_path, pharmacy_photo_path, description))
            
            conn.commit()
            pharmacy_id = cursor.lastrowid
            conn.close()
            return pharmacy_id
        except sqlite3.IntegrityError as e:
            raise ValueError(f"Error creating pharmacy: {str(e)}")
    
    def get_owner_by_email(self, email: str) -> dict:
        """Get owner information by email"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM pharmacy_owners WHERE email = ?', (email,))
        result = cursor.fetchone()
        conn.close()
        
        return dict(result) if result else None
    
    def get_pharmacy_by_id(self, pharmacy_id: int) -> dict:
        """Get pharmacy information by ID"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM pharmacies WHERE id = ?', (pharmacy_id,))
        result = cursor.fetchone()
        conn.close()
        
        return dict(result) if result else None
    
    def get_pharmacies_by_owner(self, owner_id: int) -> list:
        """Get all pharmacies for an owner"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM pharmacies WHERE owner_id = ?', (owner_id,))
        results = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in results]
    
    def update_pharmacy(self, pharmacy_id: int, **kwargs) -> bool:
        """Update pharmacy information"""
        try:
            # Allowed fields to update
            allowed_fields = [
                'name', 'address', 'city', 'state', 'zip_code', 'phone', 'email',
                'latitude', 'longitude', 'logo_path', 'pharmacy_photo_path',
                'description', 'status'
            ]
            
            updates = {k: v for k, v in kwargs.items() if k in allowed_fields}
            if not updates:
                return False
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            updates['updated_at'] = datetime.now().isoformat()
            
            set_clause = ', '.join([f'{k} = ?' for k in updates.keys()])
            values = list(updates.values()) + [pharmacy_id]
            
            cursor.execute(
                f'UPDATE pharmacies SET {set_clause} WHERE id = ?',
                values
            )
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            raise ValueError(f"Error updating pharmacy: {str(e)}")
    
    def delete_pharmacy(self, pharmacy_id: int) -> bool:
        """Soft delete pharmacy (mark as inactive)"""
        return self.update_pharmacy(pharmacy_id, status='inactive')
