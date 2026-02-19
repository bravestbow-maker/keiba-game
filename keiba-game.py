import streamlit as st
import time
import random
import plotly.graph_objects as go

# --- ページ設定とカスタムCSS ---
st.set_page_config(page_title="ドタバタ縦スクロール杯", page_icon="🏇", layout="wide")

# CSSを用いてUIをスタイリッシュに装飾
st.markdown("""
<style>
    .live-commentary {
        font-size: 24px;
        font-weight: bold;
        color: #ffffff;
        background: linear-gradient(45deg, #1e3c72, #2a5298);
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
    .result-card {
        padding: 20px;
        border-radius: 15px;
        text-align: center;
        color: white;
        box-shadow: 0 8px 15px rgba(0,0,0,0.2);
        transition: transform 0.2s;
    }
    .result-card:hover {
        transform: translateY(-5px);
    }
</style>
""", unsafe_allow_html=True)

# --- セッションステートの初期化 ---
if "race_started" not in st.session_state:
    st.session_state.race_started = False
if "prediction" not in st.session_state:
    st.session_state.prediction = None

# --- サイドバー (設定エリア) ---
with st.sidebar:
    st.header("⚙️ レース設定")
    st.write("馬の名前を自由に変更できます")
    name_0 = st.text_input("1枠 (赤)", "レッドメテオ")
    name_1 = st.text_input("2枠 (青)", "ブルーオーシャン")
    name_2 = st.text_input("3枠 (緑)", "グリーンウインド")
    name_3 = st.text_input("4枠 (黄)", "イエローフラッシュ")
    
    st.divider()
    
    st.header("🎯 優勝予想")
    st.session_state.prediction = st.radio(
        "どの馬が勝つか予想しよう！",
        [name_0, name_1, name_2, name_3],
        index=0
    )

# --- レースの設定 ---
GOAL_DISTANCE = 100
HORSES_CONFIG = [
    {"id": 0, "name": name_0, "color": "#ff4b4b", "icon": "🐎"},
    {"id": 1, "name": name_1, "color": "#4da6ff", "icon": "🐎"},
    {"id": 2, "name": name_2, "color": "#4caf50", "icon": "🐎"},
    {"id": 3, "name": name_3, "color": "#ffc107", "icon": "🐎"},
]

def start_race():
    st.session_state.race_started = True

# --- メイン画面 ---
st.title("🏇 ドタバタ縦スクロール杯")

# スタートボタン
start_container = st.empty()
if not st.session_state.race_started:
    with start_container.container():
        st.info(f"あなたの予想: **{st.session_state.prediction}**")
        st.button("🏁 レーススタート！", on_click=start_race, type="primary", use_container_width=True)

