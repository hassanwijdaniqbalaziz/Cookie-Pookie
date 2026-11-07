import streamlit as st
import base64
import os
import urllib.parse
from google import genai

# ---------------------------------------------------------
# Page Configuration
# ---------------------------------------------------------
st.set_page_config(
    page_title="Cookie Pookie | Freshly Homemade Delights",
    page_icon="🍪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------------
# Helper Functions & Safe HTML Renderer
# ---------------------------------------------------------
def render_html(raw_html):
    """
    Strips leading whitespace from every line so Markdown parsers
    NEVER mistakenly treat indented HTML as a grey <pre><code> block.
    """
    clean_html = "\n".join(line.strip() for line in raw_html.strip().splitlines())
    st.markdown(clean_html, unsafe_allow_html=True)

def get_base64_image(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    return ""

LOGO_PATH = os.path.join(os.path.dirname(__file__), "assets", "logo.jpg")
logo_b64 = get_base64_image(LOGO_PATH)

# Load Knowledge Base from README.md
def load_knowledge_base():
    readme_path = os.path.join(os.path.dirname(__file__), "README.md")
    if os.path.exists(readme_path):
        with open(readme_path, "r", encoding="utf-8") as f:
            return f.read()
    return ""

KNOWLEDGE_BASE = load_knowledge_base()

# Gemini Client Initialization (Securely loaded from st.secrets or environment)
try:
    GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY", os.environ.get("GEMINI_API_KEY", ""))
except Exception:
    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

# Session State Initialization
if "cart" not in st.session_state:
    st.session_state.cart = {
        "Choc Chip Cookie": 0,
        "BROOKIE": 0,
        "BROWNIE": 0
    }

if "current_page" not in st.session_state:
    st.session_state.current_page = "Home"

if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        {
            "role": "assistant",
            "content": "Hi there! I'm **POOKIE** 🍪✨, your sweetest cookie companion! Ask me anything about our freshly homemade Choc Chip Cookies, Brookies, Brownies, ingredients, delivery times, or how to place your order!"
        }
    ]

def set_page(page_name):
    st.session_state.current_page = page_name

# ---------------------------------------------------------
# Realistic Cookie SVGs (Clean, No Filters, Unique Gradients)
# ---------------------------------------------------------
SVG_CHOC_CHIP = """<svg viewBox="0 0 100 100" class="cookie-svg" xmlns="http://www.w3.org/2000/svg"><defs><radialGradient id="grad_cc_base" cx="42%" cy="38%" r="58%"><stop offset="0%" stop-color="#FCD590"/><stop offset="45%" stop-color="#EAA649"/><stop offset="80%" stop-color="#C77824"/><stop offset="100%" stop-color="#8E460E"/></radialGradient><radialGradient id="grad_cc_chip" cx="35%" cy="30%" r="65%"><stop offset="0%" stop-color="#55270E"/><stop offset="65%" stop-color="#281105"/><stop offset="100%" stop-color="#120601"/></radialGradient></defs><path d="M 50,4 C 67,3 84,12 91,27 C 98,41 97,59 91,74 C 84,87 69,97 51,97 C 34,97 18,89 9,75 C 1,60 2,42 8,28 C 15,13 33,5 50,4 Z" fill="url(#grad_cc_base)"/><path d="M 30,24 Q 40,28 48,20 M 20,53 Q 29,48 37,56 M 61,68 Q 69,60 77,65 M 54,40 Q 62,45 66,37" stroke="#A55615" stroke-width="1.8" stroke-linecap="round" fill="none" opacity="0.6"/><path d="M 27,33 C 32,30 38,34 37,40 C 35,45 29,47 24,44 C 20,40 22,34 27,33 Z" fill="url(#grad_cc_chip)"/><path d="M 66,23 C 71,21 76,26 75,32 C 73,37 67,39 62,36 C 58,33 60,25 66,23 Z" fill="url(#grad_cc_chip)"/><path d="M 44,52 C 51,49 57,55 55,62 C 53,68 46,71 40,67 C 36,63 38,55 44,52 Z" fill="url(#grad_cc_chip)"/><path d="M 72,55 C 77,53 82,57 81,63 C 79,68 73,70 69,67 C 65,64 67,57 72,55 Z" fill="url(#grad_cc_chip)"/><path d="M 21,68 C 25,66 30,70 29,76 C 28,80 23,82 19,79 C 16,76 17,70 21,68 Z" fill="url(#grad_cc_chip)"/><path d="M 47,76 C 52,74 57,78 56,84 C 55,88 50,90 46,88 C 43,86 44,79 47,76 Z" fill="url(#grad_cc_chip)"/><circle cx="53" cy="34" r="3.2" fill="#281105"/><circle cx="34" cy="18" r="2.6" fill="#281105"/><circle cx="72" cy="43" r="3.4" fill="#281105"/><circle cx="37" cy="74" r="2.7" fill="#281105"/></svg>"""

SVG_BROOKIE = """<svg viewBox="0 0 100 100" class="cookie-svg" xmlns="http://www.w3.org/2000/svg"><defs><radialGradient id="grad_brk_dark" cx="35%" cy="35%" r="65%"><stop offset="0%" stop-color="#55250D"/><stop offset="55%" stop-color="#381505"/><stop offset="85%" stop-color="#230A02"/><stop offset="100%" stop-color="#140501"/></radialGradient><radialGradient id="grad_brk_gold" cx="45%" cy="40%" r="55%"><stop offset="0%" stop-color="#FCD590"/><stop offset="60%" stop-color="#EAA649"/><stop offset="100%" stop-color="#A65814"/></radialGradient><radialGradient id="grad_brk_chunk" cx="30%" cy="30%" r="70%"><stop offset="0%" stop-color="#280C03"/><stop offset="100%" stop-color="#0E0300"/></radialGradient></defs><path d="M 48,5 C 65,4 83,13 90,28 C 97,42 96,60 89,75 C 82,88 67,97 50,96 C 33,96 17,87 9,72 C 2,57 3,39 10,25 C 18,12 33,5 48,5 Z" fill="url(#grad_brk_dark)"/><path d="M 48,6 C 65,5 82,14 89,28 C 95,40 94,57 88,70 C 72,55 58,40 42,32 C 34,28 38,12 48,6 Z" fill="url(#grad_brk_gold)" opacity="0.95"/><path d="M 42,32 Q 58,40 72,55 M 24,56 Q 34,50 41,60 M 64,66 Q 72,58 79,63" stroke="#1E0A02" stroke-width="2" stroke-linecap="round" fill="none" opacity="0.75"/><path d="M 28,34 C 34,31 40,36 38,42 C 36,47 30,50 25,46 C 21,42 23,35 28,34 Z" fill="url(#grad_brk_chunk)"/><path d="M 64,26 C 70,23 76,28 74,35 C 72,40 66,42 61,39 C 57,36 59,27 64,26 Z" fill="url(#grad_brk_chunk)"/><path d="M 48,55 C 55,51 62,57 60,64 C 58,71 50,74 44,69 C 39,64 42,56 48,55 Z" fill="url(#grad_brk_chunk)"/><path d="M 22,69 C 27,67 32,71 31,77 C 29,82 23,84 19,80 C 16,76 17,70 22,69 Z" fill="url(#grad_brk_chunk)"/></svg>"""

SVG_BROWNIE = """<svg viewBox="0 0 100 100" class="cookie-svg" xmlns="http://www.w3.org/2000/svg"><defs><linearGradient id="grad_brw_square" x1="10%" y1="10%" x2="90%" y2="90%"><stop offset="0%" stop-color="#4E230B"/><stop offset="45%" stop-color="#341606"/><stop offset="85%" stop-color="#200B02"/><stop offset="100%" stop-color="#120501"/></linearGradient><linearGradient id="grad_brw_drizzle" x1="0%" y1="0%" x2="100%" y2="0%"><stop offset="0%" stop-color="#723713"/><stop offset="50%" stop-color="#9C521E"/><stop offset="100%" stop-color="#552408"/></linearGradient></defs><rect x="12" y="12" width="76" height="76" rx="18" fill="url(#grad_brw_square)"/><path d="M 20,26 Q 38,32 54,22 Q 68,28 82,23" stroke="#683011" stroke-width="2" stroke-linecap="round" fill="none" opacity="0.8"/><path d="M 18,52 Q 38,44 58,56 Q 72,48 83,53" stroke="#683011" stroke-width="2" stroke-linecap="round" fill="none" opacity="0.8"/><path d="M 22,76 Q 44,70 66,77 Q 76,71 80,75" stroke="#683011" stroke-width="2" stroke-linecap="round" fill="none" opacity="0.8"/><path d="M 15,35 Q 40,55 85,38" stroke="url(#grad_brw_drizzle)" stroke-width="5.5" stroke-linecap="round" fill="none"/><path d="M 20,62 Q 52,80 84,62" stroke="url(#grad_brw_drizzle)" stroke-width="4.5" stroke-linecap="round" fill="none"/><rect x="36" y="28" width="3" height="3" fill="#FFF4E0" transform="rotate(25 36 28)" opacity="0.85"/><rect x="62" y="44" width="3.5" height="3.5" fill="#FFF4E0" transform="rotate(40 62 44)" opacity="0.85"/><rect x="46" y="66" width="3" height="3" fill="#FFF4E0" transform="rotate(15 46 66)" opacity="0.85"/></svg>"""

# ---------------------------------------------------------
# Chocolate Bakery Luxury CSS Styling
# ---------------------------------------------------------
render_html("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Montserrat:wght@400;500;600;700;800;900&display=swap');

:root {
    --cocoa-darkest: #150601;
    --cocoa-dark: #200B02;
    --cocoa-rich: #321204;
    --cocoa-medium: #542A12;
    --caramel-gold: #D97706;
    --caramel-bright: #F59E0B;
    --caramel-cream: #FDE8C5;
    --vanilla-bg: #FAF6F0;
    --vanilla-card: #FFFFFF;
    --text-primary: #1F0A02;
    --text-secondary: #52270F;
}

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    color: var(--text-primary);
}

.stApp {
    background: linear-gradient(180deg, #FAF6F0 0%, #F5EDE1 50%, #EFE4D2 100%) !important;
    background-attachment: fixed;
    overflow-x: hidden;
}

/* PREVENT ANY UNWANTED MARKDOWN CODE BOXES */
pre, code {
    display: none !important;
}

/* Floating Cookies */
.floating-cookies-canvas {
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    pointer-events: none;
    z-index: 0;
    overflow: hidden;
}

.cookie-svg {
    width: 100%;
    height: 100%;
    display: block;
}

.baked-floater {
    position: absolute;
    bottom: -110px;
    animation: driftUpward linear infinite;
    opacity: 0.8;
}

@keyframes driftUpward {
    0% {
        transform: translateY(0) rotate(0deg) scale(0.9);
        opacity: 0;
    }
    12% {
        opacity: 0.82;
    }
    85% {
        opacity: 0.82;
    }
    100% {
        transform: translateY(-118vh) rotate(360deg) scale(1.05);
        opacity: 0;
    }
}

.fl-1 { left: 4%; width: 75px; height: 75px; animation-duration: 16s; animation-delay: 0s; }
.fl-2 { left: 18%; width: 90px; height: 90px; animation-duration: 20s; animation-delay: 3s; }
.fl-3 { left: 32%; width: 65px; height: 65px; animation-duration: 14s; animation-delay: 7s; }
.fl-4 { left: 46%; width: 85px; height: 85px; animation-duration: 18s; animation-delay: 1.5s; }
.fl-5 { left: 60%; width: 95px; height: 95px; animation-duration: 22s; animation-delay: 5s; }
.fl-6 { left: 74%; width: 70px; height: 70px; animation-duration: 15s; animation-delay: 9s; }
.fl-7 { left: 88%; width: 88px; height: 88px; animation-duration: 19s; animation-delay: 4s; }
.fl-8 { left: 12%; width: 80px; height: 80px; animation-duration: 17s; animation-delay: 11s; }
.fl-9 { left: 54%; width: 72px; height: 72px; animation-duration: 13s; animation-delay: 12s; }

/* Sidebar */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1C0A02 0%, #150601 45%, #0D0300 100%) !important;
    border-right: 3px solid #D97706 !important;
    box-shadow: 8px 0 32px rgba(13, 3, 0, 0.6) !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
}

section[data-testid="stSidebar"] * {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
}

section[data-testid="stSidebar"] [data-testid="stSidebarNav"] {
    display: none !important;
}

.sidebar-brand-crest {
    text-align: center;
    padding: 22px 12px 18px 12px;
    background: linear-gradient(180deg, rgba(217, 119, 6, 0.18) 0%, rgba(21, 6, 1, 0.5) 100%);
    border-radius: 20px;
    border: 2px solid rgba(217, 119, 6, 0.4);
    margin-bottom: 22px;
    box-shadow: 0 12px 28px rgba(0, 0, 0, 0.5);
}

.brand-gold-title {
    font-family: 'Montserrat', sans-serif !important;
    font-size: 1.85rem !important;
    font-weight: 800 !important;
    color: #FEE7C4 !important;
    margin: 14px 0 4px 0 !important;
    letter-spacing: 1.2px;
    text-transform: uppercase;
    text-shadow: 0 2px 10px rgba(0,0,0,0.7);
}

.brand-gold-sub {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 0.82rem !important;
    font-weight: 700 !important;
    color: #F59E0B !important;
    letter-spacing: 2.2px;
    text-transform: uppercase;
}

section[data-testid="stSidebar"] .stButton>button {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 0.98rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.3px !important;
    text-align: left !important;
    padding: 0.75rem 1.15rem !important;
    border-radius: 14px !important;
    background: linear-gradient(135deg, #2D1407 0%, #1A0902 100%) !important;
    color: #FEE7C4 !important;
    border: 1.5px solid rgba(217, 119, 6, 0.35) !important;
    box-shadow: 0 4px 12px rgba(0,0,0,0.3) !important;
    transition: all 0.25s ease !important;
}

section[data-testid="stSidebar"] .stButton>button:hover {
    background: linear-gradient(135deg, #D97706 0%, #B45309 100%) !important;
    color: #FFFFFF !important;
    border-color: #F59E0B !important;
    transform: translateX(4px) !important;
    box-shadow: 0 6px 18px rgba(217, 119, 6, 0.45) !important;
}

.sidebar-box-summary {
    background: linear-gradient(145deg, #260E03 0%, #140500 100%);
    border: 1.8px solid #D97706;
    border-radius: 18px;
    padding: 18px;
    margin: 20px 0;
    box-shadow: 0 8px 22px rgba(0, 0, 0, 0.4);
}

.sidebar-hotline-card {
    background: rgba(217, 119, 6, 0.12);
    border-radius: 16px;
    border: 1.5px dashed rgba(245, 158, 11, 0.45);
    padding: 16px;
    text-align: center;
    margin-top: 15px;
}

/* Main typography & cards */
h1, h2, h3, h4 {
    font-family: 'Montserrat', sans-serif !important;
    color: #1F0A02;
    font-weight: 800 !important;
}

.main-hero-banner {
    background: linear-gradient(135deg, #FFFFFF 0%, #FDF8F0 60%, #F7EAD7 100%);
    border: 3px solid #D97706;
    border-radius: 28px;
    padding: 40px 36px;
    box-shadow: 0 18px 40px rgba(42, 19, 7, 0.12);
    margin-bottom: 35px;
    position: relative;
    z-index: 1;
}

.gold-ribbon {
    display: inline-block;
    background: linear-gradient(135deg, #D97706 0%, #B45309 100%);
    color: #FFFFFF !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 0.92rem;
    font-weight: 700;
    padding: 6px 16px;
    border-radius: 50px;
    letter-spacing: 0.6px;
    margin-bottom: 14px;
    box-shadow: 0 4px 12px rgba(217, 119, 6, 0.3);
}

.hero-main-heading {
    font-family: 'Montserrat', sans-serif !important;
    font-size: 3.4rem !important;
    line-height: 1.15;
    color: #1A0701 !important;
    margin-bottom: 16px;
    font-weight: 900 !important;
}

.menu-item-card {
    background: #FFFFFF !important;
    border-radius: 24px;
    padding: 24px;
    border: 2px solid #E8D3BD;
    box-shadow: 0 10px 26px rgba(32, 11, 2, 0.08);
    transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    height: 100%;
}

.menu-item-card:hover {
    transform: translateY(-6px);
    box-shadow: 0 18px 36px rgba(32, 11, 2, 0.14);
    border-color: #D97706;
}

.product-name-title {
    font-family: 'Montserrat', sans-serif !important;
    font-size: 1.7rem !important;
    font-weight: 800 !important;
    color: #150601 !important;
    margin: 12px 0 6px 0 !important;
    line-height: 1.25 !important;
    display: block !important;
}

.product-desc-text {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    color: #4A220C !important;
    font-size: 0.94rem !important;
    line-height: 1.6 !important;
    margin: 0 0 12px 0 !important;
}

.price-tag-badge {
    background: #180701 !important;
    color: #FEE7C4 !important;
    font-family: 'Montserrat', sans-serif !important;
    font-size: 1.18rem !important;
    font-weight: 800 !important;
    padding: 6px 14px;
    border-radius: 24px;
    display: inline-block;
    border: 1.5px solid #D97706;
}

.highlight-pill {
    background: #FEF3C7;
    color: #92400E !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-weight: 700;
    font-size: 0.8rem;
    padding: 4px 10px;
    border-radius: 20px;
    border: 1px solid #F59E0B;
}

.main .stButton>button {
    background: linear-gradient(135deg, #D97706 0%, #B45309 100%) !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 14px !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 1.05rem !important;
    font-weight: 700 !important;
    padding: 0.65rem 1.4rem !important;
    box-shadow: 0 6px 16px rgba(180, 83, 9, 0.35) !important;
    transition: all 0.22s ease !important;
}

.main .stButton>button:hover {
    background: linear-gradient(135deg, #EA580C 0%, #C2410C 100%) !important;
    box-shadow: 0 9px 24px rgba(194, 65, 12, 0.5) !important;
    transform: translateY(-2px) !important;
}

.whatsapp-glow-btn {
    display: inline-block;
    background: linear-gradient(135deg, #10B981 0%, #059669 100%);
    color: #FFFFFF !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 1.15rem;
    font-weight: 700;
    padding: 14px 26px;
    border-radius: 16px;
    text-decoration: none;
    text-align: center;
    box-shadow: 0 8px 22px rgba(5, 150, 105, 0.4);
    transition: all 0.22s ease;
}

.whatsapp-glow-btn:hover {
    background: linear-gradient(135deg, #059669 0%, #047857 100%);
    transform: translateY(-2px);
    box-shadow: 0 12px 28px rgba(5, 150, 105, 0.55);
    color: #FFFFFF !important;
    text-decoration: none;
}

.hero-mascot-glow {
    animation: gentleBob 3.5s ease-in-out infinite;
}

@keyframes gentleBob {
    0%, 100% { transform: translateY(0) rotate(0deg); }
    50% { transform: translateY(-10px) rotate(2deg); }
}

/* Chatbot UI Styling */
.chat-container {
    background: #FFFFFF;
    border: 2px solid #E8D3BD;
    border-radius: 26px;
    padding: 28px;
    box-shadow: 0 12px 30px rgba(42, 19, 7, 0.09);
    margin-bottom: 25px;
}

.suggestion-chip {
    display: inline-block;
    background: #FDF6EC;
    color: #92400E;
    font-size: 0.88rem;
    font-weight: 600;
    padding: 6px 14px;
    border-radius: 20px;
    border: 1px solid #F59E0B;
    margin: 4px;
    cursor: pointer;
    transition: all 0.2s ease;
}

.suggestion-chip:hover {
    background: #F59E0B;
    color: #FFFFFF;
}
</style>
""")

# Floating Cookies Layer
render_html(f"""
<div class="floating-cookies-canvas">
    <div class="baked-floater fl-1">{SVG_CHOC_CHIP}</div>
    <div class="baked-floater fl-2">{SVG_BROOKIE}</div>
    <div class="baked-floater fl-3">{SVG_BROWNIE}</div>
    <div class="baked-floater fl-4">{SVG_CHOC_CHIP}</div>
    <div class="baked-floater fl-5">{SVG_BROOKIE}</div>
    <div class="baked-floater fl-6">{SVG_BROWNIE}</div>
    <div class="baked-floater fl-7">{SVG_CHOC_CHIP}</div>
    <div class="baked-floater fl-8">{SVG_BROOKIE}</div>
    <div class="baked-floater fl-9">{SVG_CHOC_CHIP}</div>
</div>
""")

# ---------------------------------------------------------
# SIDEBAR NAVIGATION
# ---------------------------------------------------------
with st.sidebar:
    # Brand Mascot Crest
    render_html("""
    <div class="sidebar-brand-crest">
    """ + (f"""
        <div style="position: relative; display: inline-block;">
            <img src="data:image/jpeg;base64,{logo_b64}" 
                 style="width: 170px; height: 170px; object-fit: cover; border-radius: 50%; 
                        border: 4px solid #F59E0B; box-shadow: 0 10px 25px rgba(0,0,0,0.6);" 
                 alt="Cookie Pookie Logo" />
        </div>
    """ if logo_b64 else "") + """
        <h1 class="brand-gold-title">COOKIE POOKIE</h1>
        <div class="brand-gold-sub">★ Freshly Homemade ★</div>
    </div>
    """)

    # Navigation Section Header
    render_html("""
    <div style="margin: 15px 0 8px 4px;">
        <span style="color: #F59E0B; font-size: 0.78rem; font-weight: 800; letter-spacing: 2px; text-transform: uppercase;">
            NAVIGATION
        </span>
    </div>
    """)

    # Navigation Buttons (Including POOKIE Chatbot!)
    if st.button("🏠  Home Sweet Home", key="btn_nav_home", use_container_width=True):
        st.session_state.current_page = "Home"
        st.rerun()

    if st.button("🍪  Signature Menu (PKR 200)", key="btn_nav_menu", use_container_width=True):
        st.session_state.current_page = "Menu"
        st.rerun()

    if st.button("🤖  Chat with POOKIE", key="btn_nav_bot", use_container_width=True):
        st.session_state.current_page = "Chat"
        st.rerun()

    if st.button("📞  Contact Us & Order", key="btn_nav_contact", use_container_width=True):
        st.session_state.current_page = "Contact"
        st.rerun()

    # Active Page Status Pill
    render_html(f"""
    <div style="text-align: center; margin: 10px 0 16px 0;">
        <span style="background: rgba(217, 119, 6, 0.25); color: #FEE7C4; font-size: 0.82rem; font-weight: 700; padding: 4px 14px; border-radius: 20px; border: 1px solid rgba(245, 158, 11, 0.5); letter-spacing: 0.5px;">
            Active: <b>{st.session_state.current_page}</b>
        </span>
    </div>
    """)

    # Live Cookie Box Summary
    total_qty = sum(st.session_state.cart.values())
    total_price = total_qty * 200

    box_items_html = ""
    if total_qty == 0:
        box_items_html = "<p style='color: #D3B99E; font-size: 0.88rem; margin: 0;'>Box is empty. Add warm treats from the menu!</p>"
    else:
        for item, qty in st.session_state.cart.items():
            if qty > 0:
                box_items_html += f"""
                <div style="display: flex; justify-content: space-between; color: #FFF8EE; font-size: 0.9rem; margin-bottom: 4px;">
                    <span>• {item} (x{qty})</span>
                    <span style="color: #F59E0B; font-weight: 700;">PKR {qty*200}</span>
                </div>
                """
        box_items_html += f"""
        <div style="border-top: 1px dashed rgba(245, 158, 11, 0.4); margin-top: 10px; padding-top: 10px; display: flex; justify-content: space-between; align-items: center;">
            <span style="color: #FEE7C4; font-size: 0.95rem; font-weight: 600;">Total:</span>
            <span style="color: #FCD34D; font-family: 'Montserrat', sans-serif; font-size: 1.3rem; font-weight: 800;">PKR {total_price}</span>
        </div>
        """

    render_html(f"""
    <div class="sidebar-box-summary">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
            <span style="font-family: 'Montserrat', sans-serif; font-size: 1.05rem; color: #FEE7C4; font-weight: 700;">
                🛍️ Your Box
            </span>
            <span style="background: #D97706; color: #FFFFFF; font-size: 0.78rem; font-weight: 800; padding: 3px 8px; border-radius: 10px;">
                {total_qty} Items
            </span>
        </div>
        {box_items_html}
    </div>
    """)

    if total_qty > 0:
        col_box_a, col_box_b = st.columns(2)
        with col_box_a:
            if st.button("Order", key="sb_order_btn", use_container_width=True):
                st.session_state.current_page = "Menu"
                st.rerun()
        with col_box_b:
            if st.button("Clear", key="sb_empty_btn", use_container_width=True):
                for k in st.session_state.cart:
                    st.session_state.cart[k] = 0
                st.rerun()

    # Hotline Contact Card
    render_html("""
    <div class="sidebar-hotline-card">
        <div style="color: #FCD34D; font-size: 0.78rem; font-weight: 800; letter-spacing: 1.5px; text-transform: uppercase; margin-bottom: 6px;">
            📞 ORDER HOTLINES
        </div>
        <div style="font-family: 'Montserrat', sans-serif; font-size: 1.25rem; color: #FFFFFF; font-weight: 800; margin-bottom: 2px;">
            0300-8237849
        </div>
        <div style="font-family: 'Montserrat', sans-serif; font-size: 1.25rem; color: #FFFFFF; font-weight: 800; margin-bottom: 10px;">
            0300-8233395
        </div>
        <a href="https://wa.me/923008237849" target="_blank" 
           style="display: inline-block; background: #10B981; color: white !important; padding: 7px 16px; border-radius: 10px; font-weight: 700; text-decoration: none; font-size: 0.85rem; box-shadow: 0 4px 12px rgba(16,185,129,0.35);">
            💬 Chat on WhatsApp
        </a>
    </div>
    """)


# =========================================================
# PAGE 1: HOME SWEET HOME
# =========================================================
if st.session_state.current_page == "Home":
    col_hero_info, col_hero_visual = st.columns([1.35, 1], gap="large")

    with col_hero_info:
        render_html("""
        <div class="main-hero-banner">
            <div class="gold-ribbon">✨ FRESH OUT OF THE OVEN ✨</div>
            <h1 class="hero-main-heading">Crave The Ultimate <br><span style="color: #D97706;">Warm & Chewy</span> Treats</h1>
            <p style="color: #4A220C; font-size: 1.2rem; line-height: 1.65; margin-bottom: 24px; font-weight: 400;">
                Welcome to <b>COOKIE POOKIE</b>! Handcrafted in small batches with pure creamery butter, 
                rich Dutch cocoa, and overflowing pools of Belgian chocolate chunks. Each bite is baked fresh with extra love!
            </p>
            <div style="display: flex; gap: 14px; align-items: center; flex-wrap: wrap; margin-bottom: 24px;">
                <span class="price-tag-badge">🔥 All Items PKR 200 Each</span>
                <span class="highlight-pill">100% Real Butter</span>
                <span class="highlight-pill">No Preservatives</span>
            </div>
        </div>
        """)

        btn_c1, btn_c2, btn_c3 = st.columns(3)
        with btn_c1:
            if st.button("🍪 Our Menu", key="home_to_menu", use_container_width=True):
                st.session_state.current_page = "Menu"
                st.rerun()
        with btn_c2:
            if st.button("🤖 Ask POOKIE", key="home_to_bot", use_container_width=True):
                st.session_state.current_page = "Chat"
                st.rerun()
        with btn_c3:
            if st.button("📞 Contact Us", key="home_to_contact", use_container_width=True):
                st.session_state.current_page = "Contact"
                st.rerun()

    with col_hero_visual:
        if logo_b64:
            render_html(f"""
            <div style="text-align: center; padding: 10px 0;">
                <div class="hero-mascot-glow">
                    <img src="data:image/jpeg;base64,{logo_b64}" 
                         style="width: 100%; max-width: 380px; border-radius: 28px; 
                                border: 5px solid #D97706; box-shadow: 0 20px 45px rgba(42, 19, 7, 0.28);" 
                         alt="Cookie Pookie Mascot" />
                </div>
                <div style="margin-top: 18px; font-family: 'Montserrat', sans-serif; font-size: 1.15rem; color: #1F0A02; font-weight: 700;">
                    "Every cookie is baked with sweet hugs & chocolate chips!" 🍪✨
                </div>
            </div>
            """)

    render_html("<div style='height: 35px;'></div>")

    # 3 Signature Treats Teaser Showcase
    render_html("""
    <div style="text-align: center; margin-bottom: 25px;">
        <span class="gold-ribbon">THE SIGNATURE TRIO</span>
        <h2 style="font-size: 2.5rem; margin-top: 6px;">Handcrafted Perfection In Every Bite</h2>
        <p style="color: #4A220C; font-size: 1.08rem; max-width: 600px; margin: 0 auto;">
            Our three legendary recipes baked to golden perfection. Which one will you try first?
        </p>
    </div>
    """)

    t1, t2, t3 = st.columns(3, gap="medium")

    with t1:
        render_html(f"""
        <div class="menu-item-card">
            <div style="width: 130px; height: 130px; margin: 0 auto 15px auto;">
                {SVG_CHOC_CHIP}
            </div>
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <span class="highlight-pill">🔥 Classic Bestseller</span>
                <span class="price-tag-badge">PKR 200</span>
            </div>
            <div class="product-name-title">Choc Chip Cookie</div>
            <p class="product-desc-text">
                Crispy golden edges with a soft, chewy molten chocolate center. The timeless classic perfected.
            </p>
        </div>
        """)

    with t2:
        render_html(f"""
        <div class="menu-item-card">
            <div style="width: 130px; height: 130px; margin: 0 auto 15px auto;">
                {SVG_BROOKIE}
            </div>
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <span class="highlight-pill">⭐ Hybrid Sensation</span>
                <span class="price-tag-badge">PKR 200</span>
            </div>
            <div class="product-name-title">BROOKIE</div>
            <p class="product-desc-text">
                The heavenly mashup! Half fudgy dark chocolate brownie, half golden chocolate chip cookie dough.
            </p>
        </div>
        """)

    with t3:
        render_html(f"""
        <div class="menu-item-card">
            <div style="width: 130px; height: 130px; margin: 0 auto 15px auto;">
                {SVG_BROWNIE}
            </div>
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <span class="highlight-pill">🍫 Dark Decadence</span>
                <span class="price-tag-badge">PKR 200</span>
            </div>
            <div class="product-name-title">BROWNIE</div>
            <p class="product-desc-text">
                Dense, rich, ultra-fudgy chocolate square with a glossy crinkle crust and silky chocolate drizzle.
            </p>
        </div>
        """)

    render_html("<div style='height: 40px;'></div>")

    # Why Cookie Pookie Pillars
    render_html("""
    <div style="background: linear-gradient(135deg, #FFFFFF 0%, #FDF7EE 100%); border-radius: 28px; padding: 40px 30px; border: 3px solid #D97706; box-shadow: 0 16px 36px rgba(42,19,7,0.12);">
        <div style="text-align: center; margin-bottom: 30px;">
            <span class="gold-ribbon">OUR QUALITY PROMISE</span>
            <h2 style="color: #150601 !important; font-size: 2.4rem; margin: 8px 0; font-weight: 900;">Why Everyone Loves COOKIE POOKIE 💖</h2>
            <p style="color: #4A220C !important; font-size: 1.12rem; font-weight: 500; margin: 0;">We believe luxury bakery treats should be honest, delicious, and accessible.</p>
        </div>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(230px, 1fr)); gap: 20px;">
            <div style="background: #FDF6EC; padding: 24px; border-radius: 20px; border: 2px dashed #D97706; text-align: center;">
                <div style="font-size: 2.6rem; margin-bottom: 12px;">🧈</div>
                <div style="font-family: 'Montserrat', sans-serif; font-size: 1.3rem; font-weight: 800; color: #150601 !important; margin-bottom: 6px;">Pure Butter Only</div>
                <p style="color: #4A220C !important; font-size: 0.94rem; margin: 0; line-height: 1.5; font-weight: 500;">Zero margarine or preservatives. Pure golden butter aroma.</p>
            </div>
            <div style="background: #FDF6EC; padding: 24px; border-radius: 20px; border: 2px dashed #D97706; text-align: center;">
                <div style="font-size: 2.6rem; margin-bottom: 12px;">🍫</div>
                <div style="font-family: 'Montserrat', sans-serif; font-size: 1.3rem; font-weight: 800; color: #150601 !important; margin-bottom: 6px;">Belgian Chocolate</div>
                <p style="color: #4A220C !important; font-size: 0.94rem; margin: 0; line-height: 1.5; font-weight: 500;">Loaded with gooey melted dark and semi-sweet chocolate pools.</p>
            </div>
            <div style="background: #FDF6EC; padding: 24px; border-radius: 20px; border: 2px dashed #D97706; text-align: center;">
                <div style="font-size: 2.6rem; margin-bottom: 12px;">🔥</div>
                <div style="font-family: 'Montserrat', sans-serif; font-size: 1.3rem; font-weight: 800; color: #150601 !important; margin-bottom: 6px;">Baked On-Demand</div>
                <p style="color: #4A220C !important; font-size: 0.94rem; margin: 0; line-height: 1.5; font-weight: 500;">Freshly homemade per order so your box arrives warm and soft.</p>
            </div>
            <div style="background: #FDF6EC; padding: 24px; border-radius: 20px; border: 2px dashed #D97706; text-align: center;">
                <div style="font-size: 2.6rem; margin-bottom: 12px;">🏷️</div>
                <div style="font-family: 'Montserrat', sans-serif; font-size: 1.3rem; font-weight: 800; color: #150601 !important; margin-bottom: 6px;">Flat PKR 200</div>
                <p style="color: #4A220C !important; font-size: 0.94rem; margin: 0; line-height: 1.5; font-weight: 500;">Luxury bakery quality made super accessible and pocket-friendly!</p>
            </div>
        </div>
    </div>
    """)


# =========================================================
# PAGE 2: MENU & ORDER
# =========================================================
elif st.session_state.current_page == "Menu":
    render_html("""
    <div style="text-align: center; margin-bottom: 30px;">
        <span class="gold-ribbon">FRESH FROM THE OVEN</span>
        <h1 style="font-size: 3rem; margin: 8px 0; color: #150601 !important;">Our Handcrafted Menu</h1>
        <p style="color: #4A220C; font-size: 1.15rem; max-width: 680px; margin: 0 auto; font-weight: 500;">
            Choose your favorites, assemble your personalized box, and place an order directly with our bakers. Flat <b>PKR 200</b> each!
        </p>
    </div>
    """)

    mc1, mc2, mc3 = st.columns(3, gap="medium")

    # Item 1: Choc Chip Cookie
    with mc1:
        render_html(f"""
        <div class="menu-item-card">
            <div style="background: #FDF6EC; border-radius: 20px; padding: 20px; text-align: center; margin-bottom: 14px; border: 2px dashed #D97706;">
                <div style="width: 135px; height: 135px; margin: 0 auto;">
                    {SVG_CHOC_CHIP}
                </div>
            </div>
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <span class="highlight-pill">🔥 All-Time Bestseller</span>
                <span class="price-tag-badge">PKR 200</span>
            </div>
            <div class="product-name-title">Choc Chip Cookie</div>
            <p class="product-desc-text">
                The quintessential classic cookie! Crisp golden edges with a warm, soft, gooey center loaded with rich Belgian semi-sweet chocolate chunks.
            </p>
            <div style="margin-top: 8px; margin-bottom: 16px; padding: 10px 12px; background: #FAF3E8; border-radius: 12px; border-left: 3px solid #D97706;">
                <span style="font-size: 0.8rem; font-weight: 700; color: #92400E;">Baking Profile:</span>
                <p style="font-size: 0.82rem; color: #4A220C; margin: 2px 0;">Pure creamery butter, golden brown cane sugar, sea salt sprinkle.</p>
            </div>
        </div>
        """)

        qty1 = st.session_state.cart["Choc Chip Cookie"]
        q1_c1, q1_c2 = st.columns(2)
        with q1_c1:
            if st.button("➕ Add 1", key="btn_add_ccc", use_container_width=True):
                st.session_state.cart["Choc Chip Cookie"] += 1
                st.toast("Added 1 Choc Chip Cookie! 🍪")
                st.rerun()
        with q1_c2:
            if st.button("➖ Remove", key="btn_rem_ccc", use_container_width=True):
                if st.session_state.cart["Choc Chip Cookie"] > 0:
                    st.session_state.cart["Choc Chip Cookie"] -= 1
                    st.rerun()
        render_html(f"<p style='text-align:center; font-weight:700; color:#150601; margin-top:4px;'>In Box: <b>{qty1}</b> (PKR {qty1*200})</p>")

    # Item 2: BROOKIE
    with mc2:
        render_html(f"""
        <div class="menu-item-card">
            <div style="background: #FDF6EC; border-radius: 20px; padding: 20px; text-align: center; margin-bottom: 14px; border: 2px dashed #D97706;">
                <div style="width: 135px; height: 135px; margin: 0 auto;">
                    {SVG_BROOKIE}
                </div>
            </div>
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <span class="highlight-pill">⭐ Customer Favorite</span>
                <span class="price-tag-badge">PKR 200</span>
            </div>
            <div class="product-name-title">BROOKIE</div>
            <p class="product-desc-text">
                Can't pick between a brownie and a cookie? Enjoy the best of both worlds! Half decadent dark chocolate brownie merged into half chewy chocolate chip dough.
            </p>
            <div style="margin-top: 8px; margin-bottom: 16px; padding: 10px 12px; background: #FAF3E8; border-radius: 12px; border-left: 3px solid #D97706;">
                <span style="font-size: 0.8rem; font-weight: 700; color: #92400E;">Baking Profile:</span>
                <p style="font-size: 0.82rem; color: #4A220C; margin: 2px 0;">55% Dutch dark chocolate, marble swirl dough, fudge core.</p>
            </div>
        </div>
        """)

        qty2 = st.session_state.cart["BROOKIE"]
        q2_c1, q2_c2 = st.columns(2)
        with q2_c1:
            if st.button("➕ Add 1", key="btn_add_brk", use_container_width=True):
                st.session_state.cart["BROOKIE"] += 1
                st.toast("Added 1 Brookie! 🍫🍪")
                st.rerun()
        with q2_c2:
            if st.button("➖ Remove", key="btn_rem_brk", use_container_width=True):
                if st.session_state.cart["BROOKIE"] > 0:
                    st.session_state.cart["BROOKIE"] -= 1
                    st.rerun()
        render_html(f"<p style='text-align:center; font-weight:700; color:#150601; margin-top:4px;'>In Box: <b>{qty2}</b> (PKR {qty2*200})</p>")

    # Item 3: BROWNIE
    with mc3:
        render_html(f"""
        <div class="menu-item-card">
            <div style="background: #FDF6EC; border-radius: 20px; padding: 20px; text-align: center; margin-bottom: 14px; border: 2px dashed #D97706;">
                <div style="width: 135px; height: 135px; margin: 0 auto;">
                    {SVG_BROWNIE}
                </div>
            </div>
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <span class="highlight-pill">🔥 Pure Choc Rush</span>
                <span class="price-tag-badge">PKR 200</span>
            </div>
            <div class="product-name-title">BROWNIE</div>
            <p class="product-desc-text">
                Ultra-dense, intensely fudgy dark chocolate square with the iconic crinkly glossy crust, finished with silky chocolate drizzle and sea salt.
            </p>
            <div style="margin-top: 8px; margin-bottom: 16px; padding: 10px 12px; background: #FAF3E8; border-radius: 12px; border-left: 3px solid #D97706;">
                <span style="font-size: 0.8rem; font-weight: 700; color: #92400E;">Baking Profile:</span>
                <p style="font-size: 0.82rem; color: #4A220C; margin: 2px 0;">Double melted dark chocolate, Dutch cocoa, farm eggs, butter.</p>
            </div>
        </div>
        """)

        qty3 = st.session_state.cart["BROWNIE"]
        q3_c1, q3_c2 = st.columns(2)
        with q3_c1:
            if st.button("➕ Add 1", key="btn_add_brw", use_container_width=True):
                st.session_state.cart["BROWNIE"] += 1
                st.toast("Added 1 Brownie! 🍫")
                st.rerun()
        with q3_c2:
            if st.button("➖ Remove", key="btn_rem_brw", use_container_width=True):
                if st.session_state.cart["BROWNIE"] > 0:
                    st.session_state.cart["BROWNIE"] -= 1
                    st.rerun()
        render_html(f"<p style='text-align:center; font-weight:700; color:#150601; margin-top:4px;'>In Box: <b>{qty3}</b> (PKR {qty3*200})</p>")

    render_html("<div style='height: 35px;'></div>")

    # Checkout & WhatsApp Direct Order Section
    total_qty = sum(st.session_state.cart.values())
    total_price = total_qty * 200

    render_html(f"""
    <div style="background: linear-gradient(135deg, #FFFFFF 0%, #FDF7EE 100%); border: 3px solid #D97706; border-radius: 26px; padding: 35px; box-shadow: 0 14px 34px rgba(42, 19, 7, 0.12);">
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 20px;">
            <div>
                <h2 style="margin: 0 0 6px 0; font-size: 2.2rem; color: #150601 !important;">🛍️ Your Custom Cookie Box</h2>
                <p style="color: #4A220C; font-size: 1.1rem; margin: 0; font-weight: 500;">Total Selected: <b>{total_qty}</b> treats ready to be baked!</p>
            </div>
            <div style="text-align: right;">
                <span style="font-size: 0.95rem; color: #4A220C; font-weight: 600;">Total Amount:</span>
                <div style="font-family: 'Montserrat', sans-serif; font-size: 2.4rem; color: #D97706; font-weight: 800;">
                    PKR {total_price}
                </div>
            </div>
        </div>
    </div>
    """)

    if total_qty > 0:
        render_html("<div style='height: 15px;'></div>")
        c_name = st.text_input("👤 Your Full Name:", placeholder="e.g. Fatima Ali")
        c_address = st.text_input("📍 Delivery Address & City:", placeholder="e.g. House 14, Street 3, DHA Phase 5, Karachi")
        c_notes = st.text_input("📝 Special Instructions (Optional):", placeholder="e.g. Please deliver warm, extra napkins, gift ribbon")

        order_lines = []
        for item, qty in st.session_state.cart.items():
            if qty > 0:
                order_lines.append(f"• {item}: {qty} pc(s) (PKR {qty*200})")
        items_formatted = "\n".join(order_lines)

        wa_order_text = (
            f"Hello COOKIE POOKIE! 🍪✨\n"
            f"I would like to place an order:\n\n"
            f"{items_formatted}\n\n"
            f"💰 Total Amount: PKR {total_price}\n"
            f"👤 Name: {c_name if c_name else 'Customer'}\n"
            f"📍 Delivery Address: {c_address if c_address else 'To be confirmed'}\n"
            f"📝 Note: {c_notes if c_notes else 'None'}\n\n"
            f"Looking forward to fresh warm treats!"
        )

        encoded_msg = urllib.parse.quote(wa_order_text)
        wa_link_1 = f"https://wa.me/923008237849?text={encoded_msg}"
        wa_link_2 = f"https://wa.me/923008233395?text={encoded_msg}"

        render_html(f"""
        <div style="text-align: center; margin-top: 25px; display: flex; justify-content: center; gap: 16px; flex-wrap: wrap;">
            <a href="{wa_link_1}" target="_blank" class="whatsapp-glow-btn">
                💬 Send Order to WhatsApp (0300-8237849)
            </a>
            <a href="{wa_link_2}" target="_blank" class="whatsapp-glow-btn" style="background: linear-gradient(135deg, #059669 0%, #047857 100%);">
                💬 Send Order to WhatsApp (0300-8233395)
            </a>
        </div>
        """)
    else:
        st.info("💡 Click **➕ Add 1** on any of the treats above to build your cookie box!")


# =========================================================
# PAGE 3: CHAT WITH POOKIE (AI CHATBOT)
# =========================================================
elif st.session_state.current_page == "Chat":
    # Header & Mascot Intro
    col_bot_hdr, col_bot_img = st.columns([2.5, 1], gap="medium")
    with col_bot_hdr:
        render_html("""
        <div>
            <span class="gold-ribbon">AI BAKERY ASSISTANT</span>
            <h1 style="font-size: 2.8rem; margin: 8px 0; color: #150601 !important;">Chat with POOKIE 🍪</h1>
            <p style="color: #4A220C; font-size: 1.15rem; line-height: 1.6; margin-bottom: 12px; font-weight: 500;">
                Meet <b>POOKIE</b>, our warm, cheerful AI cookie mascot! Fed and trained with our complete official bakery knowledge base. 
                Ask about our ingredients, flavors, baking secrets, prices, party boxes, or delivery times!
            </p>
        </div>
        """)
    with col_bot_img:
        if logo_b64:
            render_html(f"""
            <div style="text-align: center;">
                <img src="data:image/jpeg;base64,{logo_b64}" 
                     style="width: 125px; height: 125px; object-fit: cover; border-radius: 50%; 
                            border: 3px solid #D97706; box-shadow: 0 8px 22px rgba(42, 19, 7, 0.25);" 
                     alt="POOKIE Mascot" />
            </div>
            """)

    render_html("<div style='height: 10px;'></div>")

    # Quick Suggestion Chips
    st.markdown("**💡 Quick questions to ask POOKIE:**")
    q_col1, q_col2, q_col3, q_col4 = st.columns(4)
    quick_prompt = None

    with q_col1:
        if st.button("🍪 What is a Brookie?", key="q_brookie", use_container_width=True):
            quick_prompt = "What is a Brookie and what makes it special?"
    with q_col2:
        if st.button("🏷️ What are your prices?", key="q_prices", use_container_width=True):
            quick_prompt = "How much do your cookies, brookies, and brownies cost?"
    with q_col3:
        if st.button("🧈 Tell me about ingredients", key="q_ingred", use_container_width=True):
            quick_prompt = "What ingredients do you use in your cookies?"
    with q_col4:
        if st.button("📦 How do I order?", key="q_order", use_container_width=True):
            quick_prompt = "How can I order and what are your phone numbers?"

    render_html("<div style='height: 15px;'></div>")

    # Chat Conversation Display Container
    chat_container = st.container()

    with chat_container:
        for msg in st.session_state.chat_history:
            if msg["role"] == "user":
                with st.chat_message("user", avatar="👤"):
                    st.markdown(f"**You:** {msg['content']}")
            else:
                with st.chat_message("assistant", avatar="🍪"):
                    st.markdown(f"**POOKIE:** {msg['content']}")

    # Handle User Input (via chat input or quick prompt button)
    user_input = st.chat_input("Ask POOKIE anything sweet...") or quick_prompt

    if user_input:
        # Append User Message
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        with st.chat_message("user", avatar="👤"):
            st.markdown(f"**You:** {user_input}")

        # Generate Response via Gemini
        with st.chat_message("assistant", avatar="🍪"):
            with st.spinner("POOKIE is thinking of something delicious... 🍪💭"):
                pookie_reply = ""
                try:
                    client = genai.Client(api_key=GEMINI_API_KEY)

                    system_instruction = f"""You are POOKIE, the adorable, cheerful, and enthusiastic mascot & AI bakery assistant for the brand COOKIE POOKIE.
You are trained on and have full access to the official COOKIE POOKIE knowledge base below:

=== OFFICIAL KNOWLEDGE BASE ===
{KNOWLEDGE_BASE}
=== END KNOWLEDGE BASE ===

Your Persona:
- Name: POOKIE.
- Tone: Warm, sweet, polite, bubbly, and charming. Use cookie and sweet emojis occasionally (🍪, 🍫, ✨, 🤤).
- Facts to stick strictly to:
  * Brand: COOKIE POOKIE ("Freshly Homemade with Love")
  * Products:
    1. Choc Chip Cookie (PKR 200) - golden crisp edges, soft chewy center, Belgian semi-sweet chocolate chunks.
    2. BROOKIE (PKR 200) - half fudgy dark chocolate brownie, half golden chocolate chip cookie dough.
    3. BROWNIE (PKR 200) - dense, ultra-fudgy dark chocolate square with crackly crust and chocolate drizzle.
  * Price: Flat PKR 200 per piece.
  * Ingredients: 100% pure creamery butter, real Belgian chocolate, Dutch cocoa, cane sugar, sea salt. Never margarine, artificial flavorings, or preservatives.
  * Hotlines: 0300-8237849 & 0300-8233395.
  * Delivery: Approx 30-45 mins, baked fresh on-demand so cookies arrive warm.
  * Operating Hours: Monday to Sunday, 11:00 AM – 1:00 AM (midnight cravings covered!).
  * Payments: Cash on Delivery (COD) & Bank Transfer.
  * How to order: Customers can click "Signature Menu" in the webapp to assemble their box, or message our hotlines on WhatsApp!

Keep answers concise, helpful, and mouthwatering. If asked anything unrelated to baking or cookies, playfully bring the conversation back to warm cookies!"""

                    # Build conversation context
                    contents = []
                    # Keep last 6 exchanges for context
                    recent_history = st.session_state.chat_history[-7:-1]
                    for h in recent_history:
                        contents.append(f"{h['role'].upper()}: {h['content']}")
                    contents.append(f"USER: {user_input}")
                    conversation_text = "\n\n".join(contents)

                    # Try primary model gemini-3.5-flash with fallback
                    model_to_use = "gemini-3.5-flash"
                    try:
                        response = client.models.generate_content(
                            model=model_to_use,
                            contents=conversation_text,
                            config={"system_instruction": system_instruction}
                        )
                        pookie_reply = response.text
                    except Exception:
                        response = client.models.generate_content(
                            model="gemini-3.1-flash-lite",
                            contents=conversation_text,
                            config={"system_instruction": system_instruction}
                        )
                        pookie_reply = response.text

                except Exception as e:
                    # Intelligent Offline Fallback
                    u_lower = user_input.lower()
                    if "brookie" in u_lower:
                        pookie_reply = "Our **BROOKIE** is pure heaven! 🍫🍪 It's the ultimate hybrid: half decadent fudgy dark brownie and half chewy golden chocolate chip cookie dough. And it's only **PKR 200**! Want me to help you order one?"
                    elif "price" in u_lower or "cost" in u_lower or "how much" in u_lower:
                        pookie_reply = "Every single treat at Cookie Pookie is flat **PKR 200**! 🏷️ That includes our Choc Chip Cookie, Brookie, and Brownie. Gourmet bakery luxury at an unbeatable price!"
                    elif "ingredient" in u_lower or "butter" in u_lower:
                        pookie_reply = "We believe in pure love and quality! 🧈 We use 100% pure creamery butter, rich Belgian chocolate chunks, and Dutch cocoa. We NEVER use margarine or artificial preservatives!"
                    elif "order" in u_lower or "number" in u_lower or "phone" in u_lower or "whatsapp" in u_lower:
                        pookie_reply = "You can order directly through our **Menu** page in this app, or message our hotlines on WhatsApp: **0300-8237849** or **0300-8233395**! 💬 We bake on-demand and deliver warm in 30-45 mins!"
                    elif "brownie" in u_lower:
                        pookie_reply = "Our **BROWNIE** is ultra-dense, intensely fudgy, and packed with double dark melted chocolate with that iconic crinkly top crust! 🍫 For just **PKR 200**!"
                    else:
                        pookie_reply = f"Hello from POOKIE! 🍪✨ Freshly homemade with 100% pure butter and Belgian chocolate! All our treats (Choc Chip Cookie, Brookie, Brownie) are flat **PKR 200** each. Call or WhatsApp us at **0300-8237849** to get yours warm!"

                st.markdown(f"**POOKIE:** {pookie_reply}")
                st.session_state.chat_history.append({"role": "assistant", "content": pookie_reply})

    # Clear chat button
    c_btn1, c_btn2 = st.columns([4, 1])
    with c_btn2:
        if st.button("🗑️ Reset Chat", key="clear_chat_btn", use_container_width=True):
            st.session_state.chat_history = [
                {
                    "role": "assistant",
                    "content": "Hi there! I'm **POOKIE** 🍪✨, your sweetest cookie companion! Ask me anything about our freshly homemade Choc Chip Cookies, Brookies, Brownies, ingredients, delivery times, or how to place your order!"
                }
            ]
            st.rerun()


# =========================================================
# PAGE 4: CONTACT US
# =========================================================
elif st.session_state.current_page == "Contact":
    render_html("""
    <div style="text-align: center; margin-bottom: 30px;">
        <span class="gold-ribbon">GET IN TOUCH</span>
        <h1 style="font-size: 3rem; margin: 8px 0; color: #150601 !important;">We're Always Ready To Bake For You!</h1>
        <p style="color: #4A220C; font-size: 1.15rem; max-width: 680px; margin: 0 auto; font-weight: 500;">
            Whether you want a quick midnight box, custom party catering, or have a question about our ingredients, reach out directly!
        </p>
    </div>
    """)

    ct_col1, ct_col2 = st.columns([1, 1], gap="large")

    with ct_col1:
        render_html("""
        <div style="background: #FFFFFF; border-radius: 24px; padding: 28px; border: 2px solid #E8D3BD; box-shadow: 0 10px 25px rgba(42, 19, 7, 0.08); margin-bottom: 22px;">
            <h3 style="margin-top: 0; font-size: 1.45rem; color: #150601 !important;">📞 Direct Baking Hotlines</h3>
            <p style="color: #4A220C; font-size: 0.95rem; margin-bottom: 18px;">
                Call us directly or send a WhatsApp message for instant response:
            </p>
            <div style="display: flex; flex-direction: column; gap: 14px;">
                <a href="tel:03008237849" style="text-decoration: none;">
                    <div style="background: #FDF8F0; border: 2px solid #D97706; padding: 14px 20px; border-radius: 16px; font-family: 'Montserrat', sans-serif; font-size: 1.25rem; font-weight: 800; color: #150601; display: flex; justify-content: space-between; align-items: center;">
                        <span>📱 0300-8237849</span>
                        <span style="font-size: 0.88rem; color: #D97706; font-family: 'Plus Jakarta Sans', sans-serif;">Call Now ↗</span>
                    </div>
                </a>
                <a href="tel:03008233395" style="text-decoration: none;">
                    <div style="background: #FDF8F0; border: 2px solid #D97706; padding: 14px 20px; border-radius: 16px; font-family: 'Montserrat', sans-serif; font-size: 1.25rem; font-weight: 800; color: #150601; display: flex; justify-content: space-between; align-items: center;">
                        <span>📱 0300-8233395</span>
                        <span style="font-size: 0.88rem; color: #D97706; font-family: 'Plus Jakarta Sans', sans-serif;">Call Now ↗</span>
                    </div>
                </a>
            </div>
        </div>
        """)

        render_html("""
        <div style="background: #FFFFFF; border-radius: 24px; padding: 28px; border: 2px solid #E8D3BD; box-shadow: 0 10px 25px rgba(42, 19, 7, 0.08);">
            <h3 style="margin-top: 0; font-size: 1.45rem; color: #150601 !important;">🕒 Operating Schedule & Info</h3>
            <ul style="color: #4A220C; line-height: 2; font-size: 0.96rem; padding-left: 20px; margin: 0;">
                <li><b>Baking Hours:</b> Monday – Sunday (11:00 AM – 1:00 AM)</li>
                <li><b>Delivery Time:</b> Approx 30–45 mins so treats arrive fresh & warm</li>
                <li><b>Bulk / Event Boxes:</b> Custom assorted packaging available</li>
                <li><b>Payment:</b> Cash on Delivery (COD) & Bank Transfer</li>
            </ul>
        </div>
        """)

    with ct_col2:
        render_html("""
        <div style="background: #FFFFFF; border-radius: 24px; padding: 30px; border: 2px solid #E8D3BD; box-shadow: 0 12px 28px rgba(42, 19, 7, 0.09);">
            <h3 style="margin-top: 0; font-size: 1.5rem; color: #150601 !important;">💌 Send Us a Message</h3>
            <p style="color: #4A220C; font-size: 0.95rem; margin-bottom: 20px;">
                Leave your details below and we'll get right back to you!
            </p>
        </div>
        """)

        with st.form("contact_inquiry_form", clear_on_submit=True):
            user_name = st.text_input("Your Name *", placeholder="e.g. Sara Ahmed")
            user_phone = st.text_input("Phone / WhatsApp *", placeholder="0300-XXXXXXX")
            inquiry_type = st.selectbox("What can we help you with?", [
                "Place an Order", 
                "Party / Event Bulk Order", 
                "Feedback / Review", 
                "Other Question"
            ])
            user_msg = st.text_area("Your Message *", placeholder="Tell us how we can satisfy your sweet tooth...")
            satisfaction = st.slider("How excited are you to try Cookie Pookie? 🍪", 1, 5, 5)

            form_submit = st.form_submit_button("Send Sweet Note 💌", use_container_width=True)
            if form_submit:
                if user_name and user_phone and user_msg:
                    st.balloons()
                    st.success(f"Thank you, {user_name}! 🎉 Your message has been received with a {satisfaction}-star rating! We will contact you at {user_phone} shortly.")
                else:
                    st.error("Please provide your name, phone number, and a message!")

# ---------------------------------------------------------
# Footer
# ---------------------------------------------------------
render_html("<div style='height: 50px;'></div>")
render_html("""
<div style="text-align: center; padding: 25px 0 15px 0; border-top: 2px solid #E8D3BD; color: #4A220C; font-size: 0.95rem;">
    <p style="margin: 0 0 6px 0; font-family: 'Montserrat', sans-serif; font-size: 1.25rem; font-weight: 800; color: #150601;">
        COOKIE POOKIE — Freshly Homemade with Love
    </p>
    <p style="margin: 0; font-size: 0.88rem; color: #8E460E; font-weight: 600;">
        Hotlines: 0300-8237849 &nbsp;|&nbsp; 0300-8233395 &nbsp;|&nbsp; Flat PKR 200 Fresh Treats
    </p>
</div>
""")
