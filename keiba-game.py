import streamlit as st
import time
import random
import pandas as pd
import plotly.graph_objects as go

# ページ設定（ワイド表示で見やすく）
st.set_page_config(page_title="縦型ドタバタレース", page_icon="🏇", layout="wide")

st.title("🏇 ドタバタ縦スクロール杯")
st.write("下から上へ駆け抜けろ！予測不能な縦型レースゲームです。")

# --- レースの設定 ---
GOAL_DISTANCE = 100  # ゴールまでの距離（少し長くしました）
HORSES_CONFIG = [
    {"id": 0, "name": "🔴 レッドメテオ", "color": "#ff4b4b", "icon": "🐎"},
    {"id": 1, "name": "🔵 ブルーオーシャン", "color": "#4b4bff", "icon": "🐎"},
    {"id": 2, "name": "🟢 グリーンウインド", "color": "#4bff4b", "icon": "🐎"},
    {"id": 3, "name": "🟡 イエローフラッシュ", "color": "#ffff4b", "icon": "🐎"},
]

# セッションステートの初期化
if "race_started" not in st.session_state:
    st.session_state.race_started = False

def start_race():
    st.session_state.race_started = True

# --- メイン処理 ---

# スタートボタンエリア
start_container = st.empty()
if not st.session_state.race_started:
    with start_container.container():
        st.button("🏁 レーススタート！", on_click=start_race, type="primary", use_container_width=True)

if st.session_state.race_started:
    start_container.empty() # スタートボタンを消す

    # 馬のデータ初期化
    horses_data = []
    for config in HORSES_CONFIG:
        horses_data.append({
            "name": config["name"],
            "color": config["color"],
            "icon": config["icon"],
            "pos": 0.0,
            "rank": None,
            "lane": config["id"] # レーン番号（横位置）
        })
    
    # 描画用のプレースホルダー
    chart_placeholder = st.empty()
    status_text = st.empty()
    
    finished_count = 0
    current_rank = 1
    race_running = True

    # --- レースループ開始 ---
    while race_running:
        # 1. 位置の計算ロジック (前回のロジックを踏襲)
        moved_horses_names = []
        for horse in horses_data:
            if horse["rank"] is None:
                # 緩急をつける乱数
                move = random.choices(
                    [-3, -1, 0, 1, 2, 3, 5, 8], # 少し動きを派手にしました
                    weights=[5, 10, 10, 20, 20, 15, 10, 10]
                )[0]
                
                horse["pos"] += move
                if move > 4: moved_horses_names.append(horse["name"]) # 実況用
                
                # スタート・ゴール判定
                if horse["pos"] < 0: horse["pos"] = 0
                if horse["pos"] >= GOAL_DISTANCE:
                    horse["pos"] = GOAL_DISTANCE
                    horse["rank"] = current_rank
                    current_rank += 1
                    finished_count += 1
        
        # 実況テキスト更新
        if moved_horses_names:
            status_text.info(f"💨 {'、'.join(moved_horses_names)} が猛ダッシュ！")
        else:
            status_text.write("...")

        # 2. Plotlyグラフによる視覚化
        fig = go.Figure()

        # 背景のコース（レーン）を描画
        for i in range(4):
            fig.add_shape(type="rect",
                x0=i - 0.4, x1=i + 0.4, y0=-5, y1=GOAL_DISTANCE + 5,
                fillcolor="lightgray" if i % 2 == 0 else "whitesmoke",
                opacity=0.5, layer="below", line_width=0
            )
        
        # ゴールライン
        fig.add_hline(y=GOAL_DISTANCE, line_width=3, line_dash="dash", line_color="gold", annotation_text="GOAL", annotation_position="top right")
        # スタートライン
        fig.add_hline(y=0, line_width=2, line_color="black")

        # 各馬のマーカーとテキストを描画
        for horse in horses_data:
            # ゴールした馬の表示
            rank_text = ""
            pos_y = horse["pos"]
            if horse["rank"]:
                rank_text = f"<b>[{horse['rank']}位!]</b>"
                # ゴール後少し重ならないように位置をずらす演出（任意）
                pos_y += (4 - horse['rank']) * 2

            fig.add_trace(go.Scatter(
                x=[horse["lane"]],
                y=[pos_y],
                mode='markers+text',
                marker=dict(size=40, color=horse["color"], symbol='circle'),
                text=f"{horse['icon']}<br>{horse['name']}<br>{rank_text}",
                textposition="top center",
                textfont=dict(size=14, color="black"),
                name=horse["name"],
                showlegend=False
            ))

        # グラフのレイアウト設定（縦長にする）
        fig.update_layout(
            height=700, # 高さを指定して縦長に
            xaxis=dict(
                showgrid=False, zeroline=False, showticklabels=False,
                range=[-0.5, 3.5], # 4レーン分の幅
            ),
            yaxis=dict(
                title="ゴールまでの距離",
                range=[-10, GOAL_DISTANCE + 15], # 上下に少し余裕を持たせる
                showgrid=True, zeroline=False, fixedrange=True # ズーム不可にする
            ),
            margin=dict(l=20, r=20, t=40, b=20),
            plot_bgcolor="white",
            hovermode=False # ホバー表示をオフ
        )

        # 3. 画面更新
        # config={'staticPlot': True} でインタラクティブ機能を切り、描画を高速化
        chart_placeholder.plotly_chart(fig, use_container_width=True, config={'staticPlot': True})

        # 終了判定
        if finished_count == 4:
            race_running = False
            status_text.empty()
        else:
            time.sleep(0.1) # 更新頻度（コマ送り速度）

    # --- レース終了後の結果表示 ---
    st.success("🎉 レース終了！確定順位はこちら！")
    
    # 結果発表エリア（カード風に表示）
    sorted_horses = sorted(horses_data, key=lambda x: x["rank"])
    medals = ["🥇 優勝", "🥈 2位", "🥉 3位", "🏅 4位"]
    
    cols = st.columns(4)
    for i, horse in enumerate(sorted_horses):
        with cols[i]:
            st.markdown(
                f"""
                <div style="background-color: {horse['color']}30; padding: 20px; border-radius: 10px; text-align: center; border: 3px solid {horse['color']};">
                    <h2 style="margin:0;">{medals[i]}</h2>
                    <div style="font-size: 50px;">{horse['icon']}</div>
                    <h4 style="margin:0;">{horse['name']}</h4>
                </div>
                """,
                unsafe_allow_html=True
            )
            
    # リセットボタン
    if st.button("🔄 もう一度レースをする", type="primary"):
        st.session_state.race_started = False
        st.rerun()
