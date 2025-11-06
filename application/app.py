import streamlit as st 
import logging
import sys
import os
import agent
import chat
import asyncio
import multi_mcp_agent

logging.basicConfig(
    level=logging.INFO,  # Default to INFO level
    format='%(filename)s:%(lineno)d | %(message)s',
    handlers=[
        logging.StreamHandler(sys.stderr)
    ]
)
logger = logging.getLogger("streamlit")

os.environ["DEV"] = "true"  # Skip user confirmation of get_user_input

# title
st.set_page_config(page_title='Plan Agent', page_icon=None, layout="centered", initial_sidebar_state="auto", menu_items=None)

mode_descriptions = {
    "Business_trip_Agent": [
        "MCP를 도구로 활용하는 범용 Agent + 6개 전문 Agent 협력 출장 준비 종합 리포트 생성"
    ]
}

with st.sidebar:
    st.title("♠︎ Business trip Agent")
    
    st.markdown(
        "🚀 출장 관련 질문 시 6개 전문 Agent가 자동으로 협력하여 종합 리포트를 생성합니다!"
    )
    st.markdown(
        "상세한 코드는 [Github]을 참조하세요."
    )

    # radio selection
    mode = st.radio(
        label="⇨ Agent List ",options=["Business_trip_Agent"], index=0
    )   
    st.info(mode_descriptions[mode][0])
    
    # 출장 준비 기능 안내

    with st.expander("📝 출장 질문 예시"):
        st.code("""
도쿄 3박4일 출장 준비 완벽 가이드 만들어주세요
뉴욕 1주일 출장 준비해주세요
싱가포르 5일 출장 종합 리포트 작성해주세요
        """)
    
    # model selection box
    modelName = st.selectbox(
        '🖊️ Model',
        ('Claude 4 Sonnet', 'Claude 4 Sonnet'), index=1
    )

    # debug checkbox
    select_debugMode = st.checkbox('Debug Mode', value=True)
    debugMode = 'Enable' if select_debugMode else 'Disable'

    chat.update(modelName, debugMode)

    # selecttion of single or multi mcp agent
    mcp_agent_mode = st.radio(
        label="MCP Agent 동작방식을 선택하세요. ",options=["Single", "Multiple"], index=1
    )

    st.success(f"Connected to {modelName}", icon="💚")
    clear_button = st.button("대화 초기화", key="clear")

st.title('♠︎ '+ mode)

if clear_button or "messages" not in st.session_state:
    st.session_state.messages = []        
    
    st.session_state.greetings = False
    st.rerun()  

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.greetings = False

# Display chat messages from history on app rerun
def display_chat_messages() -> None:
    """Print message history
    @returns None
    """
    for i, message in enumerate(st.session_state.messages):
        logger.info(f"메시지 {i+1} 표시: role={message['role']}, images={message.get('images', [])}")
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if "images" in message and message["images"]:
                logger.info(f"메시지 {i+1}에서 이미지 {len(message['images'])}개 발견")
                for j, url in enumerate(message["images"]):
                    logger.info(f"메시지 {i+1} 이미지 {j+1} URL: {url}")
                    try:
                        file_name = url[url.rfind('/')+1:] if '/' in url else url
                        st.image(url, caption=file_name, use_container_width=True)
                        logger.info(f"메시지 {i+1} 이미지 {j+1} 표시 성공")
                    except Exception as e:
                        logger.error(f"메시지 {i+1} 이미지 {j+1} 표시 오류: {e}")
                        st.error(f"이미지를 표시할 수 없습니다: {url}")
            else:
                logger.info(f"메시지 {i+1}에 이미지가 없습니다.")

display_chat_messages()

# Greet user
if not st.session_state.greetings:
    with st.chat_message("assistant"):
        intro = "Business Trip 계획 Agent입니다. \n[Country,City,Date,trip purpose] 를 알려주시면 Agentic AI가 계획을 세워드립니다."
        st.markdown(intro)
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": intro})
        st.session_state.greetings = True

if clear_button or "messages" not in st.session_state:
    st.session_state.messages = []        
    uploaded_file = None
    
    st.session_state.greetings = False
    chat.initiate()
    st.rerun()    

