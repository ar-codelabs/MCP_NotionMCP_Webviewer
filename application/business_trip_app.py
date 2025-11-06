"""
출장 준비 Multi-Agent 시스템 Streamlit 앱
"""
import streamlit as st
import asyncio
import json
from datetime import datetime, timedelta
from business_trip_orchestrator import BusinessTripOrchestrator

# 페이지 설정
st.set_page_config(
    page_title="🧳 출장 준비 AI Agent",
    page_icon="🧳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS 스타일
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .agent-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #667eea;
        margin: 0.5rem 0;
    }
    .result-box {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border: 1px solid #e0e0e0;
        white-space: pre-wrap;
        font-family: 'Courier New', monospace;
        font-size: 14px;
        line-height: 1.6;
    }
    .status-success {
        color: #28a745;
        font-weight: bold;
    }
    .status-error {
        color: #dc3545;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# 메인 헤더
st.markdown("""
<div class="main-header">
    <h1>🧳 출장 준비 AI Agent</h1>
    <p>6개 전문 Agent가 협력하여 완벽한 출장 준비 가이드를 제공합니다</p>
</div>
""", unsafe_allow_html=True)

# 사이드바 - Agent 상태
with st.sidebar:
    st.header("🤖 Agent 상태")
    
    agents_info = [
        {"name": "LocationAnalyzer", "icon": "📍", "desc": "지역/날씨 분석"},
        {"name": "DressCodeAdvisor", "icon": "👔", "desc": "복장 추천"},
        {"name": "QuantityCalculator", "icon": "📦", "desc": "수량 계산"},
        {"name": "LocalRequirements", "icon": "🔌", "desc": "현지 준비물"},
        {"name": "LocalIntelligence", "icon": "🗺️", "desc": "현지 정보"},
        {"name": "ShoppingCoordinator", "icon": "🛒", "desc": "쇼핑 리스트"}
    ]
    
    for agent in agents_info:
        st.markdown(f"""
        <div class="agent-card">
            <strong>{agent['icon']} {agent['name']}</strong><br>
            <small>{agent['desc']}</small>
        </div>
        """, unsafe_allow_html=True)

# 메인 컨텐츠
col1, col2 = st.columns([1, 1])

with col1:
    st.header("📋 출장 정보 입력")
    
    with st.form("trip_form"):
        destination = st.text_input("🌍 목적지", placeholder="예: 도쿄, 뉴욕, 부산")
        
        col_date1, col_date2 = st.columns(2)
        with col_date1:
            start_date = st.date_input("📅 시작일", datetime.now())
        with col_date2:
            end_date = st.date_input("📅 종료일", datetime.now() + timedelta(days=3))
        
        purpose = st.selectbox("🎯 출장 목적", [
            "업무 미팅", "컨퍼런스 참석", "교육/연수", "프로젝트 수행", 
            "고객 방문", "전시회 참관", "기타"
        ])
        
        accommodation = st.text_input("🏨 숙박", placeholder="예: 호텔명, 게스트하우스")
        
        submit_button = st.form_submit_button("🚀 AI 분석 시작", use_container_width=True)

with col2:
    st.header("💡 사용 가이드")
    
    st.info("""
    **🔄 분석 과정:**
    1. **Knowledge Base 검색** - 관련 출장 정보 조회
    2. **병렬 분석** - 지역/현지정보 동시 분석
    3. **순차 분석** - 복장→수량 의존성 분석
    4. **통합 결과** - 최종 쇼핑 리스트 생성
    """)
    
    st.success("""
    **✨ 제공 정보:**
    - 🌤️ 날씨 맞춤 준비물
    - 👔 비즈니스 복장 가이드
    - 📦 정확한 수량 계산
    - 🔌 현지 필수 정보
    - 🛒 구매처별 쇼핑 리스트
    """)

# 결과 표시 영역
if submit_button and destination:
    # 출장 정보 구성
    duration_days = (end_date - start_date).days + 1
    trip_info = {
        "destination": destination,
        "start_date": start_date.strftime("%Y-%m-%d"),
        "end_date": end_date.strftime("%Y-%m-%d"),
        "duration_days": duration_days,
        "purpose": purpose,
        "accommodation": accommodation
    }
    
    st.header("🔄 분석 진행 상황")
    
    # 진행 상황 표시
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # 오케스트레이터 초기화 및 실행
    try:
        with st.spinner("🤖 AI Agent 시스템 초기화 중..."):
            orchestrator = BusinessTripOrchestrator()
        
        progress_bar.progress(20)
        status_text.text("📚 Knowledge Base 검색 중...")
        
        # 비동기 실행
        async def run_analysis():
            return await orchestrator.analyze_business_trip(trip_info)
        
        # 이벤트 루프 실행
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        result = loop.run_until_complete(run_analysis())
        
        progress_bar.progress(100)
        status_text.text("✅ 분석 완료!")
        
        if result["status"] == "success":
            st.success("🎉 출장 준비 가이드가 완성되었습니다!")
            
            # 결과 표시
            st.header("📋 완벽한 출장 준비 가이드")
            
            # 탭으로 결과 구분
            tab1, tab2, tab3 = st.tabs(["📄 전체 가이드", "🔍 상세 분석", "📊 Agent 결과"])
            
            with tab1:
                st.markdown(f"""
                <div class="result-box">
{result["formatted"]}
                </div>
                """, unsafe_allow_html=True)
            
            with tab2:
                results = result["results"]
                
                st.subheader("🌤️ 지역 및 날씨 분석")
                st.write(results["location"]["content"])
                
                st.subheader("👔 복장 가이드")
                st.write(results["dress_code"]["content"])
                
                st.subheader("📦 수량 가이드")
                st.write(results["quantity"]["content"])
                
                st.subheader("🔌 현지 준비사항")
                st.write(results["local_req"]["content"])
                
                st.subheader("🗺️ 현지 정보")
                st.write(results["local_intel"]["content"])
                
                st.subheader("🛒 쇼핑 리스트")
                st.write(results["shopping"]["content"])
            
            with tab3:
                st.subheader("🤖 각 Agent 실행 결과")
                
                for agent_name, agent_result in results.items():
                    if agent_name != "trip_info":
                        status_class = "status-success" if agent_result.get("status") == "success" else "status-error"
                        st.markdown(f"""
                        **{agent_result.get('agent', agent_name)}**
                        <span class="{status_class}">● {agent_result.get('status', 'unknown')}</span>
                        """, unsafe_allow_html=True)
                        
                        with st.expander(f"상세 결과 보기"):
                            st.write(agent_result.get('content', ''))
        else:
            st.error(f"❌ 분석 중 오류가 발생했습니다: {result.get('message', '알 수 없는 오류')}")
    
    except Exception as e:
        st.error(f"❌ 시스템 오류: {str(e)}")
        st.info("💡 문제가 지속되면 관리자에게 문의하세요.")

elif submit_button and not destination:
    st.warning("⚠️ 목적지를 입력해주세요!")

# 푸터
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 1rem;">
    🤖 Powered by Multi-Agent System + Knowledge Base RAG<br>
    6개 전문 AI Agent가 협력하여 최적의 출장 준비 가이드를 제공합니다
</div>
""", unsafe_allow_html=True)