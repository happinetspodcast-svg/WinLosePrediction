import streamlit as st
import pandas as pd
import urllib.parse
import json

# ページ基本設定
st.set_page_config(
    page_title="秋田ノーザンハピネッツ 2026-27 勝敗予想シミュレーター",
    layout="wide"
)

APP_URL = "https://your-app.streamlit.app"

st.title("🏀 秋田ノーザンハピネッツ 2026-27シーズン勝敗予想シミュレーター")
st.write("各対戦相手の「勝」のセレクトボックスで勝利数を選んでください。")

# 1. デフォルトデータの定義
@st.cache_data
def get_default_schedule_data():
    return pd.DataFrame({
        "地区": [
            "東地区", "東地区", "東地区", "東地区", "東地区", 
            "東地区", "東地区", "東地区", "東地区", "東地区", "東地区", "東地区",
            "西地区", "西地区", "西地区", "西地区", "西地区", "西地区", "西地区",
            "西地区", "西地区", "西地区", "西地区", "西地区", "西地区"
        ],
        "対戦相手": [
            "レバンガ北海道", "仙台89ers", "茨城ロボッツ", "宇都宮ブレックス", "群馬クレインサンダーズ",
            "千葉ジェッツ", "アルティーリ千葉", "アルバルク東京", "サンロッカーズ東京", "川崎ブレイブサンダース", "横浜ビー・コルセアーズ", "富山グラウジーズ",
            "信州ブレイブウォリアーズ", "三遠ネオフェニックス", "シーホース三河", "名古屋ダイヤモンドドルフィンズ", "滋賀レイクス", "京都ハンナリーズ",
            "大阪エヴェッサ", "神戸ストークス", "島根スサノオマジック", "広島ドラゴンフライズ", "佐賀バルーナーズ", "長崎ヴェルカ", "琉球ゴールデンキングス"
        ],
        "年間対戦試合数": [
            3, 3, 3, 3, 3, 
            3, 3, 3, 3, 3, 3, 3, 
            2, 1, 2, 2, 2, 2, 
            2, 2, 1, 2, 2, 2, 2
        ],
        "勝": [0] * 25,
        "負": [3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 2, 1, 2, 2, 2, 2, 2, 2, 1, 2, 2, 2, 2],
        "メモ": [""] * 25,
        "URL": [
            "https://www.bleague.jp/club_detail/?TeamID=702&tab=2",
            "https://www.bleague.jp/club_detail/?TeamID=692&tab=2",
            "https://www.bleague.jp/club_detail/?TeamID=712&tab=2",
            "https://www.bleague.jp/club_detail/?TeamID=703&tab=2",
            "https://www.bleague.jp/club_detail/?TeamID=713&tab=2",
            "https://www.bleague.jp/club_detail/?TeamID=704&tab=2",
            "https://www.bleague.jp/club_detail/?TeamID=2486&tab=2",
            "https://www.bleague.jp/club_detail/?TeamID=706&tab=2",
            "https://www.bleague.jp/club_detail/?TeamID=726&tab=2",
            "https://www.bleague.jp/club_detail/?TeamID=727&tab=2",
            "https://www.bleague.jp/club_detail/?TeamID=694&tab=2",
            "https://www.bleague.jp/club_detail/?TeamID=696&tab=2",
            "https://www.bleague.jp/club_detail/?TeamID=716&tab=2",
            "https://www.bleague.jp/club_detail/?TeamID=697&tab=2",
            "https://www.bleague.jp/club_detail/?TeamID=728&tab=2",
            "https://www.bleague.jp/club_detail/?TeamID=729&tab=2",
            "https://www.bleague.jp/club_detail/?TeamID=698&tab=2",
            "https://www.bleague.jp/club_detail/?TeamID=699&tab=2",
            "https://www.bleague.jp/club_detail/?TeamID=700&tab=2",
            "https://www.bleague.jp/club_detail/?TeamID=718&tab=2",
            "https://www.bleague.jp/club_detail/?TeamID=720&tab=2",
            "https://www.bleague.jp/club_detail/?TeamID=721&tab=2",
            "https://www.bleague.jp/club_detail/?TeamID=1638&tab=2",
            "https://www.bleague.jp/club_detail/?TeamID=2488&tab=2",
            "https://www.bleague.jp/club_detail/?TeamID=701&tab=2"
        ]
    })

if "data" not in st.session_state:
    st.session_state.data = get_default_schedule_data()

# ツールバー（保存・読み込み・リセット）
st.markdown("---")
col_tool1, col_tool2, col_tool3 = st.columns([1.5, 2, 1])

