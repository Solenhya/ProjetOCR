from ..db.models import User



def get_user(session,userEmail):
    user = session.query(User).filter_by(userEmail = userEmail).first()
    session.close()
    return user

def save_user(session,userEmail,hashedPassword,userAccess="Not"):
    user = User(    userEmail = userEmail,
                userPassword=hashedPassword,
                userRight=userAccess)
    session.add(user)
    session.commit()
    session.close()

def getAllUser(session):
    users = session.query(User).all()
    for user in users:
        print(f"user : {user}")
    return users