import os
import streamlit as st
from dotenv import load_dotenv
from pipeline.stage1_signal import load_signal
from pipeline.factory import make_pipeline, mode_label

load_dotenv()
st.set_page_config(page_title="signal-to-story", layout="wide")

# ── Change 2: CSS injection + helpers ──────────────────────────────────────
st.markdown(
    """
    <link rel="stylesheet" as="style" crossorigin href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css" />
    <style>
      :root { --ink:#1B1D1F; --blue:#1C82E8; --line:rgba(27,29,31,0.08); --sub:rgba(27,29,31,0.60); --ter:rgba(27,29,31,0.42); --surface:#F7F9FA; }
      html, body, .stApp, [data-testid="stMarkdownContainer"] {
        font-family:'Pretendard Variable', Pretendard, -apple-system, sans-serif !important;
        letter-spacing:-0.014em;
      }
      .stApp { background:#FFFFFF; color:var(--ink); }
      #MainMenu, footer, header, [data-testid="stToolbar"], [data-testid="stAppDeployButton"], [data-testid="stDecoration"] { display:none !important; }
      .block-container { max-width:880px; padding-top:1.2rem; }
      h1,h2,h3 { color:var(--ink); font-weight:700; letter-spacing:-0.03em; }
      /* cinematic hero band (matches their site: dark-blue hero over light body) */
      .s2s-hero { background:linear-gradient(135deg,#0F1B2E 0%, #1B1D1F 70%); border-radius:22px; padding:30px 32px; margin:6px 0 10px; }
      .s2s-hero .kick { color:#5FB0FF; font-size:0.8rem; font-weight:600; letter-spacing:0.04em; text-transform:uppercase; }
      .s2s-hero .ttl { color:#fff; font-size:2.2rem; font-weight:800; letter-spacing:-0.045em; margin:4px 0 6px; }
      .s2s-hero .sub { color:rgba(255,255,255,0.66); font-size:0.92rem; line-height:1.55; }
      .s2s-hero .mode { display:inline-block; margin-top:13px; padding:5px 12px; border-radius:999px; background:rgba(28,130,232,0.16); border:1px solid rgba(28,130,232,0.45); color:#9CCBFF; font-size:0.8rem; }
      /* stage header */
      .s2s-stage { display:flex; align-items:center; margin:24px 0 8px; padding-top:18px; border-top:1px solid var(--line); }
      .s2s-badge { display:inline-flex; align-items:center; justify-content:center; width:30px; height:30px; border-radius:9px; background:var(--blue); color:#fff; font-weight:700; font-size:0.95rem; margin-right:10px; }
      .s2s-stage h3 { margin:0; font-size:1.12rem; }
      /* card */
      .s2s-card { background:#fff; border:1px solid var(--line); border-radius:16px; padding:18px 20px; margin:6px 0; box-shadow:0 1px 3px rgba(16,24,40,0.04); }
      .s2s-card .k { color:var(--ter); font-size:0.76rem; margin-bottom:2px; }
      .s2s-card .v { color:var(--ink); font-size:0.97rem; line-height:1.55; }
      .s2s-pill { display:inline-block; padding:3px 10px; border-radius:999px; background:var(--surface); border:1px solid var(--line); color:var(--sub); font-size:0.8rem; margin:2px 4px 2px 0; }
      .stButton button { border-radius:999px !important; font-weight:600; padding:0.4rem 1.1rem; }
      .stButton button[kind="primary"] { background:var(--blue); border-color:var(--blue); }
      code { color:var(--blue); }
      a { color:var(--blue); }
    </style>
    """,
    unsafe_allow_html=True,
)
import html as _html

def card(inner: str):
    st.markdown(f'<div class="s2s-card">{inner}</div>', unsafe_allow_html=True)

def stage_header(n: str, title: str):
    st.markdown(f'<div class="s2s-stage"><span class="s2s-badge">{n}</span><h3>{title}</h3></div>', unsafe_allow_html=True)