if st.session_state.race_started:
    start_container.empty()

    horses_data = []
    for config in HORSES_CONFIG:
        horses_data.append({
            "name": config["name"],
            "color": config["color"],
            "icon": config["icon"],
            "pos": 0.0,
            "rank": None,
            "lane": config["id"]
        })
    
    status_text = st.empty()
    chart_placeholder = st.empty()
    
    finished_count = 0
    current_rank = 1
    race_running = True
    frame_count = 0 

    # --- レースループ開始 ---
    while race_running:
        
        active_horses = [h for h in horses_data if h["rank"] is None]
        top_pos = max(h["pos"] for h in active_horses) if active_horses else GOAL_DISTANCE

        # 実況テキストの更新 (HTMLクラスを適用)
        if top_pos < 40:
            situation = "🟢 【序盤】 スタートしました！各馬、一斉に飛び出します！"
            sleep_time, move_choices, move_weights = 0.1, [-1, 0, 1, 2, 3], [5, 15, 40, 30, 10]
        elif top_pos < 85:
            situation = "🟡 【中盤】 仕掛けどころ！一気に順位が入れ替わる激しい展開！"
            sleep_time, move_choices, move_weights = 0.1, [-4, -1, 0, 2, 4, 8], [10, 15, 15, 30, 20, 10]
        else:
            situation = "🔥 【終盤】 ゴール前の激しいデッドヒート！抜け出すのは誰だ！？"
            sleep_time, move_choices, move_weights = 0.1, [-2, 0, 1, 2, 3, 5], [15, 25, 30, 15, 10, 5]

        status_text.markdown(f'<div class="live-commentary">{situation}</div>', unsafe_allow_html=True)

        # 位置の計算
        for horse in horses_data:
            if horse["rank"] is None:
                move = random.choices(move_choices, weights=move_weights)[0]
                horse["pos"] += move
                if horse["pos"] < 0: horse["pos"] = 0
                if horse["pos"] >= GOAL_DISTANCE:
                    horse["pos"] = GOAL_DISTANCE
                    horse["rank"] = current_rank
                    current_rank += 1
                    finished_count += 1

        # Plotlyグラフ (芝生コース風)
        fig = go.Figure()

        # 芝生コースの背景
        for i in range(4):
            fig.add_shape(type="rect",
                x0=i - 0.48, x1=i + 0.48, y0=-10, y1=GOAL_DISTANCE + 5,
                fillcolor="#388e3c" if i % 2 == 0 else="#43a047", # 芝生の濃淡
                opacity=0.8, layer="below", line_width=0
            )
        
        fig.add_hline(y=GOAL_DISTANCE, line_width=6, line_dash="solid", line_color="white", annotation_text="🏁 GOAL", annotation_font=dict(size=24, color="white", weight="bold"))
        fig.add_hline(y=0, line_width=3, line_color="white", annotation_text="START", annotation_position="bottom right", annotation_font=dict(color="white"))

        # 各馬の描画
        for horse in horses_data:
            fig.add_trace(go.Scatter(
                x=[horse["lane"]], y=[horse["pos"]],
                mode='text', text=horse["icon"],
                textfont=dict(size=70), showlegend=False, hoverinfo="none"
            ))
            
            rank_text = f"<br><b>🏆 {horse['rank']}位</b>" if horse['rank'] else ""
            fig.add_trace(go.Scatter(
                x=[horse["lane"]], y=[horse["pos"] - 7], 
                mode='text',
                text=f"<span style='background-color:rgba(0,0,0,0.5); padding:2px; border-radius:4px;'><b>{horse['name']}</b></span>{rank_text}",
                textfont=dict(size=16, color=horse["color"]), 
                showlegend=False, hoverinfo="none"
            ))

        fig.update_layout(
            height=700,
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-0.5, 3.5]),
            yaxis=dict(
                title="コース", range=[-15, GOAL_DISTANCE + 10], 
                showgrid=True, gridcolor="rgba(255,255,255,0.2)", zeroline=False, fixedrange=True
            ),
            margin=dict(l=10, r=10, t=10, b=10),
            plot_bgcolor="#2e7d32", # 全体の背景も濃い緑に
            paper_bgcolor="#0e1117", # ダークテーマ風
            hovermode=False
        )

        chart_placeholder.plotly_chart(fig, use_container_width=True, config={'staticPlot': True}, key=f"race_frame_{frame_count}")
        frame_count += 1

        if finished_count == 4:
            race_running = False
            status_text.empty()
        else:
            time.sleep(sleep_time)

    # --- 結果発表 ---
    sorted_horses = sorted(horses_data, key=lambda x: x["rank"])
    winner_name = sorted_horses[0]["name"]
    
    st.balloons() # バルーンアニメーション
    
    if st.session_state.prediction == winner_name:
        st.success(f"🎉 おめでとうございます！予想的中！ {winner_name} が見事1位に輝きました！")
    else:
        st.warning(f"ざんねん…！優勝は {winner_name} でした。あなたの予想: {st.session_state.prediction}")
    
    st.markdown("### 🏆 最終順位")
    cols = st.columns(4)
    medals = ["🥇 1位", "🥈 2位", "🥉 3位", "🏅 4位"]
    
    for i, horse in enumerate(sorted_horses):
        with cols[i]:
            st.markdown(
                f"""
                <div class="result-card" style="background: linear-gradient(135deg, {horse['color']}, #333333);">
                    <h2 style="margin:0;">{medals[i]}</h2>
                    <div style="font-size: 60px; margin: 10px 0;">{horse['icon']}</div>
                    <h4 style="margin:0;">{horse['name']}</h4>
                </div>
                """,
                unsafe_allow_html=True
            )
            
    st.write("") # スペース
    if st.button("🔄 もう一度レースをする", type="primary", use_container_width=True):
        st.session_state.race_started = False
        st.rerun()
