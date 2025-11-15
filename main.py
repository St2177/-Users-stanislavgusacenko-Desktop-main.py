"""
Самосвал360 - Core business logic for regional binding and filtering
Main module with regional binding and filtering logic (Telegram bot integration separate)
"""

import logging
from datetime import datetime
from typing import Optional, List, Dict

from models import User, Order, init_db
from regions import RUSSIAN_REGIONS, get_regions_by_district

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def check_user_region(user_id: int) -> bool:
    """
    Check if user has region set up
    
    Args:
        user_id: Telegram user ID
        
    Returns:
        True if user has region, False otherwise
    """
    user = await User.get_or_none(telegram_id=user_id)
    if not user:
        return False
    return bool(user.region and user.federal_district)


async def get_federal_districts() -> List[Dict[str, str]]:
    """Get list of federal districts for selection"""
    districts = []
    for district_code, district_data in RUSSIAN_REGIONS.items():
        districts.append({
            'code': district_code,
            'name': district_data['name']
        })
    return districts


async def get_regions_for_district(district_code: str) -> List[Dict[str, str]]:
    """Get list of regions for a specific district"""
    regions_list = get_regions_by_district(district_code)
    return [
        {'code': code, 'name': name}
        for code, name in regions_list
    ]


async def set_user_region(user_id: int, district_name: str, region_name: str) -> bool:
    """
    Set user's region and federal district
    
    Args:
        user_id: Telegram user ID
        district_name: Federal district name
        region_name: Region name
        
    Returns:
        True if successful, False otherwise
    """
    try:
        user = await User.get_or_none(telegram_id=user_id)
        if not user:
            logger.warning(f"User {user_id} not found")
            return False
        
        user.federal_district = district_name
        user.region = region_name
        await user.save()
        
        logger.info(f"Set region for user {user_id}: {region_name}, {district_name}")
        return True
    except Exception as e:
        logger.error(f"Failed to set region for user {user_id}: {e}")
        return False


async def create_order_safely_fast(
    user_id: int,
    order_type: str,
    description: str,
    **kwargs
) -> Optional[Order]:
    """
    Create order with automatic region binding
    
    Args:
        user_id: Telegram user ID
        order_type: Type of order (bring, take_away, find_dump)
        description: Order description
        **kwargs: Additional order parameters
        
    Returns:
        Created Order object or None if user has no region
    """
    user = await User.get_or_none(telegram_id=user_id)
    if not user or not user.region or not user.federal_district:
        logger.warning(f"User {user_id} has no region set")
        return None
    
    # Create order with regional binding
    order = await Order.create(
        user_id=user.id,
        order_type=order_type,
        description=description,
        federal_district=user.federal_district,
        region=user.region,
        status='active',
        created_at=datetime.now(),
        **kwargs
    )
    
    logger.info(f"Order {order.id} created in region {user.region}")
    return order


async def bring_publish_ultrafast(user_id: int, order_data: dict) -> Optional[Order]:
    """
    Fast publish for 'bring' type orders with regional information
    
    Args:
        user_id: Telegram user ID
        order_data: Order data dictionary
        
    Returns:
        Created Order object or None
    """
    order = await create_order_safely_fast(
        user_id=user_id,
        order_type='bring',
        description=order_data.get('description', ''),
        volume=order_data.get('volume'),
        address=order_data.get('address'),
        price=order_data.get('price')
    )
    
    if order:
        # Notify contractors in the same region
        await notify_contractors_in_region(order)
    
    return order


async def waste_publish_step(user_id: int, order_data: dict) -> Optional[Order]:
    """
    Publish waste removal order with regional information
    
    Args:
        user_id: Telegram user ID
        order_data: Order data dictionary
        
    Returns:
        Created Order object or None
    """
    order = await create_order_safely_fast(
        user_id=user_id,
        order_type='take_away',
        description=order_data.get('description', ''),
        waste_type=order_data.get('waste_type'),
        volume=order_data.get('volume'),
        address=order_data.get('address'),
        price=order_data.get('price')
    )
    
    if order:
        # Notify contractors in the same region
        await notify_contractors_in_region(order)
    
    return order


async def notify_contractors_in_region(order: Order):
    """
    Notify contractors about new order in their region
    
    Args:
        order: Order object
    """
    # Get user who created the order
    user = await User.get(id=order.user_id)
    
    # Find contractors in the same region
    contractors = await User.filter(
        region=order.region,
        federal_district=order.federal_district,
        is_contractor=True
    )
    
    message_text = (
        f"🆕 Новый заказ в вашем регионе!\n\n"
        f"📍 Регион: {order.region}\n"
        f"🗺 Федеральный округ: {order.federal_district}\n"
        f"📋 Тип: {order.order_type}\n"
        f"📝 Описание: {order.description}\n"
    )
    
    if hasattr(order, 'price') and order.price:
        message_text += f"💰 Цена: {order.price} руб.\n"
    
    logger.info(f"Would notify {len(contractors)} contractors about order {order.id}")
    
    # Note: Actual notification implementation would go here
    # This is a placeholder for the Telegram bot notification logic
    return message_text, len(contractors)


async def finish_search(user_id: int, search_params: Optional[dict] = None) -> List[Order]:
    """
    Search orders with regional filtering
    
    Args:
        user_id: Telegram user ID
        search_params: Optional search parameters
        
    Returns:
        List of orders in user's region
    """
    user = await User.get_or_none(telegram_id=user_id)
    if not user or not user.region:
        logger.warning(f"User {user_id} has no region for search")
        return []
    
    # Build query with regional filter
    query = Order.filter(
        region=user.region,
        federal_district=user.federal_district,
        status='active'
    )
    
    # Apply additional filters if provided
    if search_params:
        if 'order_type' in search_params:
            query = query.filter(order_type=search_params['order_type'])
        if 'min_price' in search_params:
            query = query.filter(price__gte=search_params['min_price'])
        if 'max_price' in search_params:
            query = query.filter(price__lte=search_params['max_price'])
    
    # Exclude user's own orders
    query = query.exclude(user_id=user.id)
    
    orders = await query.order_by('-created_at')
    logger.info(f"Found {len(orders)} orders in region {user.region} for user {user_id}")
    
    return orders


def format_order_card(order: Order) -> str:
    """
    Format order information as a card with region display
    
    Args:
        order: Order object
        
    Returns:
        Formatted string with order information
    """
    card = (
        f"📋 Заказ #{order.id}\n"
        f"📍 Регион: {order.region}\n"
        f"🗺 Федеральный округ: {order.federal_district}\n"
        f"📝 Тип: {order.order_type}\n"
        f"📄 Описание: {order.description}\n"
    )
    
    if hasattr(order, 'price') and order.price:
        # Convert Decimal to float to avoid scientific notation
        price_value = float(order.price)
        card += f"💰 Цена: {price_value:.2f} руб.\n"
    
    if hasattr(order, 'volume') and order.volume:
        card += f"📦 Объем: {order.volume} м³\n"
    
    if hasattr(order, 'address') and order.address:
        card += f"🏠 Адрес: {order.address}\n"
    
    card += f"📅 Создан: {order.created_at.strftime('%d.%m.%Y %H:%M')}\n"
    
    return card


async def main():
    """Main function to initialize the system"""
    # Initialize database
    await init_db()
    logger.info("System initialized")


if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
