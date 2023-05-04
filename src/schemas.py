from pydantic import BaseModel, Field, EmailStr, validator
from pydantic.types import date


class UserModel(BaseModel):
    username: str = Field(min_length=6, max_length=12)
    email: EmailStr
    password: str = Field(min_length=6, max_length=20)
    avatar: str


class UserDb(BaseModel):
    id: int
    username: str
    email: EmailStr
    avatar: str

    class Config:
        orm_mode = True


class UserResponse(BaseModel):
    user: UserDb
    detail: str = "User successfully created"


class ContactModel(BaseModel):
    first_name: str = Field("first_name")
    last_name: str = Field("last_name")
    email: EmailStr
    phone: str = Field('phone_number', min_length=12, max_length=13)
    birth_date: date

    @validator('birth_date')
    def ensure_date_range(cls, v):
        if not date.today() > v:
            raise ValueError('Wrong date format. Following format works: YYYY-MM-DD')
        return v


class ContactResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: EmailStr
    phone: str
    birth_date: date
    user: UserResponse

    class Config:
        orm_mode = True


class TokenModel(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RequestEmail(BaseModel):
    email: EmailStr
