import hmac
import os

import streamlit as st

from poster import STYLES, charts, claude_brief, demo_brief, render

st.set_page_config(page_title="Lion Heart · Lyric2Poster", page_icon="💌", layout="wide")
st.markdown("""
<style>
.block-container {max-width:1120px;padding-top:2.5rem}
.masthead {border-top:1px solid #ab8370;border-bottom:1px solid #ab8370;
padding:1.5rem 0;margin-bottom:1.4rem;text-align:center}
.masthead small {color:#802f38;letter-spacing:.25em;font-weight:700}
.masthead h1 {font-family:Georgia,serif;font-size:clamp(2.6rem,7vw,5rem);
font-weight:normal;line-height:1.05;margin:.3rem 0 .55rem;padding:0}
.masthead p {margin:0;color:#6c5042}
</style>
<div class="masthead"><small>LYRIC2POSTER · POSTCARD STUDIO</small>
<h1>Lion Heart</h1><p>가사에서 시작하는 빈티지 포스터</p></div>
""", unsafe_allow_html=True)


def setting(name):
    value = os.environ.get(name)
    if value:
        return value
    try:
        return str(st.secrets.get(name, ""))
    except FileNotFoundError:
        return ""


def analyze(title, artist):
    lyrics = st.session_state.pop("lyrics", "").strip()
    st.session_state["lyrics"] = ""
    st.session_state.pop("result", None)
    st.session_state.pop("analysis", None)
    if not title.strip() or not artist.strip():
        st.session_state["notice"] = "곡 제목과 가수를 입력해 주세요."
        return
    if st.session_state.get("brief_count", 0) >= 10:
        st.session_state["notice"] = "이 세션의 분석 한도에 도달했습니다."
        return
    st.session_state["brief_count"] = st.session_state.get("brief_count", 0) + 1
    passcode = setting("APP_PASSCODE")
    entered = st.session_state.get("passcode", "")
    authorized = bool(passcode) and hmac.compare_digest(passcode.encode(), entered.encode())
    key = st.session_state.get("visitor_key") or (setting("ANTHROPIC_API_KEY") if authorized else "")
    label = "데모 분석"
    brief = demo_brief(lyrics)
    if lyrics and key:
        try:
            brief = claude_brief(title, artist, lyrics, key, setting("L2P_CLAUDE_MODEL") or "claude-sonnet-5-5")
            label = "Claude 분석"
        except Exception:
            label = "데모 분석 · Claude 연결 또는 응답 확인 실패"
    st.session_state["notice"] = ""
    st.session_state["analysis"] = (title.strip(), artist.strip(), brief, label)
    st.session_state["style"] = brief.get("style", "앤티크 엽서")


with st.sidebar:
    st.header("분석 설정")
    st.caption("키 없이 데모를 이용할 수 있습니다. Claude 키를 입력하고 분석을 누르면 가사가 Anthropic으로 전송됩니다.")
    st.text_input("내 Claude API 키", key="visitor_key", type="password")
    if setting("APP_PASSCODE"):
        st.text_input("운영자 패스코드", key="passcode", type="password")

controls, preview = st.columns([1.05, 1], gap="large")
with controls:
    st.subheader("01  곡 선택")
    available = charts()
    group = st.selectbox("차트", [*available, "직접 입력"])
    if group == "직접 입력":
        title = st.text_input("곡 제목", max_chars=80)
        artist = st.text_input("가수", max_chars=80)
    else:
        songs = available[group]
        index = st.selectbox("곡", range(len(songs)), key=f"song-{group}",
                             format_func=lambda i: f"{songs[i]['title']} · {songs[i]['artist']}")
        title, artist = songs[index]["title"], songs[index]["artist"]
    st.subheader("02  가사 분석")
    with st.form("brief"):
        st.text_area("가사 또는 분위기 메모", key="lyrics", max_chars=4000,
                     placeholder="직접 작성한 문장이나 가사를 붙여 넣으세요.")
        st.form_submit_button("아트 브리프 만들기", on_click=analyze, args=(title, artist))
    if st.session_state.get("notice"):
        st.warning(st.session_state["notice"])
    analysis = st.session_state.get("analysis")
    if analysis and analysis[:2] == (title.strip(), artist.strip()):
        _, _, brief, label = analysis
        if brief["blocked"]:
            st.warning("이 입력으로는 포스터를 만들 수 없습니다.")
        else:
            st.caption(label)
            st.text(f"{brief['mood']} · {brief['summary']}")
            st.text(" / ".join(brief["imagery"]))
            swatches = "".join(f'<span style="display:inline-block;width:2rem;height:1rem;background:{color}"></span>' for color in brief["palette"])
            st.markdown(swatches, unsafe_allow_html=True)
            st.subheader("03  포스터 제작")
            style = st.selectbox("인쇄 스타일", list(STYLES), key="style")
            use_flux = st.checkbox("FLUX 이미지 생성", help="설정된 Hugging Face 모델에 아트 브리프를 보냅니다.") if setting("HF_TOKEN") and setting("HF_MODEL") else False
            if st.button("포스터 만들기", type="primary"):
                count = st.session_state.get("poster_count", 0)
                if count >= 6:
                    st.warning("이 세션의 포스터 제작 한도에 도달했습니다.")
                else:
                    st.session_state["poster_count"] = count + 1
                    with st.spinner("엽서를 인쇄하고 있습니다…"):
                        png, engine = render(title.strip(), artist.strip(), brief, style,
                                             setting("HF_TOKEN") if use_flux else "", setting("HF_MODEL"))
                    st.session_state["result"] = (analysis[:2], style, png, engine)

with preview:
    result = st.session_state.get("result")
    if result and result[0] == (title.strip(), artist.strip()):
        _, used_style, png, engine = result
        st.image(png, caption=f"{used_style} · {engine} · AI 삽화")
        st.download_button("PNG 다운로드", png, "lyric2poster.png", "image/png")
    else:
        png, _ = st.cache_data(show_spinner=False)(render)(
            "Lion Heart", "Girls’ Generation", demo_brief(""), "앤티크 엽서")
        st.image(png, caption="Lion Heart · 샘플 엽서 · AI 삽화")
