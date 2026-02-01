-- Schema mínimo para gestão de stock
PRAGMA foreign_keys = ON;
-- Usuarios
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome_farmacia TEXT,
    nome TEXT NOT NULL,
    numero_bi TEXT,
    area_atuacao TEXT,
    contacto TEXT,
    genero TEXT,
    foto BLOB,
    senha_hash TEXT NOT NULL,
    perfil TEXT DEFAULT 'usuario',
    ativo INTEGER NOT NULL DEFAULT 1,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Fornecedores
CREATE TABLE IF NOT EXISTS fornecedores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    telefone TEXT,
    email TEXT,
    endereco TEXT,
    observacoes TEXT,
    ativo INTEGER NOT NULL DEFAULT 1
);

-- Produtos
CREATE TABLE IF NOT EXISTS produtos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome_comercial TEXT NOT NULL,
    principio_ativo TEXT,
    foto BLOB,
    categoria TEXT,
    forma_farmaceutica TEXT,
    preco_venda REAL DEFAULT 0.0,
    preco_compra REAL DEFAULT 0.0,
    stock INTEGER DEFAULT 0,
    codigo_barras TEXT UNIQUE,
    unidade TEXT,
    descricao TEXT,
    stock_minimo INTEGER DEFAULT 0,
    fornecedor_padrao_id INTEGER,
    lote_padrao_id INTEGER,
    ativo INTEGER NOT NULL DEFAULT 1,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(fornecedor_padrao_id) REFERENCES fornecedores(id),
    FOREIGN KEY(lote_padrao_id) REFERENCES lotes(id)
);

-- Lotes
CREATE TABLE IF NOT EXISTS lotes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    produto_id INTEGER NOT NULL,
    numero_lote TEXT,
    validade DATE,
    foto BLOB,
    quantidade_inicial INTEGER DEFAULT 0,
    quantidade_atual INTEGER DEFAULT 0,
    preco_compra REAL DEFAULT 0.0,
    fornecedor_id INTEGER,
    data_entrada TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ativo INTEGER NOT NULL DEFAULT 1,
    FOREIGN KEY(produto_id) REFERENCES produtos(id),
    FOREIGN KEY(fornecedor_id) REFERENCES fornecedores(id)
);

-- Itens venda config (preço padrão por produto)
CREATE TABLE IF NOT EXISTS itens_venda_config (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    produto_id INTEGER NOT NULL,
    preco_venda REAL NOT NULL DEFAULT 0.0,
    ativo INTEGER NOT NULL DEFAULT 1,
    FOREIGN KEY(produto_id) REFERENCES produtos(id)
);

-- Vendas
CREATE TABLE IF NOT EXISTS vendas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER,
    data_venda TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    total REAL NOT NULL DEFAULT 0.0,
    FOREIGN KEY(usuario_id) REFERENCES usuarios(id)
);

-- Itens de venda (itens em cada venda)
CREATE TABLE IF NOT EXISTS itens_venda (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    venda_id INTEGER NOT NULL,
    produto_id INTEGER NOT NULL,
    lote_id INTEGER,
    quantidade INTEGER NOT NULL,
    preco_unitario REAL NOT NULL,
    subtotal REAL NOT NULL,
    FOREIGN KEY(venda_id) REFERENCES vendas(id),
    FOREIGN KEY(produto_id) REFERENCES produtos(id),
    FOREIGN KEY(lote_id) REFERENCES lotes(id)
);

-- Histórico de Compras
-- Armazena um registro de compras feitas (comprador, timestamp e lista de produtos).
CREATE TABLE IF NOT EXISTS historico_compra (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    comprador_nome TEXT NOT NULL,
    produtos_comprados JSON,
    quantidade_total INTEGER DEFAULT 0,
    tempo_compra TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Itens do histórico de compra (normalizado) — liga cada item ao produto
CREATE TABLE IF NOT EXISTS historico_compra_itens (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    historico_compra_id INTEGER NOT NULL,
    produto_id INTEGER NOT NULL,
    quantidade INTEGER NOT NULL,
    preco_unitario REAL,
    FOREIGN KEY(historico_compra_id) REFERENCES historico_compra(id),
    FOREIGN KEY(produto_id) REFERENCES produtos(id)
);

-- Logs do sistema
CREATE TABLE IF NOT EXISTS logs_sistema (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER,
    acao TEXT,
    tabela_afetada TEXT,
    registro_id INTEGER,
    data_log TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(usuario_id) REFERENCES usuarios(id)
);

-- Transações Financeiras (Entradas e Saídas)
CREATE TABLE IF NOT EXISTS transacoes_financeiras (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tipo TEXT NOT NULL,
    descricao TEXT,
    valor REAL NOT NULL,
    data_transacao TEXT,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela para administradores do sistema
CREATE TABLE IF NOT EXISTS user_admin (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    contacto TEXT,
    numero_bi TEXT,
    ft BLOB,
    senha_hash TEXT NOT NULL,
    localizacao TEXT,
    email TEXT UNIQUE,
    ativo INTEGER NOT NULL DEFAULT 1,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
