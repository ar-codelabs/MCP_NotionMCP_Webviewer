import json
import logging
import sys
import os
from mcp.server.fastmcp import FastMCP
from notion_client import Client

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Notion API 키와 페이지 ID 설정
NOTION_API_KEY = os.getenv("NOTION_API_KEY")
NOTION_PAGE_ID = os.getenv("NOTION_PAGE_ID")

mcp = FastMCP(
    name="mcp-notion",
    instructions="Notion API를 사용하여 페이지를 생성하고 관리합니다."
)

@mcp.tool()
def add_to_notion_page(title: str, content: str) -> str:
    """
    지정된 Notion 페이지에 내용을 추가합니다.
    
    Args:
        title: 제목
        content: 추가할 내용
    
    Returns:
        추가 결과
    """
    try:
        if not NOTION_API_KEY:
            return "Notion API 키가 설정되지 않았습니다."
            
        if not NOTION_PAGE_ID:
            return "Notion 페이지 ID가 설정되지 않았습니다."
            
        notion = Client(auth=NOTION_API_KEY)
        
        # 제목 블록 추가
        title_block = {
            "object": "block",
            "type": "heading_2",
            "heading_2": {
                "rich_text": [{
                    "type": "text",
                    "text": {"content": title}
                }]
            }
        }
        
        # 내용을 2000자씩 나누어 블록 생성
        content_blocks = []
        max_length = 2000
        
        for i in range(0, len(content), max_length):
            chunk = content[i:i + max_length]
            content_blocks.append({
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{
                        "type": "text",
                        "text": {"content": chunk}
                    }]
                }
            })
        
        # 모든 블록을 페이지에 추가
        all_blocks = [title_block] + content_blocks
        
        response = notion.blocks.children.append(
            block_id=NOTION_PAGE_ID,
            children=all_blocks
        )
        
        logger.info(f"블록 추가 성공: {len(all_blocks)}개 블록")
        
        # 저장된 전체 내용을 반환
        full_saved_content = f"📋 Notion에 저장된 전체 내용:\n\n# {title}\n\n{content}"
        return full_saved_content
        
    except Exception as e:
        logger.error(f"Notion 페이지 내용 추가 실패: {str(e)}")
        return f"내용 추가 실패: {str(e)}"

@mcp.tool()
def search_notion_pages(query: str) -> str:
    """
    Notion에서 페이지를 검색합니다.
    
    Args:
        query: 검색할 키워드
    
    Returns:
        검색 결과
    """
    try:
        notion = Client(auth=NOTION_API_KEY)
        
        results = notion.search(
            query=query,
            filter={
                "value": "page",
                "property": "object"
            }
        )
        
        pages = []
        for page in results["results"]:
            title = "제목 없음"
            if "properties" in page and "title" in page["properties"]:
                title_prop = page["properties"]["title"]
                if "title" in title_prop and title_prop["title"]:
                    title = title_prop["title"][0]["text"]["content"]
            
            pages.append({
                "title": title,
                "url": page["url"],
                "id": page["id"]
            })
        
        return json.dumps(pages, ensure_ascii=False, indent=2)
        
    except Exception as e:
        logger.error(f"Notion 검색 실패: {str(e)}")
        return f"검색 실패: {str(e)}"

if __name__ == "__main__":
    mcp.run(transport="stdio")