"""
Tests for regional binding and filtering functionality
"""

import pytest
import pytest_asyncio
from datetime import datetime

from models import User, Order, init_db, close_db
from main import (
    check_user_region,
    create_order_safely_fast,
    finish_search,
    format_order_card
)
from regions import (
    get_regions_by_district,
    get_district_name,
    get_region_name,
    find_region_by_name,
    validate_region,
    RUSSIAN_REGIONS
)


# Setup for tests
@pytest_asyncio.fixture(scope="function", autouse=True)
async def setup_db():
    """Initialize test database before each test"""
    await init_db('sqlite://:memory:')
    yield
    await close_db()


class TestRegions:
    """Test regional data and functions"""
    
    def test_russian_regions_structure(self):
        """Test that RUSSIAN_REGIONS has correct structure"""
        assert len(RUSSIAN_REGIONS) > 0
        
        for district_code, district_data in RUSSIAN_REGIONS.items():
            assert 'name' in district_data
            assert 'regions' in district_data
            assert len(district_data['regions']) > 0
    
    def test_get_regions_by_district(self):
        """Test getting regions by district"""
        regions = get_regions_by_district('CFD')
        assert len(regions) > 0
        assert ('MOW', 'Москва') in regions
        
        # Test invalid district
        regions = get_regions_by_district('INVALID')
        assert len(regions) == 0
    
    def test_get_district_name(self):
        """Test getting district name"""
        name = get_district_name('CFD')
        assert name == 'Центральный федеральный округ'
        
        # Test invalid district
        name = get_district_name('INVALID')
        assert name is None
    
    def test_get_region_name(self):
        """Test getting region name"""
        name = get_region_name('CFD', 'MOW')
        assert name == 'Москва'
        
        # Test invalid region
        name = get_region_name('CFD', 'INVALID')
        assert name is None
    
    def test_find_region_by_name(self):
        """Test finding region by name"""
        result = find_region_by_name('Москва')
        assert result == ('CFD', 'MOW')
        
        # Test case-insensitive search
        result = find_region_by_name('москва')
        assert result == ('CFD', 'MOW')
        
        # Test invalid region
        result = find_region_by_name('Invalid Region')
        assert result is None
    
    def test_validate_region(self):
        """Test region validation"""
        assert validate_region('CFD', 'MOW') is True
        assert validate_region('CFD', 'INVALID') is False
        assert validate_region('INVALID', 'MOW') is False


class TestModels:
    """Test database models"""
    
    @pytest.mark.asyncio
    async def test_user_creation(self):
        """Test creating user with regional information"""
        user = await User.create(
            telegram_id=123456,
            username='testuser',
            first_name='Test',
            federal_district='Центральный федеральный округ',
            region='Москва'
        )
        
        assert user.id is not None
        assert user.telegram_id == 123456
        assert user.region == 'Москва'
        assert user.federal_district == 'Центральный федеральный округ'
    
    @pytest.mark.asyncio
    async def test_order_creation_with_region(self):
        """Test creating order with mandatory regional fields"""
        user = await User.create(
            telegram_id=123457,
            username='testuser2',
            first_name='Test2',
            federal_district='Центральный федеральный округ',
            region='Москва'
        )
        
        order = await Order.create(
            user_id=user.id,
            order_type='bring',
            description='Test order',
            federal_district='Центральный федеральный округ',
            region='Москва',
            price=5000.00
        )
        
        assert order.id is not None
        assert order.region == 'Москва'
        assert order.federal_district == 'Центральный федеральный округ'
        assert order.status == 'active'


class TestRegionalBinding:
    """Test regional binding in order creation"""
    
    @pytest.mark.asyncio
    async def test_check_user_region(self):
        """Test checking if user has region"""
        # User without region
        user1 = await User.create(
            telegram_id=123458,
            username='noregion',
            first_name='NoRegion'
        )
        has_region = await check_user_region(user1.telegram_id)
        assert has_region is False
        
        # User with region
        user2 = await User.create(
            telegram_id=123459,
            username='withregion',
            first_name='WithRegion',
            federal_district='Центральный федеральный округ',
            region='Москва'
        )
        has_region = await check_user_region(user2.telegram_id)
        assert has_region is True
    
    @pytest.mark.asyncio
    async def test_create_order_safely_fast_with_region(self):
        """Test creating order automatically saves user's region"""
        user = await User.create(
            telegram_id=123460,
            username='orderuser',
            first_name='OrderUser',
            federal_district='Центральный федеральный округ',
            region='Москва'
        )
        
        order = await create_order_safely_fast(
            user_id=user.telegram_id,
            order_type='bring',
            description='Test order with region',
            price=3000.00
        )
        
        assert order is not None
        assert order.region == user.region
        assert order.federal_district == user.federal_district
    
    @pytest.mark.asyncio
    async def test_create_order_without_region_fails(self):
        """Test that order creation fails for user without region"""
        user = await User.create(
            telegram_id=123461,
            username='noregionuser',
            first_name='NoRegionUser'
        )
        
        order = await create_order_safely_fast(
            user_id=user.telegram_id,
            order_type='bring',
            description='This should fail'
        )
        
        assert order is None