# ── Change 3: Hero band (replaces st.title + st.caption) ──────────────────
st.markdown(
    f'<div class="s2s-hero">'
    f'<div class="kick">넥스트증권 · Contents Platform 지원 데모</div>'
    f'<div class="ttl">signal-to-story</div>'
    f'<div class="sub">증시 시그널 → 대본 → 컴플라이언스 게이트(HITL) → 콘티 → 전환.<br>데이터를 투자 콘텐츠로 바꾸는 AI 파이프라인.</div>'
    f'<div class="mode">⚙️ 실행 모드 — {mode_label()}</div>'
    f'</div>',
    unsafe_allow_html=True,
)

if "pipe" not in st.session_state:
    st.session_state.pipe = make_pipeline("output/sample_run")

pipe = st.session_state.pipe

# ① Signal
stage_header("1", "Signal")
signal = load_signal("data/sample_signal.json")
card(
    f'<div class="k">종목</div><div class="v">{_html.escape(signal.name)} ({_html.escape(signal.ticker)})</div>'
    f'<div class="k" style="margin-top:10px;">근거</div><div class="v">{_html.escape(signal.thesis)}</div>'
    f'<div class="k" style="margin-top:10px;">지표</div><div class="v">'
    + "".join(f'<span class="s2s-pill">{_html.escape(str(k))}: {_html.escape(str(v))}</span>' for k, v in signal.metrics.items() if not str(k).startswith("_"))
    + '</div>'
)

if st.button("파이프라인 실행 ▶") and pipe.state in ("INIT", "REJECTED"):
    with st.spinner("Claude가 대본 생성 + 컴플라이언스 검사 중…"):
        pipe.run_until_gate(signal)

# ② Script
if pipe.script:
    stage_header("2", "Script")
    cuts_html = "".join(f'<div class="k" style="margin-top:8px;">컷 {i}</div><div class="v">{_html.escape(c)}</div>' for i, c in enumerate(pipe.script.cuts, 1))
    card(
        f'<div class="k">Hook</div><div class="v">{_html.escape(pipe.script.hook)}</div>'
        f'{cuts_html}'
        f'<div class="k" style="margin-top:8px;">CTA</div><div class="v">{_html.escape(pipe.script.cta)}</div>'
        f'<div class="v" style="color:var(--ter); font-size:0.82rem; margin-top:10px;">{_html.escape(pipe.script.disclaimer)}</div>'
    )

# ③ Compliance Gate (HITL)
if pipe.report and pipe.state == "AWAITING_APPROVAL":
    stage_header("3", "Compliance Gate — 사람 승인 (HITL)")
    if pipe.report.flags:
        for f in pipe.report.flags:
            st.warning(f'[{f.severity}] "{f.text}" — {f.reason}')
    else:
        st.success("위반 표현 없음")
    if not pipe.report.passed:
        st.error("high 위험 플래그가 있어 승인할 수 없습니다. 반려 후 대본을 재생성하세요.")
    col1, col2 = st.columns(2)
    if col1.button("✅ 승인", disabled=not pipe.report.passed):
        pipe.approve(); pipe.resume(); st.rerun()
    if col2.button("⛔ 반려 (대본 재생성)"):
        pipe.reject(); st.rerun()

# ④ Storyboard
if pipe.storyboard:
    stage_header("4", "Storyboard — 영상은 콘티로 흉내")
    st.caption("운영 시 각 컷을 Veo 3.1 Lite의 레퍼런스 이미지로 image-to-video 변환")
    cols = st.columns(len(pipe.storyboard.cuts))
    for col, cut in zip(cols, pipe.storyboard.cuts):
        col.image(cut.image_path, caption=cut.caption, use_container_width=True)

# ⑤ Conversion
if pipe.conversion:
    stage_header("5", "Conversion (전환 설계)")
    metrics_html = "".join(f'<div class="k" style="margin-top:8px;">{_html.escape(str(name))}</div><div class="v">{_html.escape(str(d))}</div>' for name, d in pipe.conversion.metrics.items())
    card(
        f'<div class="k">CTA</div><div class="v">{_html.escape(pipe.conversion.cta_text)}</div>'
        f'<div class="k" style="margin-top:10px;">딥링크</div><div class="v"><code>{_html.escape(pipe.conversion.deeplink)}</code></div>'
        f'{metrics_html}'
    )
