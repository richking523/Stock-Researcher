import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import date, timedelta

st.set_page_config(page_title="AI Stock Researcher", page_icon="📊", layout="wide")
st.title("📊 AI Stock Researcher")
st.caption("국내·미국 주식 분석용 1단계 데이터 대시보드 · 자동 주문 기능 없음")

st.warning(
    "학습·연구용 도구입니다. 이 버전은 토스증권 공식 API가 아니라 Yahoo Finance 데이터 소스를 사용합니다. "
    "데이터 지연·누락·오류가 있을 수 있으며, 투자 판단의 유일한 근거로 사용하지 마세요."
)

DEFAULTS = ["005930.KS", "000660.KS", "NVDA", "MSFT", "AAPL"]
symbols_text = st.text_input(
    "종목 코드 (쉼표로 구분)",
    value=", ".join(DEFAULTS),
    help="한국 예: 005930.KS(삼성전자), 000660.KS(SK하이닉스) / 미국 예: NVDA, MSFT, AAPL"
)
period = st.selectbox("분석 기간", ["6mo", "1y", "2y", "5y"], index=1)
run = st.button("데이터 불러오기 및 분석", type="primary")

def calculate_metrics(hist: pd.DataFrame) -> dict:
    close = hist["Close"].dropna()
    daily_returns = close.pct_change().dropna()
    if close.empty:
        return {}
    total_return = (close.iloc[-1] / close.iloc[0] - 1) * 100
    vol = daily_returns.std() * np.sqrt(252) * 100 if len(daily_returns) > 1 else np.nan
    rolling_peak = close.cummax()
    drawdown = (close / rolling_peak - 1) * 100
    ma20 = close.rolling(20).mean().iloc[-1] if len(close) >= 20 else np.nan
    ma50 = close.rolling(50).mean().iloc[-1] if len(close) >= 50 else np.nan
    return {
        "최근 종가": float(close.iloc[-1]),
        "기간 수익률(%)": float(total_return),
        "연환산 변동성(%)": float(vol) if pd.notna(vol) else np.nan,
        "최대 낙폭(%)": float(drawdown.min()),
        "20일 이동평균": float(ma20) if pd.notna(ma20) else np.nan,
        "50일 이동평균": float(ma50) if pd.notna(ma50) else np.nan,
        "데이터 시작일": close.index[0].date().isoformat(),
        "데이터 기준일": close.index[-1].date().isoformat(),
    }

if run:
    symbols = list(dict.fromkeys(s.strip().upper() for s in symbols_text.split(",") if s.strip()))
    if not symbols:
        st.error("종목 코드를 하나 이상 입력하세요.")
        st.stop()

    rows = []
    tabs = st.tabs(symbols)
    for symbol, tab in zip(symbols, tabs):
        with tab:
            with st.spinner(f"{symbol} 데이터 불러오는 중..."):
                try:
                    ticker = yf.Ticker(symbol)
                    hist = ticker.history(period=period, auto_adjust=True)
                    if hist.empty or "Close" not in hist.columns:
                        st.error("데이터가 없어요. 종목 코드를 확인하거나 잠시 후 다시 시도하세요.")
                        continue
                    metrics = calculate_metrics(hist)
                    info = {}
                    try:
                        info = ticker.get_info()
                    except Exception:
                        pass
                    company_name = info.get("shortName") or info.get("longName") or symbol
                    st.subheader(f"{company_name} ({symbol})")
                    c1, c2, c3, c4 = st.columns(4)
                    c1.metric("최근 종가", f'{metrics["최근 종가"]:,.2f}')
                    c2.metric("기간 수익률", f'{metrics["기간 수익률(%)"]:.2f}%')
                    c3.metric("연환산 변동성", f'{metrics["연환산 변동성(%)"]:.2f}%' if pd.notna(metrics["연환산 변동성(%)"]) else "N/A")
                    c4.metric("최대 낙폭", f'{metrics["최대 낙폭(%)"]:.2f}%')
                    chart = hist[["Close"]].rename(columns={"Close": "종가"})
                    st.line_chart(chart)
                    st.write("**이동평균 및 데이터 기간**")
                    st.json({
                        "20일 이동평균": round(metrics["20일 이동평균"], 3) if pd.notna(metrics["20일 이동평균"]) else None,
                        "50일 이동평균": round(metrics["50일 이동평균"], 3) if pd.notna(metrics["50일 이동평균"]) else None,
                        "데이터 시작일": metrics["데이터 시작일"],
                        "데이터 기준일": metrics["데이터 기준일"],
                    })
                    st.caption("수익률은 선택 기간의 첫 종가 대비 마지막 종가입니다. 수수료·세금·환전 비용은 반영하지 않습니다.")
                    rows.append({"종목": symbol, "기업명": company_name, **metrics})
                except Exception as e:
                    st.error(f"불러오기에 실패했습니다: {e}")
    if rows:
        st.subheader("종목 비교")
        comparison = pd.DataFrame(rows).set_index("종목")
        st.dataframe(comparison, use_container_width=True)
        st.download_button(
            "분석 결과 CSV 다운로드",
            data=comparison.to_csv(index=True).encode("utf-8-sig"),
            file_name=f"stock_analysis_{date.today().isoformat()}.csv",
            mime="text/csv",
        )

st.divider()
st.subheader("지표 해석")
st.markdown(
    "- **기간 수익률**: 선택한 기간의 첫 종가에서 마지막 종가까지의 가격 변화율입니다.\n"
    "- **연환산 변동성**: 일별 수익률의 표준편차를 연간 기준으로 환산한 값입니다. 높을수록 가격 변동이 컸습니다.\n"
    "- **최대 낙폭**: 기간 중 이전 최고 종가 대비 하락폭 중 가장 큰 값입니다.\n"
    "- **이동평균**: 최근 가격 흐름을 단순화해 보여주는 지표이며, 매수·매도 신호를 보장하지 않습니다."
)
st.caption("다음 단계에서는 토스증권 Open API의 이용 자격·종목 코드·호출 한도를 확인한 뒤 공식 시세 데이터 어댑터를 별도로 추가합니다.")
