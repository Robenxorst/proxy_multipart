from pydantic import BaseModel, validator

# Pydantic модель для валидации входящего запроса
class RequestBody(BaseModel):
    user_id: int
    
    @validator('user_id')
    def check_user_id(cls, v):
        if v <= 0:
            raise ValueError('user_id должен быть положительным числом')
        return v
    
class BodyAutoDor(BaseModel):
    address: str