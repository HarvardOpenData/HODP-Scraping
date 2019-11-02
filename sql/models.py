from sqlalchemy import Column, Integer, Text, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# Declare interfaces for the data collected by scrapers


class Score(Base):
    """Gocrimson model"""
    __tablename__ = 'scores'

    team = Column(String(64), primary_key=True)
    season = Column(String(64), primary_key=True)

    overall = Column(String(64))
    conference = Column(String(64))
    streak = Column(String(64))
    home = Column(String(64))
    away = Column(String(64))
    neutral = Column(String(64))

    def __repr__(self):
        return f'<User(team={self.team} season={self.season})'
