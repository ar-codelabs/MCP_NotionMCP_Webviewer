# 📄 Notion Page Viewer

Notion 페이지의 컨텐츠를 웹에서 볼 수 있는 Streamlit 앱입니다. 

## ✨ 주요 기능

### 🔍 **4가지 보기 모드**
1. **전체 컨텐츠** - 토글, 이미지, 하위 페이지까지 모든 컨텐츠 표시
2. **제목 + 이미지** - 메인페이지의 제목과 이미지만 표시
3. **하위 페이지** - 연결된 하위 페이지들의 제목 리스트
4. **원본 데이터** - JSON 형태의 원본 데이터 (디버깅용)

## 🚀 빠른 시작

### 1. 설치

```bash
git clone https://github.com/ar-codelabs/MCP_NotionMCP_Webviewer.git
cd MCP_notion_webviewer

# 설치
pip install -r requirements.txt

```

### 2. Notion 설정

1. [developers.notion.com/](https://www.notion.so/profile/integrations))에서 Integration 생성
2. Integration Token 복사
3. 보고 싶은 Notion 페이지에 Integration 연결
4. 페이지 ID 복사 (URL에서 추출)

### 3. 설정 파일 수정 (Notion)

`application/mcp.json` 파일에서:

```json
{
  "mcpServers": {
    "notion": {
      "command": "python3",
      "args": ["./application/mcp_server_notion.py"],
      "env": {
        "NOTION_API_KEY": "your_notion_integration_token",
        "NOTION_PAGE_ID": "your_notion_page_id"
      }
    }
  }
}
```

### 4. 실행

```bash
streamlit run application/app_webview_mcp_simple.py
```

## 📖 사용 방법

### 1. 웹 앱 접속
- 브라우저에서 접속

### 2. 4가지 버튼 활용
- **🔍 전체 컨텐츠**: 페이지의 모든 내용을 구조적으로 표시
- **🖼️ 제목 + 이미지**: 제목과 이미지만 깔끔하게 정리해서 표시
- **📑 하위 페이지**: 연결된 하위 페이지들의 제목 목록과 링크
- **🔧 원본 데이터**: 개발자용 JSON 데이터 확인

### 3. 지원하는 Notion 블록
- 텍스트 (paragraph)
- 헤딩 (heading_1, heading_2, heading_3)
- 리스트 (bulleted_list_item, numbered_list_item)
- 토글 (toggle)
- 이미지 (image)
- 코드 (code)
- 인용문 (quote)
- 컬럼 (column_list, column)
- 하위 페이지 (child_page)

## 🔧 고급 설정

### Notion 페이지 ID 찾기
1. Notion 페이지 URL: `https://notion.so/페이지제목-abc123def456...`
2. 마지막 하이픈 뒤의 32자리 문자열이 페이지 ID
3. 하이픈 제거: `abc123def456...`


### 포트 변경
```bash
# MCP 방식
streamlit run application/app_webview_mcp_simple.py --server.port 8502
```


## 🛠️ 기술 스택

### 공통
- **Frontend**: Streamlit
- **API**: Notion API (notion-client)
- **Language**: Python 3.8+

### MCP 방식 추가
- **MCP**: Model Context Protocol
- **Architecture**: Server-Client 분리
- **Modularity**: 재사용 가능한 MCP 서버

## 📝 주의사항

- Notion Integration에 페이지 읽기 권한이 있어야 합니다
- 이미지는 Notion의 임시 URL을 사용하므로 일정 시간 후 만료될 수 있습니다
- 대용량 페이지의 경우 로딩 시간이 길어질 수 있습니다

