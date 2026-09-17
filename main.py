python
import streamlit as st
import pandas as pd
import plotly.express as px

# ==========================================
# 기본 설정
# ==========================================

st.set_page_config(
    page_title="영화 데이터 그래프 도감 Ⅱ",
    page_icon="🎬",
    layout="wide"
)

st.title("🎬 영화 데이터 그래프 도감 Ⅱ")
st.subheader("분포 · 구성 · 관계 · 나만의 질문")

st.write(
    "같은 영화 데이터를 여러 가지 그래프로 바라보며 "
    "분포·구성·관계를 알아봅니다."
)

# ==========================================
# 데이터 주소
# ==========================================

DATA_URL = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_movies.csv"


# ==========================================
# 데이터 불러오기
# ==========================================

@st.cache_data
def load_data():
    df = pd.read_csv(DATA_URL)

    # 숫자로 변환
    df["first_scrn"] = pd.to_numeric(
        df["first_scrn"], errors="coerce"
    )

    df["first_week_audi"] = pd.to_numeric(
        df["first_week_audi"], errors="coerce"
    )

    df["total_audi"] = pd.to_numeric(
        df["total_audi"], errors="coerce"
    )

    df["days_in_top10"] = pd.to_numeric(
        df["days_in_top10"], errors="coerce"
    )

    # 여러 장르가 있으면 첫 번째 장르 사용
    df["장르"] = (
        df["genre"]
        .fillna("미상")
        .astype(str)
        .str.split("|")
        .str[0]
    )

    # 여러 국가가 있으면 첫 번째 국가 사용
    df["대표국가"] = (
        df["nation"]
        .fillna("미상")
        .astype(str)
        .str.split("|")
        .str[0]
    )

    return df


# ==========================================
# 데이터 불러오기
# ==========================================

try:
    df = load_data()

except Exception as e:
    st.error("데이터를 불러오는 데 실패했습니다.")
    st.write(e)
    st.stop()


# ==========================================
# 데이터 정보
# ==========================================

st.success(
    "데이터를 정상적으로 불러왔습니다."
)

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "영화 수",
        f"{len(df):,}편"
    )

with col2:
    st.metric(
        "장르 수",
        f"{df['장르'].nunique():,}개"
    )

with col3:
    st.metric(
        "국가 수",
        f"{df['대표국가'].nunique():,}개"
    )


# ==========================================
# 원본 데이터 표
# ==========================================

st.header("0. 오늘의 데이터 표")

st.write(
    "영화 한 편이 한 행으로 구성되어 있습니다."
)

table_columns = [
    "movieNm",
    "openDt",
    "genre",
    "nation",
    "first_scrn",
    "first_week_audi",
    "total_audi",
    "days_in_top10"
]

available_columns = [
    c for c in table_columns if c in df.columns
]

st.dataframe(
    df[available_columns],
    use_container_width=True,
    hide_index=True
)


# ==========================================
# 그래프 1
# 도넛
# ==========================================

st.divider()

st.header("1. 장르별 영화 편수 (도넛)")

st.write(
    "질문: **10위권에 든 영화의 장르 구성은 어떠한가?**"
)

genre_count = (
    df["장르"]
    .value_counts()
    .reset_index()
)

genre_count.columns = [
    "장르",
    "편수"
]

# 표도 같이 보여주기
st.subheader("장르별 영화 편수 표")

st.dataframe(
    genre_count,
    use_container_width=True,
    hide_index=True
)

# 원형 / 도넛 그래프
fig1 = px.pie(
    genre_count,
    names="장르",
    values="편수",
    hole=0.45,
    title="장르별 영화 편수"
)

fig1.update_traces(
    textposition="inside",
    textinfo="percent+label",
    hovertemplate=(
        "<b>%{label}</b><br>"
        "영화 편수: %{value}편<br>"
        "비율: %{percent}<extra></extra>"
    )
)

st.plotly_chart(
    fig1,
    use_container_width=True
)

st.text_area(
    "이 그래프로 알 수 있는 것",
    key="answer1",
    placeholder="내 말로 한 문장을 적어 보세요."
)


