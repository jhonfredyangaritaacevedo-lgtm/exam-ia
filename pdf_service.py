import uuid
from src.core.database import SessionLocal
from src.models.user import User
from src.core.auth import hash_password

def create_admin():
    db = SessionLocal()
    try:
        admin_email = "emmendoza2794@gmail.com"
        existing = db.query(User).filter(User.email == admin_email).first()
        if not existing:
            admin = User(
                id=uuid.uuid4(),
                email=admin_email,
                full_name="Edinson Mendoza",
                password_hash=hash_password("edinson1"),
                role="admin",
                is_active=True
            )
            db.add(admin)
            db.commit()
            print(f"✅ Administrador creado: {admin_email} / edinson1")
        else:
            print(f"⚠️  El administrador ya existe: {admin_email}")
            # Update role to admin if it's not
            if existing.role != "admin":
                existing.role = "admin"
                db.commit()
                print("✅ Rol actualizado a admin")
    finally:
        db.close()

if __name__ == "__main__":
    create_admin()
