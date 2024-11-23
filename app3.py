import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.ticker as ticker
import matplotlib.font_manager as fm
import folium 
import matplotlib
import requests
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rc
import seaborn as sns
import os, json
import plotly.graph_objects as go


matplotlib.rcParams['font.family'] = 'NanumGothic'
plt.rcParams['axes.unicode_minus'] = False


st.set_page_config(
    page_title="인구 및 사업환경",
    page_icon="💵",
    layout="wide",
    initial_sidebar_state="expanded")

# 사이드바 설정
st.sidebar.title("소상공인 폐업률 분석(3)")
st.sidebar.markdown("### 인구 및 사업환경")

# 첫 번째 토글 (상위 메뉴)
with st.sidebar.expander("인구밀도 Dataset"):
    st.write("https://data.seoul.go.kr/dataList/10584/S/2/datasetView.do")
# 두 번째 토글 (상위 메뉴)
with st.sidebar.expander("폐업률 Dataset"):
    st.write("https://data.seoul.go.kr/dataList/OA-15567/S/1/datasetView.do")
# 세 번째 토글 (상위 메뉴)
with st.sidebar.expander("프랜차이즈 점포 수 Dataset"):
    st.write("https://kosis.kr/common/meta_onedepth.jsp?vwcd=MT_ZTITLE&listid=O_22")
    st.write("https://sg.sbiz.or.kr/godo/stat/area.sg")

col = st.columns((2, 2,2), gap='medium')

with col[0]:
    st.subheader("구별 프랜차이즈 점포 수")
    # 데이터 불러오기
    df = pd.read_csv('./폐업률.csv')
    with open('./seoul_municipalities_geo_simple.json', 'r', encoding='utf-8') as f:
        seoul_geo = json.load(f)
    
    # Choropleth Map 생성
    fig = px.choropleth_mapbox(
        df,
        geojson=seoul_geo,
        locations='자치구_코드_명',
        color='프랜차이즈_점포_수',
        color_continuous_scale='reds',
        featureidkey='properties.name',
        mapbox_style='carto-positron',
        zoom=9,
        center={"lat": 37.563383, "lon": 126.996039},
        opacity=0.5,
    )

    # 레이아웃 업데이트
    fig.update_layout(width=1500, height=800)

    # 첫 번째 컬럼에 Choropleth Map 추가
    st.plotly_chart(fig, use_container_width=True)


with col[1]:
    st.subheader("구별 폐업률")
    # 폐업률 표준화
    df['표준화_폐업률'] = (df['폐업_률'] - df['폐업_률'].mean()) / df['폐업_률'].std()

    # Geojson 파일 읽어오기
    with open('./seoul_municipalities_geo_simple.json', 'r', encoding='utf-8') as f:
        seoul_geo = json.load(f)

    # 사용자 정의 색상 스케일
    custom_colorscale = [
        [0, "rgb(255,255,204)"],   # 낮은 값: 옅은 노란색
        [0.2, "rgb(255,237,160)"],
        [0.4, "rgb(254,178,76)"],
        [0.6, "rgb(253,141,60)"],
        [0.8, "rgb(240,59,32)"],
        [1, "rgb(189,0,38)"]       # 높은 값: 진한 빨간색
    ]

    # Choropleth Map 생성
    fig = px.choropleth_mapbox(
        df,
        geojson=seoul_geo,
        locations='자치구_코드_명',
        color='표준화_폐업률',  # 표준화된 값 사용
        color_continuous_scale=custom_colorscale,
        range_color=(-2, 2),  # 표준화 값 범위 설정 (필요시 조정)
        featureidkey='properties.name',
        mapbox_style='carto-positron',
        zoom=9,
        center={"lat": 37.563383, "lon": 126.996039},
        opacity=0.5,
    )

    # 레이아웃 업데이트
    fig.update_layout(width=1500, height=800)

    # 두 번째 컬럼에 Choropleth Map 추가
    st.plotly_chart(fig, use_container_width=True)

    st.write('''
            - 폐업률의 단위가 3.0 ~ 4.0 이라서 표준화를 진행했음에도 구별로 크게 차이가 보이지 않아서 구별 폐업 점포 수로 표현
            ''')

# 세 번째 컬럼: 폐업 점포 수 지도
with col[2]:
    st.subheader("구별 폐업 점포 수")
    # Geojson 파일 읽어오기
    with open('./seoul_municipalities_geo_simple.json', 'r', encoding='utf-8') as f:
        seoul_geo = json.load(f)

    # 사용자 정의 색상 스케일
    custom_colorscale = [
        [0, "rgb(255,255,204)"],   # 낮은 값: 옅은 노란색
        [0.2, "rgb(255,237,160)"],
        [0.4, "rgb(254,178,76)"],
        [0.6, "rgb(253,141,60)"],
        [0.8, "rgb(240,59,32)"],
        [1, "rgb(189,0,38)"]       # 높은 값: 진한 빨간색
    ]

    # Choropleth Map 생성
    fig = px.choropleth_mapbox(
        df,
        geojson=seoul_geo,
        locations='자치구_코드_명',
        color='폐업_점포_수',
        color_continuous_scale=custom_colorscale,
        featureidkey='properties.name',
        mapbox_style='carto-positron',
        zoom=9,
        center={"lat": 37.563383, "lon": 126.996039},
        opacity=0.5,
    )

    # 레이아웃 업데이트
    fig.update_layout(width=1500, height=800)

    # 세 번째 컬럼에 Choropleth Map 추가
    st.plotly_chart(fig, use_container_width=True)


