from typing import List

from fastapi import Depends, HTTPException, status, Path, APIRouter
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.orm import Session


from src.database.db import get_db
from src.database.models import User
from src.schemas import ContactResponse, ContactModel
from src.repository import contacts as repos_contacts
from src.services.auth import auth_service

router = APIRouter(prefix='/contacts', tags=['contacts'])


@router.get('/all', response_model=List[ContactResponse], description='No more than 10 requests per minute',
            dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def get_contacts(db: Session = Depends(get_db),
                       current_user: User = Depends(auth_service.get_current_user)):
    """
    Retrieves a list of  contacts for a specific user

    :param current_user: The user to retrieve contacts for
    :type current_user: User
    :param db: The database session
    :type db: Session
    :return: A list of contacts.
    :rtype: List[Contact]
    """
    contacts = await repos_contacts.get_contacts(current_user, db)
    if contacts is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Not Found')
    return contacts


@router.get('/bday', response_model=List[ContactResponse], description='No more than 10 requests per minute',
            dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def get_nearest_bdays(db: Session = Depends(get_db),
                            current_user: User = Depends(auth_service.get_current_user)):
    """
        Retrieves a list with contacts whose bdays are in 7 days range for specified user

        :param current_user: The user to retrieve contacts for
        :type current_user: User
        :param db: The database session
        :type db: Session
        :return: A list of contacts
        :rtype: List[Contacts]
        """
    contacts = await repos_contacts.get_nearest_bdays(current_user, db)
    if contacts is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Not Found')
    return contacts


@router.get('/{contact_id}', response_model=ContactResponse, description='No more than 10 requests per minute',
            dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def get_contact(contact_id: int = Path(ge=1), db: Session = Depends(get_db),
                      current_user: User = Depends(auth_service.get_current_user)):
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
    contact = await repos_contacts.get_contact(current_user, contact_id, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Not Found')
    return contact


@router.get('/{field_name}/{field_value}', response_model=List[ContactResponse],
            description='No more than 10 requests per minute',
            dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def get_contacts_by_field(field_name: str, field_value: str, db: Session = Depends(get_db),
                                current_user: User = Depends(auth_service.get_current_user)):
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
    contacts = await repos_contacts.get_contact_by_field(current_user, field_name, field_value, db)

    if not contacts:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Not Found')
    return contacts


@router.post('/', response_model=ContactResponse, status_code=status.HTTP_201_CREATED,
             description='No more than 10 requests per minute',
             dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def create_contact(body: ContactModel, db: Session = Depends(get_db),
                         current_user: User = Depends(auth_service.get_current_user)):
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
    contact = await repos_contacts.create(current_user, body, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Wrong Data')
    return contact


@router.put('/{contact_id}', response_model=ContactResponse, description='No more than 10 requests per minute',
            dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def update_contact(body: ContactModel,
                         contact_id: int = Path(ge=1),
                         db: Session = Depends(get_db),
                         current_user: User = Depends(auth_service.get_current_user)):
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
    contact = await repos_contacts.update(current_user, contact_id, body, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Not Found')
    return contact


@router.delete('/{contact_id}', status_code=status.HTTP_204_NO_CONTENT,
               description='No more than 10 requests per minute',
               dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def remove(contact_id, db: Session = Depends(get_db),
                 current_user: User = Depends(auth_service.get_current_user)):
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
    contact = await repos_contacts.remove(current_user, contact_id, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Not Found')
    return contact
