import streamlit as st
import requests
import urllib.parse

# 🔐 Streamlit secrets.toml에서 불러오는 API 키
NAVER_CLIENT_ID = st.secrets["NAVER_CLIENT_ID"]
NAVER_CLIENT_SECRET = st.secrets["NAVER_CLIENT_SECRET"]

# 언론사 도메인 → 한글명 매핑
press_name_map = {
    "chosun.com": "조선일보", "yna.co.kr": "연합뉴스", "hani.co.kr": "한겨레",
    "joongang.co.kr": "중앙일보", "mbn.co.kr": "MBN", "kbs.co.kr": "KBS",
    "sbs.co.kr": "SBS", "ytn.co.kr": "YTN", "donga.com": "동아일보",
    "segye.com": "세계일보", "munhwa.com": "문화일보", "newsis.com": "뉴시스",
    "naver.com": "네이버", "daum.net": "다음", "kukinews.com": "국민일보",
    "kookbang.dema.mil.kr": "국방일보", "edaily.co.kr": "이데일리",
    "news1.kr": "뉴스1", "mbnmoney.mbn.co.kr": "MBN", "news.kmib.co.kr": "국민일보"
}

def extract_press_name(url):
    try:
        domain = urllib.parse.urlparse(url).netloc.replace("www.", "")
        return press_name_map.get(domain, domain[:6])
    except:
        return "출처없음"

# 뉴스 검색 함수 (OpenAPI)
def search_news(query):
    enc_query = urllib.parse.quote(query)
    url = f"https://openapi.naver.com/v1/search/news.json?query={enc_query}&display=30&sort=date"
    headers = {
        "X-Naver-Client-Id": NAVER_CLIENT_ID,
        "X-Naver-Client-Secret": NAVER_CLIENT_SECRET,
    }
    res = requests.get(url, headers=headers)
    if res.status_code == 200:
        return res.json().get("items", [])
    return []

# 상태 초기화
if "final_articles" not in st.session_state:
    st.session_state.final_articles = []
if "selected_keys" not in st.session_state:
    st.session_state.selected_keys = []

# Streamlit UI
st.title("🎥 네이버 동영상 뉴스 검색기")
default_keywords = ["육군", "국방", "외교", "안보", "북한",
                    "신병교육대", "훈련", "간부", "장교",
                    "부사관", "병사", "용사", "군무원"]
input_keywords = st.text_input("🔍 키워드 입력 (쉼표로 구분)", ", ".join(default_keywords))
keyword_list = [k.strip() for k in input_keywords.split(",") if k.strip()]

# 뉴스 검색 버튼
if st.button("🔍 뉴스 검색"):
    with st.spinner("뉴스 검색 중..."):
        all_articles = []
        for keyword in keyword_list:
            items = search_news(keyword)
            for a in items:
                url = a["link"]
                # ✅ 동영상 기사만 필터링
                if "v.news.naver.com" in url or "tv.naver.com" in url:
                    title = a["title"].replace("<b>", "").replace("</b>", "")
                    press = extract_press_name(a.get("originallink") or url)
                    article = {
                        "title": title,
                        "url": url,
                        "press": press,
                        "key": url
                    }
                    all_articles.append(article)
        # ✅ 중복 제거
        unique_articles = {a["url"]: a for a in all_articles}
        st.session_state.final_articles = list(unique_articles.values())
        st.session_state.selected_keys = [a["key"] for a in st.session_state.final_articles]

# 미리보기 UI
if st.session_state.final_articles:
    st.subheader("🧾 기사 미리보기 (동영상 기사만)")
    for article in st.session_state.final_articles:
        key = article["key"]
        cols = st.columns([0.85, 0.15])
        with cols[0]:
            st.markdown(f" ■ {article['title']} ({article['press']})")
        with cols[1]:
            checked = st.checkbox("✅", value=key in st.session_state.selected_keys, key=key)
            if checked and key not in st.session_state.selected_keys:
                st.session_state.selected_keys.append(key)
            elif not checked and key in st.session_state.selected_keys:
                st.session_state.selected_keys.remove(key)

# 결과 출력
if st.button("📄 선택된 결과 출력"):
    st.subheader("📌 선택된 뉴스 결과")
    for article in st.session_state.final_articles:
        if article["key"] in st.session_state.selected_keys:
            st.markdown(f" ■ {article['title']} ({article['press']})")
            st.markdown(f"{article['url']}\n")
