# src/models.py
from sqlalchemy import Column, Integer, String, Float, Date, Table
from src.db import Base

class Sale(Base):
    __tablename__ = "sales"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    Date = Column(Date, nullable=False)
    Product = Column(String, nullable=False)
    Quantity = Column(Integer, nullable=False)
    Price = Column(Float, nullable=False)
    Customer_ID = Column(String, nullable=True)
    Region = Column(String, nullable=True)
    Total_Sales = Column(Float, nullable=False)
