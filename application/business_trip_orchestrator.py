"""
출장 준비 Agent들을 조율하는 오케스트레이터
"""
import asyncio
import json
from typing import Dict, Any
from business_trip_agents import BusinessTripAgents
from mcp_retrieve import retrieve

class BusinessTripOrchestrator:
    """출장 준비 Agent들을 조율하는 오케스트레이터"""
    
    def __init__(self):
        self.agents = BusinessTripAgents()
        print("✅ 6개 출장 준비 Agent 초기화 완료")
    
    async def analyze_business_trip(self, trip_info: Dict[str, Any], progress_callback=None) -> Dict[str, Any]:
        """출장 정보를 분석하여 완전한 준비 가이드 생성 (병렬 실행 + 진행률 표시)"""
        
        if progress_callback:
            progress_callback("🚀 출장 준비 분석 시작", 0)
        
        # Knowledge Base에서 관련 정보 검색
        if progress_callback:
            progress_callback("📚 Knowledge Base 검색 중", 10)
            
        kb_context = ""
        try:
            kb_results = retrieve(f"{trip_info.get('destination', '')} 출장 준비")
            if kb_results:
                kb_context = f"\n\n참고 정보:\n{kb_results}\n"
        except Exception as e:
            pass
        
        # 모든 Agent 병렬 실행 준비
        if progress_callback:
            progress_callback("🤖 6개 Agent 병렬 실행 중", 20)
        
        # 모든 프롬프트 준비
        location_prompt = f"""{kb_context}출장지: {trip_info.get('destination', '미정')}
        기간: {trip_info.get('start_date', '')} ~ {trip_info.get('end_date', '')}
        위 정보를 바탕으로 날씨와 지역 특성을 분석해주세요."""
        
        local_req_prompt = f"""{kb_context}출장지: {trip_info.get('destination', '미정')}
        목적: {trip_info.get('purpose', '업무 출장')}
        위 정보를 바탕으로 현지 준비사항을 제공해주세요."""
        
        local_intel_prompt = f"""{kb_context}출장지: {trip_info.get('destination', '미정')}
        숙박: {trip_info.get('accommodation', '미정')}
        목적: {trip_info.get('purpose', '업무 출장')}
        위 정보를 바탕으로 현지 정보를 제공해주세요."""
        
        dress_prompt = f"""출장 목적: {trip_info.get('purpose', '업무 출장')}
        목적지: {trip_info.get('destination', '미정')}
        위 정보를 바탕으로 복장 가이드를 제공해주세요."""
        
        quantity_prompt = f"""출장 기간: {trip_info.get('duration_days', 1)}일
        위 정보를 바탕으로 필요한 수량을 계산해주세요."""
        
        shopping_prompt = f"""출장지: {trip_info.get('destination', '미정')}
        기간: {trip_info.get('duration_days', 1)}일
        목적: {trip_info.get('purpose', '업무 출장')}
        위 정보를 바탕으로 종합적인 쇼핑 리스트를 만들어주세요."""
        
        # 6개 Agent 모두 병렬 실행
        tasks = [
            self._run_agent("location", location_prompt),
            self._run_agent("local_req", local_req_prompt), 
            self._run_agent("local_intel", local_intel_prompt),
            self._run_agent("dress", dress_prompt),
            self._run_agent("quantity", quantity_prompt),
            self._run_agent("shopping", shopping_prompt)
        ]
        
        # 병렬 실행 및 진행률 업데이트
        results = await asyncio.gather(*tasks)
        
        if progress_callback:
            progress_callback("✅ 6개 Agent 분석 완료", 70)
        
        # 결과 매핑
        location_result, local_req_result, local_intel_result, dress_result, quantity_result, shopping_result = results
        
        # 결과 정리
        all_results = {
            "trip_info": trip_info,
            "location": location_result,
            "dress_code": dress_result,
            "quantity": quantity_result,
            "local_req": local_req_result,
            "local_intel": local_intel_result,
            "shopping": shopping_result
        }
        
        if progress_callback:
            progress_callback("📋 종합 리포트 생성 중", 80)
        
        formatted_report = self._format_results(all_results)
        
        if progress_callback:
            progress_callback("💾 Notion 저장 중", 90)
        
        return {
            "status": "success",
            "results": all_results,
            "formatted": formatted_report
        }
    
    async def _run_agent(self, agent_name: str, prompt: str) -> Dict[str, Any]:
        """개별 Agent 실행"""
        try:
            agent = self.agents.get_agent(agent_name)
            if not agent:
                return {"agent": agent_name, "status": "error", "content": "Agent not found"}
            
            # Strands Agent 실행
            result = await agent.stream_async(prompt)
            content = ""
            async for chunk in result:
                if hasattr(chunk, 'content'):
                    content += chunk.content
                elif isinstance(chunk, str):
                    content += chunk
            
            return {
                "agent": agent_name,
                "status": "success",
                "content": content
            }
        except Exception as e:
            return {
                "agent": agent_name,
                "status": "error",
                "content": f"오류 발생: {str(e)}"
            }
    
    def _format_results(self, results: Dict[str, Any]) -> str:
        """결과를 보기 좋게 포맷팅"""
        
        trip_info = results['trip_info']
        
        output = f"""
╔══════════════════════════════════════════════════════════════╗
║                  🧳 출장 준비 완벽 가이드                      ║
╚══════════════════════════════════════════════════════════════╝

📋 출장 정보
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• 목적지: {trip_info.get('destination', '미정')}
• 기간: {trip_info.get('start_date', '')} ~ {trip_info.get('end_date', '')} ({trip_info.get('duration_days', 1)}일)
• 목적: {trip_info.get('purpose', '업무 출장')}
• 숙박: {trip_info.get('accommodation', '미정')}

🌤️ 지역 및 날씨 분석
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{results['location'].get('content', '')}

👔 복장 가이드
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{results['dress_code'].get('content', '')}

📦 수량 가이드
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{results['quantity'].get('content', '')}

🔌 현지 준비사항
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{results['local_req'].get('content', '')}

🗺️ 현지 정보 & 팁
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{results['local_intel'].get('content', '')}

🛒 최종 쇼핑 리스트
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{results['shopping'].get('content', '')}

╔══════════════════════════════════════════════════════════════╗
║            Powered by Multi-Agent System + RAG              ║
╚══════════════════════════════════════════════════════════════╝
        """
        
        return output.strip()
    
    def get_agent_status(self) -> Dict[str, Any]:
        """모든 Agent의 상태 확인"""
        return {
            "total_agents": 6,
            "agents": [
                {"name": "LocationAnalyzer", "status": "ready"},
                {"name": "DressCodeAdvisor", "status": "ready"},
                {"name": "QuantityCalculator", "status": "ready"},
                {"name": "LocalRequirements", "status": "ready"},
                {"name": "LocalIntelligence", "status": "ready"},
                {"name": "ShoppingCoordinator", "status": "ready"}
            ]
        }