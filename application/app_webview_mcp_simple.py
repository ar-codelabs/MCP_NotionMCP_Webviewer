import streamlit as st
import json
import os
import sys
from typing import Dict, List, Any

# 환경변수 설정
@st.cache_data
def setup_notion_env():
    """Notion 환경변수 설정"""
    try:
        with open("application/mcp.json", "r", encoding="utf-8") as f:
            config = json.load(f)
        
        notion_config = config.get("mcpServers", {}).get("notion", {})
        notion_env = notion_config.get("env", {})
        
        api_key = notion_env.get("NOTION_API_KEY", "")
        page_id = notion_env.get("NOTION_PAGE_ID", "")
        
        if not api_key:
            st.error("NOTION_API_KEY가 설정되지 않았습니다.")
            return False
        
        if not page_id:
            st.error("NOTION_PAGE_ID가 설정되지 않았습니다.")
            return False
        
        os.environ["NOTION_API_KEY"] = api_key
        os.environ["NOTION_PAGE_ID"] = page_id
        
        st.success(f"Notion 설정 완료 - Page ID: {page_id[:8]}...")
        return True
    except Exception as e:
        st.error(f"환경변수 설정 실패: {e}")
        return False

# MCP 서버 함수들 import
sys.path.append('application')
from mcp_server_notion import get_notion_page, get_notion_blocks, get_notion_images, get_child_pages

def get_page_content_mcp() -> Dict[str, Any]:
    """페이지 정보 가져오기"""
    if not setup_notion_env():
        return {}
    try:
        result = get_notion_page()
        return json.loads(result) if isinstance(result, str) else result
    except Exception as e:
        st.error(f"페이지 정보 가져오기 실패: {e}")
        return {}

def get_blocks_mcp() -> List[Dict[str, Any]]:
    """블록 정보 가져오기"""
    if not setup_notion_env():
        return []
    try:
        result = get_notion_blocks()
        data = json.loads(result) if isinstance(result, str) else result
        return data.get("blocks", [])
    except Exception as e:
        st.error(f"블록 정보 가져오기 실패: {e}")
        return []

def get_images_mcp() -> List[Dict[str, Any]]:
    """이미지 정보 가져오기"""
    if not setup_notion_env():
        return []
    try:
        result = get_notion_images()
        data = json.loads(result) if isinstance(result, str) else result
        return data.get("images", [])
    except Exception as e:
        st.error(f"이미지 정보 가져오기 실패: {e}")
        return []

def get_child_pages_mcp() -> List[Dict[str, Any]]:
    """하위 페이지 정보 가져오기"""
    if not setup_notion_env():
        return []
    try:
        result = get_child_pages()
        data = json.loads(result) if isinstance(result, str) else result
        return data.get("child_pages", [])
    except Exception as e:
        st.error(f"하위 페이지 정보 가져오기 실패: {e}")
        return []

def render_block(block: Dict[str, Any], level: int = 0) -> None:
    """블록을 렌더링"""
    block_type = block.get("type", "")
    indent = "  " * level
    
    if block_type == "paragraph":
        text = block.get("text", "")
        if text.strip():
            st.write(f"{indent}{text}")
            
    elif block_type.startswith("heading"):
        text = block.get("text", "")
        if block_type == "heading_1":
            st.header(f"{indent}{text}")
        elif block_type == "heading_2":
            st.subheader(f"{indent}{text}")
        else:
            st.write(f"{indent}### {text}")
        
    elif block_type == "bulleted_list_item":
        text = block.get("text", "")
        st.write(f"{indent}• {text}")
        
    elif block_type == "numbered_list_item":
        text = block.get("text", "")
        st.write(f"{indent}1. {text}")
        
    elif block_type == "toggle":
        text = block.get("text", "")
        with st.expander(f"{indent}🔽 {text}"):
            children = block.get("children", [])
            for child in children:
                render_block(child, level + 1)
                    
    elif block_type == "image":
        image_url = block.get("url", "")
        caption = block.get("caption", "")
        
        try:
            st.image(image_url, caption=caption, use_container_width=True)
        except Exception as e:
            st.error(f"이미지 로드 실패: {e}")
            
    elif block_type == "code":
        code_text = block.get("text", "")
        language = block.get("language", "")
        st.code(code_text, language=language)
        
    elif block_type == "quote":
        text = block.get("text", "")
        st.info(f"{indent}> {text}")
    
    # 하위 블록들 렌더링
    children = block.get("children", [])
    if children and block_type != "toggle":
        for child in children:
            render_block(child, level + 1)

def main():
    st.set_page_config(page_title="Notion Page Viewer (MCP Direct)", layout="wide")
    
    st.title("📄 Notion Page Viewer (MCP Direct)")
    st.write("MCP 서버를 직접 import해서 Notion 페이지를 가져옵니다")
    
    # 버튼들
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        show_full_content = st.button("🔍 전체 컨텐츠", use_container_width=True)
    with col2:
        show_title_images = st.button("🖼️ 제목 + 이미지", use_container_width=True)
    with col3:
        show_child_pages = st.button("📑 하위 페이지", use_container_width=True)
    with col4:
        show_raw_data = st.button("🔧 원본 데이터", use_container_width=True)
    
    # 결과 표시 영역
    result_container = st.container()
    
    # 전체 컨텐츠 보기
    if show_full_content:
        with result_container:
            st.subheader("🔍 전체 컨텐츠 (MCP Direct)")
            
            with st.spinner("컨텐츠를 가져오는 중..."):
                blocks = get_blocks_mcp()
                
                if blocks:
                    for block in blocks:
                        render_block(block)
                else:
                    st.info("표시할 컨텐츠가 없습니다.")
    
    # 제목 + 이미지만 보기
    elif show_title_images:
        with result_container:
            st.subheader("🖼️ 제목 + 이미지 (MCP Direct)")
            
            with st.spinner("이미지를 가져오는 중..."):
                images = get_images_mcp()
                
                if images:
                    for i, img in enumerate(images):
                        if img.get("title"):
                            st.subheader(f"📝 {img['title']}")
                        st.write(f"**이미지 {i+1}**")
                        if img.get("caption"):
                            st.write(f"*{img['caption']}*")
                        try:
                            st.image(img["url"], use_container_width=True)
                        except Exception as e:
                            st.error(f"이미지 로드 실패: {e}")
                        st.divider()
                else:
                    st.info("이미지가 없습니다.")
    
    # 하위 페이지 리스트
    elif show_child_pages:
        with result_container:
            st.subheader("📑 하위 페이지 리스트 (MCP Direct)")
            
            with st.spinner("하위 페이지를 가져오는 중..."):
                child_pages = get_child_pages_mcp()
                
                if child_pages:
                    st.write(f"**총 {len(child_pages)}개의 하위 페이지가 있습니다:**")
                    
                    for i, page in enumerate(child_pages, 1):
                        st.write(f"**{i}.** 📄 {page.get('title', '제목 없음')}")
                        if page.get('url'):
                            st.write(f"   🔗 [Notion에서 열기]({page['url']})")
                        st.write("")
                else:
                    st.info("하위 페이지가 없습니다.")
    
    # 원본 데이터 보기
    elif show_raw_data:
        with result_container:
            st.subheader("🔧 원본 데이터 (MCP Direct)")
            
            with st.expander("페이지 정보"):
                page_info = get_page_content_mcp()
                st.json(page_info)
            
            with st.expander("블록 데이터"):
                blocks = get_blocks_mcp()
                st.json(blocks)

if __name__ == "__main__":
    main()