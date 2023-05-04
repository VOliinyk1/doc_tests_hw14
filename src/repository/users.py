from sqlalchemy.orm import Session

from src.database.models import User
from src.schemas import UserModel


async def get_user_by_email(email: str, db: Session) -> User | None:
    """
    Retrieves user specified by email

    :param email: email to search user by
    :type email: str
    :param db: The database session
    :type db: Session
    :return: Founded user
    :rtype: User
    """
    return db.query(User).filter(User.email == email).first()


async def update_avatar(email, url: str, db: Session) -> User:
    """
    Update avatar of specified user

    :param email: Email of user
    :type email: str
    :param url: URL for picture
    :type url: str
    :param db: The database session
    :type db: Session
    :return: user
    :rtype: User
    """
    user = await get_user_by_email(email, db)
    user.avatar = url
    db.commit()
    return user


async def create_user(body: UserModel, db: Session):
    """
    Create new user

    :param body: The data fot the new user to create
    :type body UserModel
    :param db: The database session
    :type db: Session
    :return: Just created user
    :rtype: User
    """
    new_user = User(**body.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


async def update_token(user: User, refresh_token, db: Session):
    """
    Update access token

    :param user: User which token is updating
    :type user: User
    :param refresh_token: User's refresh token
    :type refresh_token: str
    :param db: The database session
    :type db: Session
    :return: None
    """

    user.refresh_token = refresh_token
    db.commit()


async def confirmed_email(email: str, db: Session) -> None:
    """
    Mark account as confirmed in database

    :param email: email of user which is confirming it
    :type email: str
    :param db: The database session
    :type db: Session
    :return: None
    """
    user = await get_user_by_email(email, db)
    user.confirmed = True
    db.commit()
