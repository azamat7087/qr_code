from fastapi.security import OAuth2PasswordBearer
from users.schemas import User
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

