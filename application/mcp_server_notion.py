import json
import logging
import sys
import os
from mcp.server.fastmcp import FastMCP
from notion_client import Client

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Notion API 키와 페이지 ID 설정
def get_notion_credentials():
    return os.getenv("NOTION_API_KEY"), os.getenv("NOTION_PAGE_ID")

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
def get_notion_page() -> str:
    """
    현재 설정된 Notion 페이지 정보를 가져옵니다.
    
    Returns:
        페이지 정보 JSON
    """
    try:
        api_key, page_id = get_notion_credentials()
        if not api_key or not page_id:
            return "Notion API 키 또는 페이지 ID가 설정되지 않았습니다."
        
        notion = Client(auth=api_key)
        page = notion.pages.retrieve(page_id=page_id)
        return json.dumps(page, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"페이지 정보 가져오기 실패: {str(e)}")
        return f"페이지 정보 가져오기 실패: {str(e)}"

@mcp.tool()
def get_notion_blocks() -> str:
    """
    현재 설정된 Notion 페이지의 모든 블록을 재귀적으로 가져옵니다.
    
    Returns:
        블록 정보 JSON
    """
    try:
        api_key, page_id = get_notion_credentials()
        if not api_key or not page_id:
            return json.dumps({"blocks": [], "error": "Notion API 키 또는 페이지 ID가 설정되지 않았습니다."}, ensure_ascii=False)
        
        notion = Client(auth=api_key)
        
        def get_blocks_recursive(block_id):
            blocks = notion.blocks.children.list(block_id=block_id)
            result = []
            
            for block in blocks["results"]:
                block_data = {
                    "id": block["id"],
                    "type": block["type"],
                    "text": "",
                    "url": "",
                    "caption": "",
                    "children": []
                }
                
                # 텍스트 추출
                if block["type"] in ["paragraph", "heading_1", "heading_2", "heading_3", "bulleted_list_item", "numbered_list_item", "toggle", "quote"]:
                    rich_text = block[block["type"]].get("rich_text", [])
                    block_data["text"] = "".join([t.get("plain_text", "") for t in rich_text])
                
                # 이미지 처리
                elif block["type"] == "image":
                    image_data = block["image"]
                    if image_data["type"] == "file":
                        block_data["url"] = image_data["file"]["url"]
                    elif image_data["type"] == "external":
                        block_data["url"] = image_data["external"]["url"]
                    
                    caption = image_data.get("caption", [])
                    block_data["caption"] = "".join([t.get("plain_text", "") for t in caption])
                
                # 코드 처리
                elif block["type"] == "code":
                    rich_text = block["code"].get("rich_text", [])
                    block_data["text"] = "".join([t.get("plain_text", "") for t in rich_text])
                    block_data["language"] = block["code"].get("language", "")
                
                # 하위 블록 처리
                if block.get("has_children", False):
                    block_data["children"] = get_blocks_recursive(block["id"])
                
                result.append(block_data)
            
            return result
        
        blocks = get_blocks_recursive(page_id)
        return json.dumps({"blocks": blocks}, ensure_ascii=False, indent=2)
        
    except Exception as e:
        logger.error(f"블록 가져오기 실패: {str(e)}")
        return f"블록 가져오기 실패: {str(e)}"

@mcp.tool()
def get_notion_images() -> str:
    """
    현재 설정된 Notion 페이지의 모든 이미지를 가져옵니다.
    
    Returns:
        이미지 정보 JSON
    """
    try:
        api_key, page_id = get_notion_credentials()
        if not api_key or not page_id:
            return json.dumps({"images": [], "error": "Notion API 키 또는 페이지 ID가 설정되지 않았습니다."}, ensure_ascii=False)
        
        notion = Client(auth=api_key)
        
        def extract_images_recursive(block_id, current_title=""):
            blocks = notion.blocks.children.list(block_id=block_id)
            images = []
            title = current_title
            
            for block in blocks["results"]:
                # 제목 업데이트
                if block["type"] in ["heading_1", "heading_2", "heading_3"]:
                    rich_text = block[block["type"]].get("rich_text", [])
                    title = "".join([t.get("plain_text", "") for t in rich_text])
                
                # 이미지 처리
                elif block["type"] == "image":
                    image_data = block["image"]
                    image_url = ""
                    
                    if image_data["type"] == "file":
                        image_url = image_data["file"]["url"]
                    elif image_data["type"] == "external":
                        image_url = image_data["external"]["url"]
                    
                    if image_url:
                        caption = image_data.get("caption", [])
                        caption_text = "".join([t.get("plain_text", "") for t in caption])
                        
                        images.append({
                            "url": image_url,
                            "caption": caption_text,
                            "title": title
                        })
                
                # 하위 블록에서도 이미지 찾기
                if block.get("has_children", False):
                    child_images = extract_images_recursive(block["id"], title)
                    images.extend(child_images)
            
            return images
        
        images = extract_images_recursive(page_id)
        return json.dumps({"images": images}, ensure_ascii=False, indent=2)
        
    except Exception as e:
        logger.error(f"이미지 가져오기 실패: {str(e)}")
        return f"이미지 가져오기 실패: {str(e)}"

@mcp.tool()
def get_child_pages() -> str:
    """
    현재 설정된 Notion 페이지의 하위 페이지들을 가져옵니다.
    
    Returns:
        하위 페이지 정보 JSON
    """
    try:
        api_key, page_id = get_notion_credentials()
        if not api_key or not page_id:
            return json.dumps({"child_pages": [], "error": "Notion API 키 또는 페이지 ID가 설정되지 않았습니다."}, ensure_ascii=False)
        
        notion = Client(auth=api_key)
        
        def find_child_pages_recursive(block_id):
            blocks = notion.blocks.children.list(block_id=block_id)
            child_pages = []
            
            for block in blocks["results"]:
                if block["type"] == "child_page":
                    try:
                        page = notion.pages.retrieve(page_id=block["id"])
                        page_title = "제목 없음"
                        
                        if "properties" in page:
                            for prop_name, prop_data in page["properties"].items():
                                if prop_data["type"] == "title":
                                    title_array = prop_data["title"]
                                    page_title = "".join([t.get("plain_text", "") for t in title_array])
                                    break
                        
                        child_pages.append({
                            "id": block["id"],
                            "title": page_title,
                            "url": page.get("url", "")
                        })
                    except Exception as e:
                        logger.error(f"하위 페이지 정보 가져오기 실패: {e}")
                
                # 하위 블록에서도 child_page 찾기
                if block.get("has_children", False):
                    nested_pages = find_child_pages_recursive(block["id"])
                    child_pages.extend(nested_pages)
            
            return child_pages
        
        child_pages = find_child_pages_recursive(page_id)
        return json.dumps({"child_pages": child_pages}, ensure_ascii=False, indent=2)
        
    except Exception as e:
        logger.error(f"하위 페이지 가져오기 실패: {str(e)}")
        return f"하위 페이지 가져오기 실패: {str(e)}"

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