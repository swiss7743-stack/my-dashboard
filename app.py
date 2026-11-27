import streamlit as st  # 웹 화면을 만드는 라이브러리
import pandas as pd  # 표 형태 데이터를 다루는 라이브러리

# 페이지 설정: 화면을 넓게(wide) 쓰고, 브라우저 탭 제목을 정한다
st.set_page_config(page_title="매출 현황", layout="wide")


DATA_FILE = "sales_sample.csv"  # 불러올 데이터 파일 이름
REQUIRED_COLUMNS = ["date", "region", "category", "sales", "quantity"]  # 화면에 꼭 필요한 열


# 데이터 불러오기 함수
# @st.cache_data: 처음 한 번만 파일을 읽고 결과를 기억해 둔다(캐시).
# 사이드바 조건을 바꿔 화면이 다시 그려져도 파일을 또 읽지 않고 기억해 둔 표를 쓴다.
# (읽다가 오류가 나면 기억하지 않으므로, 파일을 고친 뒤 새로고침하면 다시 읽는다)
@st.cache_data
def load_data():
    try:
        return pd.read_csv(DATA_FILE)  # 먼저 보통 형식(UTF-8)으로 읽어 본다
    except UnicodeDecodeError:
        return pd.read_csv(DATA_FILE, encoding="cp949")  # 엑셀에서 저장한 한글 CSV(cp949)면 이 방식으로 다시 읽는다


# ---------------- 데이터 점검: 문제가 있으면 안내만 보여 주고 멈춘다 ----------------
# 1) 파일 읽기
try:
    df = load_data()
except FileNotFoundError:  # 파일이 없을 때
    st.error(
        f"데이터 파일 '{DATA_FILE}'을(를) 찾을 수 없습니다. "
        f"파일 이름이 정확한지, app.py와 같은 폴더에 있는지, 그 폴더에서 'streamlit run app.py'로 실행했는지 확인해 주세요."
    )
    st.stop()  # 아래 코드는 실행하지 않고 여기서 멈춘다
except Exception:  # 그 밖에 파일을 읽지 못한 경우 (빈 파일, CSV가 아닌 파일 등)
    st.error(
        f"데이터 파일 '{DATA_FILE}'을(를) 읽지 못했습니다. "
        f"파일이 비어 있지 않은지, 쉼표(,)로 구분된 CSV 형식인지 확인해 주세요."
    )
    st.stop()

# 2) 필요한 열이 모두 있는지 확인
missing_columns = [col for col in REQUIRED_COLUMNS if col not in df.columns]  # 필요한 열 중 표에 없는 것만 모은다
if missing_columns:  # 없는 열이 하나라도 있으면
    st.error(
        f"데이터 파일에 꼭 필요한 열이 없습니다: {', '.join(missing_columns)}. "
        f"'{DATA_FILE}'의 첫 줄(열 이름)에 {', '.join(REQUIRED_COLUMNS)}가 모두 있는지 확인해 주세요."
    )
    st.stop()

# 3) 자료형 바꾸기: 잘못된 값은 빈칸(NaT/NaN)으로 바꿔서 오류가 나지 않게 한다 (errors="coerce")
df["date"] = pd.to_datetime(df["date"], errors="coerce")  # 날짜로 바꿀 수 없는 값 → 빈칸
df["sales"] = pd.to_numeric(df["sales"], errors="coerce")  # 숫자로 바꿀 수 없는 값 → 빈칸
df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce")
row_count_before = len(df)  # 정리하기 전 행 개수
df = df.dropna(subset=REQUIRED_COLUMNS)  # 필요한 열 중 하나라도 빈칸인 행은 뺀다
dropped_count = row_count_before - len(df)  # 빠진 행 개수
df["region"] = df["region"].astype(str)  # 지역·카테고리는 글자로 통일한다 (숫자와 글자가 섞여 있으면 정렬할 때 오류가 나기 때문)
df["category"] = df["category"].astype(str)

if df.empty:  # 정리하고 나니 남은 행이 없으면
    st.error(
        f"'{DATA_FILE}'에 쓸 수 있는 행이 없습니다. "
        f"date는 2026-01-01 같은 날짜, sales·quantity는 숫자로 들어 있는지 확인해 주세요."
    )
    st.stop()

# 제목과 데이터 기준 캡션
st.title("영업팀 매출 현황 대시보드")  # 화면 맨 위 큰 제목
st.caption(
    "영업팀장이 지역과 기간을 고르면 월별 매출 추이와 지역별 실적을 볼 수 있는 화면 · "
    "데이터 기준: 2026년 1~10월 (sales_sample.csv)"
)  # 제목 아래 작은 회색 설명 글 (길어서 두 줄로 나눠 적었지만 화면에는 한 줄로 이어서 나온다)

# 잘못된 값 때문에 뺀 행이 있으면 알려 준다 (화면은 멈추지 않고 계속 그린다)
if dropped_count > 0:
    st.warning(
        f"날짜나 숫자가 비어 있거나 잘못된 행 {dropped_count:,}건은 빼고 보여 줍니다. "
        f"모든 행을 보려면 '{DATA_FILE}'에서 해당 칸을 고쳐 주세요."
    )

