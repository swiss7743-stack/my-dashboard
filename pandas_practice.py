import pandas as pd  # 표 형태 데이터를 다루는 라이브러리

# CSV 파일을 불러와 df(데이터프레임, 엑셀 표 같은 것)에 저장한다
# parse_dates=["date"]: date 열을 글자가 아니라 날짜 형식으로 읽으라는 뜻
df = pd.read_csv("sales_sample.csv", parse_dates=["date"])

# 1. 행·열 개수: shape는 (행 개수, 열 개수)를 알려 준다
print("=== 1. 행·열 개수 ===")
print("행 개수:", df.shape[0])
print("열 개수:", df.shape[1])

# 2. 열 이름과 자료형: dtypes는 각 열이 숫자인지 글자인지 알려 준다
print("\n=== 2. 열 이름과 자료형 ===")
print(df.dtypes)

# 3. 빈칸 개수: isna()로 빈칸을 찾고 sum()으로 열마다 개수를 센다
print("\n=== 3. 열별 빈칸 개수 ===")
print(df.isna().sum())

# 4. 숫자 열 요약: describe()는 개수·평균·표준편차·최솟값·최댓값 등을 보여 준다
print("\n=== 4. 숫자 열 요약 ===")
print(df.describe())

# 5. 월별 매출 합계 (1월부터 10월까지 시간 순서대로)
print("\n=== 5. 월별 매출 합계 ===")
month = df["date"].dt.to_period("M")  # 날짜에서 '연-월'만 뽑는다 (예: 2026-03-15 → 2026-03)
monthly_sales = df.groupby(month)["sales"].sum()  # 같은 월끼리 묶어서 매출을 더한다
print(monthly_sales)

# 6. 지역별 매출 합계 (큰 순서로)
print("\n=== 6. 지역별 매출 합계 (큰 순서) ===")
region_sales = df.groupby("region")["sales"].sum()  # 같은 지역끼리 묶어서 매출을 더한다
region_sales = region_sales.sort_values(ascending=False)  # 큰 값부터 작은 값 순서로 정렬한다
print(region_sales)

# 7. 부산 지역 매출 합계
print("\n=== 7. 부산 매출 합계 ===")
print(df[df["region"] == "부산"]["sales"].sum())  # region이 '부산'인 행만 골라서 매출을 더한다

# 8. 카테고리별 평균 매출 (큰 순서)
print("\n=== 8. 카테고리별 평균 매출 (큰 순서) ===")
print(df.groupby("category")["sales"].mean().sort_values(ascending=False))  # 카테고리끼리 묶어 평균을 낸 뒤 큰 순서로 정렬한다

# 9. 3월이면서 매출이 20만 원 이상인 거래 건수
print("\n=== 9. 3월 & 매출 20만 원 이상 거래 건수 ===")
print(len(df[(df["date"].dt.month == 3) & (df["sales"] >= 200000)]))  # 두 조건을 모두 만족하는 행만 골라 개수를 센다
