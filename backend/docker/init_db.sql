-- 问客项目数据库初始化脚本

-- 创建扩展
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 创建merchants表
CREATE TABLE IF NOT EXISTS merchants (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL,
    api_key VARCHAR(100) UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建users表
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE,
    hashed_password VARCHAR(100) NOT NULL,
    merchant_id UUID REFERENCES merchants(id),
    is_admin BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建agents表
CREATE TABLE IF NOT EXISTS agents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL,
    description TEXT,
    config JSONB NOT NULL,
    merchant_id UUID REFERENCES merchants(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建sessions表
CREATE TABLE IF NOT EXISTS sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id),
    agent_id UUID REFERENCES agents(id),
    merchant_id UUID REFERENCES merchants(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建messages表
CREATE TABLE IF NOT EXISTS messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID REFERENCES sessions(id),
    user_id UUID REFERENCES users(id),
    agent_id UUID REFERENCES agents(id),
    content TEXT NOT NULL,
    message_type VARCHAR(20) NOT NULL,
    role VARCHAR(20) NOT NULL,
    metadata JSONB,
    total_tokens_estimated INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 添加索引
CREATE INDEX IF NOT EXISTS idx_messages_session_id ON messages(session_id);
CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_sessions_agent_id ON sessions(agent_id);

-- 插入默认数据
-- 1. 创建默认商户
INSERT INTO merchants (name, api_key) 
VALUES ('默认商户', 'default_api_key') 
ON CONFLICT DO NOTHING;

-- 2. 创建默认管理员用户
INSERT INTO users (username, email, hashed_password, merchant_id, is_admin) 
SELECT 'admin', 'admin@wenke.com', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', 
       (SELECT id FROM merchants WHERE name = '默认商户'), true 
WHERE NOT EXISTS (SELECT 1 FROM users WHERE username = 'admin');

-- 3. 创建默认Agent
INSERT INTO agents (name, description, config, merchant_id) 
SELECT '默认客服Agent', '智能客服助手', 
       '{"model": "gpt-3.5-turbo", "temperature": 0.7, "max_tokens": 1000}',
       (SELECT id FROM merchants WHERE name = '默认商户') 
WHERE NOT EXISTS (SELECT 1 FROM agents WHERE name = '默认客服Agent');