with col_tool1:
    # 予想データのJSONダウンロード（安全に列を確認して出力）
    export_df = st.session_state.data.copy()
    for col in ["地区", "対戦相手", "年間対戦試合数", "勝", "負", "メモ"]:
        if col not in export_df.columns:
            export_df = get_default_schedule_data()
            break
    json_data = export_df[["地区", "対戦相手", "年間対戦試合数", "勝", "負", "メモ"]].to_json(orient="records", force_ascii=False)
    st.download_button(
        label="💾 入力データをファイルに保存",
        data=json_data,
        file_name="akita_prediction_save.json",
        mime="application/json",
        help="現在の勝敗予想とメモをファイルとして端末に保存します。"
    )

with col_tool2:
    # 保存したJSONファイルのアップロード（読み込み）
    uploaded_file = st.file_uploader("📂 保存したファイルから復元", type=["json"], label_visibility="collapsed")
    if uploaded_file is not None:
        try:
            loaded_list = json.load(uploaded_file)
            loaded_df = pd.DataFrame(loaded_list)
            if all(col in loaded_df.columns for col in ["勝", "メモ", "対戦相手"]):
                base_df = get_default_schedule_data()
                for idx, row in loaded_df.iterrows():
                    match = base_df[base_df["対戦相手"] == row["対戦相手"]]
                    if not match.empty:
                        base_idx = match.index[0]
                        max_g = int(base_df.loc[base_idx, "年間対戦試合数"])
                        w = int(row["勝"])
                        if w > max_g: w = max_g
                        base_df.loc[base_idx, "勝"] = w
                        base_df.loc[base_idx, "負"] = max_g - w
                        base_df.loc[base_idx, "メモ"] = str(row["メモ"])
                st.session_state.data = base_df
                st.success("データを正常に復元しました！")
                st.rerun()
        except Exception as e:
            st.error("ファイルの読み込みに失敗しました。")

with col_tool3:
    if st.button("🔄 入力をリセット"):
        st.session_state.data = get_default_schedule_data()
        st.rerun()

st.markdown("---")

# 2カラムレイアウト（左：カスタム入力リスト / 右：ロスター確認パネル）
col_left, col_right = st.columns([1.5, 1], gap="medium")

with col_left:
    st.markdown("##### 💡 勝敗予想・メモ入力（対戦カードリスト）")
    
    # 項目名ヘッダー行
    h_cols = st.columns([1.2, 2.2, 1.2, 1.2, 2.5])
    h_cols[0].markdown("<p style='font-size:15px; font-weight:bold; color:gray; margin-bottom:2px;'>地区</p>", unsafe_allow_html=True)
    h_cols[1].markdown("<p style='font-size:15px; font-weight:bold; color:gray; margin-bottom:2px;'>対戦相手</p>", unsafe_allow_html=True)
    h_cols[2].markdown("<p style='font-size:15px; font-weight:bold; color:#2563eb; margin-bottom:2px;'>勝</p>", unsafe_allow_html=True)
    h_cols[3].markdown("<p style='font-size:15px; font-weight:bold; color:gray; margin-bottom:2px; text-align:right;'>勝敗結果</p>", unsafe_allow_html=True)
    h_cols[4].markdown("<p style='font-size:15px; font-weight:bold; color:gray; margin-bottom:2px;'>メモ</p>", unsafe_allow_html=True)
    st.markdown("<hr style='margin:2px 0px 8px 0px;'>", unsafe_allow_html=True)

    updated_rows = []
    
    with st.container(height=620):
        for idx, row in st.session_state.data.iterrows():
            with st.container():
                cols = st.columns([1.2, 2.2, 1.2, 1.2, 2.5])
                
                with cols[0]:
                    st.markdown(f"<p style='padding-top:10px; font-size:15px; color:gray;'>{row['地区']}</p>", unsafe_allow_html=True)
                
                with cols[1]:
                    st.markdown(f"<p style='padding-top:8px; font-size:16px; font-weight:bold;'><a href='{row['URL']}' target='_blank' style='text-decoration:none; color:#2563eb;'>{row['対戦相手']}</a> <span style='font-size:13px; font-weight:normal;'>(全{row['年間対戦試合数']}戦)</span></p>", unsafe_allow_html=True)
                
                max_games = int(row["年間対戦試合数"])
                options_list = list(range(max_games + 1))
                current_win = int(row["勝"])
                if current_win > max_games:
                    current_win = max_games
                
                with cols[2]:
                    new_win = st.selectbox(
                        "勝",
                        options=options_list,
                        index=current_win,
                        key=f"win_{idx}",
                        label_visibility="collapsed"
                    )
                
                new_loss = max_games - new_win
                with cols[3]:
                    st.markdown(f"<p style='text-align:right; padding-top:10px; font-size:16px; font-weight:bold;'>勝 {new_win} - {new_loss} 敗</p>", unsafe_allow_html=True)
                
                with cols[4]:
                    new_memo = st.text_input(
                        "メモ",
                        value=row["メモ"],
                        key=f"memo_{idx}",
                        placeholder="メモ...",
                        label_visibility="collapsed"
                    )
                
                st.markdown("<hr style='margin:4px 0px; opacity:0.2;'>", unsafe_allow_html=True)
                
                updated_rows.append({
                    "地区": row["地区"],
                    "対戦相手": row["対戦相手"],
                    "年間対戦試合数": max_games,
                    "勝": new_win,
                    "負": new_loss,
                    "メモ": new_memo,
                    "URL": row["URL"]
                })
    
    new_df = pd.DataFrame(updated_rows)
    
    if not new_df.equals(st.session_state.data):
        st.session_state.data = new_df
        st.rerun()

