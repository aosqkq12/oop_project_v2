# 🎬 100만 유튜버 위기관리 시뮬레이션

> *"어제의 말실수, 오늘의 생존게임"*

텍스트 기반 위기관리 시뮬레이션 게임 — **객체지향 프로그래밍 팀 프로젝트**

콘솔로 설계한 OOP 시스템을 **한 줄도 수정하지 않고** Streamlit 웹 데모로 그대로 띄워, 캡슐화·상속·다형성·추상화의 실제 효용을 시연합니다.

---

## 🎮 데모

🔗 **[웹에서 바로 플레이하기](https://본인앱URL.streamlit.app)** ← *배포 후 본인 URL로 교체*

> 캐릭터 선택 → 자동 시나리오 배정 → 7일 위기관리 → 멀티엔딩 분기

---

## 📌 게임 개요

| 항목 | 내용 |
|------|------|
| 장르 | 텍스트 기반 위기관리 시뮬레이션 |
| 플레이타임 | 게임 내 7일 / 실제 약 5분 |
| 캐릭터 | 5종 (스트리머·브이로거·논객·플렉서·키즈) |
| 시나리오 | 3종 (말실수·뒷광고·험담) |
| 행동 | 6종 (사과·잠수·물타기·법적대응·환불·DM) |
| 이벤트 | 13종 (확률 기반, 상태 의존) |
| 엔딩 | 6종 멀티엔딩 |

---

## 🏗️ OOP 설계

### 1. 캡슐화 (Encapsulation)

`Youtuber` 클래스의 모든 능력치는 private. 외부에서 직접 변경 불가, getter로만 조회.

```python
class Youtuber:
    def __init__(self, ...):
        self.__subscribers = subs       # private
        self.__mental = mental
        self.__reputation = reputation
        # ...

    def get_mental(self): return self.__mental
    def apply_change(self, **kwargs):   # 유일한 수정 경로
        # 특성에 따른 보정 후 적용
```

### 2. 상속 (Inheritance)

3개의 추상 클래스 계층:

```
Action (추상)  ── ApologyLive, GoSilent, Diversion,
                  HireLawyer, AdmitAndRefund, DirectMessage

Event (추상)   ── UnionStatement, FTCInvestigation,
                  AdvertiserPullout, LawyerBackfire, ...  (총 13종)

Scenario (추상) ── SlipOfTongueScenario, FakeAdScenario,
                   BackbiteScenario
```

### 3. 다형성 (Polymorphism)

각 자식 클래스가 같은 이름의 메서드를 자기만의 로직으로 오버라이드:

```python
action.execute(youtuber, opinion, day)   # 6가지 다른 결과
event.trigger(youtuber, opinion, day)    # 13가지 다른 효과
```

### 4. 추상화 (Abstraction)

`@abstractmethod` 데코레이터로 인터페이스 강제:

```python
class Action(ABC):
    @abstractmethod
    def execute(self, youtuber, opinion, day): ...
```

### 5. 피드백 루프 ★

> 멘탈 ↓ → 나쁜 이벤트 확률 ↑ → `BURNED_OUT` 특성 획득 → 멘탈 감소 1.5배 → 악순환

> 진정성 사과 → `APOLOGIZED` 플래그 → 노조 화해 이벤트 발동 → `REDEEMED` 특성 → GOOD ENDING

**객체의 상태가 객체의 미래를 결정하는 구조** — OOP의 진짜 가치.

---

## 🌐 Web Demo의 의미

```
youtuber_crisis_v4.py      ← 콘솔 게임 (원본, 수정 0줄)
  │
  └─ import
      │
      └─ streamlit_app.py   ← 웹 UI (출력 계층만 담당)
```

`Youtuber`, `GameManager`, `Event` 등 모든 게임 객체를 **그대로** 활용. Streamlit은 단지 `y.get_mental()`을 호출해서 게이지 바를 그리고, `action.execute()`로 버튼 클릭을 처리할 뿐입니다.

**OOP가 잘 되어 있으면 출력 매체를 바꿔도 코어 로직은 손대지 않는다** — 관심사 분리의 실증.

---

## 🚀 실행 방법

### 콘솔 버전
```bash
python youtuber_crisis_v4.py
```

### 웹 버전 (로컬)
```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

브라우저가 자동으로 `http://localhost:8501`을 엽니다.

### 웹 버전 (배포)
[Streamlit Community Cloud](https://share.streamlit.io)에 GitHub 리포 연결하여 무료 배포.

---

## 📁 파일 구조

```
.
├── youtuber_crisis_v4.py    원본 게임 로직 (약 690줄, OOP 클래스 30여 개)
├── streamlit_app.py          Streamlit 웹 UI (import만 하고 호출)
├── requirements.txt          의존 패키지 (streamlit, plotly)
└── README.md                 이 파일
```

---

## 👥 팀 구성 (3인)

| 역할 | 담당 |
|------|------|
| 스토리보드 | 시나리오 3종, 이벤트 카드 20+장, 엔딩 6종, NPC 설정 |
| 설계도 | UML 다이어그램, 핵심 클래스 구현, 상속 구조 |
| 하이라이트 데모 | 콘솔 데모 빌드, Streamlit 웹 포팅, 시연 대본 |

---

## 📊 시스템 진화

| 버전 | 추가 시스템 | 클래스 수 |
|------|------------|----------|
| v1 | 기본 골격 (Youtuber, PublicOpinion, Action 4종, Event 3종) | ~10 |
| v2 | Scenario 추상화, 플래그 기반 연계 이벤트 | ~18 |
| v3 | 캐릭터 5종, 충성팬/안티팬, 동적 특성 시스템 | ~22 |
| v4 | 시나리오별 이벤트 풀, 확률 기반 발동, 피드백 루프 | ~30 |
| Web | 콘솔 → Streamlit 포팅 (원본 0줄 수정) | +Streamlit UI |

---

## 🎯 핵심 어필 포인트

> **"이벤트를 추가하고 싶으면 `Event` 클래스를 상속받은 클래스 하나만 만들어서 리스트에 넣으면 끝입니다. 메인 로직은 한 줄도 안 건드립니다."**

> **"콘솔에서 웹으로 옮길 때 게임 로직 파일은 손가락 하나 안 댔습니다. `Youtuber.get_mental()`을 호출해서 게이지 바를 그렸고, `action.execute()`로 버튼 클릭을 처리했을 뿐입니다. 캡슐화가 잘 됐기 때문에 가능한 일입니다."**

---

*OOP 팀 프로젝트 · 2026*
