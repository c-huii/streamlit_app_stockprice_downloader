import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.ticker as ticker
import os
import matplotlib.font_manager as fm
import folium 
import matplotlib
import requests

# Google Fonts CSS URL
font_url = "https://fonts.googleapis.com/css2?family=Nanum+Gothic&display=swap"

# 폰트 파일 다운로드 (CSS 파일)
response = requests.get(font_url)

if response.status_code == 200:
    with open("nanum_gothic.css", "wb") as f:
        f.write(response.content)
    print("CSS 파일을 다운로드 했습니다.")
else:
    print(f"다운로드 실패: {response.status_code}")
    
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

# 위도와 경도 데이터 추가 (수동 입력)
location_data = pd.DataFrame({
    '지역': ['강원', '경기', '경남', '경북', '광주', '대구', '대전', '부산', '서울', '세종',
            '울산', '인천', '전남', '전북', '제주', '충남', '충북'],
    'lat': [37.5559, 37.2751, 35.2375, 36.2486, 35.1600, 35.8714, 36.3510, 35.1796, 37.5665, 36.4803,
            35.5384, 37.4563, 34.8194, 35.8232, 33.4996, 36.5184, 36.6355],
    'lon': [128.2093, 127.0095, 128.6925, 128.8566, 126.8514, 128.6014, 127.3845, 129.0756, 126.9780, 127.2890,
            129.3115, 126.7052, 126.4630, 127.1477, 126.5312, 126.8009, 127.4913]
})

# 위도와 경도 데이터를 원본 데이터와 병합
df1 = pd.merge(df, location_data, on='지역')



# Folium 지도 생성
my_map = folium.Map(
    location=[df1['lat'].mean(), df1['lon'].mean()],
    zoom_start=6
)

# 레이아웃: 3개 그래프를 3개의 컬럼으로 배치
col = st.columns((0.7, 0.7), gap='medium')

#임대료 라인차트
# 지역 리스트를 먼저 정의해야 함
region_list = df["지역"].unique().tolist()  # 중복 제거

with col[0]:
    selected_region = st.selectbox("지역을 선택하세요", region_list)
    st.subheader(f"{selected_region} 지역 임대료 데이터")

    
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
    ax.set_xlabel("분기")
    ax.set_ylabel("천원/㎡")
    plt.xticks(rotation=45)
    st.pyplot(fig_line,
             use_container_width=True)
#지도데이터
with col[1]:  # col2 안에 지도 렌더링
    # 데이터프레임 순회하며 지도에 시각화

    # Streamlit UI 생성
    st.subheader("지역별 소규모 임대료 시각화")
    selected_quarter = st.selectbox(
        "분기를 선택하세요",
        options=df1.columns[1:10]  # 분기 열 선택 (22_1, 22_2, 22_3, ...)
    )

    # 선택된 분기의 데이터 추가
    df1['value'] = df1[selected_quarter]
    for _, row in df1.iterrows():
        # 원형 마커 추가
        folium.CircleMarker(
            location=[row['lat'], row['lon']],
            radius=row['value'] * 1.3,  # 원 크기 축소
            color='red',               # 원 테두리 색깔
            fill=True,
            fill_color='red',          # 원 내부 색깔
            fill_opacity=0.6
        ).add_to(my_map)

        # 값 표시 마커 추가
        folium.Marker(
            location=[row['lat'], row['lon']],
            icon=folium.DivIcon(html=f"""
                <div style="font-size: 12px; color: black; text-align: center; white-space: nowrap;">
                    <b>{row['지역']}: {round(row['value'], 2)}</b>  <!-- 소수점 2자리 -->
                </div>
            """)
        ).add_to(my_map)

    # Streamlit에 지도 렌더링
    st.components.v1.html(my_map._repr_html_(), width=700, height=500)
##임대료 최대/최소

# 최고값 계산
highest_values = df.set_index("지역").max(axis=1)  # 각 지역별 최고값 계산
df_highest = highest_values.reset_index()
df_highest.columns = ["지역", "최고값"]

# 최소값 계산
lowest_values = df.set_index("지역").min(axis=1)  # 각 지역별 최소값 계산
df_lowest = lowest_values.reset_index()
df_lowest.columns = ["지역", "최소값"]

# Streamlit layout: with col[1]:
with col[0]:
    st.subheader("최대값/최소값 막대그래프")
    
    # 막대그래프 생성
    fig, ax = plt.subplots(figsize=(8, 4))  # 크기 줄이기

    # 최고값과 최소값을 하나의 그래프에 표시
    bar_width = 0.35
    index = range(len(df_highest))

    bar1 = ax.bar(index, df_highest["최고값"], bar_width, label="Maxi", color='green')
    bar2 = ax.bar([i + bar_width for i in index], df_lowest["최소값"], bar_width, label="Mini", color='red')

    # 그래프 스타일 설정
    ax.set_xlabel("Area")
    ax.set_ylabel("1000won/m2")
    ax.set_xticks([i + bar_width / 2 for i in index])
    ax.set_xticklabels(df_highest["지역"], rotation=45)  # X축 라벨 회전
    ax.legend()

    # Streamlit에 그래프 렌더링
    st.pyplot(fig)

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
                 },use_container_width=True
    )
    with st.expander('As a result', expanded=True):
        st.write('''
            - :orange[**서울**]의 최대값이 가장 크고 최소값이 가장 작으며, 그 차이도 명확하다.
            ''')

# **소비자물가지수 & 대출금리 비교**: 이중 축
with col[0]:
    st.subheader("소비자물가지수(CPI)와 대출금리 비교 그래프")

    # 그래프 크기 설정 (가로 10, 세로 3)
    fig_cpi, ax1 = plt.subplots(figsize=(10, 4))

    # 첫 번째 y축: 소비자물가지수
    sns.lineplot(x='날짜', y='음식 및 숙박', data=물가, ax=ax1, color='blue', label='음식 및 숙박')
    sns.lineplot(x='날짜', y='의복·신발', data=물가, ax=ax1, color='orange', label='의복 및 신발')

    ax1.set_xlabel('날짜')
    ax1.set_ylabel('소비자물가지수CPI)', color='blue')
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

    # 그래프 출력
    st.pyplot(fig_cpi,
             use_container_width=True,)
    
