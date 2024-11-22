import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import matplotlib.ticker as ticker
import os
import matplotlib.font_manager as fm 
# 폰트 설정 (한글 깨짐 방지)
plt.rcParams['font.family'] = 'Malgun Gothic'  # Windows 환경
plt.rcParams['axes.unicode_minus'] = False

# 데이터 읽기
df = pd.read_csv('./지역별_소규모_임대료.csv')
물가 = pd.read_csv('./소비자물가지수.csv')
대출금리 = pd.read_csv('./대출금리.csv')

# 데이터 전처리
물가.rename(columns={'Unnamed: 0': '날짜'}, inplace=True)
물가['날짜'] = 물가['날짜'].astype(str).str[:4] + '-' + 물가['날짜'].astype(str).str[4:6]

대출금리['대출금리'] = 대출금리['대출금리'].replace(0, None)  # 0을 NaN으로 바꿔줌
대출금리['대출금리'] = 대출금리['대출금리'].interpolate(method='linear')  # 보간법으로 NaN 값 채우기
대출금리 = 대출금리[대출금리['날짜'] <= '2024-09']

#페이지설정
st.set_page_config(
    page_title="금융적비교",
    page_icon="💵",
    layout="wide",
    initial_sidebar_state="expanded")

# 사이드바 설정
st.sidebar.title("소상공인 폐업률 분석(1)")

# 첫 번째 토글 (상위 메뉴)
with st.sidebar.expander("임대료 Dataset"):
    st.write("소규모상가https://www.data.go.kr/data/15069766/fileData.do")
    st.write("중규모상가https://www.data.go.kr/data/15069789/fileData.do")
# 두 번째 토글 (상위 메뉴)
with st.sidebar.expander("소비자물가지수 Dataset"):
    st.write("https://data.seoul.go.kr/dataList/99/S/2/datasetView.do#")
# 세 번째 토글 (상위 메뉴)
with st.sidebar.expander("대출금리 Dataset"):
    st.write("https://www.mss.go.kr/site/smba/foffice/ex/statDB/MainStat.do?fromDtMM=2016-01&fromDtYY=2016&searchType=M&searchStartDe=2019-01&searchEndDe=2024-06")



# 레이아웃: 3개 그래프를 3개의 컬럼으로 배치
col = st.columns((2.5, 0.9,0.9), gap='medium')

#임대료 라인차트
with col[0]:
    st.subheader("임대료 데이터")
    region_list = df["지역"].unique().tolist()  # 중복 제거
    selected_region = st.selectbox("지역을 선택하세요", region_list)
    
    # 데이터 필터링
    df_selected = df[df["지역"] == selected_region].set_index("지역").T  # 선택 지역 필터링 후 전치
    df_selected.index.name = "분기"
    df_selected.reset_index(inplace=True)
    df_selected.columns = ["분기", "값"]

    # 라인차트 생성
    fig_line, ax = plt.subplots(figsize=(10, 3))  # 크기 조정
    sns.lineplot(data=df_selected, x="분기", y="값", marker="o", ax=ax)
    for i, row in df_selected.iterrows():
        ax.text(row["분기"], row["값"], f"{row['값']:.2f}", ha="center", va="bottom", fontsize=9)
    ax.set_title(f"{selected_region} 지역 데이터")
    ax.set_xlabel("분기")
    ax.set_ylabel("천원/㎡")
    plt.xticks(rotation=45)
    st.pyplot(fig_line)


    
##임대료 최대/최소

# 최고값 계산
highest_values = df.set_index("지역").max(axis=1)  # 각 지역별 최고값 계산
df_highest = highest_values.reset_index()
df_highest.columns = ["지역", "최고값"]

# 최고값의 최대값을 기준으로 진행률을 계산
max_value = df_highest["최고값"].max()  # 최고값의 최대값을 가져옴
df_highest["진행률"] = (df_highest["최고값"] / max_value) * 100  # 진행률 계산 (최고값을 최대값으로 나누어 비율을 백분율로 표현)

with col[1]:
    st.markdown('#### 지역별 최대값')
    
    # 데이터프레임에서 최고값을 진행률로 나타내기
    st.dataframe(df_highest,
                 column_order=("지역", "최고값"),  # 진행률을 추가
                 use_container_width=True,
                 hide_index=True,
                 width=None,
                 column_config={
                    "지역": st.column_config.TextColumn("지역"),
                    "최고값": st.column_config.ProgressColumn(
                        "최고값",
                        format="%.2f",  # 소수점 두 번째 자리까지 표시
                        min_value=0,
                        max_value=max_value,  # 최고값의 최대값을 max_value로 설정
                    )
                 }
    )

