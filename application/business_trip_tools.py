"""
출장 준비를 위한 유틸리티 도구들
"""
import os
import requests
from datetime import datetime
from typing import Dict, Any

def get_weather_info(destination: str, date: str = None) -> Dict[str, Any]:
    """
    목적지의 날씨 정보를 가져옵니다.
    
    Args:
        destination: 목적지 도시명
        date: 날짜 (선택사항)
        
    Returns:
        날씨 정보 딕셔너리
    """
    api_key = os.getenv('WEATHER_API_KEY')
    if not api_key:
        return {
            "temperature": "정보 없음",
            "condition": "정보 없음",
            "description": "날씨 API 키가 설정되지 않았습니다."
        }
    
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={destination}&appid={api_key}&units=metric&lang=kr"
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            return {
                "temperature": f"{data['main']['temp']}°C",
                "feels_like": f"{data['main']['feels_like']}°C",
                "condition": data['weather'][0]['main'],
                "description": data['weather'][0]['description'],
                "humidity": f"{data['main']['humidity']}%"
            }
        else:
            return {
                "temperature": "15-20°C",
                "condition": "맑음",
                "description": "날씨 정보를 가져올 수 없습니다."
            }
    except Exception as e:
        return {
            "temperature": "15-20°C",
            "condition": "맑음",
            "description": f"날씨 조회 오류: {str(e)}"
        }

def get_country_info(destination: str) -> Dict[str, Any]:
    """
    목적지 국가의 기본 정보를 가져옵니다.
    
    Args:
        destination: 목적지
        
    Returns:
        국가 정보 딕셔너리
    """
    country_data = {
        "일본": {
            "voltage": "100V",
            "plug_type": "A/B",
            "currency": "JPY",
            "timezone": "UTC+9",
            "language": "일본어",
            "business_culture": "보수적"
        },
        "도쿄": {
            "voltage": "100V",
            "plug_type": "A/B",
            "currency": "JPY",
            "timezone": "UTC+9",
            "language": "일본어",
            "business_culture": "보수적"
        },
        "미국": {
            "voltage": "110V",
            "plug_type": "A/B",
            "currency": "USD",
            "timezone": "UTC-5~-8",
            "language": "영어",
            "business_culture": "캐주얼"
        },
        "뉴욕": {
            "voltage": "110V",
            "plug_type": "A/B",
            "currency": "USD",
            "timezone": "UTC-5",
            "language": "영어",
            "business_culture": "캐주얼"
        },
        "중국": {
            "voltage": "220V",
            "plug_type": "A/C/I",
            "currency": "CNY",
            "timezone": "UTC+8",
            "language": "중국어",
            "business_culture": "보수적"
        },
        "부산": {
            "voltage": "220V",
            "plug_type": "C/F",
            "currency": "KRW",
            "timezone": "UTC+9",
            "language": "한국어",
            "business_culture": "보수적"
        },
        "서울": {
            "voltage": "220V",
            "plug_type": "C/F",
            "currency": "KRW",
            "timezone": "UTC+9",
            "language": "한국어",
            "business_culture": "보수적"
        }
    }
    
    # 목적지에 해당하는 국가 정보 찾기
    for country, info in country_data.items():
        if country in destination:
            return info
    
    # 기본값
    return {
        "voltage": "220V",
        "plug_type": "C",
        "currency": "USD",
        "timezone": "UTC+0",
        "language": "영어",
        "business_culture": "비즈니스 캐주얼"
    }

def calculate_trip_duration(start_date: str, end_date: str) -> int:
    """
    출장 기간을 계산합니다.
    
    Args:
        start_date: 시작일 (YYYY-MM-DD)
        end_date: 종료일 (YYYY-MM-DD)
        
    Returns:
        출장 기간 (일)
    """
    try:
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')
        return (end - start).days + 1
    except:
        return 1

def format_currency(amount: float, currency: str = "KRW") -> str:
    """
    통화 포맷팅
    
    Args:
        amount: 금액
        currency: 통화 코드
        
    Returns:
        포맷된 통화 문자열
    """
    currency_symbols = {
        "KRW": "₩",
        "USD": "$",
        "JPY": "¥",
        "CNY": "¥",
        "EUR": "€"
    }
    
    symbol = currency_symbols.get(currency, currency)
    return f"{symbol}{amount:,.0f}"

def get_season_info(destination: str, date: str) -> Dict[str, Any]:
    """
    목적지의 계절 정보를 가져옵니다.
    
    Args:
        destination: 목적지
        date: 날짜 (YYYY-MM-DD)
        
    Returns:
        계절 정보 딕셔너리
    """
    try:
        month = int(date.split('-')[1])
        
        # 북반구 기준 계절 정보
        if destination in ["일본", "도쿄", "미국", "뉴욕", "중국", "서울"]:
            if month in [12, 1, 2]:
                return {"season": "겨울", "temp_range": "추위", "clothing": "두꺼운 옷"}
            elif month in [3, 4, 5]:
                return {"season": "봄", "temp_range": "온화", "clothing": "가벼운 겉옷"}
            elif month in [6, 7, 8]:
                return {"season": "여름", "temp_range": "더위", "clothing": "가벼운 옷"}
            else:
                return {"season": "가을", "temp_range": "선선", "clothing": "가벼운 겉옷"}
        
        # 남반구는 반대
        else:
            if month in [12, 1, 2]:
                return {"season": "여름", "temp_range": "더위", "clothing": "가벼운 옷"}
            elif month in [3, 4, 5]:
                return {"season": "가을", "temp_range": "선선", "clothing": "가벼운 겉옷"}
            elif month in [6, 7, 8]:
                return {"season": "겨울", "temp_range": "추위", "clothing": "두꺼운 옷"}
            else:
                return {"season": "봄", "temp_range": "온화", "clothing": "가벼운 겉옷"}
    except:
        return {"season": "알 수 없음", "temp_range": "보통", "clothing": "계절에 맞는 옷"}

def validate_trip_info(trip_info: Dict[str, Any]) -> Dict[str, Any]:
    """
    출장 정보 유효성 검사
    
    Args:
        trip_info: 출장 정보
        
    Returns:
        검증 결과
    """
    errors = []
    
    if not trip_info.get('destination'):
        errors.append("목적지가 입력되지 않았습니다.")
    
    if not trip_info.get('start_date'):
        errors.append("시작일이 입력되지 않았습니다.")
    
    if not trip_info.get('end_date'):
        errors.append("종료일이 입력되지 않았습니다.")
    
    if trip_info.get('start_date') and trip_info.get('end_date'):
        try:
            start = datetime.strptime(trip_info['start_date'], '%Y-%m-%d')
            end = datetime.strptime(trip_info['end_date'], '%Y-%m-%d')
            if end < start:
                errors.append("종료일이 시작일보다 빠릅니다.")
        except:
            errors.append("날짜 형식이 올바르지 않습니다.")
    
    return {
        "valid": len(errors) == 0,
        "errors": errors
    }