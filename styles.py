# -*- coding: utf-8 -*-
"""
视觉设计系统（投行/研究报告风格，全英文，微软雅黑字体）
"""

COLOR_NAVY = "#0B1E3D"
COLOR_NAVY_LIGHT = "#16294D"
COLOR_GOLD = "#B08D57"
COLOR_GOLD_LIGHT = "#D4C0A1"
COLOR_BG = "#F7F6F3"
COLOR_TEXT = "#3D4451"
COLOR_TEXT_LIGHT = "#8B93A1"
COLOR_POSITIVE = "#4A7C6F"
COLOR_NEGATIVE = "#A0453A"

CHART_PALETTE = [
    "#0B1E3D", "#B08D57", "#4A7C6F", "#A0453A",
    "#6B7A99", "#D4C0A1", "#2C3E50", "#8B93A1",
]

FONT_FAMILY = "'Microsoft YaHei', 'Microsoft YaHei UI', -apple-system, sans-serif"


def get_plotly_template() -> dict:
    return dict(
        layout=dict(
            font=dict(family=FONT_FAMILY, color=COLOR_TEXT, size=13),
            title=dict(font=dict(family=FONT_FAMILY, color=COLOR_NAVY, size=20)),
            paper_bgcolor=COLOR_BG,
            plot_bgcolor="#FFFFFF",
            colorway=CHART_PALETTE,
            xaxis=dict(gridcolor="#E5E3DD", zerolinecolor="#E5E3DD",
                       title_font=dict(size=12, color=COLOR_TEXT_LIGHT)),
            yaxis=dict(gridcolor="#E5E3DD", zerolinecolor="#E5E3DD",
                       title_font=dict(size=12, color=COLOR_TEXT_LIGHT)),
            legend=dict(bgcolor="rgba(0,0,0,0)"),
            margin=dict(t=60, l=20, r=20, b=40),
        )
    )


def get_custom_css() -> str:
    return f"""
    <style>
        html, body, [class*="css"] {{
            font-family: {FONT_FAMILY};
            color: {COLOR_TEXT};
        }}

        .stApp {{
            background-color: {COLOR_BG};
        }}

        .ib-header {{
            background: linear-gradient(135deg, {COLOR_NAVY} 0%, {COLOR_NAVY_LIGHT} 100%);
            padding: 2.2rem 2.5rem;
            border-radius: 4px;
            margin-bottom: 1.8rem;
            border-left: 4px solid {COLOR_GOLD};
        }}
        .ib-header h1 {{
            font-family: {FONT_FAMILY};
            color: #FFFFFF;
            font-size: 2rem;
            margin: 0 0 0.4rem 0;
            font-weight: 700;
        }}
        .ib-header p {{
            color: {COLOR_GOLD_LIGHT};
            font-size: 0.95rem;
            margin: 0;
            letter-spacing: 0.03em;
        }}

        h2, h3 {{
            font-family: {FONT_FAMILY} !important;
            color: {COLOR_NAVY} !important;
            font-weight: 600 !important;
        }}

        div[data-testid="stMetric"] {{
            background-color: #FFFFFF;
            border: 1px solid #E5E3DD;
            border-top: 3px solid {COLOR_GOLD};
            border-radius: 2px;
            padding: 1rem 1.2rem;
        }}
        div[data-testid="stMetricLabel"] {{
            color: {COLOR_TEXT_LIGHT};
            font-size: 0.8rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}
        div[data-testid="stMetricValue"] {{
            color: {COLOR_NAVY};
            font-family: {FONT_FAMILY};
        }}

        hr {{
            border: none;
            border-top: 1px solid {COLOR_GOLD_LIGHT};
            margin: 1.8rem 0;
        }}

        .stDataFrame {{
            border: 1px solid #E5E3DD;
        }}

        section[data-testid="stSidebar"] {{
            background-color: {COLOR_NAVY};
        }}
        section[data-testid="stSidebar"] * {{
            color: #F7F6F3 !important;
            font-family: {FONT_FAMILY} !important;
        }}

                /* Restore icon font for Streamlit's built-in icons (sidebar collapse arrow, etc.)
           so the global YaHei font-family override doesn't turn icons into literal text */
        span[data-testid="stIconMaterial"] {{
            font-family: 'Material Symbols Rounded' !important;
        }}

        /* Fix invisible date-input text in the dark sidebar: force dark text on white
           input background, overriding the blanket white-text sidebar rule */
        section[data-testid="stSidebar"] div[data-baseweb="input"] input {{
            color: {COLOR_TEXT} !important;
            background-color: #FFFFFF !important;
        }}
        
                /* Sidebar button: match the dark navy theme with a visible gold-accent
           border, instead of Streamlit's default white button background */
        section[data-testid="stSidebar"] button {{
            background-color: {COLOR_NAVY_LIGHT} !important;
            color: #FFFFFF !important;
            border: 1px solid {COLOR_GOLD} !important;
        }}
        section[data-testid="stSidebar"] button:hover {{
            background-color: {COLOR_GOLD} !important;
            border-color: {COLOR_GOLD} !important;
            color: {COLOR_NAVY} !important;
        }}
        section[data-testid="stSidebar"] button p {{
            color: inherit !important;
        }}

        footer {{visibility: hidden;}}
        #MainMenu {{visibility: hidden;}}
    </style>
    """