# 최소값 계산
lowest_values = df.set_index("지역").min(axis=1)  # 각 지역별 최소값 계산
df_lowest = lowest_values.reset_index()
df_lowest.columns = ["지역", "최소값"]

# 최소값의 최소값을 기준으로 진행률을 계산
min_value = df_lowest["최소값"].min()  # 최소값의 최소값을 가져옴
df_lowest["진행률"] = (df_lowest["최소값"] / min_value) * 100  # 진행률 계산 (최소값을 최소값으로 나누어 비율을 백분율로 표현)
with col[2]:
    st.markdown('#### 지역별 최소값')
    
    # 데이터프레임에서 최소값을 진행률로 나타내기
    st.dataframe(df_lowest,
                 column_order=("지역", "최소값" ),  # 진행률을 추가
                 use_container_width=True,
                 hide_index=True,
                 width=None,
                 column_config={
                    "지역": st.column_config.TextColumn("지역"),
                    "최소값": st.column_config.ProgressColumn(
                        "최소값",
                        format="%.2f",  # 소수점 두 번째 자리까지 표시
                        min_value=0,
                        max_value=min_value+50,  # 최소값의 최소값을 max_value로 설정
                    )
                 }
    )

    with st.expander('As a result', expanded=True):
        st.write('''
            - :orange[**서울**]의 최대값이 가장 크고 최소값이 가장 작으며, 그 차이도 명확하다.
            ''')

# 최대값에서 최소값을 뺀 값 계산
df_comparison = pd.merge(df_highest, df_lowest, on="지역")
df_comparison["최대-최소 차이"] = df_comparison["최고값"] - df_comparison["최소값"]

# 최대-최소 차이의 최대값 구하기
max_difference = df_comparison["최대-최소 차이"].max()  # 최대-최소 차이의 최대값

# 진행률로 최대값에서 최소값 차이를 표시 (최고값과 최소값은 제외하고 차이만 표시)
with col[1]:
    st.markdown('#### 지역별 최대-최소 차이')

    # 최고값에서 최소값 차이를 진행률로 표시 (최고값과 최소값 제외)
    st.dataframe(df_comparison[["지역", "최대-최소 차이"]],  # 최고값, 최소값 제외
                 use_container_width=True,
                 hide_index=True,
                 width=None,
                 column_config={
                    "지역": st.column_config.TextColumn("지역"),
                    "최대-최소 차이": st.column_config.ProgressColumn(
                        "최대-최소 차이",
                        format="%.2f",  # 소수점 두 번째 자리까지 표시
                        min_value=0,
                        max_value=max_difference,  # 최대-최소 차이의 최대값을 max_difference로 설정
                    )
                 }
    )

# **소비자물가지수 & 대출금리 비교**: 이중 축
with col[0]:
    st.subheader("소비자물가지수와 대출금리 비교")

    # 그래프 크기 설정 (가로 10, 세로 3)
    fig_cpi, ax1 = plt.subplots(figsize=(10, 4))

    # 첫 번째 y축: 소비자물가지수
    sns.lineplot(x='날짜', y='음식 및 숙박', data=물가, ax=ax1, color='blue', label='음식 및 숙박')
    sns.lineplot(x='날짜', y='의복·신발', data=물가, ax=ax1, color='orange', label='의복·신발')

    ax1.set_xlabel('날짜')
    ax1.set_ylabel('소비자물가지수 (CPI)', color='blue')
    ax1.tick_params(axis='y', labelcolor='blue')
    ax1.legend(loc='upper left')

    # 두 번째 y축: 대출금리
    ax2 = ax1.twinx()
    sns.lineplot(x='날짜', y='대출금리', data=대출금리, ax=ax2, color='red', label='대출금리')
    ax2.set_ylabel('대출금리 (%)', color='red')
    ax2.tick_params(axis='y', labelcolor='red')
    ax2.legend(loc='upper right')

    # x축 값 10개마다 표시
    plt.xticks(rotation=45, ha='right')  # x축 값 기울이기
    ax1.set_xticks(ax1.get_xticks()[::10])  # 10개마다 x축 값 표시

    plt.title("소비자물가지수와 대출금리 그래프")

    # 그래프 출력
    st.pyplot(fig_cpi)
