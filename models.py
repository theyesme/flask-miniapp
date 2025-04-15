# -*- coding: utf-8 -*-
"""
Created on Mon Apr  7 20:59:08 2025

@author: savello
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, BigInteger
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class UserAuth(Base):
    __tablename__ = "user_auth"
    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, nullable=False, unique=True)
    phone = Column(String)
    session_file = Column(String, nullable=False)
    authenticated = Column(Boolean, default=False)
    needs_2fa = Column(Boolean, default=False)
    phone_code_hash = Column(String)

class Post(Base):
    __tablename__ = "posts"
    id = Column(Integer, primary_key=True)
    source_channel = Column(String, nullable=False)
    original_text = Column(String)
    rewritten_text = Column(String)
    media_path = Column(String)
    published_at = Column(DateTime)
    account_used = Column(String)

class ScrapingTask(Base):
    __tablename__ = "scraping_tasks"
    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, nullable=False)
    source_channel = Column(String, nullable=False)
    dest_channel = Column(String, nullable=False)
    task_id = Column(String, nullable=False)  # Celery task ID
    last_message_id = Column(BigInteger, default=0)  # Track last scraped message