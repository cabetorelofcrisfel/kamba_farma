# Kamba Sistema de Gestão

## 📚 Programas Inclusos

Este projeto contém **dois programas principais** para gestão de farmácia e banco de dados:

### 1. Pharmacy Manager - Gestor de Farmácia
A PyQt5 desktop application for registering and managing pharmacies with owner credentials, pharmacy information, and media uploads.

**Executar**: `python pharmacy_manager.py`

## Features

- **Owner Registration**: Store pharmacy owner credentials (name, email, phone, CPF, password)
- **Pharmacy Information**: Capture detailed pharmacy data including:
  - Name and CNPJ
  - Address, city, state, zip code
  - Contact information (phone, email)
  - Geographic coordinates (latitude, longitude)
  - Description
- **Media Management**: Upload and store:
  - Pharmacy logo
  - Pharmacy photo
- **Database**: SQLite database with proper relationships between owners and pharmacies
- **Validation**: Form validation to ensure data integrity
- **User-friendly UI**: Tab-based interface for organized data entry

## Project Structure

```
.
├── src/
│   ├── database/
│   │   ├── __init__.py
│   │   ├── db_manager.py           # Pharmacy database management
│   │   └── sql_manager.py          # Generic SQL database manager
│   ├── ui/
│   │   ├── __init__.py
│   │   ├── pharmacy_setup.py        # Pharmacy registration UI
│   │   └── sql_database_gui.py      # SQL database manager UI
│   └── models/
│       └── __init__.py
├── assets/
│   ├── uploads/                     # Pharmacy images stored here
│   ├── pharmacy.db                  # Pharmacy database
│   └── databases/                   # Databases created in SQL manager
├── pharmacy_manager.py              # Pharmacy manager executable
├── sql_database_manager.py          # SQL database manager executable
├── exemplos_uso.py                  # Usage examples
├── requirements.txt
├── README.md
└── DATABASE_MANAGER_README.md       # Detailed documentation
```

## Installation

1. **Clone or extract the project**

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Run Pharmacy Manager**:
```bash
python pharmacy_manager.py
```

4. **Run SQL Database Manager**:
```bash
python sql_database_manager.py
```

5. **View Usage Examples**:
```bash
python exemplos_uso.py
```

## Requirements

- Python 3.7+
- PyQt5
- SQLite3 (included with Python)

## Database Schema

### `pharmacy_owners` table
- `id`: Primary key
- `full_name`: Owner's full name
- `email`: Owner's email (unique)
- `phone`: Contact phone number
- `cpf`: CPF number (unique)
- `password`: Account password
- `created_at`: Timestamp

### `pharmacies` table
- `id`: Primary key
- `owner_id`: Foreign key to pharmacy_owners
- `name`: Pharmacy name
- `cnpj`: CNPJ number (unique)
- `address`: Street address
- `city`: City name
- `state`: State abbreviation
- `zip_code`: ZIP/postal code
- `phone`: Contact phone
- `email`: Contact email
- `latitude`: Geographic latitude
- `longitude`: Geographic longitude
- `logo_path`: Path to logo image
- `pharmacy_photo_path`: Path to pharmacy photo
- `description`: Pharmacy description
- `status`: Status (active/inactive)
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp

## Usage

1. **Launch the application**:
   ```bash
   python pharmacy_manager.py
   ```

2. **Fill in owner information**:
   - Full name, email, phone, CPF, and password

3. **Enter pharmacy details**:
   - Basic information: name, CNPJ, address
   - Location: city, state, zip code
   - Contact: phone, email
   - Optional: geographic coordinates and description

4. **Upload media**:
   - Select and upload pharmacy logo
   - Select and upload pharmacy photo

5. **Register**:
   - Click "Registrar Farmácia" to save all information

Images are automatically copied to the `assets/uploads/` directory with timestamped filenames.

### SQL Database Manager

1. **Launch the application**:
   ```bash
   python sql_database_manager.py
   ```

2. **Create or open a database**:
   - Click "Novo BD" to create a new database
   - Click "Abrir BD" to open an existing one

3. **Create tables**:
   - Click "Criar Tabela"
   - Enter table name and define columns
   - Specify data types (TEXT, INTEGER, REAL, etc.)
   - Add constraints (PRIMARY KEY, NOT NULL, UNIQUE)

4. **Work with data**:
   - Select a table from the list
   - Click "Inserir Linha" to add data
   - Select a row to delete with "Deletar Linha"
   - Click "Atualizar" to refresh the view

5. **Export**:
   - Click "Exportar para SQL" to save as .sql file

## Database Locations

**Pharmacy Manager**:
```
assets/pharmacy.db
```

**SQL Database Manager**: 
Databases created through the GUI are stored in:
```
assets/databases/
```

## Features in Detail

### Pharmacy Manager Database (`src/database/db_manager.py`)
- `create_owner()`: Create new pharmacy owner
- `create_pharmacy()`: Create new pharmacy with owner relationship
- `get_owner_by_email()`: Retrieve owner by email
- `get_pharmacy_by_id()`: Get pharmacy details
- `get_pharmacies_by_owner()`: Get all pharmacies for an owner
- `update_pharmacy()`: Update pharmacy information
- `delete_pharmacy()`: Soft delete pharmacy (mark as inactive)

### SQL Database Manager (`src/database/sql_manager.py`)
- `create_table()`: Create new table
- `drop_table()`: Delete table
- `execute_query()`: Run SELECT queries
- `execute_update()`: Run INSERT, UPDATE, DELETE
- `insert_row()`: Add data
- `delete_row()`: Remove data
- `export_to_sql()`: Export to SQL file
- `get_database_info()`: Get database statistics

### UI Components
- `pharmacy_setup.py`: Multi-tab pharmacy registration interface
- Image preview for uploaded media
- Form validation with user feedback
- File upload handling with automatic copying to assets

## Error Handling

The application includes validation for:
- Required fields
- Email and CPF uniqueness
- CNPJ uniqueness
- Image file handling
- Database operations

## License

This project is part of the Kamba Farma system.

## Support

For issues or questions, please contact the development team.
- `sql_database_gui.py`: Complete database management interface
   - Table creation dialog
   - Data insertion dialog
   - Table widget for viewing data
   - Database statistics

## Example Scripts

Run the included examples to learn how to use the database managers programmatically:

```bash
python exemplos_uso.py
```

This demonstrates:
- Creating databases and tables
- Inserting, updating, and deleting data
- Querying data
- Exporting databases

- File export/import operations

## License

This project is part of the Kamba Farma system.

## 📖 Additional Documentation

See `DATABASE_MANAGER_README.md` for detailed documentation on both programs and the database schema.

## Support

For issues or questions, please consult the documentation or contact the development team.
