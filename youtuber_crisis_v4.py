# ============================================================
#  100만 유튜버 위기관리 시뮬레이션 v4
#  "어제의 말실수, 오늘의 생존게임"
#
#  + 캐릭터 5종 선택
#  + 시나리오 3종 (각자 전용 이벤트 풀 보유)
#  + 확률 기반 이벤트 발동 (캐릭터 스탯/특성에 영향받음)
#  + 동적 특성 시스템 (이벤트가 특성을 추가/제거)
#  + 특성 → 다시 이벤트 확률에 영향 (피드백 루프)
# ============================================================

import random
from abc import ABC, abstractmethod


# ============================================================
#  1. 캐릭터 프리셋
# ============================================================
class CharacterPreset:
    def __init__(self, name, archetype, subs, mental, reputation, income,
                 loyal_fans, anti_fans, traits, description):
        self.name = name
        self.archetype = archetype
        self.subs = subs
        self.mental = mental
        self.reputation = reputation
        self.income = income
        self.loyal_fans = loyal_fans
        self.anti_fans = anti_fans
        self.traits = traits
        self.description = description


CHARACTERS = [
    CharacterPreset("박터질", "대형 게임 스트리머", 1_500_000, 80, 55, 8000,
                    70, 60, ["HIGH_LOYAL", "MANY_ANTIS"],
                    "팬덤도 안티도 많은 화제의 중심."),
    CharacterPreset("김감성", "브이로그 라이프스타일러", 800_000, 70, 75, 6000,
                    85, 20, ["HIGH_LOYAL", "FRAGILE_IMAGE"],
                    "청순 이미지 깨지면 회복 어려움."),
    CharacterPreset("이쎈언니", "사이다 사이버 논객", 600_000, 95, 40, 4000,
                    50, 80, ["STRONG_MENTAL", "MANY_ANTIS"],
                    "멘탈 갑. 안티 잘 쳐냄."),
    CharacterPreset("허세훈", "고급 라이프 플렉서", 1_200_000, 60, 45, 12000,
                    40, 70, ["RICH", "WEAK_MENTAL"],
                    "지갑은 두툼, 멘탈은 유리."),
    CharacterPreset("최순딩", "신인 키즈 크리에이터", 400_000, 90, 80, 2500,
                    90, 10, ["UNDERDOG", "HIGH_LOYAL", "PURE_IMAGE"],
                    "팬덤 결속 최강. 이미지 무너지면 치명적."),
]


# ============================================================
#  2. 플레이어 (캡슐화 + 동적 특성)
# ============================================================
class Youtuber:
    def __init__(self, preset):
        self.__name = preset.name
        self.archetype = preset.archetype
        self.__subscribers = preset.subs
        self.__mental = preset.mental
        self.__reputation = preset.reputation
        self.__income = preset.income
        self.__loyal_fans = preset.loyal_fans
        self.__anti_fans = preset.anti_fans
        self.traits = list(preset.traits)
        self.flags = set()
        self.trait_log = []

    def get_name(self): return self.__name
    def get_subs(self): return self.__subscribers
    def get_mental(self): return self.__mental
    def get_reputation(self): return self.__reputation
    def get_income(self): return self.__income
    def get_loyal(self): return self.__loyal_fans
    def get_anti(self): return self.__anti_fans
    def has_trait(self, t): return t in self.traits

    def add_trait(self, trait, day):
        if trait not in self.traits:
            self.traits.append(trait)
            self.trait_log.append((day, "+", trait))
            print(f"   ✨ [특성 획득] {trait}")

    def remove_trait(self, trait, day):
        if trait in self.traits:
            self.traits.remove(trait)
            self.trait_log.append((day, "-", trait))
            print(f"   💨 [특성 상실] {trait}")

    def apply_change(self, subs=0, mental=0, rep=0, income=0,
                     loyal=0, anti=0):
        # 특성에 따른 보정
        if self.has_trait("FRAGILE_IMAGE") and rep < 0:
            rep = int(rep * 1.5)
        if self.has_trait("STRONG_MENTAL") and mental < 0:
            mental = int(mental * 0.5)
        if self.has_trait("HIGH_LOYAL") and subs < 0:
            subs = int(subs * 0.7)
        if self.has_trait("BURNED_OUT") and mental < 0:
            mental = int(mental * 1.5)
        if self.has_trait("BATTLE_HARDENED") and mental < 0:
            mental = int(mental * 0.6)

        self.__subscribers = max(0, self.__subscribers + subs)
        self.__mental = max(0, min(100, self.__mental + mental))
        self.__reputation = max(0, min(100, self.__reputation + rep))
        self.__income = max(0, self.__income + income)
        self.__loyal_fans = max(0, min(100, self.__loyal_fans + loyal))
        self.__anti_fans = max(0, min(100, self.__anti_fans + anti))

    def add_flag(self, flag): self.flags.add(flag)
    def has_flag(self, flag): return flag in self.flags

    def status_card(self):
        traits_str = ", ".join(self.traits) if self.traits else "없음"
        return (
            f"┌─ {self.__name} ({self.archetype}) ──────────┐\n"
            f"│ 구독자  : {self.__subscribers:>10,}명         │\n"
            f"│ 멘탈    : {bar(self.__mental)}  {self.__mental:>3}%      │\n"
            f"│ 평판    : {bar(self.__reputation)}  {self.__reputation:>3}%      │\n"
            f"│ 수익    : {self.__income:>6,}만원/일             │\n"
            f"│ 충성팬  : {bar(self.__loyal_fans)}  {self.__loyal_fans:>3}%      │\n"
            f"│ 안티팬  : {bar(self.__anti_fans)}  {self.__anti_fans:>3}%      │\n"
            f"│ 특성    : {traits_str:<28}│\n"
            f"└────────────────────────────────────┘"
        )


