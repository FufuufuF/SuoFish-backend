from pydantic import BaseModel, Field

class SignUp(BaseModel):
    email: str = Field(..., format="email")
    password: str = Field(..., min_length=4, max_length=20)

class SignIn(BaseModel):
    email: str = Field(..., format="email")
    password: str = Field(..., min_length=4, max_length=20)
