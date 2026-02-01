# Kamba - Configuração do Projeto

## Informações do Projeto

**Nome**: Kamba Sistema de Gestão  
**Versão**: 1.0.0  
**Descrição**: Sistema completo de gestão para farmácias com gerenciador de banco de dados

## Componentes

### 1. Pharmacy Manager
- **Arquivo**: `pharmacy_manager.py`
- **Descrição**: Aplicativo para registrar e gerenciar farmácias
- **Banco de Dados**: `assets/pharmacy.db`
- **Módulos**:
  - `src.database.db_manager`: Gerenciamento de dados da farmácia
  - `src.ui.pharmacy_setup`: Interface PyQt5

### 2. SQL Database Manager
- **Arquivo**: `sql_database_manager.py`
- **Descrição**: Ferramenta para criar e gerenciar bancos de dados SQL genéricos
- **Banco de Dados**: `assets/databases/` (múltiplos bancos)
- **Módulos**:
  - `src.database.sql_manager`: Gerenciador SQL genérico
  - `src.ui.sql_database_gui`: Interface PyQt5

## Requisitos

- Python 3.7 ou superior
- PyQt5 >= 5.15.0
- SQLite3 (incluído no Python)

## Instalação

```bash
pip install -r requirements.txt
```

## Execução

### Pharmacy Manager
```bash
python pharmacy_manager.py
```

### SQL Database Manager
```bash
python sql_database_manager.py
```

### Exemplos de Uso
```bash
python exemplos_uso.py
```

## Estrutura de Diretórios

```
.
├── src/
│   ├── database/
│   │   ├── db_manager.py          # Gerenciador de farmácia
│   │   └── sql_manager.py         # Gerenciador SQL genérico
│   ├── ui/
│   │   ├── pharmacy_setup.py       # UI de registro de farmácia
│   │   └── sql_database_gui.py     # UI do gerenciador SQL
│   └── models/
├── assets/
│   ├── uploads/                    # Imagens de farmácia
│   ├── pharmacy.db                 # BD da farmácia
│   └── databases/                  # BDs criados no gerenciador
├── pharmacy_manager.py
├── sql_database_manager.py
├── exemplos_uso.py
├── requirements.txt
├── README.md
├── DATABASE_MANAGER_README.md
├── CONFIG.md (este arquivo)
└── .github/
```

## Variáveis de Ambiente (Opcional)

```bash
# Para debug
KAMBA_DEBUG=1

# Caminho customizado para banco de dados
KAMBA_DB_PATH=/custom/path/pharmacy.db
```

## Comandos Úteis

### Criar novo banco de dados
```python
from src.database.sql_manager import SQLDatabaseManager

db = SQLDatabaseManager('novo_banco.db')
db.create_table('tabela', {'id': 'INTEGER PRIMARY KEY', 'nome': 'TEXT'})
```

### Consultar dados
```python
resultados = db.execute_query('SELECT * FROM tabela')
for row in resultados:
    print(row)
```

### Exportar banco de dados
```python
db.export_to_sql('backup.sql')
```

## Troubleshooting

### Erro: "No module named 'PyQt5'"
```bash
pip install PyQt5
```

### Banco de dados locked
- Feche todas as instâncias do aplicativo
- Verifique se não há processos Python abertos
- Tente novamente

### Imagens não aparecem
- Verifique se `assets/uploads/` existe
- Verifique permissões de escrita do diretório

## Padrões de Código

### Nomenclatura
- Classes: `PascalCase` (ex: `PharmacyDatabaseManager`)
- Funções: `snake_case` (ex: `create_table()`)
- Constantes: `UPPER_SNAKE_CASE` (ex: `DB_PATH`)

### Comentários
- Use docstrings para funções e classes
- Use `#` para comentários inline
- Documente parâmetros com tipos

### Exemplo:
```python
def get_pharmacy(self, pharmacy_id: int) -> dict:
    """
    Obtém informações da farmácia
    
    Args:
        pharmacy_id: ID da farmácia
        
    Returns:
        Dicionário com dados da farmácia
    """
    return self.execute_query(
        'SELECT * FROM pharmacies WHERE id = ?',
        (pharmacy_id,)
    )
```

## Logging

Para ativar debug, adicione ao início do arquivo:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Segurança

### Importante
- **Nunca** armazene senhas em texto plano em produção
- Use hash criptográfico (bcrypt, argon2)
- Valide todos os inputs de usuário
- Use prepared statements para queries

### Exemplo de melhor prática:
```python
# BOM
cursor.execute('SELECT * FROM users WHERE email = ?', (email,))

# RUIM - SQL Injection
cursor.execute(f'SELECT * FROM users WHERE email = {email}')
```

## Performance

### Dicas de Otimização
1. Use índices para colunas frequentemente consultadas
2. Limite resultados com LIMIT
3. Use batch operations para múltiplas inserções
4. Close connections properly

## Contribução

1. Crie um branch para sua feature
2. Faça commits descritivos
3. Submeta um pull request

## Versionamento

Seguimos Semantic Versioning (MAJOR.MINOR.PATCH)

Exemplo: v1.0.0
- MAJOR: mudanças incompatíveis
- MINOR: novas funcionalidades compatíveis
- PATCH: correções de bugs

## Contato

Para dúvidas ou sugestões, entre em contato com o time de desenvolvimento Kamba.

---

**Última atualização**: 9 de janeiro de 2026
