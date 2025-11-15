"""
Database models for Самосвал360 bot
"""

from tortoise import fields
from tortoise.models import Model
from tortoise import Tortoise
from typing import Optional


class User(Model):
    """User model with regional information"""
    id = fields.IntField(pk=True)
    telegram_id = fields.BigIntField(unique=True, index=True)
    username = fields.CharField(max_length=255, null=True)
    first_name = fields.CharField(max_length=255, null=True)
    last_name = fields.CharField(max_length=255, null=True)
    
    # Regional fields
    federal_district = fields.CharField(max_length=255, null=True, index=True)
    region = fields.CharField(max_length=255, null=True, index=True)
    
    # Additional fields
    is_contractor = fields.BooleanField(default=False)
    phone = fields.CharField(max_length=20, null=True)
    
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    
    class Meta:
        table = "users"
    
    def __str__(self):
        return f"User {self.telegram_id} ({self.first_name})"


class Order(Model):
    """Order model with mandatory regional binding"""
    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField('models.User', related_name='orders')
    
    # Order type: bring, take_away, find_dump
    order_type = fields.CharField(max_length=50, index=True)
    description = fields.TextField()
    
    # Regional fields (mandatory)
    federal_district = fields.CharField(max_length=255, index=True)
    region = fields.CharField(max_length=255, index=True)
    
    # Order details
    address = fields.CharField(max_length=500, null=True)
    volume = fields.FloatField(null=True)  # Volume in m³
    waste_type = fields.CharField(max_length=255, null=True)
    price = fields.DecimalField(max_digits=10, decimal_places=2, null=True)
    
    # Status: active, in_progress, completed, cancelled
    status = fields.CharField(max_length=50, default='active', index=True)
    
    # Contractor who took the order
    contractor = fields.ForeignKeyField('models.User', related_name='contractor_orders', null=True)
    
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    completed_at = fields.DatetimeField(null=True)
    
    class Meta:
        table = "orders"
        indexes = [
            # Composite index for regional search
            ('region', 'federal_district', 'status'),
        ]
    
    def __str__(self):
        return f"Order {self.id} ({self.order_type}) in {self.region}"


async def init_db(db_url: str = "sqlite://db.sqlite3"):
    """
    Initialize database connection and create tables
    
    Args:
        db_url: Database connection URL
    """
    await Tortoise.init(
        db_url=db_url,
        modules={'models': ['models']}
    )
    await Tortoise.generate_schemas()


async def close_db():
    """Close database connections"""
    await Tortoise.close_connections()