# ---------------- 왼쪽 사이드바: 조건(필터) 고르기 ----------------
st.sidebar.header("조건 선택")

# 1) 지역: 여러 개 고를 수 있고, 처음에는 모든 지역이 선택되어 있다
region_list = sorted(df["region"].unique())  # 지역 이름을 중복 없이 뽑아 가나다순으로 정렬한다
selected_regions = st.sidebar.multiselect("지역", region_list, default=region_list)

# 2) 카테고리: 드롭다운에서 하나만 고른다. 맨 앞에 '전체'를 넣는다
category_list = ["전체"] + sorted(df["category"].unique())  # ['전체', '생활용품', '식품', ...]
selected_category = st.sidebar.selectbox("카테고리", category_list)

# 3) 기간: 먼저 버튼으로 기간 종류를 고르고, '직접 선택'이면 달력으로 날짜를 고른다
min_date = df["date"].min().date()  # 데이터에서 가장 이른 날짜 (.date()로 시간은 빼고 날짜만)
max_date = df["date"].max().date()  # 데이터에서 가장 늦은 날짜 → '최근 N개월'의 기준 날짜
period_option = st.sidebar.radio("기간", ["전체", "최근 1개월", "최근 3개월", "직접 선택"])

if period_option == "전체":
    start_date, end_date = min_date, max_date
elif period_option in ["최근 1개월", "최근 3개월"]:
    months = 1 if period_option == "최근 1개월" else 3  # 몇 개월을 볼지 정한다
    # 기준 날짜에서 N개월 전의 다음 날부터 (예: 10월 30일 기준 1개월 → 10월 1일 ~ 10월 30일)
    start_date = (pd.Timestamp(max_date) - pd.DateOffset(months=months) + pd.Timedelta(days=1)).date()
    start_date = max(start_date, min_date)  # 데이터 시작일보다 앞으로 가지 않게 한다
    end_date = max_date
else:  # '직접 선택'
    picked = st.sidebar.date_input(
        "시작일과 종료일",
        value=(min_date, max_date),  # 처음에는 전체 기간이 골라져 있다
        min_value=min_date,  # 데이터에 있는 날짜 범위 안에서만 고를 수 있다
        max_value=max_date,
        format="YYYY-MM-DD",
    )
    # 달력에서 시작일만 누르고 종료일을 아직 안 누른 중간 상태에서는 날짜가 1개(또는 0개)만 들어온다
    if len(picked) < 2:
        st.sidebar.info("달력에서 종료일도 골라 주세요.")
        st.info("기간을 고르는 중입니다. 사이드바 달력에서 종료일까지 골라 주세요.")
        st.stop()  # 날짜가 다 정해질 때까지 아래(지표·그래프·표)는 그리지 않는다
    start_date, end_date = picked
    if start_date > end_date:  # 직접 입력하다가 순서가 뒤바뀌면 바로잡는다
        start_date, end_date = end_date, start_date

st.sidebar.caption(f"조회 기간: {start_date} ~ {end_date}")  # 실제로 적용되는 기간을 보여 준다

# 세 조건을 모두 만족하는 행만 골라 filtered에 저장한다
condition = df["region"].isin(selected_regions)  # 고른 지역 중 하나에 속하는가?
if selected_category != "전체":  # '전체'가 아니면 카테고리 조건도 추가한다
    condition = condition & (df["category"] == selected_category)
# 기간 안에 있는가? (종료일 '다음 날 0시 전'까지로 비교해야 종료일 당일 데이터가 빠지지 않는다)
condition = condition & (df["date"] >= pd.Timestamp(start_date)) & (df["date"] < pd.Timestamp(end_date) + pd.Timedelta(days=1))
filtered = df[condition]

# 필터 아래에 몇 건이 골라졌는지 보여 준다
st.sidebar.markdown(f"**선택 조건: {len(filtered):,}건 / 전체 {len(df):,}건**")

# 조건에 맞는 데이터가 하나도 없으면 안내 문구만 보여 주고 여기서 멈춘다
# (멈추지 않으면 평균 주문액을 0으로 나누게 되어 오류가 난다)
if filtered.empty:
    st.warning(
        "선택한 조건에 맞는 데이터가 0건입니다. "
        "사이드바에서 지역을 더 고르거나, 카테고리를 '전체'로 바꾸거나, 기간을 늘려서 조건을 넓혀 보세요."
    )
    st.stop()

# ---------------- 본문 ----------------
# 본문 탭 두 개 만들기
tab_summary, tab_detail = st.tabs(["요약", "상세 데이터"])

