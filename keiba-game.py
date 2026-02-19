import streamlit as st
import time
import random

# ページ設定
st.set_page_config(page_title="ドタバタ競馬 抽選ゲーム", page_icon="🏇")

st.title("🏇 ドタバタ競馬風 抽選ゲーム")
st.write("急に速くなったり、なぜか後ろに戻ったり…！？最後まで予測不能なレース！")

# レースの設定
GOAL_DISTANCE = 40  # ゴールまでの距離

# セッションステートの初期化（再実行時に状態をリセットするため）
if "race_started" not in st.session_state:
    st.session_state.race_started = False

def start_race():
    st.session_state.race_started = True

# スタートボタン
if not st.session_state.race_started:
    st.button("🏁 レース開始！", on_click=start_race)

if st.session_state.race_started:
    # 4匹の馬の初期データ
    horses = [
        {"name": "🔴 レッドメテオ", "icon": "🐎", "pos": 0, "rank": None},
        {"name": "🔵 ブルーオーシャン", "icon": "🐎", "pos": 0, "rank": None},
        {"name": "🟢 グリーンウインド", "icon": "🐎", "pos": 0, "rank": None},
        {"name": "🟡 イエローフラッシュ", "icon": "🐎", "pos": 0, "rank": None},
    ]

    # 描画用のプレースホルダー（この枠の中を書き換え続ける）
    track_placeholder = st.empty()
    
    finished_count = 0
    current_rank = 1

    # 全馬がゴールするまでループ
    while finished_count < 4:
        display_text = ""
        
        for horse in horses:
            # ゴールしていない馬だけ動かす
            if horse["rank"] is None:
                # 緩急をつける乱数 (マイナスは後退、大きい数字は猛ダッシュ)
                # 例: -2(後退), 0(停止), 1〜3(通常), 4〜6(ダッシュ)
                move = random.choices(
                    [-2, -1, 0, 1, 2, 3, 4, 6],
                    weights=[10, 10, 10, 25, 20, 15, 5, 5] # 確率の重み付け
                )[0]
                
                horse["pos"] += move
                
                # スタートラインより後ろには行かないようにする
                if horse["pos"] < 0:
                    horse["pos"] = 0
                
                # ゴール判定
                if horse["pos"] >= GOAL_DISTANCE:
                    horse["pos"] = GOAL_DISTANCE
                    horse["rank"] = current_rank
                    current_rank += 1
                    finished_count += 1
            
            # コースの文字列を生成
            # 例: -----🐎------------------------- (ゴール)
            track_past = "-" * horse["pos"]
            track_future = "-" * (GOAL_DISTANCE - horse["pos"])
            
            # 描画用テキストの組み立て
            if horse["rank"] is not None:
                display_text += f"**{horse['name']}** [{horse['rank']}位 ゴール!]\n"
                display_text += f"|{track_past}{horse['icon']}|\n\n"
            else:
                display_text += f"**{horse['name']}**\n"
                display_text += f"|{track_past}{horse['icon']}{track_future}|\n\n"

        # プレースホルダーを更新（画面の書き換え）
        track_placeholder.markdown(display_text)
        
        # コマ送りの速度（0.2秒待機）
        time.sleep(0.2)

    # レース終了後の処理
    st.success("🎉 全馬ゴール！レース終了！")
    
    st.subheader("🏆 最終結果発表")
    # 順位順に並び替えて表示
    sorted_horses = sorted(horses, key=lambda x: x["rank"])
    
    # 順位を見やすく表示
    cols = st.columns(4)
    medals = ["🥇 1位", "🥈 2位", "🥉 3位", "🏅 4位"]
    for i, horse in enumerate(sorted_horses):
        with cols[i]:
            st.metric(label=medals[i], value=horse["name"].split(" ")[1])

    # もう一度遊ぶためのリセットボタン
    if st.button("もう一度レースをする"):
        st.session_state.race_started = False
        st.rerun()
