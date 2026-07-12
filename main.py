
# -*- coding: utf-8 -*-
"""
RNA 치료제 탐구 웹앱
------------------------------------------------
고등학생 세특(생명과학) 탐구 과정을 한눈에 볼 수 있도록 정리한 Streamlit 앱.
탐구 흐름:
 1. RNA 치료제의 작동 원리(전사/번역 단계별) 조사
 2. CRISPR gRNA 오프타겟 문제 -> RNA 치료제 오프타겟 가능성에 대한 착안
 3. 나침반: 근접이웃모델(Nearest-Neighbor) + 볼츠만 분포/자유에너지로
    오프타겟 확률을 정량화하려던 시도 (한계에 부딪혀 중단)
 4. 2026년 IBS·서울대 공동연구(아고넛-샤페론 메커니즘, Nature)와의 연결
"""

import math
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(
    page_title="RNA 치료제 탐구 웹앱",
    page_icon="🧬",
    layout="wide",
)

# ----------------------------------------------------------------------
# 공통 스타일
# ----------------------------------------------------------------------
st.markdown(
    """
    <style>
    .step-box {
        background-color: #f5f7fb;
        border-left: 6px solid #4C6FFF;
        border-radius: 10px;
        padding: 14px 18px;
        margin-bottom: 10px;
    }
    .flow-box {
        background-color: #ffffff;
        border: 2px solid #4C6FFF;
        border-radius: 12px;
        padding: 10px 8px;
        text-align: center;
        font-weight: 600;
        font-size: 0.85rem;
        min-height: 78px;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .flow-arrow {
        text-align: center;
        font-size: 1.4rem;
        color: #4C6FFF;
        padding-top: 22px;
    }
    .tag-aso {background-color:#FFE8CC; border-radius:6px; padding:2px 6px; font-size:0.75rem;}
    .tag-sirna {background-color:#D3F9D8; border-radius:6px; padding:2px 6px; font-size:0.75rem;}
    .tag-mrna {background-color:#D0EBFF; border-radius:6px; padding:2px 6px; font-size:0.75rem;}
    .caption-small {color:#666; font-size:0.85rem;}
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("🧬 RNA 치료제 탐구 웹앱")
st.caption("전사·번역 단계별 RNA 치료제 작동 원리부터, CRISPR 오프타겟 문제, 정량적 예측 시도, 최신 연구(2026)까지의 탐구 과정을 한눈에 정리했습니다.")

tabs = st.tabs([
    "🗺️ 탐구 개요",
    "🔬 RNA 치료제 작동 원리",
    "⚠️ 오프타겟 문제 비교",
    "📐 오프타겟 확률 예측 시도",
    "🧫 최신 연구 연결 (2026)",
    "📝 결론",
])

# ========================================================================
# TAB 0. 탐구 개요
# ========================================================================
with tabs[0]:
    st.subheader("탐구 흐름 한눈에 보기")

    steps = [
        ("① RNA 치료제 조사",
         "RNA 치료제를 조사하며, 전사(transcription) 및 번역(translation)의 각 단계에서 "
         "RNA 치료제가 구체적으로 어떤 방식으로 작동하는지, 그리고 실제로 얼마나 많은 연구·개발이 "
         "이루어지고 있는지를 알아봄."),
        ("② CRISPR 오프타겟 문제와의 연결",
         "CRISPR 유전자가위를 조사하던 중 gRNA의 오프타겟(off-target) 문제를 알게 되었고, "
         "'RNA 치료제에도 비슷한 오프타겟 문제가 발생할 수 있지 않을까?'라는 의문을 갖게 됨."),
        ("③ 오프타겟을 수식으로 예측해보려던 시도",
         "오프타겟 발생 가능성을 수학·화학적으로 분석하기 위해 근접이웃모델(Nearest-Neighbor model), "
         "볼츠만 분포식과 자유에너지 개념을 이용해 오프타겟 확률을 계산해보려 했으나, "
         "실제 계산은 고려해야 할 변수가 너무 많아 지나치게 복잡해져 중단함."),
        ("④ 최신 연구와의 재연결",
         "국내 연구진이 유전자 발현을 조절하는 핵심 단백질(아고넛, Argonaute)의 활성화 원리를 "
         "세계 최초로 밝혀냈다는 기사를 접하고, 이를 앞선 탐구 내용과 연결할 수 없을지 고민하며 "
         "샤페론(chaperone)과 siRNA의 관계를 추가로 조사함."),
    ]
    for title, desc in steps:
        st.markdown(f"<div class='step-box'><b>{title}</b><br>{desc}</div>", unsafe_allow_html=True)

    st.info(
        "💡 이 탐구는 '알게 된 개념 → 스스로 의문을 확장 → 정량화 시도 → 한계 인식 → 최신 연구로 재해석'"
        "이라는 흐름을 가지고 있어요. 각 탭에서 단계별 내용을 자세히 확인할 수 있습니다."
    )

# ========================================================================
# TAB 1. RNA 치료제 작동 원리
# ========================================================================
with tabs[1]:
    st.subheader("전사·번역 단계별 RNA 치료제 작동 원리")

    st.markdown("##### 중심원리(central dogma) 위에서, RNA 치료제는 어느 지점을 공략할까?")
    flow_labels = [
        "DNA",
        "전사\n(Transcription)",
        "1차 전사체\n(pre-mRNA)",
        "스플라이싱\n(Splicing)",
        "성숙 mRNA",
        "번역\n(Translation)",
        "단백질",
    ]
    cols = st.columns(len(flow_labels) * 2 - 1)
    for i, label in enumerate(flow_labels):
        col_idx = i * 2
        with cols[col_idx]:
            st.markdown(f"<div class='flow-box'>{label}</div>", unsafe_allow_html=True)
        if col_idx + 1 < len(cols):
            with cols[col_idx + 1]:
                st.markdown("<div class='flow-arrow'>→</div>", unsafe_allow_html=True)

    st.markdown(" ")
    intervention = pd.DataFrame({
        "작용 지점": ["스플라이싱 조절", "성숙 mRNA 분해", "성숙 mRNA 번역 억제(RISC)", "번역(직접 발현)", "단백질(직접 결합)"],
        "RNA 치료제 종류": ["Splice-switching ASO", "Gapmer ASO (RNase H 매개)", "siRNA", "mRNA 치료제/백신", "압타머(Aptamer)"],
    })
    st.dataframe(intervention, width='stretch', hide_index=True)

    st.markdown("---")
    st.markdown("##### RNA 치료제 종류별 작동 메커니즘 정리")

    drug_table = pd.DataFrame([
        {"종류": "Gapmer ASO", "작용 단계": "전사 후 (mRNA 분해)",
         "메커니즘": "표적 mRNA에 상보결합 후, RNase H 효소가 DNA-RNA 이중나선을 인식해 mRNA를 절단",
         "대표 약물": "Mipomersen(2013), Inotersen(2018)"},
        {"종류": "Splice-switching ASO", "작용 단계": "전사 후 가공(스플라이싱)",
         "메커니즘": "pre-mRNA의 스플라이싱 부위에 결합해 특정 엑손의 포함/제외를 유도",
         "대표 약물": "Nusinersen(2016), Eteplirsen(2016)"},
        {"종류": "siRNA", "작용 단계": "번역 전(RISC 매개 mRNA 절단)",
         "메커니즘": "RISC(Argonaute 포함 복합체)에 로딩되어 상보적인 mRNA를 서열 특이적으로 절단",
         "대표 약물": "Patisiran(2018), Inclisiran(2021)"},
        {"종류": "mRNA 치료제/백신", "작용 단계": "번역",
         "메커니즘": "외래 mRNA를 세포질로 전달해 리보솜이 직접 번역, 항원·치료 단백질 생산",
         "대표 약물": "Comirnaty, Spikevax(2020~)"},
        {"종류": "압타머", "작용 단계": "번역 후(단백질 직접 결합)",
         "메커니즘": "RNA가 접힌 3차구조로 표적 단백질에 직접 결합해 기능을 억제",
         "대표 약물": "Pegaptanib(2004)"},
    ])
    st.dataframe(drug_table, width='stretch', hide_index=True)

    st.markdown("---")
    st.markdown("##### 연구·개발은 얼마나 이루어지고 있을까? (승인 현황)")

    approvals = pd.DataFrame([
        {"연도": 1998, "종류": "ASO", "약물": "Fomivirsen"},
        {"연도": 2004, "종류": "압타머", "약물": "Pegaptanib"},
        {"연도": 2013, "종류": "ASO", "약물": "Mipomersen"},
        {"연도": 2016, "종류": "ASO", "약물": "Eteplirsen"},
        {"연도": 2016, "종류": "ASO", "약물": "Nusinersen"},
        {"연도": 2018, "종류": "siRNA", "약물": "Patisiran"},
        {"연도": 2018, "종류": "ASO", "약물": "Inotersen"},
        {"연도": 2019, "종류": "siRNA", "약물": "Givosiran"},
        {"연도": 2019, "종류": "ASO", "약물": "Golodirsen"},
        {"연도": 2020, "종류": "siRNA", "약물": "Lumasiran"},
        {"연도": 2020, "종류": "ASO", "약물": "Viltolarsen"},
        {"연도": 2020, "종류": "mRNA", "약물": "Comirnaty/Spikevax(긴급승인)"},
        {"연도": 2021, "종류": "siRNA", "약물": "Inclisiran"},
        {"연도": 2021, "종류": "ASO", "약물": "Casimersen"},
        {"연도": 2022, "종류": "siRNA", "약물": "Vutrisiran"},
        {"연도": 2023, "종류": "siRNA", "약물": "Nedosiran"},
        {"연도": 2023, "종류": "ASO", "약물": "Tofersen"},
    ])
    approvals_sorted = approvals.sort_values("연도")
    approvals_sorted["누적 승인 수"] = range(1, len(approvals_sorted) + 1)

    fig = px.bar(
        approvals,
        x="연도", color="종류", barmode="stack",
        title="연도별 FDA 승인 RNA(핵산) 치료제 (대표 사례, 종류별)",
        hover_data=["약물"],
    )
    fig.update_layout(yaxis_title="승인 건수", xaxis_title="연도")
    st.plotly_chart(fig, width='stretch')

    st.markdown(
        "<p class='caption-small'>※ 표에는 대표적인 승인 사례만 나타냈습니다. 2026년 발표된 한 학술 리뷰에 따르면, "
        "지금까지 FDA가 승인한 핵산 기반(올리고뉴클레오타이드) 치료제는 ASO 15건, siRNA 8건을 포함해 총 30건에 이르며, "
        "현재 300건이 넘는 ASO·siRNA 임상 개발 프로그램이 진행 중이라고 합니다.</p>",
        unsafe_allow_html=True,
    )

# ========================================================================
# TAB 2. 오프타겟 문제 비교
# ========================================================================
with tabs[2]:
    st.subheader("CRISPR gRNA 오프타겟 → RNA 치료제도 같은 문제가 있을까?")

    st.markdown(
        "CRISPR-Cas9의 gRNA는 PAM 서열에 인접한 부위(seed 부위)의 불일치에는 민감하지만, "
        "PAM에서 먼 부위의 불일치는 상대적으로 잘 허용하는 경향이 있어요. 그 결과 의도하지 않은 "
        "유전체 부위를 절단하는 오프타겟 효과가 발생할 수 있습니다.\n\n"
        "siRNA 역시 비슷한 구조적 이유로 오프타겟 문제가 생길 수 있어요. siRNA의 2~8번째 염기(시드 서열)가 "
        "마치 내인성 miRNA처럼 작동하면서, 완전히 다른 유전자라도 3'UTR에 시드 서열과 상보적인 부분이 있으면 "
        "그 mRNA의 번역을 의도치 않게 억제할 수 있습니다."
    )

    compare = pd.DataFrame([
        {"항목": "인식 서열 길이", "CRISPR-Cas9 gRNA": "약 20nt (PAM 인접 필요)", "siRNA": "약 19~21nt (그중 2~8nt 시드 영역이 핵심)"},
        {"항목": "오프타겟 핵심 원인", "CRISPR-Cas9 gRNA": "PAM 근접부 불일치에 민감, 원위부 불일치는 허용", "siRNA": "시드 서열이 miRNA처럼 다수 전사체의 3'UTR과 부분 상보결합"},
        {"항목": "결과", "CRISPR-Cas9 gRNA": "의도치 않은 유전체 절단 → 영구적 돌연변이 가능", "siRNA": "의도치 않은 mRNA 번역 억제 → 대개 일시적(유전체 변형 아님)"},
        {"항목": "대표 완화 전략", "CRISPR-Cas9 gRNA": "고정밀 Cas9 변이체, 최적 gRNA 설계 알고리즘, 니커(nickase) 전략", "siRNA": "시드 영역 화학적 변형(2'-O-메틸화 등), 서열 설계 최적화"},
    ])
    st.dataframe(compare, width='stretch', hide_index=True)

    st.success(
        "🔎 **탐구 포인트**: '유전체를 자르는 CRISPR'과 'mRNA를 억제하는 siRNA'는 표적이 다르지만, "
        "둘 다 '짧은 상보서열 인식'이라는 원리를 공유하기 때문에 오프타겟이라는 공통된 약점을 가진다는 점에서 "
        "유비적으로 연결할 수 있었어요."
    )

# ========================================================================
# TAB 3. 오프타겟 확률 예측 시도 (근접이웃모델 + 볼츠만분포)
# ========================================================================
with tabs[3]:
    st.subheader("오프타겟 결합을 열역학적으로 예측해볼 수 있을까?")

    st.markdown(
        "RNA 이중나선의 안정성은 인접한 두 염기쌍이 서로 어떻게 쌓이는지에 따라 결정되는데, 이를 "
        "**근접이웃모델(Nearest-Neighbor model)**로 정량화할 수 있어요. 각 인접 염기쌍 조합(NN step)마다 "
        "고유한 자유에너지(ΔG, kcal/mol) 값이 있고, 이를 모두 더하면 전체 이중나선의 안정성을 추정할 수 있습니다. "
        "값이 더 음수(더 낮음)일수록 결합이 더 안정적이라는 뜻이에요."
    )

    nn_table = pd.DataFrame([
        {"NN step (5'→3')": "AA / UU", "ΔG°37 (kcal/mol)": -0.93},
        {"NN step (5'→3')": "AU", "ΔG°37 (kcal/mol)": -1.10},
        {"NN step (5'→3')": "UA", "ΔG°37 (kcal/mol)": -1.33},
        {"NN step (5'→3')": "CU / AG", "ΔG°37 (kcal/mol)": -2.08},
        {"NN step (5'→3')": "CA / UG", "ΔG°37 (kcal/mol)": -2.11},
        {"NN step (5'→3')": "GU / AC", "ΔG°37 (kcal/mol)": -2.24},
        {"NN step (5'→3')": "GA / UC", "ΔG°37 (kcal/mol)": -2.35},
        {"NN step (5'→3')": "CG", "ΔG°37 (kcal/mol)": -2.36},
        {"NN step (5'→3')": "GG / CC", "ΔG°37 (kcal/mol)": -3.26},
        {"NN step (5'→3')": "GC", "ΔG°37 (kcal/mol)": -3.42},
    ])
    st.dataframe(nn_table, width='stretch', hide_index=True)
    st.caption("Turner 그룹의 RNA 이중나선 근접이웃 파라미터(간략화된 버전)를 사용했습니다. 실제 파라미터에는 말단 효과, 내부 미스매치, 벌지(bulge) 등이 별도로 존재합니다.")

    st.markdown("---")
    st.markdown("##### 직접 계산해보기: 완전상보 결합 vs 미스매치(오프타겟 후보) 결합")

    NN = {
        "AA": -0.93, "UU": -0.93, "AU": -1.10, "UA": -1.33,
        "CU": -2.08, "AG": -2.08, "CA": -2.11, "UG": -2.11,
        "GU": -2.24, "AC": -2.24, "GA": -2.35, "UC": -2.35,
        "CG": -2.36, "GG": -3.26, "CC": -3.26, "GC": -3.42,
    }
    INIT = 3.61
    AU_END_PENALTY = 0.45
    R_KCAL = 1.987e-3  # kcal / (mol*K)
    T_KELVIN = 310.15  # 37C, 체온 기준

    def clean_seq(s: str) -> str:
        return "".join(ch for ch in s.strip().upper().replace("T", "U") if ch in "AUGC")

    def nn_deltaG(seq: str) -> float:
        dG = INIT
        for base in (seq[0], seq[-1]):
            if base in ("A", "U"):
                dG += AU_END_PENALTY
        for i in range(len(seq) - 1):
            dG += NN[seq[i:i + 2]]
        return dG

    def boltzmann_probs(dGs, T=T_KELVIN):
        RT = R_KCAL * T
        weights = [math.exp(-g / RT) for g in dGs]
        total = sum(weights)
        return [w / total for w in weights]

    col_a, col_b = st.columns(2)
    with col_a:
        raw_seq = st.text_input("표적(가이드) 서열 입력 (6~12nt, A/U/G/C)", value="GCAGUCAU")
    with col_b:
        seq = clean_seq(raw_seq)
        max_pos = max(len(seq) - 1, 1)
        mismatch_pos = st.slider("미스매치 위치 (0부터 시작)", 0, max_pos, min(3, max_pos))

    if len(seq) < 4:
        st.warning("4nt 이상의 서열을 입력해주세요. (A, U, G, C만 사용)")
    else:
        perfect_dG = nn_deltaG(seq)

        # 단순화한 위치별 미스매치 패널티: 중앙에 가까울수록 더 크게 불안정화된다고 가정
        center = (len(seq) - 1) / 2
        position_weight = 1 - (abs(mismatch_pos - center) / (center + 1e-9)) * 0.5
        base_penalty = 2.4  # kcal/mol, 문헌에서 보고되는 대략적 미스매치 평균 불안정화 범위(1~3) 참고
        mismatch_dG = perfect_dG + base_penalty * position_weight

        c1, c2, c3 = st.columns(3)
        c1.metric("완전상보 결합 ΔG", f"{perfect_dG:.2f} kcal/mol")
        c2.metric("미스매치 결합 ΔG (추정)", f"{mismatch_dG:.2f} kcal/mol", delta=f"+{mismatch_dG - perfect_dG:.2f}")
        probs = boltzmann_probs([perfect_dG, mismatch_dG])
        c3.metric("미스매치 상대적 결합확률", f"{probs[1]*100:.2f} %")

        bar_fig = go.Figure(data=[
            go.Bar(name="ΔG (kcal/mol)", x=["완전상보(표적)", "미스매치(오프타겟 후보)"],
                   y=[perfect_dG, mismatch_dG], marker_color=["#4C6FFF", "#FF6B6B"])
        ])
        bar_fig.update_layout(title="자유에너지(ΔG) 비교 — 낮을수록 안정적", yaxis_title="ΔG (kcal/mol)")
        st.plotly_chart(bar_fig, width='stretch')

        pie_fig = go.Figure(data=[go.Pie(
            labels=["완전상보(표적)", "미스매치(오프타겟 후보)"],
            values=probs, hole=0.45,
            marker_colors=["#4C6FFF", "#FF6B6B"],
        )])
        pie_fig.update_layout(title="볼츠만 분포 기반 상대적 결합확률 (37°C 기준)")
        st.plotly_chart(pie_fig, width='stretch')

    st.markdown("---")
    st.warning(
        "⚠️ **이 계산이 '단순화한 교육용 모델'인 이유** — 실제로 오프타겟 확률을 제대로 예측하려면 다음을 "
        "모두 고려해야 해서 계산이 급격히 복잡해집니다.\n\n"
        "- 전사체 전체(수만 개 유전자)를 대상으로 후보 상보 서열을 전부 탐색해야 함\n"
        "- mRNA의 2차구조에 따라 실제 결합 가능 여부(접근성)가 달라짐\n"
        "- 미스매치는 위치·종류(어떤 염기끼리 잘못 짝지어졌는지)에 따라 서로 다른 고유 파라미터가 필요함\n"
        "- 열역학적 안정성뿐 아니라 RISC 로딩 효율 같은 반응속도론적(kinetic) 요인도 함께 작용함\n\n"
        "→ 이런 이유로, 이 탐구에서는 근접이웃모델과 볼츠만 분포를 이용한 정량적 예측을 "
        "끝까지 정교화하기보다 **개념적으로 이해하는 선에서 정리**하기로 함."
    )

# ========================================================================
# TAB 4. 최신 연구 연결 (2026 Nature, 아고넛-샤페론)
# ========================================================================
with tabs[4]:
    st.subheader("최신 연구와의 연결: 아고넛(Argonaute) 활성화와 샤페론")

    st.markdown(
        "2026년 6월, IBS RNA 연구단(김빛내리 단장)과 서울대 생명과학부(노성훈 교수) 공동 연구팀이 "
        "유전자 발현을 조절하는 단백질 **아고넛(Argonaute)**이 활성화되는 과정을 세계 최초로 규명해 "
        "국제학술지 *Nature*에 발표했습니다."
    )

    mech_steps = [
        ("1", "샤페론이 아고넛과 결합", "샤페론 단백질이 아고넛에 결합해, miRNA가 들어갈 수 있도록 아고넛을 완전히 열린 구조로 붙잡아 둠"),
        ("2", "이중가닥 miRNA 결합", "세포 내 원래 형태인 '이중가닥' miRNA가 열린 공간에 들어와 결합함 (단일가닥이거나 miRNA가 없으면 정상 구조가 만들어지지 않음)"),
        ("3", "샤페론 이탈", "제 역할을 마친 샤페론이 아고넛에서 떨어져 나감"),
        ("4", "활성 RISC 완성", "아고넛이 유전자를 조절할 수 있는 닫힌 형태로 완성되며, 표적 mRNA를 정확히 인식·절단하는 기능을 수행"),
    ]
    mcols = st.columns(len(mech_steps))
    for col, (num, title, desc) in zip(mcols, mech_steps):
        with col:
            st.markdown(
                f"<div class='step-box' style='min-height:190px'><b>STEP {num}</b><br>"
                f"<b>{title}</b><br><span class='caption-small'>{desc}</span></div>",
                unsafe_allow_html=True,
            )

    st.markdown("##### 이 연구가 siRNA 치료제 설계와 어떻게 연결될까?")
    st.markdown(
        "- 그동안 siRNA 치료제 설계는 상당 부분 **시행착오(trial and error)**에 의존해왔는데, "
        "이번 연구는 아고넛이 miRNA(또는 siRNA)와 결합해 활성을 갖추는 과정에 **분자적·이론적 근거**를 "
        "제시했다는 의미가 있습니다.\n"
        "- 아고넛에 잘 결합하는 RNA의 구조적 특징(이중가닥 형태의 중요성 등)이 밝혀지면서, "
        "차세대 siRNA 치료제를 더 정교하게 설계해 오프타겟 부작용을 줄이고 효율을 높이는 데 활용될 수 있을 것으로 기대됩니다."
    )

    st.info(
        "🔗 **탐구 연결고리**: 앞선 탭에서 '오프타겟을 어떻게 줄일 수 있을까'를 열역학적으로 접근하려다 "
        "한계에 부딪혔는데, 이 연구는 '애초에 아고넛이 어떤 RNA와 안정적으로 결합해 활성화되는가'라는 "
        "더 근본적인 질문에 구조생물학적 답을 제시했다는 점에서, 제 탐구의 다음 방향을 시사해주었습니다."
    )

# ========================================================================
# TAB 5. 결론
# ========================================================================
with tabs[5]:
    st.subheader("탐구 정리 및 의의")
    st.markdown(
        """
        **탐구를 통해 배운 점**

        1. RNA 치료제는 중심원리(central dogma)의 여러 단계(전사 후 가공, 번역 전/중/후)에서
           각기 다른 방식으로 작동하며, 실제로 지난 5~10년 사이 승인 건수와 임상 프로그램이
           빠르게 늘어나고 있는 활발한 연구 분야임을 확인함.
        2. CRISPR gRNA의 오프타겟 문제를 통해, '짧은 상보서열 인식'이라는 공통 원리를 가진
           RNA 치료제(특히 siRNA)에도 유사한 오프타겟 가능성이 있다는 것을 유추함.
        3. 오프타겟 가능성을 근접이웃모델과 볼츠만 분포로 정량화해보려는 시도를 통해,
           단순한 열역학 모델만으로는 실제 세포 내 오프타겟 현상을 설명하기 어렵다는 한계를
           직접 체감함. (전사체 전반의 탐색, 2차구조, 반응속도론적 요인 등을 함께 고려해야 함)
        4. 위 한계를 인식한 상태에서 2026년 발표된 아고넛-샤페론 연구를 접하며,
           '정량적으로 예측하기보다, 분자 수준의 구조적 메커니즘을 규명하는 접근'이
           실제 치료제 설계에 훨씬 직접적인 기여를 할 수 있다는 것을 깨달음.

        이 탐구 과정은 하나의 정답을 찾기보다, **스스로 세운 가설(오프타겟 정량 예측)이 벽에
        부딪혔을 때 이를 인정하고, 최신 연구를 통해 관점을 넓혀가는 탐구 태도**를 보여주는
        흐름으로 정리할 수 있습니다.
        """
    )
