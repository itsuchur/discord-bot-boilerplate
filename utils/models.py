# models.py
from sqlalchemy import Column, BigInteger, String, DateTime, Boolean, Integer
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class Guild(Base):
    __tablename__ = 'guilds'

    # Primary key
    id = Column(BigInteger, primary_key=True)

    # Discord-specific fields
    guild_id = Column(BigInteger, unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    owner_id = Column(BigInteger, nullable=False)

    # Guild stats
    member_count = Column(Integer, nullable=False, default=0)
    is_large = Column(Boolean, nullable=False, default=False)

    # Server limits and features
    premium_tier = Column(Integer, nullable=False, default=0)
    max_members = Column(Integer, nullable=True)
    max_presences = Column(Integer, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), nullable=False)
    joined_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Bot-specific fields
    prefix = Column(String(10), nullable=False, default='!')
    is_blacklisted = Column(Boolean, nullable=False, default=False)

    def __repr__(self):
        return f"<Guild id={self.guild_id} name='{self.name}'>"