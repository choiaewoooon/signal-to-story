# signal-to-story

> 증시 시그널 → 숏폼 투자 콘텐츠 자동 생산 파이프라인 (넥스트증권 PM 지원 데모)

---

## 1. 문제 정의 — 왜 이걸 만들었나

증권사 콘텐츠 플랫폼의 핵심 과제는 **데이터가 있어도 콘텐츠가 늦게 나온다**는 것이다.  
기관 순매수 신호가 뜨는 순간부터 유저가 15초 숏폼으로 그 맥락을 소화하기까지, 편집·자막·규제 검수·배포 사이클이 수 시간~수일을 잡아먹는다.

넥스트증권이 구상하는 **콘텐츠 플랫폼(증시 데이터 → LLM 원고 → 숏폼 영상 자동 생산)** 파이프라인을 이해하기 위해, 그 구조를 작게 직접 복제해봤다.  
"말로 설명하는 PM"이 아니라 **"직접 만들어 보여주는 PM"** 이 되고 싶었다.

---

## 2. 파이프라인 (5단계)

```
Signal → Script → Compliance Gate (HITL) → Storyboard → Conversion
```

| 단계 | 파일 | 역할 |
|------|------|------|
| **1. Signal** | `pipeline/stage1_signal.py` | `data/sample_signal.json`(합성 데이터)을 로드해 종목·근거·지표를 구조화된 `Signal` 객체로 변환 |
| **2. Script** | `pipeline/stage2_script.py` | Claude가 15초 숏폼 대본(hook + 3컷 + CTA)을 생성. `prompts/script.md`에 자본시장법 준수 템플릿(수익보장·단정적 매수권유·과장 금지 + 면책 1줄) 내재화 |
| **3. Compliance Gate** | `pipeline/stage3_compliance.py` | Claude가 대본의 자본시장법 위험 표현을 플래그. `high` 심각도 플래그가 하나라도 있으면 `ComplianceReport.passed = False`. Streamlit에서 사람이 ✅승인 / ⛔반려를 클릭해야만 다음 단계로 진행 |
| **4. Storyboard** | `pipeline/stage4_storyboard.py` | OpenAI GPT Image (`gpt-image-1`)가 4장의 콘티 프레임(hook + 3컷)을 생성해 `output/sample_run/`에 저장. **영상은 이 콘티 단계에서 흉내내며**, 실제 배포 시 각 프레임이 Veo 3.1 Lite(image-to-video)로 넘어간다 |
| **5. Conversion** | `pipeline/stage5_conversion.py` | CTA 문구 + 딥링크(UTM 파라미터 포함) + Watchtime/CTR/Conversion 지표 정의(목업 수치)를 설계. 조회수가 아닌 **앱 내 전환**을 끝점으로 설계 |

오케스트레이션: `pipeline/orchestrator.py`의 `Pipeline` 클래스가 상태(`INIT → AWAITING_APPROVAL → APPROVED/REJECTED → DONE`)를 관리하고, Streamlit(`app.py`)이 UI 껍데기로 감싼다.

> **콘티 이미지 샘플:** 로컬에서 `.env`에 키 입력 후 `streamlit run app.py`를 1회 완주하면 `output/sample_run/`에 콘티가 생성됩니다. 생성 이미지는 `.gitignore`로 커밋에서 제외되므로 직접 실행해 확인하세요.

---

## 3. 도구 위임 결정 — 왜 이 조합

"Claude가 모든 걸 혼자 처리하지 않는다"는 것이 핵심 원칙이다.  
**모달리티별 현재 1군 모델에 위임**해 품질을 최대화하고, Python이 글루 코드로 묶는다.

| 역할 | 선택 | 이유 |
|------|------|------|
| 대본·컴플라이언스 | **Claude** | 한국어 금융 텍스트 생성 + 규제 리스크 판단 |
| 콘티 이미지 | **OpenAI GPT Image (`gpt-image-1`)** | 2026.6 이미지 아레나 1위, 지시 이해 정확도 최강 |
| 영상화 | **Veo 3.1 Lite** (설계만) | 9:16 네이티브 비율·음성 포함·image-to-video·저비용 |
| 음성 | **Supertone** (스코프 밖) | 한국어 TTS는 토종 특화 모델 우위 |
| 글루 | **Python** | 재현·버전관리·"직접 빌드" 증거 |

상세 결정 배경은 [docs/decisions.md](docs/decisions.md) 참조.

---

## 4. 전환(Conversion) — 콘텐츠는 목적이 아니라 미끼

증권사에서 콘텐츠의 끝점은 **조회수가 아니라 앱 내 전환**이다.  
15초 숏폼이 아무리 잘 만들어져도, 유저가 해당 종목 상세 화면까지 들어와야 비즈니스 가치가 생긴다.

Stage 5가 설계하는 것:

- **CTA:** `{종목명} 상세 보기 →` — 영상 마지막 프레임에 오버레이
- **딥링크:** `nextsec://stock/{ticker}?utm_source=shorts&utm_campaign=signal_demo` — 앱 직접 진입 + UTM으로 캠페인 추적
- **추적 지표 (목업):**
  - `Watchtime` — 평균 시청 시간, 목표 ≥ 7초/15초 (목업: 8.4초)
  - `CTR` — CTA 노출 대비 클릭률, 목표 ≥ 4% (목업: 5.1%)
  - `Conversion` — 클릭 → 앱 내 종목 상세 진입, 딥링크+UTM 추적 (목업: 1.9%)

콘텐츠 PM이 콘텐츠 품질만 보는 게 아니라 **전환 퍼널 전체를 설계해야 한다**는 관점을 코드로 표현했다.

---

## 5. 실행

```bash
# 의존성 설치
uv sync --group dev

# 테스트 (API 키 불필요, 외부 I/O는 Fake 클라이언트로 목킹)
uv run pytest -q
# → 14 passed

# 라이브 실행 (API 키 필요)
cp .env.example .env   # ANTHROPIC_API_KEY, OPENAI_API_KEY 입력
uv run streamlit run app.py
```

---

## 6. 스코프 / 한계 (정직하게)

이 데모가 **실제로 하는 것:**
- 합성 시그널 → Claude 대본 생성 → 자본시장법 컴플라이언스 검수 → HITL 승인 게이트 → GPT Image 콘티 4장 → 전환 지표 설계까지의 **전체 파이프라인을 코드로 연결**
- 14개 테스트, 외부 API 없이 로컬에서 검증 가능

이 데모가 **하지 않는 것 (확장안):**
- **실제 영상 렌더링:** Veo 3.1 Lite 연동은 설계 수준. 콘티(이미지 4장)로 흉내
- **Supertone TTS:** 음성 합성은 스코프 밖
- **실시간 데이터 연동:** 현재는 `data/sample_signal.json` 합성 데이터
- **다종목 대량 생산:** 단일 시그널 단일 콘텐츠 데모
- **자동 배포:** 플랫폼 업로드(유튜브 쇼츠·인스타 릴스 등) 연동 없음