# ==========================================
# 그래프 2
# 트리맵
# ==========================================

st.divider()

st.header("2. 장르 안의 영화 (트리맵)")

st.write(
    "질문: **장르 안에서 어떤 영화가 컸나?**"
)

tree_df = df.dropna(
    subset=["movieNm", "total_audi"]
).copy()

fig2 = px.treemap(
    tree_df,
    path=["장르", "movieNm"],
    values="total_audi",
    title="장르별 총 관객과 영화"
)

fig2.update_traces(
    hovertemplate=(
        "<b>%{label}</b><br>"
        "총 관객: %{value:,}명"
        "<extra></extra>"
    )
)

st.plotly_chart(
    fig2,
    use_container_width=True
)

st.text_area(
    "이 그래프로 알 수 있는 것",
    key="answer2",
    placeholder="내 말로 한 문장을 적어 보세요."
)


# ==========================================
# 그래프 3
# 히스토그램
# ==========================================

st.divider()

st.header("3. 총 관객 분포 (히스토그램)")

st.write(
    "질문: **영화 대부분은 관객이 몇 명쯤인가?**"
)

hist_df = df.dropna(
    subset=["total_audi"]
).copy()

fig3 = px.histogram(
    hist_df,
    x="total_audi",
    nbins=30,
    title="영화별 총 관객 분포"
)

fig3.update_layout(
    xaxis_title="총 관객 수",
    yaxis_title="영화 편수"
)

fig3.update_traces(
    hovertemplate=(
        "총 관객: %{x:,}명<br>"
        "영화 편수: %{y}편"
        "<extra></extra>"
    )
)

st.plotly_chart(
    fig3,
    use_container_width=True
)

st.text_area(
    "이 그래프로 알 수 있는 것",
    key="answer3",
    placeholder="내 말로 한 문장을 적어 보세요."
)


# ==========================================
# 그래프 4
# 산점도
# ==========================================

st.divider()

st.header("4. 개봉일 스크린 수와 총 관객 (산점도)")

st.write(
    "질문: **스크린을 많이 받은 영화가 관객도 많나?**"
)

scatter_df = df.dropna(
    subset=[
        "first_scrn",
        "total_audi",
        "movieNm",
        "장르"
    ]
).copy()