# Always show the chat input
if prompt := st.chat_input("메시지를 입력하세요."):
    with st.chat_message("user"):  # display user message in chat message container
        st.markdown(prompt)

    st.session_state.messages.append({"role": "user", "content": prompt})  # add user message to chat history
    prompt = prompt.replace('"', "").replace("'", "")
    logger.info(f"prompt: {prompt}")

    with st.chat_message("assistant"):        
        sessionState = ""            
        
        # 출장 관련 질문 감지
        is_trip_question = any(keyword in prompt.lower() for keyword in [
            '출장', '여행', '가이드', '리포트', '준비', '도쿄', '뉴욕', '싱가포르'
        ])
        
        if is_trip_question:
            # 출장 준비 전용 UI
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # 6개 Agent 진행률 표시
            agent_status = st.columns(6)
            agent_names = ["LocationAnalyzer", "DressCodeAdvisor", "QuantityCalculator", 
                          "LocalRequirements", "LocalIntelligence", "ShoppingCoordinator"]
            
            for i, name in enumerate(agent_names):
                with agent_status[i]:
                    st.write(f"🤖 {name}")
                    st.write("⏳ 대기 중")
            
            status_text.info("🚀 출장 준비 분석 시작...")
            progress_bar.progress(10)
            
            # Agent 실행
            containers = {
                "tools": st.empty(),
                "status": status_text,
                "notification": [st.empty() for _ in range(500)],
                "progress": progress_bar,
                "agent_status": agent_status
            }
            
            response = asyncio.run(agent.run_agent(query=prompt, containers=containers))
            
            # 완료 후 상태 업데이트
            for i, name in enumerate(agent_names):
                with agent_status[i]:
                    st.write(f"🤖 {name}")
                    st.success("✅ 완료")
            
            progress_bar.progress(100)
            status_text.success("✅ 모든 분석 완료!")
            
            image_url = None
        else:
            # 일반 질문 처리
            with st.status("thinking...", expanded=True, state="running") as status:     
                containers = {
                    "tools": st.empty(),
                    "status": st.empty(),
                    "notification": [st.empty() for _ in range(500)]
                }  
                       
                image_url = None
                if mode == "Business_trip_Agent" and mcp_agent_mode == "Single":                                          
                    response = asyncio.run(agent.run_agent(query=prompt, containers=containers))
                else:
                    response, image_url = asyncio.run(multi_mcp_agent.run_agent(query=prompt, containers=containers))

            logger.info(f"image_url type: {type(image_url)}, value: {image_url}")
            assistant_message = {
                "role": "assistant", 
                "content": response,
                "images": image_url if image_url else []
            }
            st.session_state.messages.append(assistant_message)
            
            if image_url:
                if isinstance(image_url, list):
                    valid_image_urls = [url for url in image_url if url and url.strip()]
                    if not valid_image_urls:
                        logger.info("유효한 이미지 URL이 없습니다.")
                        image_url = None
                    else:
                        image_url = valid_image_urls
                elif not image_url or not image_url.strip():
                    logger.info("유효한 이미지 URL이 없습니다.")
                    image_url = None
                
                if image_url:
                    logger.info(f"이미지 표시 시작: {image_url}")
                    if isinstance(image_url, list):
                        logger.info(f"이미지 리스트 길이: {len(image_url)}")
                        for i, url in enumerate(image_url):
                            logger.info(f"이미지 {i+1} URL: {url}")
                            try:
                                file_name = url[url.rfind('/')+1:] if '/' in url else url
                                st.image(url, caption=file_name, use_container_width=True)
                                logger.info(f"이미지 {i+1} 표시 성공")
                            except Exception as e:
                                logger.error(f"이미지 {i+1} 표시 오류: {e}")
                                st.error(f"이미지를 표시할 수 없습니다: {url}")
                    else:
                        logger.info(f"단일 이미지 URL: {image_url}")
                        try:
                            file_name = image_url[image_url.rfind('/')+1:] if '/' in image_url else image_url
                            st.image(image_url, caption=file_name, use_container_width=True)
                            logger.info("단일 이미지 표시 성공")
                        except Exception as e:
                            logger.error(f"단일 이미지 표시 오류: {e}")
                            st.error(f"이미지를 표시할 수 없습니다: {image_url}")
            else:
                logger.info("표시할 이미지가 없습니다.")
            