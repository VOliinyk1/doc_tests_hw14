import datetime

from fastapi import HTTPException
from sqlalchemy.orm import Session

from src.database.models import Contact
from src.schemas import ContactModel


async def get_contacts(current_user, db: Session):
    """
    Retrieves a list of  contacts for a specific user

    :param current_user: The user to retrieve contacts for
    :type current_user: User
    :param db: The database session
    :type db: Session
    :return: A list of contacts.
    :rtype: List[Contact]
    """
    contacts = db.query(Contact).filter_by(user_id=current_user.id).all()
    return contacts


async def get_contact(current_user, contact_id, db: Session):
    """
    Retrieves a contact for a specific user with specified by id parameter

    :param current_user: The user to retrieve contacts for
    :type current_user: User
    :param contact_id: ID of contact
    :type contact_id: int
    :param db: The database session
    :type db: Session
    :return: Wanted contact
    :rtype: Contact
    """
    contact = db.query(Contact).filter_by(user_id=current_user.id).filter_by(id=contact_id).first()
    return contact


def nearest_bdays(contacts: list) -> list:
    """
    Form a list with contacts whose bdays are in 7 days range

    :param contacts: A List of contacts
    :type contacts: list[Contacts]
    :return: A list of contacts
    :rtype: List[Contacts]
    """
    near_contacts = []
    for contact in contacts:
        next_bday = datetime.date(datetime.date.today().year, contact.birth_date.month, contact.birth_date.day)
        if next_bday > datetime.date.today():
            if next_bday - datetime.date.today() < datetime.timedelta(7):
                near_contacts.append(contact)
    return near_contacts


async def get_nearest_bdays(current_user, db: Session):
    """
    Retrieves a list with contacts whose bdays are in 7 days range for specified user

    :param current_user: The user to retrieve contacts for
    :type current_user: User
    :param db: The database session
    :type db: Session
    :return: A list of contacts
    :rtype: List[Contacts]
    """
    contacts = nearest_bdays(db.query(Contact).filter_by(user_id=current_user.id).all())
    return contacts


async def get_contact_by_field(current_user, field_name: str, field_value: str, db: Session) -> list[Contact]:
    """
    Retrieves list of contacts selected by specific field and it's value for specified user

    :param current_user: The user to retrieve contacts for
    :type current_user: User
    :param field_name: Field to search contact by
    :type field_name: str
    :param field_value: Value of wanted field
    :type field_value: str
    :param db: The database session
    :type db: Session
    :return: A list of contacts
    :rtype: list[Contact]
    """
    if not hasattr(Contact, field_name):
        raise HTTPException(status_code=404, detail="Invalid field name")
    contacts = db.query(Contact).filter_by(user_id=current_user.id) \
        .filter(getattr(Contact, field_name) == field_value).all()
    return contacts


async def create(current_user, body: ContactModel, db: Session):
    """
    Create new contact for specified user

    :param current_user: The user to create contact for
    :type current_user: User
    :param body: The data for the new contact to create
    :type body: ContactModel
    :param db: The database session
    :type db: Session
    :return: Just created contact
    :rtype: Contact
    """
    contact = Contact(**body.dict())
    contact.user_id = current_user.id
    if contact:
        db.add(contact)
        db.commit()
        db.refresh(contact)
        db.commit()
    return contact


async def update(current_user, contact_id: int, body: ContactModel, db: Session):
    """
    Update contact for specified user

    :param current_user: The user to update contact for
    :type current_user: User
    :param contact_id: Contact to update
    :type contact_id: int
    :param body: The data for the new contact to create
    :type body: ContactModel
    :param db: The database session
    :type db: Session
    :return: Just updated contact
    :rtype: Contact
    """

    contact = await get_contact(current_user, contact_id, db)
    if contact:
        contact.first_name = body.first_name
        contact.last_name = body.last_name
        contact.email = body.email
        contact.phone = body.phone
        contact.birth_date = body.birth_date
        db.commit()
        db.refresh(contact)
    return contact


async def remove(current_user, contact_id, db: Session):
    """
    Create new contact for specified user

    :param current_user: The user to create contact for
    :type current_user: User
    :param contact_id: Contact to update
    :type contact_id: int
    :param db: The database session
    :type db: Session
    :return: Just deleted contact
    :rtype: Contact
    """
    contact = await get_contact(current_user, contact_id, db)
    if contact:
        db.delete(contact)
        db.commit()
    return contact
