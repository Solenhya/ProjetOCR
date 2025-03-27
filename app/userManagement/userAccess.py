from app.db import connection
from app.db.models import User

def get_user(userEmail):
    session = connection.get_session()
    user = session.query(User).filter_by(userEmail = userEmail).first()
    session.close()
    return user

def save_user(userEmail,hashedPassword,userAccess="All"):
    user = User(    userEmail = userEmail,
                userPassword=hashedPassword,
                userRight=userAccess)
    session = connection.get_session()
    session.add(user)
    session.commit()
    session.close()

def getAllUser():
    session = connection.get_session()
    users = session.query(User).all()
    for user in users:
        print(f"user : {user}")
    return users