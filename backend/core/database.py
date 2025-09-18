from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from core.config import settings

# 数据库连接URL
SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

# 创建引擎
engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=True)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建基础类
Base = declarative_base()

# 数据库依赖项
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()