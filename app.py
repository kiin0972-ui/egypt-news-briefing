import streamlit as st
from google import genai
import feedparser
from datetime import datetime

# -----------------------------------------------------------------------------
# 1. 페이지 기본 설정 및 헤더
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="이집트 일일 언론 브리핑",
    page_icon="🗞️",
    layout="wide"
)

st.title("🗞️ 이집트 정세 일일 언론 브리핑")
st.caption(f"이집트 국내외 주요 언론 모니터링 시스템 | 생성 일시: {datetime.now().strftime('%Y-%m-%d %H:%M')}")

# 사이드바: Gemini API 키 입력
with st.sidebar:
    st.header("⚙️ 설정")
    api_key = st.text_input("Gemini API Key를 입력하세요", type="password")
    st.markdown("[Google AI Studio](https://aistudio.google.com/)에서 API 키를 발급받을 수 있습니다.")
    
    st.divider()
    st.markdown("**수집 언론사 범위**")
    st.markdown("- **이집트 국내:** Ahram Online, Daily News Egypt, Egypt Independent")
    st.markdown("- **중동 지역:** Al Jazeera (Middle East), The National (UAE)")
    st.markdown("- **글로벌 외신:** Reuters World, BBC Middle East")
    st.markdown("- **한국어 뉴스:** 구글 뉴스 (이집트 키워드)")

# -----------------------------------------------------------------------------
# 2. RSS 뉴스 수집 함수
# -----------------------------------------------------------------------------
RSS_FEEDS = {
    "이집트 국내 (Ahram Online)": "https://english.ahram.org.eg/rss/Egypt.xml",
    "이집트 국내 (Daily News Egypt)": "https://dailynewsegypt.com/feed/",
    "이집트 국내 (Egypt Independent)": "https://egyptindependent.com/feed/",
    "중동 지역 (Al Jazeera)": "https://www.aljazeera.com/xml/rss/all.xml",
    "중동 지역 (The National)": "https://www.thenationalnews.com/arc/outboundfeeds/rss/category/mena/?outputType=xml",
    "글로벌 외신 (Reuters)": "https://www.reutersagency.com/feed/?best-topics=world-news&post_type=best",
    "글로벌 외신 (BBC Middle East)": "http://feeds.bbci.co.uk/news/world/middle_east/rss.xml",
    "한국어 뉴스 (구글 뉴스)": "https://news.google.com/rss/search?q=%EC%9D%B4%EC%A7%91%ED%8A%B8&hl=ko&gl=KR&ceid=KR:ko"
}

def fetch_latest_news():
    raw_articles = []
    for source_name, url in RSS_FEEDS.items():
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:3]:  # 출처당 최신 기사 3개씩 추출
                raw_articles.append({
                    "source": source_name,
                    "title": entry.title,
                    "link": entry.link,
                    "summary": entry.get("summary", "")[:300]
                })
        except Exception as e:
            continue
    return raw_articles

# -----------------------------------------------------------------------------
# 3. Gemini API 기반 브리핑 생성 함수
# -----------------------------------------------------------------------------
def generate_briefing(articles, key):
    client = genai.Client(api_key=key)
    
    prompt = f"""
    너는 이집트 및 중동 정세를 전문적으로 분석하는 베테랑 외교관 겸 정세 분석가야.
    아래 수집된 뉴스 기사 목록을 바탕으로 매일 아침 보고할 '이집트 정세 일일 브리핑'을 작성해줘.

    [기사 데이터]
    {articles}

    [작성 요구사항 및 출력 형식]
    1. 수집된 기사들을 내용에 따라 아래 5가지 카테고리로 엄격히 분류할 것:
       - 🏛️ 정치
       - 📈 경제
       - 👥 사회
       - 🌐 외교
       - ☕ 기타 / 가십
    2. 각 카테고리별로 핵심 기사를 종합하여 2~3줄 내외로 핵심 요점을 한국어로 명확히 요약할 것.
    3. 각 요약 내용 바로 아래에 관련 기사 원문의 출처, 제목, 링크를 아래 마크다운 형식으로 명시할 것:
       - 출처: [기사 제목](URL)
    4. 언어가 영어나 아랍어인 기사도 수사적 뉘앙스를 살려 한국어로 매끄럽게 번역 및 요약할 것.
    5. 이집트와 직접적인 관련이 적은 일반 중동/글로벌 기사는 이집트에 미치는 영향 관점에서 다루거나 제외할 것.
    """

    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt
    )
    return response.text

# -----------------------------------------------------------------------------
# 4. 앱 UI 동작 부분
# -----------------------------------------------------------------------------
if st.button("🚀 매일 아침 브리핑 생성하기", type="primary"):
    if not api_key:
        st.error("사이드바에 Gemini API Key를 입력해주세요.")
    else:
        with st.spinner("이집트 현지 언론 및 글로벌 외신 데이터를 수집하고 분석 중입니다..."):
            articles = fetch_latest_news()
            
            if not articles:
                st.warning("뉴스를 가져오지 못했습니다. RSS 출처를 확인해 주세요.")
            else:
                briefing_result = generate_briefing(articles, api_key)
                
                st.success("브리핑이 완료되었습니다!")
                st.markdown("---")
                st.markdown(briefing_result)

                # 복사 및 보고서 저장 편의를 위한 텍스트 다운로드 버튼
                st.download_button(
                    label="📄 마크다운 보고서 다운로드",
                    data=briefing_result,
                    file_name=f"Egypt_Daily_Briefing_{datetime.now().strftime('%Y%m%m')}.md",
                    mime="text/markdown"
                )
