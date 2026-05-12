# ============================================================
#  100만 유튜버 위기관리 시뮬레이션 — Streamlit Web Demo v2
#
#  ※ youtuber_crisis_v4.py 의 클래스를 그대로 import하여 사용.
#    원본 OOP 설계는 한 줄도 수정하지 않음.
#
#  v2 변경점:
#  - HTML 들여쓰기 버그 패치 (코드 블록 오인 방지)
#  - Plotly 라인차트 (7일간 능력치 추이)
#  - 가짜 댓글/트윗 피드 (시나리오·여론 연동)
#  - 토스트 알림 (이벤트/특성 획득)
# ============================================================

import io
import random
import contextlib
import streamlit as st
import plotly.graph_objects as go

from youtuber_crisis_v4 import (
    CHARACTERS,
    Youtuber,
    PublicOpinion,
    GameManager,
    SlipOfTongueScenario,
    FakeAdScenario,
    BackbiteScenario,
)

st.set_page_config(
    page_title="유튜버 위기관리 시뮬레이션",
    page_icon="📺",
    layout="wide",
)

# CSS는 들여쓰기 없이 한 덩어리로 (코드 블록 오인 방지)
st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=JetBrains+Mono:wght@400;700&family=Noto+Sans+KR:wght@400;500;700;800&display=swap');
html, body, [class*="css"] { font-family: 'Noto Sans KR', sans-serif; }
.stApp { background: #050505; color: #fff; }
h1, h2, h3 { font-family: 'Bebas Neue', 'Noto Sans KR', sans-serif !important; letter-spacing: 0.02em !important; color: #fff !important; }
.crisis-tag { display: inline-block; font-family: 'JetBrains Mono', monospace; font-size: 11px; letter-spacing: 0.3em; color: #ff0033; font-weight: 700; margin-bottom: 8px; }
.scenario-card { background: linear-gradient(135deg, #1a0008 0%, #0d0d0d 100%); border: 1px solid #330011; border-left: 3px solid #ff0033; padding: 18px; border-radius: 4px; margin: 12px 0; }
.event-card { background: #0d0d0d; border: 1px solid #222; padding: 16px; border-radius: 4px; margin: 12px 0; }
.section-label { font-family: 'JetBrains Mono', monospace; font-size: 10px; letter-spacing: 0.3em; color: #666; margin-bottom: 10px; text-transform: uppercase; }
.trait-chip { display: inline-block; font-family: 'JetBrains Mono', monospace; font-size: 10px; padding: 4px 8px; background: #1a0a0e; border: 1px solid #330011; border-radius: 2px; color: #ff5577; margin: 2px; }
.starting-trait-chip { display: inline-block; font-family: 'JetBrains Mono', monospace; font-size: 10px; padding: 3px 7px; background: #1a1a1a; border: 1px solid #2a2a2a; border-radius: 2px; color: #ff0033; margin: 2px; }
.ending-card-good { background: #0d0d0d; border: 1px solid #00ff88; border-top: 3px solid #00ff88; padding: 32px; border-radius: 4px; }
.ending-card-bad { background: #0d0d0d; border: 1px solid #ff0033; border-top: 3px solid #ff0033; padding: 32px; border-radius: 4px; }
.stat-box { background: #141414; border: 1px solid #222; padding: 14px; border-radius: 3px; }
.gauge-wrap { margin-bottom: 8px; }
.gauge-label-row { display: flex; justify-content: space-between; font-family: 'JetBrains Mono', monospace; font-size: 11px; letter-spacing: 0.1em; color: #888; margin-bottom: 4px; }
.gauge-track { height: 6px; background: #1a1a1a; border-radius: 1px; overflow: hidden; }
.gauge-fill { height: 100%; transition: width 0.6s cubic-bezier(0.4, 0, 0.2, 1); }
.comment-feed { max-height: 280px; overflow-y: auto; padding-right: 4px; }
.comment-item { background: #0a0a0a; border-left: 2px solid #333; padding: 8px 10px; margin-bottom: 6px; font-size: 12px; }
.comment-item.angry { border-left-color: #ff0033; }
.comment-item.support { border-left-color: #00ff88; }
.comment-item.meme { border-left-color: #ffcc00; }
.comment-author { font-family: 'JetBrains Mono', monospace; font-size: 10px; color: #888; margin-bottom: 3px; }
.comment-text { color: #ccc; line-height: 1.4; }
div[data-testid="stHorizontalBlock"] > div[data-testid="column"] > div > div > div > button { background: #141414 !important; border: 1px solid #2a2a2a !important; color: #fff !important; padding: 14px !important; width: 100% !important; text-align: left !important; transition: all 0.15s !important; }
div[data-testid="stHorizontalBlock"] > div[data-testid="column"] > div > div > div > button:hover { border-color: #ff0033 !important; background: #1a0a0e !important; }
hr { border-color: #222 !important; }
[data-testid="stSidebar"] { background: #0a0a0a; }
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: #0d0d0d; }
::-webkit-scrollbar-thumb { background: #2a2a2a; border-radius: 3px; }
</style>""", unsafe_allow_html=True)


TRAIT_LABEL = {
    "HIGH_LOYAL": "충성팬↑", "MANY_ANTIS": "안티多", "STRONG_MENTAL": "강철멘탈",
    "FRAGILE_IMAGE": "유리이미지", "RICH": "재력가", "WEAK_MENTAL": "유리멘탈",
    "UNDERDOG": "언더독", "PURE_IMAGE": "순수이미지", "BURNED_OUT": "번아웃",
    "BATTLE_HARDENED": "전투단련", "MEDIA_FRIENDLY": "언론우호",
    "LAWSUIT_TYRANT": "소송폭군", "UNDER_INVESTIGATION": "조사중",
    "INTEGRITY": "정직", "ISOLATED": "고립", "RECONCILED": "화해", "REDEEMED": "구원",
}


def render_gauge(label, value, color, max_val=100):
    pct = min(100, (value / max_val) * 100)
    html = (
        f'<div class="gauge-wrap">'
        f'<div class="gauge-label-row"><span>{label}</span>'
        f'<span style="color:{color};">{int(value)}%</span></div>'
        f'<div class="gauge-track">'
        f'<div class="gauge-fill" style="width:{pct}%;background:{color};'
        f'box-shadow:0 0 8px {color}66;"></div>'
        f'</div></div>'
    )
    st.markdown(html, unsafe_allow_html=True)


def trait_chips_html(traits, style="dynamic"):
    cls = "trait-chip" if style == "dynamic" else "starting-trait-chip"
    if not traits:
        return '<span style="color:#666;font-size:11px;">없음</span>'
    return "".join(f'<span class="{cls}">{TRAIT_LABEL.get(t, t)}</span>' for t in traits)


# ============================================================
#  댓글 피드
# ============================================================
COMMENT_POOLS = {
    "angry": [
        ("@cyberwrecker_TV", "이게 100만 유튜버가 할 짓인가요? 진짜 실망"),
        ("@news_pickup", "📢 단독: {name} 논란 일파만파, 광고주 5곳 검토 중"),
        ("@anti_official", "오늘부터 구독취소 ✂️ 다 끊자"),
        ("@truthseeker", "이 사람 옛날부터 이상했어요. 증거 다 있음"),
        ("@coolheaded", "사과 한 번으로 끝낼 일이 아니죠"),
        ("@user_realtalk", "이게 진짜 본성이지. 가면 벗겨졌네"),
    ],
    "support": [
        ("@loyal_fan_01", "그래도 {name}님 응원합니다 💚"),
        ("@daily_subscriber", "사람이 실수할 수도 있죠. 너무 몰아가지 말자"),
        ("@still_here", "다들 한 번씩 말실수는 하잖아요. 진심으로 사과하셨으면 됐어요"),
        ("@positivevibes", "예전 영상들 보고 응원하던 사람입니다. 힘내세요"),
        ("@founder_member", "5년 전부터 구독한 사람으로서 믿습니다"),
    ],
    "meme": [
        ("@meme_machine", "이거 짤로 만들어도 돼요? ㅋㅋㅋㅋㅋㅋ"),
        ("@youtube_reactor", "🎬 반응영상 올렸습니다 (제가 더 화남)"),
        ("@spicy_take", "사과 BGM 너무 슬픔ㅋㅋㅋ 의도된거임?"),
        ("@catch_phrase", "오늘부터 '말실수챌린지' 시작합니다"),
        ("@youtube_clipper", "이미 클립 4만뷰 돌파 ㅋㅋㅋㅋ"),
    ],
    "forget": [
        ("@today_news", "오늘의 핫이슈: 새 드라마 출연진 발표"),
        ("@bored_user", "이 채널 또 왜 떴지... 별 관심 없는데"),
        ("@trend_watcher", "이거 무슨 일이었지? 기억도 안남"),
        ("@scrolling_thru", "음 그래서 결론이 뭐였더라"),
    ],
}


def generate_comments(state, n=6):
    anger = state.opinion.anger
    forget = state.opinion.forgetting
    loyal = state.youtuber.get_loyal()
    w_angry = max(5, anger - 10)
    w_support = max(5, loyal - 10)
    w_meme = max(10, 100 - forget)
    w_forget = max(5, forget - 20)

    pool = []
    for c in COMMENT_POOLS["angry"]: pool.append((c, w_angry, "angry"))
    for c in COMMENT_POOLS["support"]: pool.append((c, w_support, "support"))
    for c in COMMENT_POOLS["meme"]: pool.append((c, w_meme, "meme"))
    for c in COMMENT_POOLS["forget"]: pool.append((c, w_forget, "forget"))

    weights = [w for (_, w, _) in pool]
    picked = random.choices(pool, weights=weights, k=min(n, len(pool)))
    name = state.youtuber.get_name()
    return [
        {"author": author, "text": text.format(name=name), "cls": cls}
        for (author, text), _, cls in picked
    ]


def render_comment_feed(state):
    comments = generate_comments(state, n=6)
    items_html = "".join(
        f'<div class="comment-item {c["cls"]}">'
        f'<div class="comment-author">{c["author"]}</div>'
        f'<div class="comment-text">{c["text"]}</div></div>'
        for c in comments
    )
    html = (
        f'<div class="event-card">'
        f'<div class="section-label">▌ 실시간 댓글·반응 📡</div>'
        f'<div class="comment-feed">{items_html}</div>'
        f'</div>'
    )
    st.markdown(html, unsafe_allow_html=True)


# ============================================================
#  라인차트
# ============================================================
def render_history_chart(history):
    if len(history) < 2:
        return
    days = [h["day"] for h in history]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=days, y=[h["mental"] for h in history],
        mode="lines+markers", name="멘탈",
        line=dict(color="#00d4ff", width=2), marker=dict(size=6)))
    fig.add_trace(go.Scatter(x=days, y=[h["reputation"] for h in history],
        mode="lines+markers", name="평판",
        line=dict(color="#ffffff", width=2), marker=dict(size=6)))
    fig.add_trace(go.Scatter(x=days, y=[h["loyal"] for h in history],
        mode="lines+markers", name="충성팬",
        line=dict(color="#00ff88", width=2), marker=dict(size=6)))
    fig.add_trace(go.Scatter(x=days, y=[h["anti"] for h in history],
        mode="lines+markers", name="안티팬",
        line=dict(color="#ff0033", width=2), marker=dict(size=6)))
    fig.update_layout(
        plot_bgcolor="#0d0d0d", paper_bgcolor="#0d0d0d",
        font=dict(color="#aaa", family="JetBrains Mono", size=11),
        height=240, margin=dict(l=10, r=10, t=10, b=10),
        xaxis=dict(title="DAY", gridcolor="#1a1a1a", zerolinecolor="#1a1a1a",
                   tickmode="linear", dtick=1, range=[-0.5, 7.5]),
        yaxis=dict(gridcolor="#1a1a1a", zerolinecolor="#1a1a1a", range=[0, 105]),
        legend=dict(orientation="h", yanchor="bottom", y=1.02,
                    xanchor="right", x=1, bgcolor="rgba(0,0,0,0)"),
        hovermode="x unified",
    )
    st.plotly_chart(fig, use_container_width=True, key=f"chart_d{len(history)}")


# ============================================================
#  세션 상태
# ============================================================
def init_session():
    defaults = {
        "phase": "select", "manager": None, "logs": [],
        "current_event_msg": None, "ending": None,
        "history": [], "pending_toasts": [],
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def snapshot_stats():
    mgr = st.session_state.manager
    y = mgr.youtuber
    st.session_state.history.append({
        "day": mgr.day, "subs": y.get_subs(),
        "mental": y.get_mental(), "reputation": y.get_reputation(),
        "loyal": y.get_loyal(), "anti": y.get_anti(),
    })


def detect_new_traits(before, after):
    return ([t for t in after if t not in before],
            [t for t in before if t not in after])


# ============================================================
#  게임 진행 로직
# ============================================================
def start_new_game(preset_idx):
    preset = CHARACTERS[preset_idx]
    mgr = GameManager(preset)
    st.session_state.manager = mgr
    st.session_state.logs = []
    st.session_state.ending = None
    st.session_state.phase = "playing"
    st.session_state.history = [{
        "day": 0, "subs": mgr.youtuber.get_subs(),
        "mental": mgr.youtuber.get_mental(),
        "reputation": mgr.youtuber.get_reputation(),
        "loyal": mgr.youtuber.get_loyal(), "anti": mgr.youtuber.get_anti(),
    }]
    st.session_state.pending_toasts = []
    advance_to_next_day()


def advance_to_next_day():
    mgr = st.session_state.manager
    mgr.day += 1
    mgr.opinion.daily_drift()

    before_traits = list(mgr.youtuber.traits)
    event = mgr.pick_event()
    if event:
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            msg = event.trigger(mgr.youtuber, mgr.opinion, mgr.day)
        st.session_state.current_event_msg = msg
        st.session_state.pending_toasts.append(("📡 이벤트", msg, "🔔"))
    else:
        st.session_state.current_event_msg = "☀️ 큰 이슈 없이 흘러갔다."

    added, removed = detect_new_traits(before_traits, mgr.youtuber.traits)
    for t in added:
        st.session_state.pending_toasts.append(
            (f"✨ 특성 획득", TRAIT_LABEL.get(t, t), "⭐"))
    for t in removed:
        st.session_state.pending_toasts.append(
            (f"💨 특성 상실", TRAIT_LABEL.get(t, t), "🌬️"))


def do_action(action_idx):
    mgr = st.session_state.manager
    action = mgr.actions[action_idx]
    before_traits = list(mgr.youtuber.traits)

    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        result = action.execute(mgr.youtuber, mgr.opinion, mgr.day)

    added, removed = detect_new_traits(before_traits, mgr.youtuber.traits)
    for t in added:
        st.session_state.pending_toasts.append(
            (f"✨ 특성 획득", TRAIT_LABEL.get(t, t), "⭐"))
    for t in removed:
        st.session_state.pending_toasts.append(
            (f"💨 특성 상실", TRAIT_LABEL.get(t, t), "🌬️"))

    st.session_state.logs.append({
        "day": mgr.day,
        "event": st.session_state.current_event_msg,
        "action_name": action.name,
        "result": result,
    })
    st.session_state.current_event_msg = None
    snapshot_stats()

    ending_str = mgr.check_ending()
    if ending_str:
        st.session_state.ending = ending_str
        st.session_state.phase = "ended"
        return
    if mgr.day >= 7:
        st.session_state.ending = "⏰ [NORMAL] 그럭저럭 살아남음"
        st.session_state.phase = "ended"
        return
    advance_to_next_day()


def restart():
    for k in ("phase", "manager", "logs", "current_event_msg",
              "ending", "history", "pending_toasts"):
        if k in st.session_state:
            del st.session_state[k]
    init_session()


def flush_toasts():
    for title, body, icon in st.session_state.pending_toasts:
        st.toast(f"**{title}** — {body}", icon=icon)
    st.session_state.pending_toasts = []


# ============================================================
#  화면 1: 캐릭터 선택
# ============================================================
def render_select():
    st.markdown('<div class="crisis-tag">◉ LIVE — CRISIS MODE</div>', unsafe_allow_html=True)
    st.markdown(
        '<h1 style="font-size:56px;line-height:1;margin:0;">어제의 말실수,<br>'
        '<span style="color:#ff0033;">오늘의 생존게임</span></h1>'
        '<p style="color:#888;margin-top:16px;font-size:14px;">'
        '7일의 시간이 주어졌다. 구독자 10만 명 밑으로 떨어지면 끝.<br>'
        '누가 이 위기에서 살아남을 것인가.</p>',
        unsafe_allow_html=True,
    )
    st.markdown('<div class="section-label">── 캐릭터 선택 ──</div>', unsafe_allow_html=True)

    cols = st.columns(3)
    for i, c in enumerate(CHARACTERS):
        with cols[i % 3]:
            card = (
                f'<div style="background:#0d0d0d;border:1px solid #222;border-radius:4px;'
                f'padding:18px;margin-bottom:12px;">'
                f'<div style="font-family:\'JetBrains Mono\',monospace;font-size:10px;'
                f'color:#666;margin-bottom:4px;">CH.0{i+1} / {c.archetype}</div>'
                f'<div style="font-family:\'Bebas Neue\',sans-serif;font-size:24px;'
                f'font-weight:800;letter-spacing:0.02em;margin-bottom:8px;">{c.name}</div>'
                f'<div style="font-size:12px;color:#aaa;margin-bottom:14px;min-height:32px;">'
                f'{c.description}</div>'
                f'<div style="font-family:\'JetBrains Mono\',monospace;font-size:11px;color:#888;">'
                f'<div style="display:flex;justify-content:space-between;padding:3px 0;">'
                f'<span>SUBS</span><span style="color:#fff;">{c.subs:,}</span></div>'
                f'<div style="display:flex;justify-content:space-between;padding:3px 0;">'
                f'<span>MENTAL / REP</span>'
                f'<span style="color:#fff;">{c.mental} / {c.reputation}</span></div>'
                f'<div style="display:flex;justify-content:space-between;padding:3px 0;">'
                f'<span>LOYAL / ANTI</span>'
                f'<span style="color:#fff;">{c.loyal_fans} / {c.anti_fans}</span></div>'
                f'</div>'
                f'<div style="margin-top:12px;">{trait_chips_html(c.traits, "starting")}</div>'
                f'</div>'
            )
            st.markdown(card, unsafe_allow_html=True)
            if st.button(f"▸ {c.name} 선택", key=f"pick_{i}", use_container_width=True):
                start_new_game(i)
                st.rerun()


# ============================================================
#  화면 2: 게임 진행
# ============================================================
def render_playing():
    mgr = st.session_state.manager
    y = mgr.youtuber
    o = mgr.opinion
    s = mgr.scenario

    flush_toasts()

    col_a, col_b = st.columns([4, 1])
    with col_a:
        st.markdown(
            f'<div class="crisis-tag">◉ DAY {mgr.day} / 07 — 위기 진행 중</div>'
            f'<div style="font-family:\'Bebas Neue\',sans-serif;font-size:24px;font-weight:800;">'
            f'{y.get_name()} <span style="color:#666;font-weight:400;font-size:14px;">'
            f'· {y.archetype}</span></div>',
            unsafe_allow_html=True,
        )
    with col_b:
        if st.button("RESTART", use_container_width=True):
            restart()
            st.rerun()

    st.markdown("---")

    st.markdown(
        f'<div class="scenario-card">'
        f'<div class="crisis-tag">▌ 사건 발생</div>'
        f'<div style="font-family:\'Bebas Neue\',sans-serif;font-size:18px;'
        f'font-weight:700;margin-bottom:8px;">{s.title}</div>'
        f'<div style="font-size:13px;color:#aaa;line-height:1.6;">{s.get_intro()}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    main_col, side_col = st.columns([2, 1])

    with main_col:
        if st.session_state.current_event_msg:
            st.markdown(
                f'<div class="event-card">'
                f'<div class="section-label">▸ DAY {mgr.day} — 오늘의 이벤트</div>'
                f'<div style="color:#ffcc00;font-size:14px;">📡 {st.session_state.current_event_msg}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

        st.markdown(
            '<div class="section-label" style="margin-top:8px;">▌ 여론 게이지</div>',
            unsafe_allow_html=True,
        )
        render_gauge("분노 ANGER", o.anger, "#ff0033")
        render_gauge("망각 FORGET", o.forgetting, "#00d4ff")

        if len(st.session_state.history) >= 2:
            st.markdown(
                '<div class="section-label" style="margin-top:18px;">▌ 능력치 추이</div>',
                unsafe_allow_html=True,
            )
            render_history_chart(st.session_state.history)

        st.markdown(
            '<div class="section-label" style="margin-top:14px;">▌ 행동 선택</div>',
            unsafe_allow_html=True,
        )
        action_cols = st.columns(2)
        for i, act in enumerate(mgr.actions):
            with action_cols[i % 2]:
                if st.button(
                    f"**{act.name}**\n\n{act.description}",
                    key=f"act_{i}_d{mgr.day}",
                    use_container_width=True,
                ):
                    do_action(i)
                    st.rerun()

        if st.session_state.logs:
            with st.expander(f"📜 진행 로그 ({len(st.session_state.logs)}개)", expanded=False):
                for log in reversed(st.session_state.logs):
                    st.markdown(
                        f'<div style="border-bottom:1px solid #1a1a1a;padding:10px 0;font-size:12px;">'
                        f'<span style="color:#ff0033;font-family:\'JetBrains Mono\',monospace;">'
                        f'D{log["day"]}</span>'
                        f'<div style="color:#aaa;margin-top:4px;">📡 {log["event"]}</div>'
                        f'<div style="color:#fff;margin-top:4px;">'
                        f'<span style="color:#888;">[{log["action_name"]}]</span> {log["result"]}'
                        f'</div></div>',
                        unsafe_allow_html=True,
                    )

    with side_col:
        st.markdown(
            f'<div class="event-card">'
            f'<div class="section-label">▌ 채널 상태</div>'
            f'<div style="font-family:\'Bebas Neue\',sans-serif;font-size:28px;font-weight:800;">'
            f'{y.get_subs():,}</div>'
            f'<div style="font-family:\'JetBrains Mono\',monospace;font-size:10px;color:#666;'
            f'letter-spacing:0.2em;margin-bottom:12px;">구독자 SUBSCRIBERS</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
        render_gauge("멘탈 MENTAL", y.get_mental(), "#00d4ff")
        render_gauge("평판 REP", y.get_reputation(), "#ffffff")
        render_gauge("충성팬 LOYAL", y.get_loyal(), "#00ff88")
        render_gauge("안티팬 ANTI", y.get_anti(), "#ff0033")

        st.markdown(
            f'<div class="event-card">'
            f'<div style="display:flex;justify-content:space-between;'
            f'font-family:\'JetBrains Mono\',monospace;font-size:11px;color:#888;'
            f'padding-bottom:8px;border-bottom:1px solid #1a1a1a;margin-bottom:12px;">'
            f'<span>일 수익</span><span style="color:#fff;">{y.get_income():,}만원</span></div>'
            f'<div class="section-label">▌ 특성 ({len(y.traits)})</div>'
            f'<div>{trait_chips_html(y.traits)}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

        render_comment_feed(mgr)


# ============================================================
#  화면 3: 엔딩
# ============================================================
def render_ended():
    mgr = st.session_state.manager
    y = mgr.youtuber
    ending = st.session_state.ending

    is_good = any(k in ending for k in ["GOOD", "TRUE"])
    card_cls = "ending-card-good" if is_good else "ending-card-bad"
    accent = "#00ff88" if is_good else "#ff0033"

    col = st.columns([1, 6, 1])[1]
    with col:
        st.markdown(
            f'<div class="{card_cls}">'
            f'<div style="font-family:\'JetBrains Mono\',monospace;font-size:11px;'
            f'letter-spacing:0.4em;color:{accent};margin-bottom:16px;">'
            f'── DAY {mgr.day} / FINAL ──</div>'
            f'<h2 style="font-size:42px;margin:0 0 20px 0;">{ending}</h2>'
            f'<div style="color:#888;font-size:12px;font-family:\'JetBrains Mono\',monospace;'
            f'margin-bottom:24px;">CHARACTER: {y.get_name()} · '
            f'SCENARIO: {mgr.scenario.title}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

        if len(st.session_state.history) >= 2:
            st.markdown(
                '<div class="section-label" style="margin-top:20px;">▌ 전체 여정 능력치 추이</div>',
                unsafe_allow_html=True,
            )
            render_history_chart(st.session_state.history)

        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(
                f'<div class="stat-box"><div class="section-label">최종 구독자</div>'
                f'<div style="font-family:\'Bebas Neue\',sans-serif;font-size:24px;">'
                f'{y.get_subs():,}</div></div>',
                unsafe_allow_html=True,
            )
        with c2:
            st.markdown(
                f'<div class="stat-box"><div class="section-label">최종 평판</div>'
                f'<div style="font-family:\'Bebas Neue\',sans-serif;font-size:24px;">'
                f'{y.get_reputation()}%</div></div>',
                unsafe_allow_html=True,
            )
        with c3:
            st.markdown(
                f'<div class="stat-box"><div class="section-label">특성 변화</div>'
                f'<div style="font-family:\'Bebas Neue\',sans-serif;font-size:24px;">'
                f'{len(y.trait_log)}회</div></div>',
                unsafe_allow_html=True,
            )

        if y.trait_log:
            st.markdown(
                '<div class="section-label" style="margin-top:24px;">▌ 특성 변화 로그</div>',
                unsafe_allow_html=True,
            )
            for day, sign, trait in y.trait_log:
                color = "#00ff88" if sign == "+" else "#ff5577"
                st.markdown(
                    f'<div style="font-family:\'JetBrains Mono\',monospace;font-size:12px;'
                    f'color:#aaa;padding:4px 0;">'
                    f'<span style="color:#666;margin-right:8px;">D{day}</span>'
                    f'<span style="color:{color};margin-right:8px;">{sign}</span>'
                    f'{TRAIT_LABEL.get(trait, trait)}</div>',
                    unsafe_allow_html=True,
                )

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("▸ 다시 도전", use_container_width=True, type="primary"):
            restart()
            st.rerun()


# ============================================================
#  사이드바
# ============================================================
def render_sidebar():
    with st.sidebar:
        st.markdown("### 📺 위기관리 시뮬레이션")
        st.markdown(
            '<div style="font-size:12px;color:#aaa;line-height:1.6;">'
            '<b>OOP 팀 프로젝트</b><br>'
            '원본 <code style="font-size:11px;">youtuber_crisis_v4.py</code>의 '
            '클래스를 그대로 <code style="font-size:11px;">import</code>하여 '
            'Streamlit으로 시각화한 웹 데모.<br><br>'
            '<b>설계 어필 포인트</b>'
            '<ul style="padding-left:16px;margin-top:8px;">'
            '<li>캡슐화: 모든 능력치 private + getter</li>'
            '<li>상속: Action/Event/Scenario 추상 클래스</li>'
            '<li>다형성: <code style="font-size:10px;">execute()</code>, '
            '<code style="font-size:10px;">trigger()</code></li>'
            '<li>피드백 루프: 특성→확률→특성</li>'
            '</ul></div>',
            unsafe_allow_html=True,
        )
        st.markdown("---")
        if st.session_state.manager:
            st.markdown(f"**Day**: `{st.session_state.manager.day}/7`")
            st.markdown(f"**시나리오**: {st.session_state.manager.scenario.title}")


# ============================================================
#  메인 라우터
# ============================================================
def main():
    init_session()
    render_sidebar()

    if st.session_state.phase == "select":
        render_select()
    elif st.session_state.phase == "playing":
        render_playing()
    elif st.session_state.phase == "ended":
        render_ended()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        st.error(f"렌더링 에러: {e}")
        import traceback
        st.code(traceback.format_exc())
