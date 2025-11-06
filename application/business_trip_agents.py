"""
출장 준비를 위한 6개 전문 Agent 정의
"""
import boto3
import json
import os
from dotenv import load_dotenv
from strands_agents import Agent
from strands_agents_tools import bedrock_tool

load_dotenv()

class BusinessTripAgents:
    """출장 준비 전문 Agent들을 관리하는 클래스"""
    
    def __init__(self):
        self.bedrock = boto3.client(
            'bedrock-runtime',
            region_name=os.getenv('AWS_REGION', 'us-west-2')
        )
        self.agents = self._initialize_agents()
    
    def _initialize_agents(self):
        """6개 전문 Agent 초기화"""
        
        # 1. 지역 및 날씨 분석 Agent
        location_analyzer = Agent(
            name="LocationAnalyzer",
            instructions="""당신은 출장지 지역과 날씨를 분석하는 전문가입니다.
            목적지의 날씨, 계절, 기후 특성을 분석하고 그에 맞는 준비사항을 추천해주세요.
            
            응답 형식:
            온도범위: [최저-최고]도
            날씨상태: [맑음/흐림/비/눈]
            계절특성: [설명]
            추천사항: [준비물 3-5가지]""",
            model="anthropic.claude-3-sonnet-20240229-v1:0"
        )
        
        # 2. 복장 추천 Agent
        dress_code_advisor = Agent(
            name="DressCodeAdvisor",
            instructions="""당신은 비즈니스 복장 전문가입니다.
            출장 목적, 날씨, 지역 문화를 고려하여 적절한 복장을 추천해주세요.
            
            응답 형식:
            격식수준: [캐주얼/비즈니스캐주얼/포멀]
            추천의류: [구체적인 아이템 5-7가지]
            추천색상: [색상 3가지]
            피해야할것: [부적절한 복장 3가지]""",
            model="anthropic.claude-3-sonnet-20240229-v1:0"
        )
        
        # 3. 수량 계산 Agent
        quantity_calculator = Agent(
            name="QuantityCalculator",
            instructions="""당신은 출장 준비물 수량 계산 전문가입니다.
            출장 기간과 복장 수준을 고려하여 필요한 의류와 용품의 수량을 계산해주세요.
            
            응답 형식:
            의류수량: [아이템:개수, ...]
            액세서리: [아이템:개수, ...]
            기타용품: [아이템:개수, ...]
            총개수: [숫자]개""",
            model="anthropic.claude-3-sonnet-20240229-v1:0"
        )
        
        # 4. 현지 준비물 Agent
        local_requirements = Agent(
            name="LocalRequirements",
            instructions="""당신은 해외/국내 출장 준비물 전문가입니다.
            목적지의 전압, 통화, 필수품 등을 안내해주세요.
            
            응답 형식:
            전압정보: [전압 및 플러그 타입]
            통화정보: [통화 및 환전 팁]
            필수품: [반드시 챙겨야 할 것 5가지]
            현지관습: [알아야 할 문화 3가지]""",
            model="anthropic.claude-3-sonnet-20240229-v1:0"
        )
        
        # 5. 현지 정보 Agent
        local_intelligence = Agent(
            name="LocalIntelligence",
            instructions="""당신은 현지 여행 정보 전문가입니다.
            교통, 식당, 쇼핑, 응급상황 정보를 제공해주세요.
            
            응답 형식:
            교통정보: [이동 수단 및 팁 3가지]
            식당추천: [비즈니스 미팅 적합한 곳 3곳]
            쇼핑정보: [긴급 구매 가능한 곳 3곳]
            응급정보: [병원, 약국, 대사관 정보]""",
            model="anthropic.claude-3-sonnet-20240229-v1:0"
        )
        
        # 6. 쇼핑 리스트 조합 Agent
        shopping_coordinator = Agent(
            name="ShoppingCoordinator",
            instructions="""당신은 출장 준비물 쇼핑 전문가입니다.
            모든 Agent의 정보를 종합하여 최종 쇼핑 리스트를 만들어주세요.
            한국에서 준비할 것과 현지에서 구매할 것을 구분해주세요.
            
            응답 형식:
            🇰🇷 한국에서 준비:
            - 의류: [리스트]
            - 전자기기: [리스트]
            - 기타: [리스트]
            
            🌍 현지에서 구매:
            - 편의점: [리스트]
            - 백화점: [리스트]
            
            💰 예상비용: [금액]
            ⭐ 우선순위: [반드시 필요한 것 5가지]""",
            model="anthropic.claude-3-sonnet-20240229-v1:0"
        )
        
        return {
            "location": location_analyzer,
            "dress": dress_code_advisor,
            "quantity": quantity_calculator,
            "local_req": local_requirements,
            "local_intel": local_intelligence,
            "shopping": shopping_coordinator
        }
    
    def get_agent(self, agent_name: str):
        """특정 Agent 반환"""
        return self.agents.get(agent_name)
    
    def get_all_agents(self):
        """모든 Agent 반환"""
        return self.agents
    
    def get_agent_list(self):
        """Agent 목록 반환"""
        return list(self.agents.keys())