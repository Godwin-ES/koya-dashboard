import streamlit as st


def inject_theme() -> None:
    """Apply the dashboard's restrained operations-product visual system."""

    st.markdown(
        """
        <style>
        :root {
            --canvas: #f3f6f8;
            --surface: #ffffff;
            --surface-soft: #f8fafb;
            --ink: #142a38;
            --muted: #627582;
            --border: #dce5e9;
            --accent: #087f78;
            --accent-soft: #e5f5f2;
            --navy: #17384b;
            --success: #197552;
            --success-soft: #e9f6ef;
            --warning: #a96713;
            --warning-soft: #fff5df;
            --danger: #b6403b;
            --danger-soft: #fff0ef;
            --shadow: 0 1px 2px rgba(20, 42, 56, .04), 0 8px 24px rgba(20, 42, 56, .045);
        }

        html, body, [class*="css"] {
            font-family: Inter, ui-sans-serif, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
            color: var(--ink);
        }

        .stApp { background: var(--canvas); }
        [data-testid="stHeader"] { background: rgba(243, 246, 248, .88); }
        [data-testid="stToolbar"] { right: 1rem; }
        [data-testid="stSidebar"] {
            background: #102c3c;
            border-right: 0;
        }
        [data-testid="stSidebar"] { color: #edf5f6; }
        [data-testid="stSidebar"] p,
        [data-testid="stSidebar"] label,
        [data-testid="stSidebar"] [data-testid="stCaptionContainer"] { color: #d4e1e6; }
        [data-testid="stSidebar"] [data-baseweb="select"] > div,
        [data-testid="stSidebar"] [data-baseweb="input"] > div {
            background: #17394b;
            border-color: #426170;
        }
        [data-testid="stSidebar"] [data-baseweb="select"] *,
        [data-testid="stSidebar"] [data-baseweb="input"] * { color: #edf5f6 !important; }
        [data-testid="stSidebar"] [data-testid="stExpander"] {
            background: rgba(255,255,255,.035); border-color: #3a5968;
        }
        [data-testid="stSidebar"] [data-testid="stExpander"] summary * { color: #d4e1e6 !important; }
        [data-testid="stSidebar"] .stButton > button {
            min-height: 2.9rem;
            font-weight: 700;
            border-radius: .65rem;
            box-shadow: none;
        }
        [data-testid="stSidebar"] .stButton > button[kind="primary"] {
            color: white;
            background: #0b948a;
            border-color: #0b948a;
        }
        [data-testid="stSidebar"] hr { border-color: #365464; }

        .block-container {
            max-width: 1480px;
            padding-top: 2rem;
            padding-bottom: 3.5rem;
        }

        h1, h2, h3 { color: var(--ink); letter-spacing: -.025em; }
        h1 { font-size: clamp(1.8rem, 3vw, 2.55rem) !important; }
        h2 { font-size: 1.35rem !important; }
        h3 { font-size: 1rem !important; }

        [data-testid="stTabs"] [role="tablist"] {
            gap: .25rem;
            padding: .3rem;
            border: 1px solid var(--border);
            border-radius: .8rem;
            background: var(--surface);
            box-shadow: 0 1px 2px rgba(20, 42, 56, .03);
        }
        [data-testid="stTabs"] [data-testid="stTab"] {
            height: 2.65rem;
            padding: 0 1rem;
            border-radius: .58rem;
            color: var(--muted);
            font-weight: 650;
        }
        [data-testid="stTabs"] [data-testid="stTab"][aria-selected="true"] {
            color: var(--navy);
            background: #edf3f5;
        }
        [data-testid="stTabs"] [data-baseweb="tab-highlight"] { display: none; }

        .koya-brand {
            display: flex; align-items: center; gap: .7rem;
            padding: .35rem 0 1.15rem;
        }
        .koya-mark {
            width: 2rem; height: 2rem; border-radius: .55rem;
            display: grid; place-items: center; color: white;
            background: #0b948a; font-weight: 850; letter-spacing: -.04em;
        }
        .koya-brand strong { display: block; font-size: 1rem; color: #fff; }
        .koya-brand span { display: block; color: #a9bdc7; font-size: .76rem; margin-top: .05rem; }
        .sidebar-kicker {
            color: #93aeba !important; text-transform: uppercase;
            font-size: .68rem; letter-spacing: .13em; font-weight: 800;
            margin: .35rem 0 .4rem;
        }
        .sidebar-note {
            color: #b7c8cf !important; font-size: .78rem; line-height: 1.45;
        }
        .sidebar-current {
            padding: .85rem; margin: .65rem 0 .25rem; border-radius: .65rem;
            border: 1px solid #3a5968; background: rgba(255,255,255,.035);
        }
        .sidebar-current strong { color: white; font-size: .86rem; }
        .sidebar-current span { color: #b7c8cf; font-size: .76rem; }

        .report-header {
            display: flex; align-items: flex-start; justify-content: space-between;
            gap: 1.5rem; margin-bottom: 1.15rem;
        }
        .eyebrow {
            color: var(--accent); text-transform: uppercase; letter-spacing: .12em;
            font-size: .69rem; font-weight: 800; margin-bottom: .38rem;
        }
        .report-title { margin: 0; font-size: clamp(1.8rem, 3vw, 2.55rem); line-height: 1.08; }
        .report-subtitle { color: var(--muted); margin-top: .5rem; font-size: .92rem; }
        .report-meta { text-align: right; min-width: 10rem; }
        .report-meta .updated { color: var(--muted); font-size: .76rem; margin-top: .45rem; }

        .status-badge {
            display: inline-flex; align-items: center; gap: .42rem;
            padding: .38rem .65rem; border-radius: 999px;
            font-size: .72rem; font-weight: 800; text-transform: uppercase;
            letter-spacing: .055em; border: 1px solid transparent;
        }
        .status-badge::before { content: ""; width: .42rem; height: .42rem; border-radius: 50%; background: currentColor; }
        .status-completed, .status-success, .status-ok { color: var(--success); background: var(--success-soft); border-color: #cfe9db; }
        .status-partial, .status-warning { color: var(--warning); background: var(--warning-soft); border-color: #f0dfb8; }
        .status-error, .status-failed { color: var(--danger); background: var(--danger-soft); border-color: #f0d0cd; }
        .status-unknown, .status-processing { color: #587080; background: #edf2f4; border-color: #dce5e9; }
        [data-testid="stSidebar"] .status-completed,
        [data-testid="stSidebar"] .status-success,
        [data-testid="stSidebar"] .status-ok { color: var(--success) !important; }
        [data-testid="stSidebar"] .status-partial,
        [data-testid="stSidebar"] .status-warning { color: var(--warning) !important; }

        .health-grid, .metric-grid {
            display: grid; gap: .8rem; margin: .7rem 0 1.35rem;
        }
        .health-grid { grid-template-columns: repeat(4, minmax(0, 1fr)); }
        .metric-grid { grid-template-columns: repeat(4, minmax(0, 1fr)); }
        .health-card, .metric-card, .content-card {
            background: var(--surface); border: 1px solid var(--border);
            border-radius: .82rem; box-shadow: var(--shadow);
        }
        .health-card { padding: .85rem 1rem; min-height: 5.25rem; }
        .health-top { display: flex; align-items: center; justify-content: space-between; gap: .5rem; }
        .health-label { color: var(--muted); font-size: .76rem; font-weight: 700; }
        .health-value { color: var(--ink); font-size: .96rem; font-weight: 780; margin-top: .55rem; }
        .health-detail { color: var(--muted); font-size: .7rem; margin-top: .13rem; }

        .metric-card { padding: 1rem 1rem .9rem; min-height: 8.2rem; position: relative; overflow: hidden; }
        .metric-card.warning::before {
            content: ""; position: absolute; top: 0; left: 0; right: 0; height: 3px; background: #d99a34;
        }
        .metric-label { color: var(--muted); font-size: .76rem; font-weight: 700; line-height: 1.3; min-height: 2em; }
        .metric-value { color: var(--navy); font-size: 1.62rem; line-height: 1.1; font-weight: 760; letter-spacing: -.035em; margin: .55rem 0 .45rem; }
        .metric-foot { color: var(--muted); font-size: .7rem; line-height: 1.35; }
        .metric-delta { color: #435d6c; font-weight: 750; }
        .metric-prior { color: #81919a; }
        .metric-note { display: inline-block; color: var(--warning); font-weight: 750; margin-top: .25rem; }

        .section-heading { margin: 1.35rem 0 .75rem; }
        .section-heading h2 { margin: 0 0 .28rem; }
        .section-heading p { margin: 0; color: var(--muted); font-size: .86rem; max-width: 58rem; }
        .content-card { padding: 1.1rem 1.2rem; margin-bottom: .8rem; }
        .content-card h3 { margin: 0 0 .55rem; }
        .content-card p { margin: 0; color: #344f5d; line-height: 1.62; font-size: .9rem; }
        .summary-card { border-left: 4px solid var(--accent); padding: 1.25rem 1.35rem; }
        .summary-card p { font-size: .98rem; color: #263f4d; }
        .card-meta { color: var(--muted); font-size: .72rem; margin-top: .72rem; line-height: 1.45; }
        .item-card { min-height: 8rem; }
        .item-head { display: flex; justify-content: space-between; gap: 1rem; margin-bottom: .6rem; }
        .item-area { color: var(--accent); text-transform: uppercase; letter-spacing: .08em; font-size: .67rem; font-weight: 850; }
        .severity { font-size: .67rem; text-transform: uppercase; font-weight: 850; letter-spacing: .05em; }
        .severity-high { color: var(--danger); }
        .severity-medium { color: var(--warning); }
        .severity-low { color: var(--success); }
        .action-number { color: #8ba0aa; font-size: .72rem; font-weight: 800; }
        .trust-note { color: var(--muted); font-size: .74rem; margin: -.2rem 0 1rem; }

        .callout { border-radius: .72rem; padding: .85rem 1rem; margin: .75rem 0 1rem; border: 1px solid; font-size: .82rem; line-height: 1.5; }
        .callout strong { display: block; margin-bottom: .16rem; }
        .callout-info { color: #315a6d; background: #edf6f8; border-color: #cee5ea; }
        .callout-warning { color: #765018; background: var(--warning-soft); border-color: #efddba; }
        .callout-error { color: #873834; background: var(--danger-soft); border-color: #efcfcc; }
        .callout-success { color: #266348; background: var(--success-soft); border-color: #cee7da; }

        [data-testid="stDataFrame"] { border: 1px solid var(--border); border-radius: .75rem; overflow: hidden; }
        [data-testid="stExpander"] { background: var(--surface); border-color: var(--border); border-radius: .75rem; }
        .stAlert { border-radius: .72rem; }

        @media (max-width: 1050px) {
            .metric-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
            .health-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
        }
        @media (max-width: 700px) {
            .block-container { padding-top: 1.2rem; }
            .report-header { display: block; }
            .report-meta { text-align: left; margin-top: .8rem; }
            .metric-grid, .health-grid { grid-template-columns: 1fr; }
            .metric-card { min-height: 0; }
            [data-testid="stTabs"] [role="tablist"] { overflow-x: auto; }
            [data-testid="stTabs"] [data-testid="stTab"] { padding: 0 .75rem; white-space: nowrap; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