fig4 = px.scatter(
    scatter_df,
    x="first_scrn",
    y="total_audi",
    color="장르",
    hover_name="movieNm",
    title="개봉일 스크린 수와 총 관객"
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

st.plotly_chart(
    fig4,
    use_container_width=True
)

st.text_area(
    "이 그래프로 알 수 있는 것",
    key="answer4",
    placeholder="내 말로 한 문장을 적어 보세요."
)


# ==========================================
# 그래프 5
# 박스플롯
# ==========================================

st.divider()

st.header("5. 장르별 총 관객 (박스플롯)")

st.write(
    "질문: **장르별 관객 분포는 어떻게 다른가?**"
)

genre_number = (
    df["장르"]
    .value_counts()
)

large_genres = genre_number[
    genre_number >= 10
].index

box_df = df[
    df["장르"].isin(large_genres)
].dropna(
    subset=["total_audi"]
).copy()

fig5 = px.box(
    box_df,
    x="장르",
    y="total_audi",
    points="outliers",
    hover_name="movieNm",
    title="장르별 총 관객 분포"
)

fig5.update_layout(
    xaxis_title="장르",
    yaxis_title="총 관객 수"
)

st.plotly_chart(
    fig5,
    use_container_width=True
)

st.text_area(
    "이 그래프로 알 수 있는 것",
    key="answer5",
    placeholder="내 말로 한 문장을 적어 보세요."
)


# ==========================================
# 그래프 6
# 버블
# ==========================================

st.divider()

st.header("6. 첫 주 관객을 점 크기로 (버블)")

st.write(
    "질문: **첫 주 관객까지 넣으면 무엇이 더 보이나?**"
)

bubble_df = df.dropna(
    subset=[
        "first_scrn",
        "total_audi",
        "first_week_audi",
        "movieNm",
        "장르"
    ]
).copy()

# 0 이하인 값은 버블 크기로 사용할 수 없으므로 1로 변경
bubble_df["버블크기"] = (
    bubble_df["first_week_audi"]
    .clip(lower=1)
)

fig6 = px.scatter(
    bubble_df,
    x="first_scrn",
    y="total_audi",
    color="장르",
    size="버블크기",
    size_max=45,
    hover_name="movieNm",
    title="스크린 수 · 총 관객 · 첫 주 관객"
)

fig6.update_layout(
    xaxis_title="개봉일 스크린 수",
    yaxis_title="총 관객 수"
)

st.plotly_chart(
    fig6,
    use_container_width=True
)

st.text_area(
    "이 그래프로 알 수 있는 것",
    key="answer6",
    placeholder="내 말로 한 문장을 적어 보세요."
)


# ==========================================
# 그래프 7
# 선버스트
# ==========================================

st.divider()

st.header("7. 국가에서 장르로 (선버스트)")

st.write(
    "질문: **국가에서 장르로 내려가면 무엇이 보이나?**"
)

sun_df = (
    df.groupby(
        ["대표국가", "장르"]
    )
    .size()
    .reset_index(
        name="편수"
    )
)

fig7 = px.sunburst(
    sun_df,
    path=[
        "대표국가",
        "장르"
    ],
    values="편수",
    title="국가 → 장르 영화 구성"
)

fig7.update_traces(
    hovertemplate=(
        "<b>%{label}</b><br>"
        "영화 편수: %{value}편"
        "<extra></extra>"
    )
)

st.plotly_chart(
    fig7,
    use_container_width=True
)

st.text_area(
    "이 그래프로 알 수 있는 것",
    key="answer7",
    placeholder="내 말로 한 문장을 적어 보세요."
)


# ==========================================
# 그래프 8
# 나만의 질문
# ==========================================

st.divider()

st.header("8. 나만의 질문")

st.write(
    "### 질문"
)

st.markdown(
    """
**영화가 10위권에 오래 머문 영화일수록 총 관객도 많은가?**

이 질문에서는 다음 두 열을 사용합니다.

- `days_in_top10` → 10위권에 머문 일수
- `total_audi` → 총 관객 수

따라서 두 숫자의 관계를 보기 위해 **산점도**를 사용합니다.
"""
)

question_df = df.dropna(
    subset=[
        "days_in_top10",
        "total_audi",
        "movieNm",
        "장르"
    ]
).copy()

fig8 = px.scatter(
    question_df,
    x="days_in_top10",
    y="total_audi",
    color="장르",
    hover_name="movieNm",
    title="10위권 체류일수와 총 관객의 관계"
)

fig8.update_layout(
    xaxis_title="10위권에 머문 일수",
    yaxis_title="총 관객 수"
)

st.plotly_chart(
    fig8,
    use_container_width=True
)

st.text_area(
    "8번째 질문의 분석",
    key="answer8",
    height=180,
    placeholder=(
        "그래프를 보고 내 말로 분석해 보세요. "
        "두 변수 사이에 어떤 관계가 있는지, "
        "특이하게 벗어나는 영화가 있는지도 적어 보세요."
    )
)


# ==========================================
# 마지막 데이터 표
# ==========================================

st.divider()

st.header("📋 영화 데이터 전체 표")

display_df = df.copy()

# 숫자를 읽기 편하게 표시
for column in [
    "first_scrn",
    "first_week_audi",
    "total_audi",
    "days_in_top10"
]:
    if column in display_df.columns:
        display_df[column] = display_df[column].apply(
            lambda x: f"{int(x):,}"
            if pd.notna(x)
            else ""
        )

st.dataframe(
    display_df,
    use_container_width=True,
    hide_index=True
)


# ==========================================
# 마지막
# ==========================================

st.divider()

st.success(
    "🎉 영화 데이터 그래프 도감 Ⅱ 완성!"
)

st.caption(
    "원출처: 영화진흥위원회 KOBIS"
)
