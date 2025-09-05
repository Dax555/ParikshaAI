from pydantic import BaseModel

class StudentCreate(BaseModel):
    full_name: str
    email: str

class StudentOut(BaseModel):
    id: int
    full_name: str
    email: str
    total_score: float

    class Config:
        orm_mode = True

class ExamSubmission(BaseModel):
    code_answer: str
    error_answer: str