class TestRegionalFiltering:
    """Test regional filtering in search"""
    
    @pytest.mark.asyncio
    async def test_finish_search_filters_by_region(self):
        """Test that search returns only orders from user's region"""
        # Create users in different regions
        user_moscow = await User.create(
            telegram_id=123462,
            username='moscow_user',
            first_name='Moscow',
            federal_district='Центральный федеральный округ',
            region='Москва'
        )
        
        user_spb = await User.create(
            telegram_id=123463,
            username='spb_user',
            first_name='SPB',
            federal_district='Северо-Западный федеральный округ',
            region='Санкт-Петербург'
        )
        
        # Create orders in different regions
        order_moscow = await Order.create(
            user_id=user_moscow.id,
            order_type='bring',
            description='Moscow order',
            federal_district='Центральный федеральный округ',
            region='Москва',
            status='active'
        )
        
        order_spb = await Order.create(
            user_id=user_spb.id,
            order_type='bring',
            description='SPB order',
            federal_district='Северо-Западный федеральный округ',
            region='Санкт-Петербург',
            status='active'
        )
        
        # Search from Moscow user - should only see SPB orders (excluding own)
        user_moscow_contractor = await User.create(
            telegram_id=123464,
            username='moscow_contractor',
            first_name='MoscowContractor',
            federal_district='Центральный федеральный округ',
            region='Москва'
        )
        
        results = await finish_search(user_moscow_contractor.telegram_id)
        assert len(results) == 1
        assert results[0].id == order_moscow.id
        assert results[0].region == 'Москва'
    
    @pytest.mark.asyncio
    async def test_finish_search_excludes_own_orders(self):
        """Test that search excludes user's own orders"""
        user = await User.create(
            telegram_id=123465,
            username='test_exclude',
            first_name='TestExclude',
            federal_district='Центральный федеральный округ',
            region='Москва'
        )
        
        # Create order by the user
        await Order.create(
            user_id=user.id,
            order_type='bring',
            description='Own order',
            federal_district='Центральный федеральный округ',
            region='Москва',
            status='active'
        )
        
        # Search should not return own orders
        results = await finish_search(user.telegram_id)
        assert len(results) == 0
    
    @pytest.mark.asyncio
    async def test_finish_search_filters_by_status(self):
        """Test that search only returns active orders"""
        user1 = await User.create(
            telegram_id=123466,
            username='user1',
            first_name='User1',
            federal_district='Центральный федеральный округ',
            region='Москва'
        )
        
        user2 = await User.create(
            telegram_id=123467,
            username='user2',
            first_name='User2',
            federal_district='Центральный федеральный округ',
            region='Москва'
        )
        
        # Create active order
        active_order = await Order.create(
            user_id=user1.id,
            order_type='bring',
            description='Active order',
            federal_district='Центральный федеральный округ',
            region='Москва',
            status='active'
        )
        
        # Create completed order
        await Order.create(
            user_id=user1.id,
            order_type='bring',
            description='Completed order',
            federal_district='Центральный федеральный округ',
            region='Москва',
            status='completed'
        )
        
        # Search should only return active orders
        results = await finish_search(user2.telegram_id)
        assert len(results) == 1
        assert results[0].id == active_order.id
        assert results[0].status == 'active'


class TestOrderCard:
    """Test order card formatting"""
    
    @pytest.mark.asyncio
    async def test_format_order_card(self):
        """Test that order card includes region information"""
        user = await User.create(
            telegram_id=123468,
            username='carduser',
            first_name='CardUser',
            federal_district='Центральный федеральный округ',
            region='Москва'
        )
        
        order = await Order.create(
            user_id=user.id,
            order_type='bring',
            description='Test order for card',
            federal_district='Центральный федеральный округ',
            region='Москва',
            price=5000.00,
            volume=10.0,
            address='Test address, 123',
            status='active'
        )
        
        card = format_order_card(order)
        
        assert 'Москва' in card
        assert 'Центральный федеральный округ' in card
        assert 'Test order for card' in card
        assert '5000.00' in card
        assert '10.0' in card
        assert 'Test address, 123' in card


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
