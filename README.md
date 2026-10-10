# AI Stock Researcher — 1단계

## 기능
- 국내·미국 종목의 과거 가격 데이터 조회
- 기간 수익률, 연환산 변동성, 최대 낙폭, 20/50일 이동평균 계산
- 가격 차트와 종목 비교표
- CSV 다운로드
- 자동 주문 기능 없음

## 실행 방법 (Windows)
1. Python 3.13 또는 3.12를 설치합니다: https://www.python.org/downloads/windows/
   설치 화면에서 `Add python.exe to PATH` 옵션이 보이면 체크하세요.
2. ZIP 압축을 풉니다.
3. `run.bat`을 더블클릭합니다.
4. 설치가 끝나면 브라우저가 열립니다. 주소가 표시되면 보통 `http://localhost:8501`입니다.

대체 방법: 압축 폴더에서 명령 프롬프트를 열고 다음을 실행합니다.
```bat
py -3.13 -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python -m streamlit run app.py
```
Python 3.13이 없으면 명령의 `-3.13`을 `-3.12`로 바꾸세요.

## 종목 코드 예시
- 삼성전자: `005930.KS`
- SK하이닉스: `000660.KS`
- 코스닥 종목은 Yahoo Finance에서 `.KQ` 접미사를 지원하는지 확인하세요.
- 미국 주식: `NVDA`, `MSFT`, `AAPL`

## 중요 제약
- 이 버전은 토스증권 공식 API를 사용하지 않습니다. Yahoo Finance 데이터를 이용하므로 지연·누락·서비스 변경 가능성이 있습니다.
- 지표는 과거 가격을 설명할 뿐 미래 수익을 보장하지 않습니다.
- 수수료, 세금, 배당금, 환전 비용은 현재 계산에 반영되지 않습니다.
- 자동 주문 기능이나 증권사 로그인 정보 수집 기능은 없습니다.
- 토스증권 API를 연결할 때는 공식 개발자 문서, API 이용 자격, IP 허용 목록, 호출 한도, 데이터 사용 조건을 먼저 확인해야 합니다.
