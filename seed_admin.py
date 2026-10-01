from app import app,db
from models import User
import os
with app.app_context():
    email=os.getenv('ADMIN_EMAIL','admin@cinematch.local').lower(); password=os.getenv('ADMIN_PASSWORD','Admin@12345')
    u=User.query.filter_by(email=email).first()
    if not u: u=User(name='CineMatch Admin',email=email); db.session.add(u)
    u.role='admin'; u.set_password(password); db.session.commit(); print(f'Admin ready: {email}')
