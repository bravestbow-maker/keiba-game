import streamlit as st
import time
import random
import pandas as pd
import plotly.graph_objects as go

# ページ設定
st.set_page_config(page_title="ドタバタ縦スクロール杯", page_icon="🏇", layout="wide")

st.title("🏇 ドタバタ縦スクロール杯")
st.write("ゴール前は魔物が棲んでいる…！？ 予測不能な大波乱レース！")

# --- レースの設定 ---
GOAL_DISTANCE = 100
HORSES_CONFIG = [
    {"id": 0, "name": "レッドメテオ", "color": "#d62728", "icon": "🐎"},
    {"id": 1, "name": "ブルーオーシャン", "color": "#1f77b4", "icon": "🐎"},
    {"id": 2, "name": "グリーンウインド", "color": "#2ca02c", "icon": "🐎"},
    {"id": 3, "name": "イエローフラッシュ", "color": "#d4a000", "icon": "🐎"},
]

if "race_started" not in st.session_state:
    st.session_state.race_started = False

def start_race():
    st.session_state.race_started = True

# スタートボタン
start_container = st.empty()
if not st.session_state.race_started:
    with start_container.container():
        st.button("🏁 レーススタート！", on_click=start_race, type="primary", use_container_width=True)

if st.session_state.race_started:
    start_container.empty()

    # 馬のデータ初期化
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
    
    # 描画プレースホルダー
    status_text = st.empty()
    chart_placeholder = st.empty()
    
    finished_count = 0
    current_rank = 1
    race_running = True

    # --- レースループ開始 ---
    while race_running:
        
        # 現在のトップの馬の位置を取得（焦らし演出のトリガー用）
        active_horses = [h for h in horses_data if h["rank"] is None]
        if active_horses:
            top_pos = max(h["pos"] for h in active_horses)
        else:
            top_pos = GOAL_DISTANCE

        # 状況に応じた「焦らし」モードの設定
        if top_pos < 40:
            situation = "🟢 【序盤】 各馬、順調な滑り出しです！"
            sleep_time = 0.1
            # 序盤は普通に進む
            move_choices = [-1, 0, 1, 2, 3, 5, 8]
            move_weights = [5,  10, 20, 30, 20, 10, 5]
        elif top_pos < 85:
            situation = "🟡 【中盤】 抜け出すのはどの馬だ！？"
            sleep_time = 0.1
            # 中盤は動きが激しくなる（大ダッシュか大後退か）
            move_choices = [-3, -1, 0, 2, 4, 7, 10]
            move_weights = [10, 10, 10, 20, 20, 20, 10]
        else:
            situation = "🔥 【終盤】 デッドヒート！ゴール前のプレッシャーで足が重い！！"
            sleep_time = 0.25 # コマ送りを少し遅くして「焦らし」を強調
            # 終盤（ゴール直前）は極端に進みにくく、たまに大きく後退する（焦らし！）
            move_choices = [-5, -2, -1, 0, 0, 1, 2]
            move_weights = [5,  15, 20, 30, 15, 10, 5]

        status_text.markdown(f"### {situation}")

        # 1. 位置の計算ロジック
        for horse in horses_data:
            if horse["rank"] is None:
                move = random.choices(move_choices, weights=move_weights)[0]
                horse["pos"] += move
                
                # 下がりすぎ防止
                if horse["pos"] < 0: horse["pos"] = 0
                
                # ゴール判定
                if horse["pos"] >= GOAL_DISTANCE:
                    horse["pos"] = GOAL_DISTANCE
                    horse["rank"] = current_rank
                    current_rank += 1
                    finished_count += 1

        # 2. Plotlyグラフによる視覚化（馬のアイコンを主役に）
        fig = go.Figure()

        # 背景レーン
        for i in range(4):
            fig.add_shape(type="rect",
                x0=i - 0.45, x1=i + 0.45, y0=-10, y1=GOAL_DISTANCE + 5,
                fillcolor="#f8f9fa" if i % 2 == 0 else "#e9ecef",
                opacity=0.7, layer="below", line_width=0
            )
        
        # ゴールラインとスタートライン
        fig.add_hline(y=GOAL_DISTANCE, line_width=4, line_dash="dash", line_color="gold", annotation_text="🏁 GOAL", annotation_font=dict(size=20, color="gold"))
        fig.add_hline(y=0, line_width=2, line_color="black", annotation_text="START", annotation_position="bottom right")

        # 各馬の描画（マーカーを消して、巨大なテキストとしてアイコンを配置）
        for horse in horses_data:
            # アイコンの描画（超特大サイズ）
            fig.add_trace(go.Scatter(
                x=[horse["lane"]],
                y=[horse["pos"]],
                mode='text',
                text=horse["icon"],
                textfont=dict(size=70), # 馬の絵文字を大きく！
                showlegend=False,
                hoverinfo="none"
            ))
            
            # 馬の名前と順位の描画（アイコンの少し下に追従させる）
            rank_text = f"<br><b>🏆 {horse['rank']}位</b>" if horse['rank'] else ""
            fig.add_trace(go.Scatter(
                x=[horse["lane"]],
                y=[horse["pos"] - 6], # アイコンの少し下に配置
                mode='text',
                text=f"<b>{horse['name']}</b>{rank_text}",
                textfont=dict(size=14, color=horse["color"]), # 名前は馬のテーマカラーで
                showlegend=False,
                hoverinfo="none"
            ))

        # グラフのレイアウト設定
        fig.update_layout(
            height=750,
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-0.5, 3.5]),
            yaxis=dict(
                title="コース",
                range=[-15, GOAL_DISTANCE + 10], # 下に名前が入るよう余白を調整
                showgrid=True, gridcolor="lightgray", zeroline=False, fixedrange=True
            ),
            margin=dict(l=10, r=10, t=30, b=10),
            plot_bgcolor="white",
            hovermode=False
        )

        # 3. 画面更新
        chart_placeholder.plotly_chart(fig, use_container_width=True, config={'staticPlot': True})

        # 終了判定
        if finished_count == 4:
            race_running = False
            status_text.empty()
        else:
            time.sleep(sleep_time)

    # --- レース終了後の結果表示 ---
    st.success("🎉 全馬ゴール！！ 大波乱のレースが決着しました！")
    
    sorted_horses = sorted(horses_data, key=lambda x: x["rank"])
    medals = ["🥇 1位", "🥈 2位", "🥉 3位", "🏅 4位"]
    
    cols = st.columns(4)
    for i, horse in enumerate(sorted_horses):
        with cols[i]:
            st.markdown(
                f"""
                <div style="background-color: {horse['color']}15; padding: 15px; border-radius: 10px; text-align: center; border: 2px solid {horse['color']}; box-shadow: 2px 2px 5px rgba(0,0,0,0.1);">
                    <h3 style="margin:0; color: #333;">{medals[i]}</h3>
                    <div style="font-size: 60px; margin: 10px 0;">{horse['icon']}</div>
                    <h4 style="margin:0; color: {horse['color']};">{horse['name']}</h4>
                </div>
                """,
                unsafe_allow_html=True
            )
            
    if st.button("🔄 もう一度レースをする", type="primary", use_container_width=True):
        st.session_state.race_started = False
        st.rerun()