with tab_summary:
    # 핵심 숫자 3개 계산하기
    total_sales = filtered["sales"].sum()  # 총 매출: 걸러낸 데이터의 매출을 모두 더한다
    order_count = len(filtered)  # 주문 건수: 표의 행 하나가 주문 한 건이므로 행 개수를 센다
    avg_order = total_sales / order_count  # 평균 주문액: 총 매출 ÷ 주문 건수

    # 화면을 가로로 3칸 나누고, 칸마다 숫자 하나씩 보여 준다
    col1, col2, col3 = st.columns(3)
    col1.metric("총 매출", f"{total_sales:,.0f}원")  # :,.0f → 쉼표를 넣고 소수점은 없앤다
    col2.metric("주문 건수", f"{order_count:,}건")  # :, → 천 단위마다 쉼표를 넣는다
    col3.metric("평균 주문액", f"{avg_order:,.0f}원")  # 소수점 아래는 반올림해서 없앤다

    # 매출 추이 (선 그래프): 선택 기간이 3개월 이하면 일별, 더 길면 월별로 묶는다
    # '종료일에서 3개월 전'보다 시작일이 뒤에 있으면 3개월 이하라는 뜻 (예: 최근 1개월, 최근 3개월)
    is_short_period = pd.Timestamp(start_date) > pd.Timestamp(end_date) - pd.DateOffset(months=3)
    if is_short_period:
        unit_name, date_format = "일", "%Y-%m-%d"  # 일별: '2026-10-01' 모양
    else:
        unit_name, date_format = "월", "%Y-%m"  # 월별: '2026-10' 모양

    st.subheader(f"{unit_name}별 매출 추이")  # 소제목도 '일별 매출 추이' / '월별 매출 추이'로 바뀐다
    period = filtered["date"].dt.strftime(date_format).rename("period")  # 날짜를 일 또는 월 단위 글자로 바꾼다 (표에 열을 추가하지 않고 따로 저장)
    trend_sales = filtered.groupby(period)["sales"].sum().reset_index()  # 같은 날(또는 같은 달)끼리 매출을 더한다
    st.line_chart(trend_sales, x="period", y="sales", x_label=unit_name, y_label="매출(원)")  # 가로축은 일 또는 월, 세로축은 매출

    # 지역별 매출 (막대 그래프, 큰 순서)
    st.subheader("지역별 매출")  # 그래프 위 소제목
    region_sales = filtered.groupby("region")["sales"].sum().reset_index()  # 지역별로 매출을 더한다
    max_sales = region_sales["sales"].max()  # 지역별 매출 중 가장 큰 값
    # st.vega_lite_chart: 그래프 모양을 직접 정할 수 있는 Streamlit 그래프 (세로축 범위를 정하려고 사용)
    st.vega_lite_chart(
        region_sales,
        {
            "mark": {"type": "bar"},  # 막대 그래프
            "encoding": {
                "x": {
                    "field": "region",  # 가로축: 지역
                    "type": "nominal",  # 지역은 이름(글자)이라는 뜻
                    "title": "지역",
                    "sort": "-y",  # 세로축 값(매출)이 큰 순서로 막대를 놓는다
                    "axis": {"labelAngle": 0},  # 지역 이름을 눕히지 않고 똑바로 쓴다
                },
                "y": {
                    "field": "sales",  # 세로축: 매출
                    "type": "quantitative",  # 매출은 숫자라는 뜻
                    "title": "매출(원)",
                    "scale": {"domain": [0, max_sales * 1.1]},  # 세로축을 0부터 '가장 큰 매출 + 10%'까지만 잡는다
                    "axis": {"format": ",d"},  # 눈금 숫자에 쉼표를 넣는다 (예: 16,000,000)
                },
                "tooltip": [  # 막대에 마우스를 올리면 나오는 설명
                    {"field": "region", "title": "지역"},
                    {"field": "sales", "title": "매출(원)", "format": ","},
                ],
            },
        },
        width="stretch",  # 그래프를 화면 폭에 맞춘다
    )

    # 요약 탭 맨 아래: 이 화면을 보고 내릴 수 있는 경영 판단
    # (조건에 맞는 데이터가 0건이면 위에서 st.stop()으로 멈추므로, 이 문장은 자동으로 보이지 않는다)
    st.subheader("이 화면으로 내릴 수 있는 경영 판단")
    st.write(
        "지역별 매출 기여도와 카테고리별 매출 구성을 함께 보면, 매출을 견인하는 핵심 지역과 주력 카테고리를 파악해 "
        "영업 자원과 마케팅 예산을 우선 배분할 수 있다. "
        "반대로 매출 비중이 낮은 지역·카테고리는 원인 분석을 통해 판촉 강화 또는 운영 효율화 대상으로 선정할 수 있다."
    )  # 문장이 길어서 여러 줄로 나눠 적었지만 화면에는 한 문단으로 이어서 나온다

with tab_detail:
    st.dataframe(
        filtered,
        width="stretch",  # 표를 화면 폭에 꽉 차게 늘린다
        hide_index=True,  # 왼쪽의 행 번호(0, 1, 2 …)를 숨긴다
        column_config={
            "date": st.column_config.DateColumn("date", format="YYYY-MM-DD"),  # 날짜를 '2026-01-01'처럼 시간 없이 보여 준다
        },
    )