with col_right:
    st.markdown("##### 🔗 ロスター確認・チーム別リンク集")
    with st.container(height=720):
        for _, row in st.session_state.data.iterrows():
            memo_text = f"（メモ: {row['メモ']}）" if row['メモ'] else ""
            st.markdown(f"**{row['対戦相手']}** {memo_text} 👉 [ロスター確認 🔗]({row['URL']})", unsafe_allow_html=True)

# 2. 全体の集計
current_data = st.session_state.data
total_games = int(current_data["年間対戦試合数"].sum())
total_wins = int(current_data["勝"].sum())
total_losses = int(current_data["負"].sum())
win_rate = (total_wins / total_games * 100) if total_games > 0 else 0.0

# 3. サマリー表示
st.markdown("---")
st.subheader("📊 2026-27シーズン 最終成績シミュレーション")

col1, col2, col3, col4 = st.columns(4)
col1.metric("予想通算成績", f"{total_wins}勝 {total_losses}敗")
col2.metric("全体勝率", f"{win_rate:.1f}%")
col3.metric("総試合数", f"{total_games}試合")

cs_benchmark_wins = 41
win_diff = total_wins - cs_benchmark_wins
col4.metric(
    "昨季CSライン(41勝比)", 
    f"{total_wins}勝", 
    delta=f"{win_diff:+d}勝 (基準: 41勝)", 
    delta_color="normal" if win_diff >= 0 else "inverse"
)

# 4. ハピネッツ・トーク YouTubeチャンネルへの誘導バナー
st.markdown("---")
st.markdown(
    """
    <div style="background-color: #f8fafc; padding: 20px; border-radius: 10px; border: 1px solid #e2e8f0; text-align: center;">
        <h4 style="margin-bottom: 8px; color: #1e293b;">ハピネッツ・トークby秋田ブースター</h4>
        <p style="font-size: 14px; color: #64748b; margin-bottom: 15px;">ハピネッツを語るポッドキャスト 配信中！</p>
        <a href="https://www.youtube.com/channel/UCJ6na2Xp35fzf4ZM2EFCLwg" target="_blank">
            <button style="background-color: #ff0000; color: white; padding: 12px 24px; border: none; border-radius: 6px; font-weight: bold; cursor: pointer; font-size: 15px;">
                🔴 YouTubeチャンネルを見る・登録する 📺
            </button>
        </a>
    </div>
    """,
    unsafe_allow_html=True
)

# 5. シェア＆URL出力機能
st.markdown("---")
st.subheader("📤 あなたの予想結果をみんなにシェアしよう！")

share_text = f"私の来季の予想は【{total_wins}勝 {total_losses}敗 (勝率 {win_rate:.1f}%)】でした！\n\nあなたは何勝予想？ぜひシミュレーションして遊んでみてね！ 👇\n{APP_URL}\n\n#秋田ノーザンハピネッツ #Bリーグ #ハピネッツ #勝敗予想シミュレーター"

twitter_url = f"https://twitter.com/intent/tweet?text={urllib.parse.quote(share_text)}"

col_s1, col_s2 = st.columns(2)
with col_s1:
    st.markdown(
        f"""
        <a href="{twitter_url}" target="_blank">
            <button style="background-color: #000000; color: white; padding: 12px 20px; border: none; border-radius: 6px; font-weight: bold; cursor: pointer; width: 100%; font-size: 15px;">
                𝕏 (Twitter) でシェアしてフォロワーを誘う 🚀
            </button>
        </a>
        """,
        unsafe_allow_html=True
    )

with col_s2:
    st.text_input("🔗 アプリのURL", value=APP_URL)

st.text_area("📋 シェア用テキスト（コピーしてLINEやDiscord、SNSに貼れます）", value=share_text, height=140)

# 6. CSVダウンロード
st.markdown("---")
csv_export = current_data[["地区", "対戦相手", "年間対戦試合数", "勝", "負", "メモ"]].to_csv(index=False).encode("utf-8-sig")
st.download_button(
    label="📥 この予想データをCSVで保存",
    data=csv_export,
    file_name="akita_happinets_2026_27_prediction.csv",
    mime="text/csv"
)
