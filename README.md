# 🧳 GenAI Business Trip Agent

AI 기반 출장 준비 도우미 시스템입니다. 6개의 전문 AI Agent가 협력하여 완벽한 출장 준비 가이드를 제공합니다.

## ✨ 주요 기능

### 🤖 6개 전문 AI Agent
1. **LocationAnalyzer** - 목적지의 날씨, 계절, 기후 특성 분석
2. **DressCodeAdvisor** - 비즈니스 문화에 맞는 복장 추천  
3. **QuantityCalculator** - 출장 기간에 따른 정확한 수량 계산
4. **LocalRequirements** - 전압, 통화, 현지 필수품 안내
5. **LocalIntelligence** - 교통, 식당, 쇼핑, 응급상황 정보
6. **ShoppingCoordinator** - 한국/현지 구분 쇼핑 리스트 생성

### 🎯 핵심 특징
- **Multi-Agent 협업**: 각 전문 분야별 Agent가 협력하여 종합적인 출장 준비 가이드 제공
- **Strands Agent 기반**: Multi-step reasoning을 통한 향상된 RAG 검색
- **MCP Server 활용**: Knowledge Base, Code Interpreter 등 다양한 도구 연동
- **PDF 리포트 생성**: 출장 준비 체크리스트를 PDF로 다운로드
- **Notion 연동**: 출장 계획을 Notion 페이지로 자동 생성

## 🚀 빠른 시작

### 1. 설치

```bash
git clone https://github.com/ar-codelabs/GenAI_BusinessTrip_Agent.git
cd genai_businesstrip_agent
pip install -r requirements.txt
```

### 2. 환경 설정

`.env` 파일을 생성하고 필요한 환경 변수를 설정하세요:

```bash
cp .env.example .env
```

`.env` 파일에 다음 정보를 입력:
```
# AWS Configuration
AWS_ACCESS_KEY_ID=your_aws_access_key_id
AWS_SECRET_ACCESS_KEY=your_aws_secret_access_key
AWS_REGION=us-west-2

# S3 버킷 (Knowledge Base 연동)
S3_BUCKET_NAME=your-knowledge-base-bucket

# Notion Integration (Optional)
NOTION_API_KEY=your_notion_integration_token
NOTION_PAGE_ID=your_notion_page_id

# 기타 설정
FASTMCP_LOG_LEVEL=ERROR
OAUTHLIB_INSECURE_TRANSPORT=1
```

### 3. 설정 파일 수정

`application/config.json`에서 Knowledge Base ID를 업데이트:

```json
{
    "projectName": "genai-business-trip-agent",
    "region": "us-west-2", 
    "knowledge_base_id": "YOUR_KNOWLEDGE_BASE_ID"
}
```

### 4. 실행

```bash
# 통합 앱 실행 (여러 모드 선택 가능)
streamlit run application/app.py
```

```

## 🛠️ 기술 스택

- **Frontend**: Streamlit
- **AI Framework**: Strands Agents
- **LLM**: Claude (Anthropic)
- **RAG**: AWS Bedrock Knowledge Base
- **MCP**: Model Context Protocol
- **Integration**: Notion API

## 📖 사용 방법

### 1. 출장 준비 시작
1. 웹 앱에 접속
2. 출장 목적지와 기간 입력
3. 출장 목적 선택 (비즈니스 미팅, 컨퍼런스 등)

### 2. AI Agent 분석
- 각 전문 Agent가 순차적으로 분석 수행
- 실시간으로 분석 과정 확인 가능
- 종합적인 출장 준비 가이드 생성

### 3. 결과 활용
- 체크리스트 PDF 다운로드
- Notion 페이지 자동 생성

## 🔧 고급 설정

### Knowledge Base 설정
1. [AWS Bedrock Console](https://console.aws.amazon.com/bedrock/)에서 Knowledge Base 생성
2. S3에 출장 관련 문서 업로드
3. Knowledge Base ID를 `config.json`에 설정

### MCP 서버 추가
`application/mcp.json`에서 새로운 MCP 서버 추가:

```json
{
  "mcpServers": {
    "your_server": {
      "command": "python",
      "args": ["path/to/your_mcp_server.py"],
      "env": {}
    }
  }
}
```

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 `LICENSE` 파일을 참조하세요.

