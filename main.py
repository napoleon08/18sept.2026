```python
import streamlit as st
import pandas as pd
import plotly.express as px

# ─────────────────────────────────────────────
# 영화 데이터 그래프 도감 Ⅱ
# 분포 · 구성 · 관계 · 나만의 질문
# ─────────────────────────────────────────────

st.set_page_config(
    page_title="영화 데이터 그래프 도감 2",
    page_icon="🎬",
    layout="wide"
)

st.title("🎬 영화 데이터 그래프 도감 Ⅱ")
st.markdown("### 분포 · 구성 · 관계 · 나만의 질문")
st.caption("원출처: 영화진흥위원회 KOBIS · 216편 영화 데이터")

DATA_URL = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_movies.csv"


@st.cache_data
def load_data():
    df = pd.read_csv(DATA_URL)

    # 숫자 열 정리
    numeric_cols = [
        "first_scrn",
        "first_week_audi",
        "total_audi",
        "days_in_top10"
    ]

    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # 여러 장르가 | 로 연결된 경우 첫 번째 장르를 대표 장르로 사용
    df["장르"] = (
        df["genre"]
        .fillna("미상")
        .astype(str)
        .str.split("|")
        .str[0]
        .replace("", "미상")
    )

    # 여러 국가가 | 로 연결된 경우 첫 번째 국가를 대표 국가로 사용
    df["대표국가"] = (
        df["nation"]
        .fillna("미상")
        .astype(str)
        .str.split("|")
        .str[0]
        .replace("", "미상")
    )

    return df


# 데이터 불러오기
try:
    df = load_data()
except Exception as e:
    st.error("데이터를 불러오지 못했습니다.")
    st.exception(e)
    st.stop()


# 데이터 정보
st.info(
    f"현재 데이터: **{len(df):,}편** · "
    f"영화 한 편이 한 행입니다. "
    f"그래프마다 서로 다른 기준으로 같은 데이터를 바라봅니다."
)


# ═════════════════════════════════════════════
# 그래프 1. 도넛
# ═════════════════════════════════════════════

st.header("1. 장르별 영화 편수 (도넛)")
st.write("질문: **10위권에 든 영화의 장르 구성은 어떠한가?**")

genre_count = df["장르"].value_counts().reset_index()
genre_count.columns = ["장르", "편수"]

fig1 = px.pie(
    genre_count,
    names="장르",
    values="편수",
    hole=0.45
)

fig1.update_traces(
    hovertemplate="%{label}<br>%{value}편 (%{percent})<extra></extra>"
)

fig1.update_layout(
    legend_title_text="장르",
    margin=dict(t=20, b=20, l=20, r=20)
)

st.plotly_chart(fig1, use_container_width=True)

st.text_input(
    "이 그래프로 알 수 있는 것",
    key="note1",
    placeholder="예: 어떤 장르의 영화가 가장 많이 포함되어 있는지 알 수 있다."
)

st.divider()


# ═════════════════════════════════════════════
# 그래프 2. 트리맵
# ═════════════════════════════════════════════

st.header("2. 장르 안의 영화 (트리맵)")
st.write("질문: **장르 안에서 어떤 영화가 컸나?**")

treemap_df = df.dropna(subset=["total_audi"]).copy()

fig2 = px.treemap(
    treemap_df,
    path=["장르", "movieNm"],
    values="total_audi",
    hover_data={"total_audi": ":,"}
)

fig2.update_traces(
    hovertemplate="<b>%{label}</b><br>총 관객: %{value:,}명<extra></extra>"
)

st.plotly_chart(fig2, use_container_width=True)

st.text_input(
    "이 그래프로 알 수 있는 것",
    key="note2",
    placeholder="예: 총 관객이 많은 영화일수록 트리맵에서 큰 영역으로 나타난다."
)

st.divider()


# ═════════════════════════════════════════════
# 그래프 3. 히스토그램
# ═════════════════════════════════════════════

st.header("3. 총 관객 분포 (히스토그램)")
st.write("질문: **영화 대부분은 관객이 몇 명쯤인가?**")

hist_df = df.dropna(subset=["total_audi"]).copy()

fig3 = px.histogram(
    hist_df,
    x="total_audi",
    nbins=30
)

fig3.update_layout(
    xaxis_title="총 관객 수",
    yaxis_title="영화 편수"
)

fig3.update_traces(
    hovertemplate="총 관객 구간: %{x}<br>영화 편수: %{y}편<extra></extra>"
)

st.plotly_chart(fig3, use_container_width=True)

st.text_input(
    "이 그래프로 알 수 있는 것",
    key="note3",
    placeholder="예: 대부분의 영화가 어느 정도의 총 관객 구간에 몰려 있는지 알 수 있다."
)

st.divider()


# ═════════════════════════════════════════════
# 그래프 4. 산점도
# ═════════════════════════════════════════════

st.header("4. 개봉일 스크린 수와 총 관객 (산점도)")
st.write("질문: **스크린을 많이 받은 영화가 관객도 많나?**")

scatter_df = df.dropna(
    subset=["first_scrn", "total_audi", "movieNm", "장르"]
).copy()

fig4 = px.scatter(
    scatter_df,
    x="first_scrn",
    y="total_audi",
    color="장르",
    hover_name="movieNm",
    hover_data={
        "first_scrn": ":,",
        "total_audi": ":,",
        "장르": True
    }
)

fig4.update_layout(
    xaxis_title="개봉일 스크린 수",
    yaxis_title="총 관객 수"
)

fig4.update_traces(
    marker=dict(
        size=9,
        opacity=0.75
    )
)

st.plotly_chart(fig4, use_container_width=True)

st.text_input(
    "이 그래프로 알 수 있는 것",
    key="note4",
    placeholder="예: 개봉일 스크린 수와 총 관객 사이에 어떤 관계가 나타나는지 볼 수 있다."
)

st.divider()


# ═════════════════════════════════════════════
# 그래프 5. 박스플롯
# ═════════════════════════════════════════════

st.header("5. 장르별 총 관객 (박스플롯)")
st.write("질문: **장르별 관객 분포는 어떻게 다른가?**")

genre_sizes = df["장르"].value_counts()

# 영화가 10편 이상인 장르만 선택
big_genres = genre_sizes[genre_sizes >= 10].index

box_df = df[
    df["장르"].isin(big_genres)
].dropna(
    subset=["total_audi"]
).copy()

fig5 = px.box(
    box_df,
    x="장르",
    y="total_audi",
    points="outliers",
    hover_name="movieNm",
    hover_data={
        "total_audi": ":,"
    }
)

fig5.update_layout(
    xaxis_title="장르",
    yaxis_title="총 관객 수"
)

st.plotly_chart(fig5, use_container_width=True)

st.text_input(
    "이 그래프로 알 수 있는 것",
    key="note5",
    placeholder="예: 장르별 중앙값과 총 관객 분포의 차이를 볼 수 있다."
)

st.divider()


# ═════════════════════════════════════════════
# 그래프 6. 버블
# ═════════════════════════════════════════════

st.header("6. 첫 주 관객을 점 크기로 (버블)")
st.write("질문: **첫 주 관객까지 넣으면 무엇이 더 보이나?**")

bubble_df = df.dropna(
    subset=[
        "first_scrn",
        "total_audi",
        "first_week_audi",
        "movieNm",
        "장르"
    ]
).copy()

# 버블 크기는 1 이상이어야 함
bubble_df["버블크기"] = bubble_df["first_week_audi"].clip(lower=1)

fig6 = px.scatter(
    bubble_df,
    x="first_scrn",
    y="total_audi",
    color="장르",
    size="버블크기",
    size_max=45,
    hover_name="movieNm",
    hover_data={
        "first_scrn": ":,",
        "total_audi": ":,",
        "first_week_audi": ":,",
        "장르": True
    }
)

fig6.update_layout(
    xaxis_title="개봉일 스크린 수",
    yaxis_title="총 관객 수"
)

st.plotly_chart(fig6, use_container_width=True)

st.text_input(
    "이 그래프로 알 수 있는 것",
    key="note6",
    placeholder="예: 첫 주 관객이 큰 영화가 총 관객에서도 어떤 위치를 차지하는지 볼 수 있다."
)

st.divider()


# ═════════════════════════════════════════════
# 그래프 7. 선버스트
# ═════════════════════════════════════════════

st.header("7. 국가에서 장르로 (선버스트)")
st.write("질문: **국가에서 장르로 내려가면 무엇이 보이나?**")

sun_df = (
    df.groupby(
        ["대표국가", "장르"],
        as_index=False
    )
    .agg(
        편수=("movieNm", "count")
    )
)

fig7 = px.sunburst(
    sun_df,
    path=["대표국가", "장르"],
    values="편수"
)

fig7.update_traces(
    hovertemplate="%{label}<br>영화 편수: %{value}편<extra></extra>"
)

st.plotly_chart(fig7, use_container_width=True)

st.text_input(
    "이 그래프로 알 수 있는 것",
    key="note7",
    placeholder="예: 국가별로 어떤 장르의 영화가 많이 포함되어 있는지 볼 수 있다."
)

st.divider()


# ═════════════════════════════════════════════
# 그래프 8. 나만의 질문
# ═════════════════════════════════════════════

st.header("8. 나만의 질문 — 내가 만든 그래프로 답하기")

st.markdown(
    """
### 나만의 질문

**“영화가 10위권에 오래 머문 영화일수록 총 관객도 많은가?”**

이 질문은 `days_in_top10`과 `total_audi`의 관계를 묻습니다.
따라서 **산점도**를 사용합니다.

- 가로축: `days_in_top10` — 10위권에 머문 일수
- 세로축: `total_audi` — 총 관객 수
- 점 하나: 영화 한 편
- 색: 장르
"""
)

q8_df = df.dropna(
    subset=[
        "days_in_top10",
        "total_audi",
        "movieNm",
        "장르"
    ]
).copy()

fig8 = px.scatter(
    q8_df,
    x="days_in_top10",
    y="total_audi",
    color="장르",
    hover_name="movieNm",
    hover_data={
        "days_in_top10": True,
        "total_audi": ":,",
        "장르": True
    },
    trendline="ols"
)

fig8.update_layout(
    xaxis_title="10위권에 머문 일수",
    yaxis_title="총 관객 수"
)

st.plotly_chart(fig8, use_container_width=True)

st.text_area(
    "8번째 질문의 분석 — 그래프를 보고 내 말로 쓰기",
    key="note8",
    height=150,
    placeholder="예: 10위권에 오래 머문 영화일수록 총 관객이 많은 경향이 나타나는지, 예외적인 영화가 있는지 적어 보세요."
)

st.success(
    "🎉 도감 Ⅱ 완성! "
    "7개의 그래프와 나만의 8번째 질문까지 완성했습니다."
)


# ═════════════════════════════════════════════
# 원본 데이터 확인
# ═════════════════════════════════════════════

with st.expander("📋 사용한 데이터 확인"):
    st.write(
        "사용 열: movieNm, openDt, genre, nation, "
        "first_scrn, first_week_audi, total_audi, days_in_top10"
    )

    st.dataframe(
        df,
        use_container_width=True
    )
```
