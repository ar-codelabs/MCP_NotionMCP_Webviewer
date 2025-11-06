"""
출장 준비 종합 리포트 생성을 위한 MCP 서버
"""
from mcp.server.fastmcp import FastMCP
from business_trip_orchestrator import BusinessTripOrchestrator
import json
import asyncio
import re

mcp = FastMCP(
    name="business-trip-orchestrator",
    instructions=(
        "You are a comprehensive business trip preparation assistant. "
        "You coordinate 6 specialized agents to create complete trip preparation reports."
    ),
)

@mcp.tool()
def create_comprehensive_trip_report(destination: str, start_date: str = "", end_date: str = "", purpose: str = "업무 출장", accommodation: str = "") -> str:
    """
    Create a comprehensive business trip preparation report using 6 specialized agents.
    
    Args:
        destination: The destination city or country
        start_date: Start date in YYYY-MM-DD format (optional)
        end_date: End date in YYYY-MM-DD format (optional)
        purpose: Purpose of the trip (default: 업무 출장)
        accommodation: Accommodation information (optional)
    
    Returns:
        Comprehensive trip preparation report as formatted string
    """
    try:
        # 기간 계산
        duration_days = 3  # 기본값
        if start_date and end_date:
            from datetime import datetime
            try:
                start = datetime.strptime(start_date, '%Y-%m-%d')
                end = datetime.strptime(end_date, '%Y-%m-%d')
                duration_days = (end - start).days + 1
            except:
                pass
        
        # 출장 정보 구성
        trip_info = {
            "destination": destination,
            "start_date": start_date or "미정",
            "end_date": end_date or "미정", 
            "duration_days": duration_days,
            "purpose": purpose,
            "accommodation": accommodation or "미정"
        }
        
        # 오케스트레이터 실행
        orchestrator = BusinessTripOrchestrator()
        
        # 진행률 콜백 함수
        progress_messages = []
        def progress_callback(message, percent):
            progress_messages.append(f"[{percent}%] {message}")
        
        # 비동기 실행을 동기로 변환
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(orchestrator.analyze_business_trip(trip_info, progress_callback))
            
            # 진행률 메시지와 최종 결과 결합
            progress_info = "\n".join(progress_messages)
            final_report = result.get("formatted", "리포트 생성 중 오류가 발생했습니다.")
            
            return f"📈 진행 상황:\n{progress_info}\n\n{final_report}"
        finally:
            loop.close()
            
    except Exception as e:
        return f"종합 리포트 생성 중 오류: {str(e)}"

@mcp.tool()
def detect_trip_request(query: str) -> str:
    """
    Detect if the query is asking for business trip preparation.
    
    Args:
        query: User query to analyze
    
    Returns:
        JSON string with detection result and extracted information
    """
    # 출장 관련 키워드 패턴
    trip_keywords = [
        r'출장.*준비', r'여행.*준비', r'출장.*가이드', r'여행.*가이드',
        r'출장.*리포트', r'여행.*리포트', r'출장.*계획', r'여행.*계획',
        r'출장.*갑니다', r'여행.*갑니다', r'출장.*가요', r'여행.*가요',
        r'준비.*해.*주세요', r'가이드.*만들어', r'리포트.*작성'
    ]
    
    # 목적지 패턴 (도시/국가명)
    destination_patterns = [
        r'(도쿄|일본|Tokyo)', r'(뉴욕|미국|New York)', r'(서울|부산|대구|인천)',
        r'(싱가포르|Singapore)', r'(홍콩|Hong Kong)', r'(상하이|베이징|중국)',
        r'(런던|파리|독일|영국|프랑스)', r'(방콕|태국)', r'(시드니|호주)'
    ]
    
    # 기간 패턴
    duration_patterns = [
        r'(\d+)박(\d+)일', r'(\d+)일간?', r'(\d+)주일?간?'
    ]
    
    is_trip_request = False
    destination = ""
    duration = ""
    
    # 출장 키워드 검사
    for pattern in trip_keywords:
        if re.search(pattern, query):
            is_trip_request = True
            break
    
    # 목적지 추출
    for pattern in destination_patterns:
        match = re.search(pattern, query)
        if match:
            destination = match.group(1)
            is_trip_request = True
            break
    
    # 기간 추출
    for pattern in duration_patterns:
        match = re.search(pattern, query)
        if match:
            duration = match.group(0)
            break
    
    result = {
        "is_trip_request": is_trip_request,
        "destination": destination,
        "duration": duration,
        "confidence": "high" if is_trip_request and destination else "low"
    }
    
    return json.dumps(result, ensure_ascii=False)

if __name__ == "__main__":
    print("Starting Business Trip Orchestrator MCP Server...")
    mcp.run(transport="stdio")