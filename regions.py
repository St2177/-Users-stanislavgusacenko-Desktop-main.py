"""
Russian regions and federal districts data
"""

from typing import List, Tuple, Optional

# Russian Federal Districts and their regions
RUSSIAN_REGIONS = {
    'CFD': {
        'name': 'Центральный федеральный округ',
        'regions': {
            'MOW': 'Москва',
            'MOS': 'Московская область',
            'BEL': 'Белгородская область',
            'BRY': 'Брянская область',
            'VLA': 'Владимирская область',
            'VOR': 'Воронежская область',
            'IVA': 'Ивановская область',
            'KLU': 'Калужская область',
            'KOS': 'Костромская область',
            'KUR': 'Курская область',
            'LIP': 'Липецкая область',
            'ORL': 'Орловская область',
            'RYA': 'Рязанская область',
            'SMO': 'Смоленская область',
            'TAM': 'Тамбовская область',
            'TVE': 'Тверская область',
            'TUL': 'Тульская область',
            'YAR': 'Ярославская область',
        }
    },
    'NFD': {
        'name': 'Северо-Западный федеральный округ',
        'regions': {
            'SPE': 'Санкт-Петербург',
            'LEN': 'Ленинградская область',
            'KGD': 'Калининградская область',
            'KAR': 'Республика Карелия',
            'KOM': 'Республика Коми',
            'ARK': 'Архангельская область',
            'NEN': 'Ненецкий автономный округ',
            'VOL': 'Вологодская область',
            'MUR': 'Мурманская область',
            'NOV': 'Новгородская область',
            'PSK': 'Псковская область',
        }
    },
    'SFD': {
        'name': 'Южный федеральный округ',
        'regions': {
            'ADY': 'Республика Адыгея',
            'KAL': 'Республика Калмыкия',
            'KRI': 'Республика Крым',
            'SEV': 'Севастополь',
            'KRA': 'Краснодарский край',
            'AST': 'Астраханская область',
            'VGG': 'Волгоградская область',
            'ROS': 'Ростовская область',
        }
    },
    'NCFD': {
        'name': 'Северо-Кавказский федеральный округ',
        'regions': {
            'DAG': 'Республика Дагестан',
            'ING': 'Республика Ингушетия',
            'KB': 'Кабардино-Балкарская Республика',
            'KC': 'Карачаево-Черкесская Республика',
            'SO': 'Республика Северная Осетия — Алания',
            'CHE': 'Чеченская Республика',
            'STA': 'Ставропольский край',
        }
    },
    'PFD': {
        'name': 'Приволжский федеральный округ',
        'regions': {
            'BA': 'Республика Башкортостан',
            'ME': 'Республика Марий Эл',
            'MO': 'Республика Мордовия',
            'TA': 'Республика Татарстан',
            'UD': 'Удмуртская Республика',
            'CHU': 'Чувашская Республика',
            'PER': 'Пермский край',
            'KIR': 'Кировская область',
            'NIZ': 'Нижегородская область',
            'ORE': 'Оренбургская область',
            'PNZ': 'Пензенская область',
            'SAM': 'Самарская область',
            'SAR': 'Саратовская область',
            'ULY': 'Ульяновская область',
        }
    },
    'UFD': {
        'name': 'Уральский федеральный округ',
        'regions': {
            'KGN': 'Курганская область',
            'SVE': 'Свердловская область',
            'TYU': 'Тюменская область',
            'KHM': 'Ханты-Мансийский автономный округ — Югра',
            'YAN': 'Ямало-Ненецкий автономный округ',
            'CHE_OBL': 'Челябинская область',
        }
    },
    'SIB': {
        'name': 'Сибирский федеральный округ',
        'regions': {
            'AL': 'Республика Алтай',
            'TY': 'Республика Тыва',
            'KHA': 'Республика Хакасия',
            'ALT': 'Алтайский край',
            'KRA_SIB': 'Красноярский край',
            'IRK': 'Иркутская область',
            'KEM': 'Кемеровская область',
            'NVS': 'Новосибирская область',
            'OMS': 'Омская область',
            'TOM': 'Томская область',
        }
    },
    'DFD': {
        'name': 'Дальневосточный федеральный округ',
        'regions': {
            'BU': 'Республика Бурятия',
            'SA': 'Республика Саха (Якутия)',
            'ZAB': 'Забайкальский край',
            'KAM': 'Камчатский край',
            'PRI': 'Приморский край',
            'KHA_DV': 'Хабаровский край',
            'AMU': 'Амурская область',
            'MAG': 'Магаданская область',
            'SAK': 'Сахалинская область',
            'YEV': 'Еврейская автономная область',
            'CHU_DV': 'Чукотский автономный округ',
        }
    },
}


def get_regions_by_district(district_code: str) -> List[Tuple[str, str]]:
    """
    Get list of regions for a federal district
    
    Args:
        district_code: Federal district code (e.g., 'CFD', 'NFD')
        
    Returns:
        List of tuples (region_code, region_name)
    """
    if district_code not in RUSSIAN_REGIONS:
        return []
    
    regions = RUSSIAN_REGIONS[district_code]['regions']
    return [(code, name) for code, name in regions.items()]


def get_district_name(district_code: str) -> Optional[str]:
    """
    Get federal district name by code
    
    Args:
        district_code: Federal district code
        
    Returns:
        District name or None if not found
    """
    if district_code not in RUSSIAN_REGIONS:
        return None
    return RUSSIAN_REGIONS[district_code]['name']


def get_region_name(district_code: str, region_code: str) -> Optional[str]:
    """
    Get region name by district and region codes
    
    Args:
        district_code: Federal district code
        region_code: Region code
        
    Returns:
        Region name or None if not found
    """
    if district_code not in RUSSIAN_REGIONS:
        return None
    
    regions = RUSSIAN_REGIONS[district_code]['regions']
    return regions.get(region_code)


def find_region_by_name(region_name: str) -> Optional[Tuple[str, str]]:
    """
    Find district and region codes by region name
    
    Args:
        region_name: Region name to search for
        
    Returns:
        Tuple of (district_code, region_code) or None if not found
    """
    for district_code, district_data in RUSSIAN_REGIONS.items():
        for region_code, name in district_data['regions'].items():
            if name.lower() == region_name.lower():
                return (district_code, region_code)
    return None


def validate_region(district_code: str, region_code: str) -> bool:
    """
    Validate that region belongs to the specified district
    
    Args:
        district_code: Federal district code
        region_code: Region code
        
    Returns:
        True if valid, False otherwise
    """
    if district_code not in RUSSIAN_REGIONS:
        return False
    
    regions = RUSSIAN_REGIONS[district_code]['regions']
    return region_code in regions
