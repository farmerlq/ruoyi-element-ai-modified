#!/usr/bin/env python3
"""
数据库初始化脚本
用于创建默认用户和测试数据
"""

import sys
from sqlalchemy.orm import Session
from core.database import engine, Base, get_db
from models.user import User
from models.merchant import Merchant
from core.security import get_password_hash
from datetime import datetime

def init_database():
    """初始化数据库，创建默认用户"""
    
    # 创建所有表
    Base.metadata.create_all(bind=engine)
    
    # 获取数据库会话
    db = Session(bind=engine)
    
    try:
        # 检查是否已存在默认商户
        default_merchant = db.query(Merchant).filter(Merchant.name == "默认商户").first()
        
        if not default_merchant:
            # 创建默认商户
            default_merchant = Merchant(
                name="默认商户",
                description="系统默认商户",
                api_key="default_api_key_123456",
                balance=1000.00,
                status="active",
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.add(default_merchant)
            db.commit()
            db.refresh(default_merchant)
            print(f"✅ 创建默认商户: {default_merchant.name} (ID: {default_merchant.id})")
        else:
            print(f"ℹ️  默认商户已存在: {default_merchant.name} (ID: {default_merchant.id})")
        
        # 检查是否已存在admin用户
        admin_user = db.query(User).filter(User.username == "admin").first()
        
        if not admin_user:
            # 创建默认管理员用户
            admin_user = User(
                merchant_id=default_merchant.id,
                username="admin",
                email="admin@example.com",
                password_hash=get_password_hash("admin123"),
                full_name="系统管理员",
                role="admin",
                status="active",
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.add(admin_user)
            db.commit()
            db.refresh(admin_user)
            print(f"✅ 创建默认管理员用户: {admin_user.username} (ID: {admin_user.id})")
            print(f"   用户名: admin")
            print(f"   密码: admin123")
            print(f"   邮箱: {admin_user.email}")
        else:
            print(f"ℹ️  管理员用户已存在: {admin_user.username} (ID: {admin_user.id})")
        
        # 检查是否已存在测试用户
        test_user = db.query(User).filter(User.username == "testuser").first()
        
        if not test_user:
            # 创建测试用户
            test_user = User(
                merchant_id=default_merchant.id,
                username="testuser",
                email="testuser@example.com",
                password_hash=get_password_hash("test123"),
                full_name="测试用户",
                role="user",
                status="active",
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.add(test_user)
            db.commit()
            db.refresh(test_user)
            print(f"✅ 创建测试用户: {test_user.username} (ID: {test_user.id})")
            print(f"   用户名: testuser")
            print(f"   密码: test123")
            print(f"   邮箱: {test_user.email}")
        else:
            print(f"ℹ️  测试用户已存在: {test_user.username} (ID: {test_user.id})")
        
        print("\n🎉 数据库初始化完成！")
        print("您可以使用以下凭据登录:")
        print("管理员 - 用户名: admin, 密码: admin123")
        print("测试用户 - 用户名: testuser, 密码: test123")
        
    except Exception as e:
        db.rollback()
        print(f"❌ 数据库初始化失败: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    print("🚀 开始初始化数据库...")
    init_database()