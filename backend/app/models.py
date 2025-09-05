from sqlalchemy import Column, Integer, String, Float
from .db import Base

class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, index=True, nullable=False)
    email = Column(String, unique=True, index=True)
    password = Column(String, nullable=False)

    code_score = Column(Float, default=0.0)
    error_score = Column(Float, default=0.0)
    total_score = Column(Float, default=0.0)
