"""
Example usage of regional binding and filtering functionality
This demonstrates how to use the core functions
"""

import asyncio
from models import User, Order, init_db, close_db
from main import (
    check_user_region,
    create_order_safely_fast,
    bring_publish_ultrafast,
    waste_publish_step,
    finish_search,
    format_order_card,
    set_user_region,
    get_federal_districts,
    get_regions_for_district,
)
from regions import RUSSIAN_REGIONS


async def example_user_registration():
    """Example: Register new user with region selection"""
    print("\n=== User Registration Example ===")
    
    # Create new user
    user = await User.create(
        telegram_id=999001,
        username='demo_user',
        first_name='Иван'
    )
    print(f"Created user: {user.first_name} (ID: {user.telegram_id})")
    
    # Check if user has region (should be False for new user)
    has_region = await check_user_region(user.telegram_id)
    print(f"Has region: {has_region}")
    
    # Get federal districts for selection
    districts = await get_federal_districts()
    print(f"\nAvailable districts: {len(districts)}")
    for dist in districts[:3]:  # Show first 3
        print(f"  - {dist['name']}")
    
    # User selects Central Federal District
    regions = await get_regions_for_district('CFD')
    print(f"\nRegions in CFD: {len(regions)}")
    for reg in regions[:5]:  # Show first 5
        print(f"  - {reg['name']}")
    
    # Set user's region
    await set_user_region(
        user_id=user.telegram_id,
        district_name='Центральный федеральный округ',
        region_name='Москва'
    )
    
    # Verify region is set
    user = await User.get(telegram_id=user.telegram_id)
    print(f"\nUser region set to: {user.region}, {user.federal_district}")
    has_region = await check_user_region(user.telegram_id)
    print(f"Has region: {has_region}")


async def example_order_creation():
    """Example: Create orders with automatic regional binding"""
    print("\n=== Order Creation Example ===")
    
    # Create user in Moscow
    user_moscow = await User.create(
        telegram_id=999002,
        username='moscow_customer',
        first_name='Алексей',
        federal_district='Центральный федеральный округ',
        region='Москва'
    )
    print(f"Created user in Moscow: {user_moscow.first_name}")
    
    # Create order using create_order_safely_fast
    order1 = await create_order_safely_fast(
        user_id=user_moscow.telegram_id,
        order_type='bring',
        description='Привезти 15 кубов песка на стройку',
        volume=15.0,
        price=7500.00,
        address='ул. Строителей, 25'
    )
    print(f"\nOrder created: #{order1.id}")
    print(f"  Region: {order1.region}")
    print(f"  District: {order1.federal_district}")
    print(f"  Type: {order1.order_type}")
    print(f"  Description: {order1.description}")
    
    # Create order using bring_publish_ultrafast
    order2 = await bring_publish_ultrafast(
        user_id=user_moscow.telegram_id,
        order_data={
            'description': 'Доставка щебня фракции 20-40',
            'volume': 20.0,
            'price': 10000.00,
            'address': 'Промзона, участок 7'
        }
    )
    print(f"\nFast order created: #{order2.id}")
    
    # Create waste removal order
    order3 = await waste_publish_step(
        user_id=user_moscow.telegram_id,
        order_data={
            'description': 'Вывоз строительного мусора',
            'waste_type': 'Бетон, кирпич',
            'volume': 10.0,
            'price': 5000.00,
            'address': 'ул. Ленина, 10, офис 5'
        }
    )
    print(f"Waste removal order created: #{order3.id}")
    
    # Try to create order for user without region (should fail)
    user_no_region = await User.create(
        telegram_id=999003,
        username='no_region_user',
        first_name='Петр'
    )
    order_fail = await create_order_safely_fast(
        user_id=user_no_region.telegram_id,
        order_type='bring',
        description='This should fail'
    )
    print(f"\nOrder without region: {order_fail}")  # Should print None


