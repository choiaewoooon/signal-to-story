import os
import streamlit as st
from dotenv import load_dotenv
from pipeline.stage1_signal import load_signal
from pipeline.orchestrator import Pipeline
from pipeline.clients import ClaudeClient, ImageClient

load_dotenv()
st.set_page_config(page_title="signal-to-story", layout="wide")
st.title("📈 signal-to-story — 투자 콘텐츠 파이프라인 데모")

if "pipe" not in st.session_state:
    st.session_state.pipe = Pipeline(ClaudeClient(), ImageClient(), out_dir="output/sample_run")

pipe = st.session_state.pipe

# ① Signal
st.header("① Signal")
signal = load_signal("data/sample_signal.json")
st.json({"종목": f"{signal.name} ({signal.ticker})", "근거": signal.thesis, "지표": signal.metrics})

if st.button("파이프라인 실행 ▶") and pipe.state in ("INIT", "REJECTED"):
    with st.spinner("Claude가 대본 생성 + 컴플라이언스 검사 중…"):
        pipe.run_until_gate(signal)

# ② Script
if pipe.script:
    st.header("② Script (Claude)")
    st.write(f"**Hook:** {pipe.script.hook}")
    for i, c in enumerate(pipe.script.cuts, 1):
        st.write(f"**컷 {i}:** {c}")
    st.write(f"**CTA:** {pipe.script.cta}")
    st.caption(pipe.script.disclaimer)

# ③ Compliance Gate (HITL)
if pipe.report and pipe.state == "AWAITING_APPROVAL":
    st.header("③ Compliance Gate — 사람 승인 필요 (HITL)")
    if pipe.report.flags:
        for f in pipe.report.flags:
            st.warning(f'[{f.severity}] “{f.text}” — {f.reason}')
    else:
        st.success("위반 표현 없음")
    col1, col2 = st.columns(2)
    if col1.button("✅ 승인"):
        pipe.approve(); pipe.resume(); st.rerun()
    if col2.button("⛔ 반려 (대본 재생성)"):
        pipe.reject(); st.rerun()

# ④ Storyboard
if pipe.storyboard:
    st.header("④ Storyboard (GPT Image) — 영상은 콘티로 흉내")
    st.caption("운영 시 각 컷을 Veo 3.1 Lite의 레퍼런스 이미지로 image-to-video 변환")
    cols = st.columns(len(pipe.storyboard.cuts))
    for col, cut in zip(cols, pipe.storyboard.cuts):
        col.image(cut.image_path, caption=cut.caption, use_container_width=True)

# ⑤ Conversion
if pipe.conversion:
    st.header("⑤ Conversion (전환 설계)")
    st.write(f"**CTA:** {pipe.conversion.cta_text}")
    st.code(pipe.conversion.deeplink)
    st.json(pipe.conversion.metrics)
