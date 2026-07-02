"""
JWT - JSON Web Token used to transmit information between two parties using json object.
each jwt token is digitally signed using a secret key
JWT should be used to deal with authorization
JWT consist of three parts: header, payload and signature
JWT Header - consist of two part - type of token and signing algorithm, its encoded using base64
JWT Payload - consist of actual data and additional information. there are three types of claim - register, public and private
JWT Signature - created using algorithm in the header and secret key. secret is saved on server and used to verify authenticity.

openssl rand -hex 32 - to generate random secret key for JWT
"""

from fastapi import APIRouter, Depends, HTTPException, Request  # APIRouter for route grouping, Depends for dependency injection
from pydantic import BaseModel, EmailStr, field_validator  # For data validation and schema definition
from ..models import User  # User model from database
from passlib.context import CryptContext  # For password hashing and verification
from typing import Annotated  # For type hints with metadata
from ..database import SessionLocal  # Session factory for database connections
from sqlalchemy.orm import Session  # Database session type
from starlette import status  # HTTP status codes
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer  # OAuth2 security utilities
from jose import jwt, JWTError  # JWT token creation and error handling
from datetime import timedelta, datetime, timezone  # For token expiration time calculations


router = APIRouter(
    prefix="/auth",  # All routes in this router will start with /auth
    tags=["auth"]  # Groups routes under "auth" tag in API documentation
)

# Secret key used to sign and verify JWT tokens - should be kept secure
SECRET_KEY="e80238c316e1cb0340204bf7df5e2a9d3e0988629c2085b3eff76004b27c105a"

# Algorithm used for JWT encoding - HS256 is a widely used algorithm
ALGORITHM="HS256"

# Creates a bcrypt context for hashing and verifying passwords
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 bearer token configuration - specifies where the token endpoint is
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="auth/token")

# Request model for user registration - validates incoming data
class CreateUserRequest(BaseModel):
    username: str
    email: EmailStr
    first_name: str
    last_name: str
    password: str
    role: str
    phone_number: str
    @field_validator("email")
    @classmethod
    def restrict_to_google_domain(cls, value: str) -> str:
        email_lower = value.lower()
        if not (
            email_lower.endswith("@gmail.com")
            or email_lower.endswith("@googlemail.com")
        ):
            raise ValueError("Only Google email addresses (@gmail.com) are allowed.")

        return value

# Response model for token endpoint - returns the JWT token
class Token(BaseModel):
    access_token: str  # The JWT token to be used for subsequent authenticated requests
    token_type: str  # Type of token (typically "bearer")

# Dependency function that provides database connection to routes
def get_db():
    db = SessionLocal()  # Creates a new database session
    try:
        yield db  # Provides the connection to the route
    finally:
        db.close()  # Closes the connection after the request is completed

# Type dependency - annotates that db_dependancy is a Session provided by get_db function
db_dependancy = Annotated[Session, Depends(get_db)]


# Function to create a JWT token with user information
def create_access_token(username: str, user_id: int, role: str, expire_delta: timedelta):
    encode = { "sub": username, "id": user_id, "role": role}  # Create token payload with user data
    expire = datetime.now(timezone.utc) + expire_delta  # Calculate expiration time
    encode.update({ "exp": expire })  # Add expiration time to payload

    # Encode and sign the JWT token using the secret key
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


# Function to verify user credentials
def authenticate_user(username: str, password: str, db):
    user = db.query(User).filter(User.username == username).first()  # Query database for user by username
    if not user:  # User doesn't exist
        return False
    if not bcrypt_context.verify(password, user.hashed_password):  # Verify password against stored hash
        return False
    return user  # Return user object if authentication successful

# Dependency function to verify and extract user from JWT token
async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)], db: db_dependancy):
    try:
        # Decode the JWT token using the secret key and algorithm
        payload = jwt.decode(token=token, key=SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")  # Extract username from token payload
        user_id: int = payload.get("id")  # Extract user ID from token payload
        user_role: str = payload.get("role")  # Extract user role from token payload
        
        # Validate that required fields exist in token
        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")
    
        # Return user information extracted from valid token
        return { "username": username, "id": user_id, "user_role": user_role }
    except JWTError:  # Token is invalid or tampered with
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")

    


# POST endpoint to register a new user
@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependancy, create_user_request: CreateUserRequest):
    # Create new User model instance with data from request
    create_user_model = User(
        email=create_user_request.email,
        username=create_user_request.username,
        first_name=create_user_request.first_name,
        last_name=create_user_request.last_name,
        role=create_user_request.role,
        hashed_password=bcrypt_context.hash(create_user_request.password),  # Hash password before storing
        is_active=True,  # Set user as active
        phone_number=create_user_request.phone_number
    )

    db.add(create_user_model)  # Add user to database session
    db.commit()  # Commit transaction to save user to database

# POST endpoint to login and receive JWT token
@router.post("/token", response_model=Token ,status_code=status.HTTP_200_OK)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependancy):
    # Verify username and password against database
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:  # Authentication failed
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")
    
    # Create JWT token valid for 20 minutes
    token = create_access_token(user.username, user.id, user.role, timedelta(minutes=20))
    # Return token to client for future authenticated requests
    return { "access_token": token, "token_type": "bearer"}
    
