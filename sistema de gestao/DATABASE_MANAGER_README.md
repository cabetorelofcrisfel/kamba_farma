# Kamba Sistema de Gestão - Documentação Completa

## 📋 Visão Geral

Este projeto contém dois programas principais:

### 1. **Pharmacy Manager** - Gestor de Farmácia
Aplicação para registrar farmácias com dados do proprietário, informações da farmácia, logotipo e fotos.

**Arquivo de inicialização**: `pharmacy_manager.py`

#### Funcionalidades:
- Cadastro de proprietário com credenciais (CPF, email, telefone, senha)
- Cadastro de farmácia (nome, CNPJ, endereço, localização geográfica)
- Upload de logotipo e foto da farmácia
- Banco de dados relacional com tabelas `pharmacy_owners` e `pharmacies`

#### Como usar:
```bash
python pharmacy_manager.py
```

#### Estrutura do banco:
- **Tabela `pharmacy_owners`**: Armazena credenciais do proprietário
- **Tabela `pharmacies`**: Armazena dados da farmácia com FK para owner

---

### 2. **SQL Database Manager** - Gerenciador de Banco de Dados SQL
Ferramenta gráfica completa para criar, editar e gerenciar bancos de dados SQLite.

**Arquivo de inicialização**: `sql_database_manager.py`

#### Funcionalidades:
- ✅ Criar novo banco de dados
- ✅ Abrir banco de dados existente
- ✅ Criar tabelas com coluna PRIMARY KEY automática
- ✅ Inserir dados nas tabelas
- ✅ Visualizar dados em table widget
- ✅ Editar/deletar linhas
- ✅ Deletar tabelas
- ✅ Exportar banco para arquivo SQL
- ✅ Visualizar informações do banco (tamanho, número de tabelas, linhas)

#### Como usar:
```bash
python sql_database_manager.py
```

#### Interface:
- **Painel Esquerdo**: Operações de banco de dados
  - Seleção de arquivo do banco
  - Lista de tabelas
  - Botões para criar/deletar tabelas
  - Exportar para SQL

- **Painel Direito**: Operações com dados
  - Visualização de dados em table widget
  - Inserir, deletar linhas
  - Atualizar visualização

---

## 📁 Estrutura do Projeto

```
.
├── src/
│   ├── database/
│   │   ├── __init__.py
│   │   ├── db_manager.py           # Gerenciador farmácia
│   │   └── sql_manager.py          # Gerenciador SQL genérico
│   ├── ui/
│   │   ├── __init__.py
│   │   ├── pharmacy_setup.py       # UI Farmácia
│   │   └── sql_database_gui.py     # UI Gerenciador SQL
│   └── models/
│       └── __init__.py
├── assets/
│   ├── uploads/                    # Imagens farmácia
│   ├── pharmacy.db                 # BD Farmácia
│   └── databases/                  # BDs criados no gerenciador
├── pharmacy_manager.py             # Executável 1
├── sql_database_manager.py         # Executável 2
├── requirements.txt
└── README.md
```

---

## 🛠️ Classes Principais

### `PharmacyDatabaseManager` (src/database/db_manager.py)
Gerencia banco de dados da farmácia.

**Métodos principais**:
```python
create_owner(full_name, email, phone, cpf, password) -> int
create_pharmacy(owner_id, name, cnpj, ...) -> int
get_owner_by_email(email) -> dict
get_pharmacy_by_id(pharmacy_id) -> dict
update_pharmacy(pharmacy_id, **kwargs) -> bool
```

### `SQLDatabaseManager` (src/database/sql_manager.py)
Gerenciador genérico de banco de dados SQL.

**Métodos principais**:
```python
connect() -> Connection
execute_query(query, params) -> List[Dict]
execute_update(query, params) -> int
create_table(table_name, columns) -> bool
drop_table(table_name) -> bool
get_tables() -> List[str]
get_table_schema(table_name) -> List[Dict]
insert_row(table_name, data) -> int
update_row(table_name, data, where, where_params) -> int
delete_row(table_name, where, where_params) -> int
export_to_sql(output_path) -> bool
```

### `PharmacySetupWizard` (src/ui/pharmacy_setup.py)
Interface PyQt5 para registrar farmácias.

**Abas**:
1. Informações do Proprietário
2. Informações da Farmácia
3. Logotipo e Fotos

### `SQLDatabaseGUI` (src/ui/sql_database_gui.py)
Interface PyQt5 para gerenciar bancos de dados.

**Componentes**:
- Painel de gestão de banco de dados
- Lista de tabelas
- Table widget para visualizar dados
- Dialogs para criar tabelas e inserir dados

---

## 📦 Dependências

```
PyQt5>=5.15.0
PyQt5-sip>=12.9.0
SQLite3 (incluso no Python)
```

### Instalação:
```bash
pip install -r requirements.txt
```

---

## 🗄️ Schema do Banco Pharmacy

### Tabela `pharmacy_owners`
```sql
CREATE TABLE pharmacy_owners (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    phone TEXT NOT NULL,
    cpf TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

### Tabela `pharmacies`
```sql
CREATE TABLE pharmacies (
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
```

---

## 🎨 Interface e Estilo

Ambas as aplicações utilizam:
- **Framework**: PyQt5
- **Fonte**: Segoe UI
- **Cor primária**: Teal (#009688)
- **Cor secundária**: Cinza (#B0BEC5)
- **Cor de fundo**: Branco/Cinza claro (#FAFAFA)

---

## 📝 Exemplo de Uso

### Pharmacy Manager:
1. Execute: `python pharmacy_manager.py`
2. Preencha dados do proprietário na Aba 1
3. Preencha dados da farmácia na Aba 2
4. Faça upload do logotipo e foto na Aba 3
5. Clique "Registrar Farmácia"

### SQL Database Manager:
1. Execute: `python sql_database_manager.py`
2. Clique "Novo BD" para criar um banco
3. Clique "Criar Tabela" para adicionar tabelas
4. Clique "Inserir Linha" para adicionar dados
5. Clique "Exportar para SQL" para salvar em arquivo

---

## ⚠️ Tratamento de Erros

Ambas as aplicações implementam:
- Validação de campos obrigatórios
- Verificação de unicidade (email, CPF, CNPJ)
- Tratamento de exceções de banco de dados
- Mensagens de erro ao usuário
- Confirmação antes de deletar dados

---

## 📄 Licença

Este projeto faz parte do sistema Kamba Farma.

---

## 🔧 Manutenção

Para adicionar novos recursos:

1. **Novo método no gerenciador**: Editar `src/database/sql_manager.py`
2. **Nova interface**: Criar arquivo em `src/ui/`
3. **Novo executável**: Criar script em raiz com import dos módulos

---

## 📞 Suporte

Para problemas ou sugestões, consulte a documentação ou entre em contato com o time de desenvolvimento.