with col[0]:
    st.subheader("구별 인구밀도")

    # 데이터 불러오기
    df_d = pd.read_csv('./서울시 동별 인구밀도.csv')

    # 사용자에게 연도 선택을 받기
    year_options = ['2019', '2020', '2021', '2022']
    selected_year = st.selectbox("연도를 선택하세요:", year_options)

    # 2023년도 제외하고 처리 (2023년도는 결측치가 많아서)
    if selected_year == '2023':
        st.warning("2023년도는 결측치가 많아 제외되었습니다.")
    
    # '-' 값을 NaN으로 변환한 후, 콤마 제거하고 float로 변환
    df_d[selected_year] = df_d[selected_year].replace({'-': np.nan, ',': ''}, regex=True).astype(float)

    # Geojson 파일 읽어오기
    with open('./seoul_municipalities_geo_simple.json', 'r', encoding='utf-8') as f:
        seoul_geo = json.load(f)

    # 사용자 정의 색상 스케일
    custom_colorscale = [
        [0, "rgb(255,255,204)"],   # 낮은 값: 옅은 노란색
        [0.2, "rgb(255,237,160)"],
        [0.4, "rgb(254,178,76)"],
        [0.6, "rgb(253,141,60)"],
        [0.8, "rgb(240,59,32)"],
        [1, "rgb(189,0,38)"]       # 높은 값: 진한 빨간색
    ]

    # Choropleth Map 생성
    fig = px.choropleth_mapbox(
        df_d,
        geojson=seoul_geo,
        locations='자치구',
        color=selected_year,
        color_continuous_scale=custom_colorscale,  # 사용자 정의 색상 스케일 적용
        featureidkey='properties.name',
        mapbox_style='carto-positron',
        zoom=9,
        center={"lat": 37.563383, "lon": 126.996039},
        opacity=0.5,
    )

    # 레이아웃 업데이트
    fig.update_layout(width=1500, height=800)

    # Streamlit에서 플롯 표시
    st.plotly_chart(fig, use_container_width=True)

with col[1]:
    st.subheader("년도별 폐업률")

    # 서브플롯 생성
    fig, ax = plt.subplots(figsize=(10, 6))

    # 년도별 폐업률 그래프
    sns.lineplot(data=df, x='년', y='폐업_률', ax=ax, palette='husl')
    ax.set_title("년도별 폐업률")

    # 그래프 레이아웃 조정
    plt.tight_layout()

    # Streamlit에서 플롯 표시
    st.pyplot(fig)

# 두 번째 컬럼에 분기별 폐업률 그래프 표시
with col[2]:
    st.markdown("<div style='height: 70px;'></div>", unsafe_allow_html=True)
with col[2]:
    st.subheader("분기별 폐업률")

    # 서브플롯 생성
    fig, ax = plt.subplots(figsize=(10, 6))

    # 분기별 폐업률 그래프
    sns.lineplot(data=df, x='분기', y='폐업_률', ax=ax)
    ax.set_title("분기별 폐업률")

    # 그래프 레이아웃 조정
    plt.tight_layout()

    # Streamlit에서 플롯 표시
    st.pyplot(fig)

    st.write('''
            - 서울시 음식업, 폐업률이 2023년도 부터 크게 증가하는 추세를 확인
            - 3분기(7~9월)에 폐업률이 크게 상승하는 추세를 확인
            ''')

with col[1]:
    st.markdown("<div style='height: 100px;'></div>", unsafe_allow_html=True)
with col[1]:
    st.subheader("강남구 폐업률")

    plt.figure(figsize=(20, 8))
    plt.plot(df[df['자치구_코드_명'] == '강남구'].groupby(['년_분기'])['폐업_률'].mean())
    plt.title("강남구 폐업률")
    plt.xlabel('년/분기')
    plt.ylabel('폐업률')
    plt.xticks(rotation=45)
    st.pyplot(plt)

# 두 번째 그래프: 서초구
with col[2]:
    st.subheader("서초구 폐업률")

    plt.figure(figsize=(20, 8))
    plt.plot(df[df['자치구_코드_명'] == '서초구'].groupby(['년_분기'])['폐업_률'].mean())
    plt.title("서초구 폐업률")
    plt.xlabel('년/분기')
    plt.ylabel('폐업률')
    plt.xticks(rotation=45)
    st.pyplot(plt)