def bar(value, length=10):
    filled = int(value / 100 * length)
    return "■" * filled + "□" * (length - filled)


# ============================================================
#  3. 여론 엔진
# ============================================================
class PublicOpinion:
    def __init__(self, youtuber):
        self.anger = min(100, 70 + (youtuber.get_anti() // 4))
        self.forgetting = 0
        self.youtuber = youtuber

    def daily_drift(self):
        loyal_bonus = self.youtuber.get_loyal() // 20
        self.anger = max(0, self.anger - random.randint(3, 8))
        self.forgetting = min(100, self.forgetting +
                              random.randint(5, 12) + loyal_bonus)

    def shift(self, anger_delta=0, forget_delta=0):
        self.anger = max(0, min(100, self.anger + anger_delta))
        self.forgetting = max(0, min(100, self.forgetting + forget_delta))

    def display(self):
        return (f"🔥 분노 : {bar(self.anger)} {self.anger}%\n"
                f"💭 망각 : {bar(self.forgetting)} {self.forgetting}%")


# ============================================================
#  4. 이벤트 시스템 (확률 + 특성 변화)
# ============================================================
class Event(ABC):
    def get_base_probability(self, youtuber, day):
        return 0.5

    def modify_probability(self, base_prob, youtuber, opinion, day):
        return base_prob

    def can_trigger(self, youtuber, opinion, day):
        return True

    def roll_probability(self, youtuber, opinion, day):
        if not self.can_trigger(youtuber, opinion, day):
            return 0.0
        base = self.get_base_probability(youtuber, day)
        return max(0.0, min(1.0,
                  self.modify_probability(base, youtuber, opinion, day)))

    @abstractmethod
    def trigger(self, youtuber, opinion, day):
        pass


# ============================================================
#  5. 시나리오 (자기 이벤트 풀 보유)
# ============================================================
class Scenario(ABC):
    def __init__(self, scenario_id, title):
        self.scenario_id = scenario_id
        self.title = title

    @abstractmethod
    def get_intro(self): pass
    @abstractmethod
    def get_actions(self): pass
    @abstractmethod
    def get_random_events(self): pass
    @abstractmethod
    def get_chained_events(self): pass


# ============================================================
#  6. 시나리오 1: 말실수
# ============================================================
class SlipOfTongueScenario(Scenario):
    def __init__(self):
        super().__init__("SLIP_TONGUE", "라이브 중 직업 비하 발언")

    def get_intro(self):
        return ("어제 라이브에서 특정 직업을 비하하는 발언이 송출됐다.\n"
                "0.7초 만에 클립이 만들어졌고, 이미 200만 뷰다.")

    def get_actions(self):
        return [ApologyLive(), GoSilent(), Diversion(), HireLawyer()]

    def get_random_events(self):
        return [JobUnionStatement(), ProtestComment(), SupportiveColumnist()]

    def get_chained_events(self):
        return [LawyerBackfireSlip(), ApologyMovesUnion()]


class JobUnionStatement(Event):
    def get_base_probability(self, youtuber, day): return 0.4
    def modify_probability(self, base, youtuber, opinion, day):
        if youtuber.get_mental() < 50: base += 0.15
        if youtuber.has_trait("MANY_ANTIS"): base += 0.1
        return base
    def trigger(self, youtuber, opinion, day):
        opinion.shift(anger_delta=+20, forget_delta=-15)
        youtuber.apply_change(subs=-25000, rep=-10, mental=-15, anti=+10)
        if youtuber.get_mental() < 30 and not youtuber.has_trait("BURNED_OUT"):
            youtuber.add_trait("BURNED_OUT", day)
        return ("🏛️ [노조 성명] 해당 직업군 노조가 공식 규탄 성명을 발표했다.\n"
                "    뉴스 헤드라인에 당신 채널명이 박혔다.")


class ProtestComment(Event):
    def get_base_probability(self, youtuber, day): return 0.5
    def modify_probability(self, base, youtuber, opinion, day):
        if youtuber.has_trait("FRAGILE_IMAGE"): base += 0.2
        return base
    def trigger(self, youtuber, opinion, day):
        opinion.shift(anger_delta=+10)
        youtuber.apply_change(mental=-10, anti=+5)
        return "💬 [댓글 시위] 당사자들이 모든 영상 댓글창을 점령했다."


class SupportiveColumnist(Event):
    def get_base_probability(self, youtuber, day): return 0.25
    def modify_probability(self, base, youtuber, opinion, day):
        if youtuber.get_reputation() > 60: base += 0.2
        if youtuber.has_trait("PURE_IMAGE"): base += 0.15
        return base
    def trigger(self, youtuber, opinion, day):
        opinion.shift(anger_delta=-15, forget_delta=+10)
        youtuber.apply_change(rep=+10, mental=+10)
        if not youtuber.has_trait("MEDIA_FRIENDLY"):
            youtuber.add_trait("MEDIA_FRIENDLY", day)
        return "📰 [우호 칼럼] 한 칼럼니스트가 '맥락이 있다'며 옹호 칼럼을 썼다."


class LawyerBackfireSlip(Event):
    def can_trigger(self, youtuber, opinion, day):
        return youtuber.has_flag("HIRED_LAWYER") and day >= 3
    def get_base_probability(self, youtuber, day): return 0.7
    def modify_probability(self, base, youtuber, opinion, day):
        if youtuber.has_trait("RICH"): base += 0.15
        return base
    def trigger(self, youtuber, opinion, day):
        opinion.shift(anger_delta=+25, forget_delta=-20)
        youtuber.apply_change(subs=-40000, rep=-15, mental=-20, anti=+15)
        if not youtuber.has_trait("LAWSUIT_TYRANT"):
            youtuber.add_trait("LAWSUIT_TYRANT", day)
        return ("⚖️💥 [연계] '돈으로 입막음' 프레임이 형성됐다.\n"
                "    당신은 '소송 폭군' 이미지를 얻었다.")


class ApologyMovesUnion(Event):
    def can_trigger(self, youtuber, opinion, day):
        return youtuber.has_flag("APOLOGIZED") and day >= 3
    def get_base_probability(self, youtuber, day): return 0.4
    def modify_probability(self, base, youtuber, opinion, day):
        if youtuber.get_mental() > 70: base += 0.2
        if youtuber.has_trait("MEDIA_FRIENDLY"): base += 0.15
        return base
    def trigger(self, youtuber, opinion, day):
        opinion.shift(anger_delta=-25, forget_delta=+20)
        youtuber.apply_change(subs=+10000, rep=+20, loyal=+10, mental=+15)
        if not youtuber.has_trait("REDEEMED"):
            youtuber.add_trait("REDEEMED", day)
        return ("🕊️ [연계] 노조가 사과를 공식적으로 수용했다.\n"
                "    '진정성 있다'는 평이 퍼졌다.")


# ============================================================
#  7. 시나리오 2: 뒷광고
# ============================================================
class FakeAdScenario(Scenario):
    def __init__(self):
        super().__init__("FAKE_AD", "뒷광고 의혹 폭로")

    def get_intro(self):
        return ("내부 고발자가 '내돈내산' 리뷰가 광고였다고 폭로했다.\n"
                "공정위 신고까지 들어갔다는 소문이 돈다.")

    def get_actions(self):
        return [ApologyLive(), GoSilent(), AdmitAndRefund(), HireLawyer()]

    def get_random_events(self):
        return [FTCInvestigation(), AdvertiserPullout(), VictimTestimony()]

    def get_chained_events(self):
        return [RefundSpreads(), SilenceTaxAudit()]


class FTCInvestigation(Event):
    def get_base_probability(self, youtuber, day): return 0.35
    def modify_probability(self, base, youtuber, opinion, day):
        if youtuber.has_trait("RICH"): base += 0.2
        if youtuber.get_anti() > 60: base += 0.1
        return base
    def trigger(self, youtuber, opinion, day):
        opinion.shift(anger_delta=+15, forget_delta=-15)
        youtuber.apply_change(income=-3000, mental=-15, rep=-10)
        if not youtuber.has_trait("UNDER_INVESTIGATION"):
            youtuber.add_trait("UNDER_INVESTIGATION", day)
        return ("🏛️ [공정위] 정식 조사가 시작됐다.\n"
                "    광고주들이 눈치를 본다.")


class AdvertiserPullout(Event):
    def get_base_probability(self, youtuber, day): return 0.5
    def modify_probability(self, base, youtuber, opinion, day):
        if youtuber.has_trait("UNDER_INVESTIGATION"): base += 0.3
        if youtuber.has_trait("FRAGILE_IMAGE"): base += 0.1
        return base
    def trigger(self, youtuber, opinion, day):
        youtuber.apply_change(income=-3500, mental=-10)
        return "💼 [광고 이탈] 메인 광고주 3곳이 계약 해지를 통보했다."


class VictimTestimony(Event):
    def get_base_probability(self, youtuber, day): return 0.45
    def modify_probability(self, base, youtuber, opinion, day):
        if youtuber.get_anti() > 50: base += 0.15
        return base
    def trigger(self, youtuber, opinion, day):
        opinion.shift(anger_delta=+20)
        youtuber.apply_change(subs=-20000, rep=-15, anti=+10)
        return "📸 [피해 인증] '이거 보고 샀는데...' 인증글이 쏟아진다."


class RefundSpreads(Event):
    def can_trigger(self, youtuber, opinion, day):
        return youtuber.has_flag("REFUNDED") and day >= 2
    def get_base_probability(self, youtuber, day): return 0.6
    def modify_probability(self, base, youtuber, opinion, day):
        if youtuber.has_trait("HIGH_LOYAL"): base += 0.2
        return base
    def trigger(self, youtuber, opinion, day):
        opinion.shift(anger_delta=-25, forget_delta=+25)
        youtuber.apply_change(subs=+20000, rep=+20, loyal=+15)
        if not youtuber.has_trait("INTEGRITY"):
            youtuber.add_trait("INTEGRITY", day)
        if youtuber.has_trait("UNDER_INVESTIGATION"):
            youtuber.remove_trait("UNDER_INVESTIGATION", day)
        return ("✨ [연계] 환불 미담이 메인 포털 1면에 걸렸다.\n"
                "    공정위도 '자율 시정'으로 마무리 분위기.")


class SilenceTaxAudit(Event):
    def can_trigger(self, youtuber, opinion, day):
        return youtuber.has_flag("WENT_SILENT") and day >= 4
    def get_base_probability(self, youtuber, day): return 0.4
    def modify_probability(self, base, youtuber, opinion, day):
        if youtuber.has_trait("RICH"): base += 0.25
        return base
    def trigger(self, youtuber, opinion, day):
        opinion.shift(anger_delta=+15)
        youtuber.apply_change(income=-5000, mental=-20, rep=-15)
        if not youtuber.has_trait("BURNED_OUT") and youtuber.get_mental() < 40:
            youtuber.add_trait("BURNED_OUT", day)
        return "💸 [연계] 잠수타는 동안 국세청이 세무조사를 통보했다."


# ============================================================
#  8. 시나리오 3: 동료 험담
# ============================================================
class BackbiteScenario(Scenario):
    def __init__(self):
        super().__init__("BACKBITE", "동료 험담이 마이크로 송출됨")

    def get_intro(self):
        return ("끄지 않은 마이크로 동료 험담이 송출됐다.\n"
                "당사자가 SNS에 '실망했다'를 올렸다.")

    def get_actions(self):
        return [ApologyLive(), GoSilent(), DirectMessage(), Diversion()]

    def get_random_events(self):
        return [VictimGoesPublic(), CommunityCutoff(), MutualFriendMediates()]

    def get_chained_events(self):
        return [DMReconcile(), DiversionExposesMore()]


class VictimGoesPublic(Event):
    def get_base_probability(self, youtuber, day): return 0.4
    def modify_probability(self, base, youtuber, opinion, day):
        if youtuber.get_mental() < 50: base += 0.2
        if youtuber.has_trait("WEAK_MENTAL"): base += 0.15
        return base
    def trigger(self, youtuber, opinion, day):
        opinion.shift(anger_delta=+25, forget_delta=-20)
        youtuber.apply_change(subs=-30000, rep=-15, mental=-20, anti=+15)
        if youtuber.get_mental() < 30 and not youtuber.has_trait("BURNED_OUT"):
            youtuber.add_trait("BURNED_OUT", day)
        return "📢 [추가 폭로] 당사자가 '예전에도 이런 일이 있었다'고 폭로했다."


class CommunityCutoff(Event):
    def get_base_probability(self, youtuber, day): return 0.35
    def modify_probability(self, base, youtuber, opinion, day):
        if youtuber.has_trait("MANY_ANTIS"): base += 0.15
        if youtuber.has_trait("LAWSUIT_TYRANT"): base += 0.2
        return base
    def trigger(self, youtuber, opinion, day):
        opinion.shift(anger_delta=+10)
        youtuber.apply_change(mental=-15, rep=-10, loyal=-5)
        if not youtuber.has_trait("ISOLATED"):
            youtuber.add_trait("ISOLATED", day)
        return "🚪 [손절] 동료 유튜버 5명이 단체로 언팔/구독 해제했다."


class MutualFriendMediates(Event):
    def get_base_probability(self, youtuber, day): return 0.3
    def modify_probability(self, base, youtuber, opinion, day):
        if youtuber.get_reputation() > 60: base += 0.2
        if youtuber.has_trait("ISOLATED"): base -= 0.3
        return base
    def trigger(self, youtuber, opinion, day):
        opinion.shift(anger_delta=-15, forget_delta=+10)
        youtuber.apply_change(rep=+10, mental=+10)
        return "🕊️ [중재] 공통 지인이 양측을 중재하기 시작했다."


class DMReconcile(Event):
    def can_trigger(self, youtuber, opinion, day):
        return youtuber.has_flag("DM_SENT") and day >= 2
    def get_base_probability(self, youtuber, day): return 0.5
    def modify_probability(self, base, youtuber, opinion, day):
        if youtuber.get_mental() > 70: base += 0.15
        if youtuber.has_trait("ISOLATED"): base -= 0.2
        return base
    def trigger(self, youtuber, opinion, day):
        opinion.shift(anger_delta=-30, forget_delta=+20)
        youtuber.apply_change(subs=+15000, rep=+20, loyal=+10, mental=+10)
        if not youtuber.has_trait("RECONCILED"):
            youtuber.add_trait("RECONCILED", day)
        if youtuber.has_trait("ISOLATED"):
            youtuber.remove_trait("ISOLATED", day)
        return "💌 [연계] 당사자가 '진심이 느껴졌다'며 화해 인증샷을 올렸다."


class DiversionExposesMore(Event):
    def can_trigger(self, youtuber, opinion, day):
        return youtuber.has_flag("USED_DIVERSION") and day >= 3
    def get_base_probability(self, youtuber, day): return 0.55
    def modify_probability(self, base, youtuber, opinion, day):
        if youtuber.has_trait("FRAGILE_IMAGE"): base += 0.2
        return base
    def trigger(self, youtuber, opinion, day):
        opinion.shift(anger_delta=+20)
        youtuber.apply_change(subs=-25000, rep=-15, mental=-10)
        return "🎭 [연계] 물타기 영상에서 또 다른 실언이 발견됐다."


# ============================================================
#  9. 행동 시스템
# ============================================================
class Action(ABC):
    def __init__(self, name, description):
        self.name = name
        self.description = description
    @abstractmethod
    def execute(self, youtuber, opinion, day): pass


class ApologyLive(Action):
    def __init__(self):
        super().__init__("진정성 사과 라이브", "눈물 한 방울이 살릴 수도, 죽일 수도.")
    def execute(self, youtuber, opinion, day):
        already_apologized = youtuber.has_flag("APOLOGIZED")
        youtuber.add_flag("APOLOGIZED")
        if already_apologized:
            # 반복 사과: '또 사과야?' 효과 격감, 진정성 의심
            opinion.shift(anger_delta=-5, forget_delta=+3)
            youtuber.apply_change(subs=-20000, mental=-12, rep=-5, anti=+5)
            return "😩 '또 사과야?' 진정성이 의심받는다."
        if opinion.anger > 70:
            opinion.shift(anger_delta=-25, forget_delta=+10)
            youtuber.apply_change(subs=-30000, mental=-10, rep=+15, loyal=+5)
            return "💧 눈물의 사과가 통했다."
        else:
            opinion.shift(anger_delta=+15, forget_delta=-20)
            youtuber.apply_change(subs=-80000, mental=-15, rep=-10, anti=+10)
            return "😡 잠잠해지던 여론에 기름을 부었다."


class GoSilent(Action):
    def __init__(self):
        super().__init__("잠수 타기", "운이 좋다면.")
    def execute(self, youtuber, opinion, day):
        youtuber.add_flag("WENT_SILENT")
        opinion.shift(forget_delta=+15)
        youtuber.apply_change(income=-1000, mental=+5, loyal=-5)
        return "🤐 일단 조용히 지나간다."


class Diversion(Action):
    def __init__(self):
        super().__init__("물타기 콘텐츠 업로드", "강아지 영상 가즈아.")
    def execute(self, youtuber, opinion, day):
        youtuber.add_flag("USED_DIVERSION")
        if opinion.forgetting > 50:
            opinion.shift(anger_delta=-15, forget_delta=+10)
            youtuber.apply_change(subs=+10000, income=+500, mental=+5)
            return "🐶 알고리즘의 승리."
        else:
            opinion.shift(anger_delta=+25)
            youtuber.apply_change(subs=-50000, rep=-15, mental=-15, anti=+10)
            return "🤬 댓글창이 불바다."


class HireLawyer(Action):
    def __init__(self):
        super().__init__("법적 대응 선언", "고소장은 무거울수록 좋다.")
    def execute(self, youtuber, opinion, day):
        youtuber.add_flag("HIRED_LAWYER")
        opinion.shift(anger_delta=+10, forget_delta=-10)
        rep_bonus = 10 if youtuber.has_trait("RICH") else 5
        youtuber.apply_change(income=-2000, rep=+rep_bonus, mental=+10)
        return "⚖️ 변호사 선임."


class AdmitAndRefund(Action):
    def __init__(self):
        super().__init__("전액 환불 + 시인", "지갑을 열면 마음이 열릴까?")
    def execute(self, youtuber, opinion, day):
        youtuber.add_flag("REFUNDED")
        opinion.shift(anger_delta=-30, forget_delta=+15)
        youtuber.apply_change(subs=-10000, income=-3000, rep=+25, loyal=+10)
        return "💸 전액 환불 + 공식 시인."


class DirectMessage(Action):
    def __init__(self):
        super().__init__("당사자에게 사과 DM", "공개보다 진심이 통할 수도.")
    def execute(self, youtuber, opinion, day):
        youtuber.add_flag("DM_SENT")
        if random.random() < 0.6:
            opinion.shift(anger_delta=-20, forget_delta=+10)
            youtuber.apply_change(rep=+15, mental=+5)
            return "📩 당사자가 '잘 받았다'고 SNS에 올렸다."
        else:
            opinion.shift(anger_delta=+15)
            youtuber.apply_change(rep=-10, mental=-10, anti=+10)
            return "📵 DM이 캡처돼 공개됐다."


# ============================================================
#  10. 캐릭터 선택 화면
# ============================================================
def character_select():
    print("\n" + "=" * 55)
    print("  🎭  캐릭터를 선택하세요  🎭")
    print("=" * 55)
    for i, c in enumerate(CHARACTERS, 1):
        print(f"\n  [{i}] {c.name}  ({c.archetype})")
        print(f"      구독자 {c.subs:,} / 멘탈 {c.mental} / 평판 {c.reputation}")
        print(f"      충성팬 {c.loyal_fans} / 안티팬 {c.anti_fans}")
        print(f"      특성: {', '.join(c.traits)}")
        print(f"      💬 {c.description}")
    while True:
        try:
            ch = int(input(f"\n선택 (1~{len(CHARACTERS)}): "))
            if 1 <= ch <= len(CHARACTERS): return CHARACTERS[ch-1]
        except ValueError: pass


# ============================================================
#  11. 게임 매니저
# ============================================================
class GameManager:
    def __init__(self, preset):
        self.youtuber = Youtuber(preset)
        self.opinion = PublicOpinion(self.youtuber)
        self.day = 0
        self.scenario = random.choice([
            SlipOfTongueScenario(), FakeAdScenario(), BackbiteScenario(),
        ])
        self.actions = self.scenario.get_actions()

    def intro(self):
        print("\n" + "=" * 55)
        print("  📺  100만 유튜버 위기관리 시뮬레이션  📺")
        print("=" * 55)
        print(f"\n🎭 캐릭터: 「{self.youtuber.get_name()}」")
        print(f"📰 사건: 「{self.scenario.title}」\n")
        print(self.scenario.get_intro())

    def pick_event(self):
        all_events = (self.scenario.get_random_events() +
                      self.scenario.get_chained_events())
        weighted = []
        for ev in all_events:
            prob = ev.roll_probability(self.youtuber, self.opinion, self.day)
            if prob > 0:
                weighted.append((ev, prob))
        if not weighted: return None
        if random.random() < 0.2: return None  # 20% 무이벤트
        events, probs = zip(*weighted)
        return random.choices(events, weights=probs, k=1)[0]

    def play_day(self):
        self.day += 1
        print("\n" + "═" * 55)
        print(f"  📅  Day {self.day}")
        print("═" * 55)
        self.opinion.daily_drift()

        event = self.pick_event()
        if event:
            print(f"\n[오늘의 이벤트]")
            print(f"  {event.trigger(self.youtuber, self.opinion, self.day)}")
        else:
            print("\n[오늘의 이벤트]\n  ☀️ 큰 이슈 없이 흘러갔다.")

        print(f"\n{self.opinion.display()}")
        print(f"\n{self.youtuber.status_card()}")
        print("\n[행동 선택]")
        for i, act in enumerate(self.actions, 1):
            print(f"  {i}. {act.name} — {act.description}")
        ch = self._get_choice(len(self.actions))
        print(f"\n👉 {self.actions[ch-1].execute(self.youtuber, self.opinion, self.day)}")

    def _get_choice(self, n):
        while True:
            try:
                c = int(input(f"\n선택 (1~{n}): "))
                if 1 <= c <= n: return c
            except ValueError: pass

    def check_ending(self):
        y, o = self.youtuber, self.opinion
        if y.get_subs() < 100_000:
            return "💀 [BAD ENDING] 채널 폭파"
        if y.get_mental() <= 0:
            return "🏥 [ENDING] 무기한 활동 중단"
        if y.has_trait("REDEEMED") and o.forgetting >= 70:
            return "🌟 [TRUE GOOD] 진정성 있는 컴백"
        if y.has_trait("LAWSUIT_TYRANT") and y.get_anti() > 80:
            return "👹 [BAD ENDING] 소송 폭군의 몰락"
        if y.has_trait("INTEGRITY") and y.get_reputation() >= 75:
            return "👑 [TRUE ENDING] 신뢰의 아이콘"
        if o.forgetting >= 80 and o.anger <= 20:
            return "🌟 [GOOD ENDING] 완벽한 컴백"
        return None

    def run(self):
        self.intro()
        for _ in range(7):
            self.play_day()
            ending = self.check_ending()
            if ending:
                self._print_ending(ending)
                return
        self._print_ending("⏰ [NORMAL] 그럭저럭 살아남음")

    def _print_ending(self, ending):
        print("\n" + "═" * 55)
        print(ending)
        print(f"\n캐릭터: {self.youtuber.get_name()}")
        print(f"시나리오: {self.scenario.title}")
        print(f"\n[특성 변화 로그]")
        for day, sign, trait in self.youtuber.trait_log:
            print(f"  Day {day}: {sign} {trait}")
        print("═" * 55)
        print(self.youtuber.status_card())


# ============================================================
#  실행
# ============================================================
if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        st.error(f"렌더링 에러: {e}")
        import traceback
        st.code(traceback.format_exc())