async def example_regional_search():
    """Example: Search orders with regional filtering"""
    print("\n=== Regional Search Example ===")
    
    # Create users in different regions
    user_moscow = await User.create(
        telegram_id=999004,
        username='moscow_contractor',
        first_name='Сергей',
        federal_district='Центральный федеральный округ',
        region='Москва',
        is_contractor=True
    )
    
    user_spb = await User.create(
        telegram_id=999005,
        username='spb_customer',
        first_name='Дмитрий',
        federal_district='Северо-Западный федеральный округ',
        region='Санкт-Петербург'
    )
    
    user_spb_contractor = await User.create(
        telegram_id=999006,
        username='spb_contractor',
        first_name='Николай',
        federal_district='Северо-Западный федеральный округ',
        region='Санкт-Петербург',
        is_contractor=True
    )
    
    # Create orders in different regions
    order_moscow = await Order.create(
        user_id=user_moscow.id,
        order_type='bring',
        description='Заказ в Москве',
        federal_district='Центральный федеральный округ',
        region='Москва',
        price=5000.00,
        status='active'
    )
    
    order_spb = await Order.create(
        user_id=user_spb.id,
        order_type='take_away',
        description='Заказ в Санкт-Петербурге',
        federal_district='Северо-Западный федеральный округ',
        region='Санкт-Петербург',
        price=3000.00,
        status='active'
    )
    
    # Search from Moscow contractor - should only see Moscow orders
    moscow_orders = await finish_search(user_moscow.telegram_id)
    print(f"\nMoscow contractor sees {len(moscow_orders)} order(s):")
    for order in moscow_orders:
        print(f"  - Order #{order.id} in {order.region}")
    
    # Search from SPB contractor - should only see SPB orders
    spb_orders = await finish_search(user_spb_contractor.telegram_id)
    print(f"\nSPB contractor sees {len(spb_orders)} order(s):")
    for order in spb_orders:
        print(f"  - Order #{order.id} in {order.region}")
    
    # Search with filters
    filtered_orders = await finish_search(
        user_id=user_moscow.telegram_id,
        search_params={
            'order_type': 'bring',
            'min_price': 4000
        }
    )
    print(f"\nFiltered search (Moscow, type=bring, price>=4000): {len(filtered_orders)} order(s)")


async def example_order_cards():
    """Example: Format order cards with regional information"""
    print("\n=== Order Card Formatting Example ===")
    
    # Create user and order
    user = await User.create(
        telegram_id=999007,
        username='card_demo',
        first_name='Владимир',
        federal_district='Центральный федеральный округ',
        region='Москва'
    )
    
    order = await Order.create(
        user_id=user.id,
        order_type='bring',
        description='Доставка песка карьерного',
        federal_district='Центральный федеральный округ',
        region='Москва',
        price=8500.00,
        volume=15.0,
        address='ул. Промышленная, 42',
        status='active'
    )
    
    # Format order card
    card = format_order_card(order)
    print("\nFormatted order card:")
    print(card)


async def example_cross_region_filtering():
    """Example: Demonstrate that cross-region orders are filtered out"""
    print("\n=== Cross-Region Filtering Example ===")
    
    # Create users in different regions
    regions_data = [
        ('Москва', 'Центральный федеральный округ'),
        ('Санкт-Петербург', 'Северо-Западный федеральный округ'),
        ('Краснодар', 'Южный федеральный округ'),
        ('Екатеринбург', 'Уральский федеральный округ'),
    ]
    
    users_created = []
    orders_created = []
    
    for idx, (region, district) in enumerate(regions_data, start=1):
        user = await User.create(
            telegram_id=999010 + idx,
            username=f'user_{region.lower()}',
            first_name=f'User{idx}',
            federal_district=district,
            region=region
        )
        users_created.append(user)
        
        order = await Order.create(
            user_id=user.id,
            order_type='bring',
            description=f'Заказ в регионе {region}',
            federal_district=district,
            region=region,
            price=5000.00,
            status='active'
        )
        orders_created.append(order)
        print(f"Created user and order in {region}")
    
    # Each user should only see orders from their own region
    print("\nSearch results by region:")
    for user in users_created:
        orders = await finish_search(user.telegram_id)
        print(f"  {user.region}: {len(orders)} order(s) visible")
        # Should be 0 because users see only other users' orders, not their own


async def main():
    """Run all examples"""
    print("=" * 60)
    print("Regional Binding and Filtering - Usage Examples")
    print("=" * 60)
    
    # Initialize database
    await init_db('sqlite://example.db')
    
    try:
        # Run examples
        await example_user_registration()
        await example_order_creation()
        await example_regional_search()
        await example_order_cards()
        await example_cross_region_filtering()
        
        print("\n" + "=" * 60)
        print("All examples completed successfully!")
        print("=" * 60)
        
    finally:
        # Cleanup
        await close_db()
        
        # Remove example database
        import os
        if os.path.exists('example.db'):
            os.remove('example.db')
            print("\nCleaned up example database")


if __name__ == '__main__':
    asyncio.run(main())
