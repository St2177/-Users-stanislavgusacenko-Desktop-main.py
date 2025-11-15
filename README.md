# Самосвал360 - Telegram Bot with Regional Binding

Telegram bot for waste removal orders with mandatory regional binding and filtering.

## Features

### 1. Automatic Regional Binding
- All orders automatically save user's `federal_district` and `region`
- Regional information is mandatory for order creation
- Orders cannot be created without user's region being set

### 2. Regional Filtering
- Search results show only orders from user's region
- Contractors receive notifications only for orders in their region
- Optimized database queries with composite indexes

### 3. User Region Management
- New users must select region on first bot start
- Existing users without region are prompted to select one
- Region can be changed through profile settings
- Region selection uses full RUSSIAN_REGIONS system

### 4. Enhanced UI
- Order cards display region and federal district
- Notifications include regional information
- Clear indication of regional filtering in search results

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
python main.py
```

## Database Models

### User Model
- `telegram_id` - Unique Telegram user ID
- `federal_district` - User's federal district (indexed)
- `region` - User's region (indexed)
- `is_contractor` - Whether user is a contractor

### Order Model
- `user_id` - Foreign key to User
- `order_type` - Type of order (bring, take_away, find_dump)
- `federal_district` - Order's federal district (mandatory, indexed)
- `region` - Order's region (mandatory, indexed)
- `status` - Order status (active, in_progress, completed, cancelled)

Composite index on `(region, federal_district, status)` for optimal search performance.

## Key Functions

### `create_order_safely_fast()`
Creates order with automatic regional binding from user profile.

### `finish_search()`
Searches orders with automatic filtering by user's region.

### `check_user_region()`
Validates that user has region set up.

### `format_order_card()`
Formats order information including regional details.

## Regional System

The bot uses comprehensive `RUSSIAN_REGIONS` data structure covering:
- Центральный федеральный округ (CFD)
- Северо-Западный федеральный округ (NFD)
- Южный федеральный округ (SFD)
- Северо-Кавказский федеральный округ (NCFD)
- Приволжский федеральный округ (PFD)
- Уральский федеральный округ (UFD)
- Сибирский федеральный округ (SIB)
- Дальневосточный федеральный округ (DFD)

Each district contains all its regions for accurate geographical binding.

## Testing

```bash
pytest test_regional.py -v
```

Tests cover:
- Regional data structure validation
- User and order model creation
- Automatic regional binding
- Regional filtering in search
- Order card formatting
- Edge cases (users without region, cross-region filtering)

## Bot Commands

- `/start` - Start bot (with region setup if needed)
- `/search` - Search orders in user's region
- `/profile` - View profile and change region

## Implementation Details

### Backward Compatibility
- Existing orders without region continue to work
- Users without region are prompted to select one
- No breaking changes to existing functionality

### Performance Optimization
- Composite database indexes for efficient regional queries
- Filtered queries at database level
- Minimal data transfer

### Security
- Region changes only through explicit user action
- No automatic region switching
- Region validation on all operations