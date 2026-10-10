import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timezone

st.set_page_config(page_title="AI Stock Researcher", page_icon="📈", layout="wide")
st.title("📈 AI Stock Researcher")
st.caption("국내·미국 주식 분석용 · 최신 데이터 요청 + 1분마다 자동 갱신")

st.warning(
    "Yahoo Finance 데이터를 사용합니다. '최신'은 제공처에서 조회 가능한 가장 최근 데이터라는 뜻이며, "
    "실시간 시세를 보장하지 않습니다. 자동 주문 기능은 없습니다."
)

default_symbols = "005930.KS, 000660.KS, NVDA, MSFT, AAPL"
symbols_text = st.text_input(
    "종목 코드 (쉼표로 구분)",
    value=default_symbols,
    help="삼성전자 005930.KS · SK하이닉스 000660.KS · 엔비디아 NVDA"
)
refresh_on = st.toggle("1분마다 최신 데이터 자동 갱신", value=True)

if "loaded" not in st.session_state:
    st.session_state.loaded = False
if "symbols" not in st.session_state:
    st.session_state.symbols = ["005930.KS"]
if "refresh_enabled" not in st.session_state:
    st.session_state.refresh_enabled = True

if st.button("데이터 불러오기", type="primary"):
    symbols = list(dict.fromkeys(s.strip().upper() for s in symbols_text.split(",") if s.strip()))
    if not symbols:
        st.error("종목 코드를 하나 이상 입력해 주세요.")
    else:
        st.session_state.symbols = symbols
        st.session_state.refresh_enabled = refresh_on
        st.session_state.loaded = True

if st.session_state.loaded:
    st.session_state.refresh_enabled = refresh_on
    if st.session_state.refresh_enabled:
        try:
            from streamlit_autorefresh import st_autorefresh
            refresh_count = st_autorefresh(interval=60_000, limit=None, key="latest_stock_refresh")
            st.caption(f"자동 갱신 켜짐 · 60초마다 데이터 재조회 · 갱신 횟수: {refresh_count}")
        except Exception:
            st.error("자동 갱신 모듈을 불러오지 못했습니다. requirements.txt를 확인해 주세요.")

    latest_rows = []
    tabs = st.tabs(st.session_state.symbols)

    for symbol, tab in zip(st.session_state.symbols, tabs):
        with tab:
            with st.spinner(f"{symbol}의 최신 조회 가능 데이터를 불러오는 중..."):
                try:
                    ticker = yf.Ticker(symbol)
                    # 1-minute interval provides the latest available intraday points.
                    # Yahoo may restrict intraday history or return delayed/incomplete data.
                    hist = ticker.history(period="1d", interval="1m", auto_adjust=False, prepost=False)
                    mode_label = "장중 1분 데이터"
                    if hist.empty or "Close" not in hist.columns or hist["Close"].dropna().empty:
                        st.warning("1분 데이터가 없어서 일별 데이터로 다시 조회합니다. 이 경우 그래프는 장중 실시간 흐름이 아닐 수 있습니다.")
                        hist = ticker.history(period="5d", interval="5m", auto_adjust=False, prepost=False)
                        mode_label = "최근 5일의 5분 데이터"
                    if hist.empty or "Close" not in hist.columns or hist["Close"].dropna().empty:
                        st.error("데이터가 없어요. 종목 코드 또는 Yahoo Finance 데이터 제공 여부를 확인해 주세요.")
                        continue

                    close = hist["Close"].dropna()
                    last_price = float(close.iloc[-1])
                    previous = float(close.iloc[-2]) if len(close) >= 2 else last_price
                    delta = last_price - previous
                    delta_pct = (delta / previous * 100) if previous else 0.0
                    last_time = close.index[-1]
                    if getattr(last_time, "tzinfo", None) is not None:
                        try:
                            last_time_display = last_time.tz_convert("Asia/Seoul").strftime("%Y-%m-%d %H:%M:%S %Z")
                        except Exception:
                            last_time_display = last_time.strftime("%Y-%m-%d %H:%M:%S %Z")
                    else:
                        last_time_display = last_time.strftime("%Y-%m-%d %H:%M:%S")

                    company_name = symbol
                    try:
                        info = ticker.get_info()
                        company_name = info.get("shortName") or info.get("longName") or symbol
                    except Exception:
                        pass

                    st.subheader(f"{company_name} ({symbol})")
                    a, b, c = st.columns(3)
                    a.metric("가장 최근 조회 가격", f"{last_price:,.2f}", f"{delta:+,.2f} ({delta_pct:+.2f}%)")
                    b.metric("조회 데이터 구간", mode_label)
                    c.metric("마지막 데이터 시각", last_time_display)

                    st.line_chart(close.rename("가격").to_frame(), height=380)
                    st.caption(
                        "그래프는 제공처에서 반환한 가장 최근 구간의 데이터입니다. "
                        "장 마감·휴장·데이터 지연 중에는 1분마다 갱신해도 가격과 그래프가 바뀌지 않을 수 있습니다."
                    )

                    latest_rows.append({
                        "종목 코드": symbol,
                        "기업명": company_name,
                        "최근 조회 가격": last_price,
                        "직전 데이터 대비 변화": delta,
                        "직전 데이터 대비 변화율(%)": delta_pct,
                        "마지막 데이터 시각": last_time_display,
                        "데이터 구간": mode_label,
                    })
                except Exception as e:
                    st.error(f"{symbol} 데이터를 불러오지 못했습니다: {e}")

    if latest_rows:
        st.subheader("최신 조회 결과")
        st.dataframe(pd.DataFrame(latest_rows), use_container_width=True)
        csv = pd.DataFrame(latest_rows).to_csv(index=False).encode("utf-8-sig")
        st.download_button("최신 조회 결과 CSV 다운로드", csv, "latest_stock_data.csv", "text/csv")
else:
    st.info("종목 코드를 입력하고 '데이터 불러오기'를 누르면 최신 조회 가능 데이터를 표시합니다. 자동 갱신은 기본으로 켜져 있습니다.")

st.divider()
st.caption(
    "안내: 이 앱은 Yahoo Finance의 공개 데이터 조회를 사용하며 토스증권의 공식 시세 피드가 아닙니다. "
    "자동 갱신은 60초마다 재조회하는 기능이고, 실시간 시세·체결 가격을 보장하지 않습니다."
)
