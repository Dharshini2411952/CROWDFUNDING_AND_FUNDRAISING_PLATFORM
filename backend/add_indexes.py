from app.core.database import SessionLocal
from sqlalchemy import text

def add_indexes():
    db = SessionLocal()
    queries = [
        ('users', 'idx_users_role', 'CREATE INDEX idx_users_role ON users(role)'),
        ('users', 'idx_users_is_active', 'CREATE INDEX idx_users_is_active ON users(is_active)'),
        ('campaigns', 'idx_campaigns_status', 'CREATE INDEX idx_campaigns_status ON campaigns(status)'),
        ('campaigns', 'idx_campaigns_category', 'CREATE INDEX idx_campaigns_category ON campaigns(category)'),
        ('donations', 'idx_donations_campaign_id', 'CREATE INDEX idx_donations_campaign_id ON donations(campaign_id)'),
        ('donations', 'idx_donations_donor_id', 'CREATE INDEX idx_donations_donor_id ON donations(donor_id)'),
        ('transactions', 'idx_transactions_status', 'CREATE INDEX idx_transactions_status ON transactions(status)')
    ]
    try:
        for tbl, idx, stmt in queries:
            check_res = db.execute(text(f"SHOW INDEX FROM {tbl} WHERE Key_name = '{idx}'")).fetchall()
            if not check_res:
                db.execute(text(stmt))
                print(f"Created index {idx} on {tbl}")
        db.commit()
        print("ALL INDEXES VERIFIED SUCCESSFULLY.")
    except Exception as e:
        db.rollback()
        print(f"Index check info: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    add_indexes()
