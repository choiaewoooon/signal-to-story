from dataclasses import dataclass, field


@dataclass
class Signal:
    ticker: str          # 종목코드 (예: "005930")
    name: str            # 종목명
    thesis: str          # 시그널 근거 한 줄
    metrics: dict        # 보조 지표 (등락률, 거래량 등)


@dataclass
class Script:
    hook: str            # 첫 컷 후킹 문장
    cuts: list[str]      # 컷별 내레이션 (3컷)
    cta: str             # 마지막 행동 유도 문구
    disclaimer: str      # 면책 문구


@dataclass
class ComplianceFlag:
    text: str            # 문제 표현
    reason: str          # 사유 (예: "수익 보장 암시")
    severity: str        # "high" | "med" | "low"


@dataclass
class ComplianceReport:
    flags: list[ComplianceFlag] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return not any(f.severity == "high" for f in self.flags)


@dataclass
class StoryboardCut:
    caption: str         # 컷 내레이션
    image_path: str      # 생성된 콘티 이미지 경로


@dataclass
class Storyboard:
    cuts: list[StoryboardCut] = field(default_factory=list)


@dataclass
class ConversionDesign:
    cta_text: str
    deeplink: str
    metrics: dict        # 지표 정의 + 목업 수치
