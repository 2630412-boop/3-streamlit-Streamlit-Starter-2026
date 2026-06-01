import streamlit as st
import math
import random

st.title("당첨 확률 계산기")
st.write("확률을 입력하여 사건에 당첨될 확률을 알아보세요.")

if 'total_n' not in st.session_state:
    st.session_state.total_n = 0
if 'total_success' not in st.session_state:
    st.session_state.total_success = 0
if 'last_p' not in st.session_state:
    st.session_state.last_p = None

p_input = st.text_input(
    "당첨 확률 (%)", 
    value="10", 
    help="당첨 확률을 입력하세요.(0~100)"
)

n_input = st.text_input(
    "시도 횟수 (n)", 
    value="100",
    help="전체 시도할 횟수를 입력하세요."
)

k_input = st.text_input(
    "당첨 목표 횟수 (k)", 
    value="1",
    help="최소 몇 번 당첨되는 것을 목표로 하는지 입력하세요."
)

if st.session_state.last_p is not None and st.session_state.last_p != p_input:
    st.session_state.total_n = 0
    st.session_state.total_success = 0
st.session_state.last_p = p_input

col_btn1, col_btn2, col_btn3, col_btn4 = st.columns([1, 1, 1.2, 1])

with col_btn1:
    calc_btn = st.button("계산하기")

with col_btn2:
    sim_btn = st.button("시뮬레이션")

with col_btn3:
    auto_btn = st.button("당첨될 때까지 실행")

with col_btn4:
    if st.button("기록 리셋"):
        st.session_state.total_n = 0
        st.session_state.total_success = 0
        st.rerun()

try:
    p_raw = float(p_input.split("/")[0]) / float(p_input.split("/")[1]) if "/" in p_input else float(p_input)
    p = p_raw / 100
    n = int(n_input)
    k = int(k_input)

    if not (0 <= p_raw <= 100):
        st.error(f"❌ 당첨 확률은 0%에서 100% 사이여야 합니다! (입력: {p_raw}%)")
        st.stop() 
    
    if k > n:
        st.error(f"❌ 당첨 목표({k})는 시도 횟수({n})보다 클 수 없습니다.")
        st.stop()

    if calc_btn:
        def get_binom_pmf(n, k, p):
            return math.comb(n, k) * (p**k) * ((1-p)**(n-k))
        prob_none = get_binom_pmf(n, 0, p)
        prob_exact = get_binom_pmf(n, k, p)
        prob_at_least = sum(get_binom_pmf(n, i, p) for i in range(k, n + 1))
        st.subheader("📊 통계적 계산 결과")
        st.metric("한 번도 당첨되지 않을 확률 (꽝)", f"{prob_none:.4%}")
        c1, c2 = st.columns(2)
        c1.metric(f"정확히 {k}번 당첨될 확률", f"{prob_exact:.4%}")
        c2.metric(f"{k}번 이상 당첨될 확률", f"{prob_at_least:.4%}")

    if sim_btn:
        st.subheader("🎲 시뮬레이션 결과")
        current_success = 0
        results = []
        for i in range(n):
            is_success = random.random() < p
            if is_success: current_success += 1
            if len(results) < 50: results.append("✅" if is_success else "❌")
        
        st.session_state.total_n += n
        st.session_state.total_success += current_success
        
        st.write(f"**이번 시도:** {n}번 중 {current_success}번 당첨")
        st.write(f"**🔥 총 누적 기록:** {st.session_state.total_n}번 시도 중 {st.session_state.total_success}번 당첨")
        st.info(" ".join(results) + (" ..." if n > 50 else ""))
        if current_success >= k: st.balloons(); st.success("목표 달성!")
        else: st.warning("목표 달성 실패")

    if auto_btn:
        if p <= 0:
            st.error("확률이 0%면 영원히 당첨될 수 없습니다!")
        else:
            st.subheader("🚀 실시간 추적 중...")
            
            placeholder = st.empty()
            
            attempts = 0
            successes = 0
            
            while successes < k:
                attempts += 1
                if random.random() < p:
                    successes += 1
                
                if attempts % 1 == 1: 
                    with placeholder.container():
                        st.metric("현재 시도 횟수", f"{attempts}회")
                        st.write(f"현재 당첨 횟수: **{successes} / {k}**")
                
                if attempts > 1000000: break 

            st.session_state.total_n += attempts
            st.session_state.total_success += successes
            
            placeholder.empty() 
            st.metric("최종 시도 횟수", f"{attempts}번")
            st.write(f"**🔥 총 누적 기록:** {st.session_state.total_n}번 시도 중 {st.session_state.total_success}번 당첨")
            st.balloons()
            st.success(f"축하합니다! {attempts}번 만에 {k}번 당첨되었습니다.")

except (ValueError, ZeroDivisionError):
    st.error("입력값을 확인해주세요.")