from sqlalchemy import Column, String, Integer

from src.db.session import Base

class Sessions(Base):
    __tablename__ = "sessions"
    session_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    session_name = Column(String(20), index=True)