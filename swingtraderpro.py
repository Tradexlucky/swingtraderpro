"""
SwingTrader Pro — Single File Streamlit App
Supabase backend, no complex frameworks!
Fixes: sidebar navigation, forgot password, news fetch, CMP display, user invitations
"""

import streamlit as st
import hashlib
import datetime
import requests
from supabase import create_client

# ── Page Config ────────────────────────────────────────────
st.set_page_config(
    page_title="SwingTrader Pro",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Supabase Config ────────────────────────────────────────
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
ADMIN_EMAIL  = st.secrets["ADMIN_EMAIL"]

@st.cache_resource
def get_supabase():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

sb = get_supabase()

# ── CSS ────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&family=JetBrains+Mono:wght@400;600&display=swap');

:root {
  --bg:      #080c14;
  --bg2:     #0d1220;
  --bg3:     #111827;
  --accent:  #00d4ff;
  --green:   #00e676;
  --red:     #ff4444;
  --yellow:  #ffd600;
  --text1:   #f0f4ff;
  --text2:   #8899bb;
  --text3:   #4a5568;
  --border:  #1e2a3a;
}

html, body, [data-testid="stAppViewContainer"] {
  background: var(--bg) !important;
  font-family: 'DM Sans', sans-serif !important;
  color: var(--text1) !important;
}

[data-testid="stSidebar"] {
  background: var(--bg2) !important;
  border-right: 1px solid var(--border) !important;
  display: block !important;
  visibility: visible !important;
  min-width: 250px !important;
}
[data-testid="stSidebar"] > div:first-child {
  display: block !important;
  padding-top: 1rem !important;
}
/* Hide collapse button */
button[data-testid="collapsedControl"] {
  display: none !important;
}

h1,h2,h3 { font-family: 'Syne', sans-serif !important; }

/* Main buttons */
.stButton > button {
  background: var(--accent) !important;
  color: #000 !important;
  font-weight: 700 !important;
  border: none !important;
  border-radius: 8px !important;
  font-family: 'Syne', sans-serif !important;
  transition: all 0.2s !important;
}
.stButton > button:hover {
  background: #00b8d9 !important;
  transform: translateY(-1px);
}

/* Sidebar nav buttons — override main button style */
[data-testid="stSidebar"] .stButton > button {
  background: transparent !important;
  color: var(--text2) !important;
  border: 1px solid var(--border) !important;
  width: 100% !important;
  text-align: left !important;
  margin-bottom: 4px !important;
  font-family: 'DM Sans', sans-serif !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
  background: var(--bg3) !important;
  color: var(--accent) !important;
  border-color: var(--accent) !important;
}

.stTextInput > div > div > input,
.stSelectbox > div > div,
.stNumberInput > div > div > input,
.stDateInput > div > div > input,
.stTextArea > div > div > textarea {
  background: var(--bg3) !important;
  color: var(--text1) !important;
  border: 1px solid var(--border) !important;
  border-radius: 8px !important;
}

.stTextInput > label, .stSelectbox > label,
.stNumberInput > label, .stDateInput > label,
.stTextArea > label {
  color: var(--text2) !important;
  font-size: 12px !important;
}

.metric-card {
  background: var(--bg2);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 20px;
  text-align: center;
}
.metric-val {
  font-family: 'DM Sans', Arial, sans-serif !important;
  font-size: 32px !important;
  font-weight: 800 !important;
  margin: 4px 0 !important;
  line-height: 1.3 !important;
  display: block !important;
}
.metric-label {
  font-size: 12px;
  color: var(--text2);
  text-transform: uppercase;
  letter-spacing: 1px;
}

.stock-card {
  background: var(--bg2);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 16px;
  margin-bottom: 12px;
  transition: all 0.2s;
}
.stock-card:hover { border-color: var(--accent); }

.badge {
  display: inline-block;
  padding: 3px 10px;
  border-radius: 20px;
  font-size: 11px;
  font-weight: 700;
  font-family: 'Syne', sans-serif;
}
.badge-buy  { background: #00e67622; color: var(--green); border: 1px solid #00e67644; }
.badge-sell { background: #ff444422; color: var(--red);   border: 1px solid #ff444444; }
.badge-watch{ background: #ffd60022; color: var(--yellow);border: 1px solid #ffd60044; }

.trade-row {
  background: var(--bg2);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 12px 16px;
  margin-bottom: 8px;
}

.news-card {
  background: var(--bg2);
  border: 1px solid var(--border);
  border-left: 3px solid var(--accent);
  border-radius: 8px;
  padding: 14px 16px;
  margin-bottom: 10px;
}

.page-title {
  font-family: 'Syne', sans-serif;
  font-size: 28px;
  font-weight: 800;
  color: var(--text1);
  margin-bottom: 4px;
}
.page-sub {
  font-size: 13px;
  color: var(--text2);
  margin-bottom: 24px;
}
.divider {
  border: none;
  border-top: 1px solid var(--border);
  margin: 20px 0;
}

.stDataFrame { background: var(--bg2) !important; }
.stAlert { border-radius: 8px !important; }
#MainMenu, footer, header { visibility: hidden; }
.stDeployButton { display: none; }
</style>
""", unsafe_allow_html=True)


# ── Auth Helpers ───────────────────────────────────────────
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def get_user_by_email(email: str):
    try:
        res = sb.table("users").select("*").eq("email", email.strip().lower()).execute()
        return res.data[0] if res.data else None
    except:
        return None

def get_user_by_username(username: str):
    try:
        res = sb.table("users").select("*").eq("username", username.strip()).execute()
        return res.data[0] if res.data else None
    except:
        return None

def create_user(username, email, password):
    try:
        sb.table("users").insert({
            "username": username.strip(),
            "email": email.strip().lower(),
            "password_hash": hash_password(password),
            "role": "admin" if email.strip().lower() == ADMIN_EMAIL.strip().lower() else "user",
            "status": "approved" if email.strip().lower() == ADMIN_EMAIL.strip().lower() else "pending",
            "created_at": datetime.datetime.now().isoformat()
        }).execute()
        return True
    except:
        return False

def login_user(email, password):
    user = get_user_by_email(email)
    if not user:
        return None, "Email milala nahi!"
    if user["password_hash"] != hash_password(password):
        return None, "Password chukiche ahe!"
    if user["status"] == "pending":
        return None, "Tuzha account pending ahe — admin approval var wait kar!"
    if user["status"] == "blocked":
        return None, "Tuzha account blocked ahe!"
    try:
        sb.table("users").update({
            "last_login": datetime.datetime.now().isoformat()
        }).eq("id", user["id"]).execute()
    except:
        pass
    return user, None

def reset_password(email, new_password):
    try:
        sb.table("users").update({
            "password_hash": hash_password(new_password)
        }).eq("email", email.strip().lower()).execute()
        return True
    except:
        return False


# ── Session State ──────────────────────────────────────────
if "user" not in st.session_state:
    st.session_state.user = None
if "page" not in st.session_state:
    st.session_state.page = "scanner"
if "auth_tab" not in st.session_state:
    st.session_state.auth_tab = "login"


# ── Auth Pages ─────────────────────────────────────────────
def show_auth():
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown("""
        <div style='text-align:center; padding: 40px 0 20px'>
          <div style='font-family:Syne; font-size:42px; font-weight:800; color:#00d4ff'>📈 SwingTrader</div>
          <div style='color:#8899bb; font-size:14px; margin-top:4px'>Professional Swing Trading Platform · Indian Markets</div>
        </div>
        """, unsafe_allow_html=True)

        # FIX: Use buttons instead of tabs to avoid sidebar navigation issue
        b1, b2, b3 = st.columns(3)
        with b1:
            if st.button("🔐 Login", use_container_width=True, key="auth_login_btn"):
                st.session_state.auth_tab = "login"; st.rerun()
        with b2:
            if st.button("📝 Register", use_container_width=True, key="auth_reg_btn"):
                st.session_state.auth_tab = "register"; st.rerun()
        with b3:
            if st.button("🔓 Forgot Password", use_container_width=True, key="auth_forgot_btn"):
                st.session_state.auth_tab = "forgot"; st.rerun()

        st.markdown("<hr style='border-color:#1e2a3a; margin:12px 0'>", unsafe_allow_html=True)

        # ── LOGIN ──
        if st.session_state.auth_tab == "login":
            st.markdown("#### 🔐 Login")
            email    = st.text_input("Email", key="li_email", placeholder="your@email.com")
            password = st.text_input("Password", type="password", key="li_pass")
            if st.button("Login →", key="login_btn", use_container_width=True):
                if email and password:
                    user, err = login_user(email, password)
                    if user:
                        st.session_state.user = user
                        st.session_state.page = "scanner"
                        st.success(f"Welcome back, {user['username']}! 🎉")
                        st.rerun()
                    else:
                        st.error(err)
                else:
                    st.warning("Email ani password bhara!")

        # ── REGISTER ──
        elif st.session_state.auth_tab == "register":
            st.markdown("#### 📝 Register")
            username = st.text_input("Username", key="reg_user", placeholder="YourName")
            email2   = st.text_input("Email", key="reg_email", placeholder="your@email.com")
            pass2    = st.text_input("Password", type="password", key="reg_pass")
            pass3    = st.text_input("Confirm Password", type="password", key="reg_pass2")
            if st.button("Register →", key="reg_btn", use_container_width=True):
                if not all([username, email2, pass2, pass3]):
                    st.warning("Sagale fields bhara!")
                elif pass2 != pass3:
                    st.error("Passwords match nahi!")
                elif len(pass2) < 6:
                    st.error("Password 6+ characters pahije!")
                elif get_user_by_email(email2):
                    st.error("He email already registered ahe!")
                else:
                    if create_user(username, email2, pass2):
                        if email2.strip().lower() == ADMIN_EMAIL.strip().lower():
                            st.success("Admin account tayar! Login kara.")
                        else:
                            st.success("Registration zali! Admin approval nantar login karta yeil.")
                    else:
                        st.error("Registration failed — try again!")

        # ── FORGOT PASSWORD ──
        elif st.session_state.auth_tab == "forgot":
            st.markdown("#### 🔓 Reset Password")
            forgot_email = st.text_input("Registered Email", key="forgot_email", placeholder="your@email.com")
            new_pass1    = st.text_input("New Password", type="password", key="new_pass1")
            new_pass2    = st.text_input("Confirm New Password", type="password", key="new_pass2")

            if st.button("Reset Password →", key="forgot_btn", use_container_width=True):
                if not forgot_email or not new_pass1 or not new_pass2:
                    st.warning("Sagale fields bhara!")
                elif new_pass1 != new_pass2:
                    st.error("Passwords match nahi!")
                elif len(new_pass1) < 6:
                    st.error("Password 6+ characters pahije!")
                else:
                    user = get_user_by_email(forgot_email)
                    if not user:
                        st.error("He email registered nahi ahe!")
                    else:
                        if reset_password(forgot_email, new_pass1):
                            st.success("✅ Password reset zala! Ata login kara.")
                            st.session_state.auth_tab = "login"
                            st.rerun()
                        else:
                            st.error("Reset failed — try again!")


# ── Sidebar ────────────────────────────────────────────────
def show_sidebar():
    user = st.session_state.user
    with st.sidebar:
        st.markdown(f"""
        <div style='padding:16px 0 20px; border-bottom:1px solid var(--border); margin-bottom:16px'>
          <div style='font-family:Syne; font-size:20px; font-weight:800; color:#00d4ff'>📈 SwingTrader</div>
          <div style='font-size:12px; color:#8899bb; margin-top:4px'>
            {user['username']} · <span style='color:{"#00e676" if user["role"]=="admin" else "#ffd600"}'>{"👑 Admin" if user["role"]=="admin" else "👤 User"}</span>
          </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<div style='font-size:11px; color:var(--text3); text-transform:uppercase; letter-spacing:1px; margin-bottom:8px'>Navigation</div>", unsafe_allow_html=True)

        pages = [
            ("📊", "scanner",  "Algo Scanner"),
            ("📖", "journal",  "Trading Journal"),
            ("⚡", "risk",     "Risk Calculator"),
            ("📰", "news",     "Market News"),
        ]
        if user["role"] == "admin":
            pages.append(("👑", "admin", "Admin Panel"))

        for icon, page_key, label in pages:
            if st.button(f"{icon}  {label}", key=f"nav_{page_key}", use_container_width=True):
                st.session_state.page = page_key
                st.rerun()

        st.markdown("<hr style='border-color:var(--border); margin:20px 0'>", unsafe_allow_html=True)
        if st.button("🚪  Logout", use_container_width=True, key="logout_btn"):
            st.session_state.user = None
            st.session_state.page = "scanner"
            st.rerun()


# ── Scanner Page ───────────────────────────────────────────
def page_scanner():
    user = st.session_state.user
    st.markdown("<div class='page-title'>📊 Algo Scanner</div>", unsafe_allow_html=True)
    st.markdown("<div class='page-sub'>Today's swing trading opportunities · Daily 4:30 PM IST auto-scan</div>", unsafe_allow_html=True)

    today = datetime.date.today().isoformat()
    try:
        res = sb.table("scan_results").select("*").eq("scan_date", today).order("created_at", desc=True).execute()
        results = res.data or []
    except:
        results = []

    buys  = sum(1 for r in results if r["signal"] == "BUY")
    sells = sum(1 for r in results if r["signal"] == "SELL")

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"<div class='metric-card'><div class='metric-label'>Total Signals</div><div class='metric-val' style='color:#00d4ff'>{len(results)}</div></div>", unsafe_allow_html=True)
    with c2:
        st.markdown(f"<div class='metric-card'><div class='metric-label'>Buy Signals</div><div class='metric-val' style='color:#00e676'>{buys}</div></div>", unsafe_allow_html=True)
    with c3:
        st.markdown(f"<div class='metric-card'><div class='metric-label'>Sell Signals</div><div class='metric-val' style='color:#ff4444'>{sells}</div></div>", unsafe_allow_html=True)
    with c4:
        st.markdown(f"<div class='metric-card'><div class='metric-label'>Scan Date</div><div class='metric-val' style='font-size:18px'>{today}</div></div>", unsafe_allow_html=True)

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)

    # Admin: Add Stock Form
    if user["role"] == "admin":
        with st.expander("➕ Nava Stock Add Kara", expanded=False):
            c1, c2, c3 = st.columns(3)
            with c1:
                sym    = st.text_input("Symbol *", placeholder="e.g. RELIANCE", key="scan_sym").upper().strip()
                signal = st.selectbox("Signal", ["BUY", "SELL", "WATCH"], key="scan_signal")
                # FIX: CMP as simple number input, no special formatting issues
                cmp    = st.number_input("CMP / Current Price (₹)", min_value=0.0, step=0.05, format="%.2f", key="scan_cmp")
            with c2:
                entry  = st.number_input("Entry Price (₹) *", min_value=0.0, step=0.05, format="%.2f", key="scan_entry")
                sl     = st.number_input("Stop Loss (₹) *", min_value=0.0, step=0.05, format="%.2f", key="scan_sl")
                tp     = st.number_input("Target (₹) *", min_value=0.0, step=0.05, format="%.2f", key="scan_tp")
            with c3:
                notes  = st.text_input("Notes / Setup", placeholder="VCP Breakout, EMA Cross...", key="scan_notes")
                # Live RR preview
                if entry > 0 and sl > 0 and tp > 0:
                    risk   = abs(entry - sl)
                    reward = abs(tp - entry)
                    rr     = round(reward / risk, 2) if risk > 0 else 0
                    color  = "#00e676" if rr >= 2 else "#ffd600" if rr >= 1 else "#ff4444"
                    st.markdown(f"""
                    <div style='background:var(--bg3); border-radius:8px; padding:12px; margin-top:8px; text-align:center'>
                      <div style='font-family:JetBrains Mono; font-size:24px; font-weight:700; color:{color}'>1 : {rr}</div>
                      <div style='font-size:11px; color:var(--text2)'>Risk:Reward</div>
                      <div style='font-size:12px; color:var(--text2); margin-top:4px'>Risk ₹{round(risk,2)} · Reward ₹{round(reward,2)}</div>
                    </div>
                    """, unsafe_allow_html=True)

            if st.button("✅ Stock Add Kara", use_container_width=True, key="scan_add_btn"):
                if not sym:
                    st.error("Symbol required!")
                elif not entry or not sl or not tp:
                    st.error("Entry, SL aani Target required!")
                else:
                    try:
                        sb.table("scan_results").insert({
                            "scan_date": today,
                            "symbol": sym,
                            "signal": signal,
                            "price": float(cmp) if cmp else None,
                            "entry": float(entry),
                            "sl": float(sl),
                            "tp": float(tp),
                            "notes": notes,
                            "added_by": user["id"]
                        }).execute()
                        st.success(f"✅ {sym} added! Users la disel ata.")
                        _notify_users_new_stock(sym, signal, entry, sl, tp, notes)
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")

    # Show Stocks
    if not results:
        st.markdown("""
        <div style='text-align:center; padding:60px; background:var(--bg2); border-radius:12px; border:1px solid var(--border)'>
          <div style='font-size:48px'>📭</div>
          <div style='font-family:Syne; font-size:20px; margin-top:16px'>Aajache Scan Pending</div>
          <div style='color:var(--text2); font-size:13px; margin-top:8px'>Admin ne stocks add kelya ki ithech disel.</div>
        </div>
        """, unsafe_allow_html=True)
        return

    # Stock Cards — 3 per row
    cols = st.columns(3)
    for i, r in enumerate(results):
        signal_class = "badge-buy" if r["signal"] == "BUY" else "badge-sell" if r["signal"] == "SELL" else "badge-watch"

        rr_html = ""
        if r.get("entry") and r.get("sl") and r.get("tp"):
            risk   = abs(float(r["entry"]) - float(r["sl"]))
            reward = abs(float(r["tp"]) - float(r["entry"]))
            rr     = round(reward / risk, 2) if risk > 0 else 0
            rr_col = "#00e676" if rr >= 2 else "#ffd600" if rr >= 1 else "#ff4444"
            rr_html = f"<div style='font-size:12px; color:{rr_col}; font-family:JetBrains Mono; margin-top:4px'>R:R = 1:{rr}</div>"

        # FIX: CMP display — properly handle None and show correctly
        cmp_val = r.get("price")
        cmp_html = ""
        if cmp_val is not None and cmp_val != 0:
            cmp_html = f"<div style='font-family:JetBrains Mono; font-size:13px; color:var(--text2); margin-top:6px'>CMP: <span style='color:var(--text1)'>₹{float(cmp_val):,.2f}</span></div>"

        price_html = ""
        if r.get("entry"):
            price_html = f"""
            <div style='margin-top:10px; font-size:12px; display:flex; flex-direction:column; gap:4px'>
              <div style='display:flex;justify-content:space-between'>
                <span style='color:var(--text3)'>Entry</span>
                <span style='font-family:JetBrains Mono; color:#00d4ff'>₹{float(r['entry']):,.2f}</span>
              </div>
              <div style='display:flex;justify-content:space-between'>
                <span style='color:var(--text3)'>SL</span>
                <span style='font-family:JetBrains Mono; color:#ff4444'>₹{float(r['sl']):,.2f}</span>
              </div>
              <div style='display:flex;justify-content:space-between'>
                <span style='color:var(--text3)'>Target</span>
                <span style='font-family:JetBrains Mono; color:#00e676'>₹{float(r['tp']):,.2f}</span>
              </div>
            </div>"""

        notes_html = f"<div style='font-size:11px; color:var(--text3); margin-top:8px'>{r['notes']}</div>" if r.get("notes") else ""

        with cols[i % 3]:
            st.markdown(f"""
            <div class='stock-card'>
              <div style='display:flex; justify-content:space-between; align-items:start'>
                <div style='font-family:JetBrains Mono; font-size:18px; font-weight:700'>{r["symbol"]}</div>
                <span class='badge {signal_class}'>{r["signal"]}</span>
              </div>
              {cmp_html}
              {price_html}
              {rr_html}
              {notes_html}
            </div>
            """, unsafe_allow_html=True)

            if user["role"] == "admin":
                if st.button("🗑 Remove", key=f"del_{r['id']}"):
                    sb.table("scan_results").delete().eq("id", r["id"]).execute()
                    st.rerun()


def _notify_users_new_stock(symbol, signal, entry, sl, tp, notes):
    """Email pathav saglya approved users la."""
    try:
        smtp_user = st.secrets.get("SMTP_USER", "")
        smtp_pass = st.secrets.get("SMTP_PASS", "")
        smtp_host = st.secrets.get("SMTP_HOST", "smtp.gmail.com")
        smtp_port = int(st.secrets.get("SMTP_PORT", 587))
        if not smtp_user or not smtp_pass:
            return

        users = sb.table("users").select("email,username").eq("status", "approved").execute()
        if not users.data:
            return

        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart

        subject = f"📈 New Signal: {symbol} {signal} — SwingTrader Pro"
        body = f"""
<html><body style="font-family:Arial; background:#080c14; color:#f0f4ff; padding:20px">
<div style="max-width:500px; margin:0 auto; background:#0d1220; border-radius:12px; padding:24px; border:1px solid #1e2a3a">
  <h2 style="color:#00d4ff">📈 New Algo Signal</h2>
  <div style="background:#111827; border-radius:8px; padding:16px; margin:16px 0">
    <div style="font-size:28px; font-weight:bold; color:{'#00e676' if signal=='BUY' else '#ff4444'}">{symbol} — {signal}</div>
    <table style="width:100%; margin-top:12px; font-size:14px">
      <tr><td style="color:#8899bb; padding:4px 0">Entry Price</td><td style="color:#00d4ff; font-weight:bold; text-align:right">₹{entry}</td></tr>
      <tr><td style="color:#8899bb; padding:4px 0">Stop Loss</td><td style="color:#ff4444; font-weight:bold; text-align:right">₹{sl}</td></tr>
      <tr><td style="color:#8899bb; padding:4px 0">Target</td><td style="color:#00e676; font-weight:bold; text-align:right">₹{tp}</td></tr>
    </table>
    {"<div style='margin-top:12px; font-size:13px; color:#8899bb'>Setup: " + notes + "</div>" if notes else ""}
  </div>
  <div style="font-size:12px; color:#4a5568; margin-top:16px">SwingTrader Pro · Indian Markets</div>
</div>
</body></html>"""

        server = smtplib.SMTP(smtp_host, smtp_port)
        server.starttls()
        server.login(smtp_user, smtp_pass)
        for u in users.data:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"]    = f"SwingTrader Pro <{smtp_user}>"
            msg["To"]      = u["email"]
            msg.attach(MIMEText(body, "html"))
            server.sendmail(smtp_user, u["email"], msg.as_string())
        server.quit()
    except Exception as e:
        pass  # Silent fail — don't block UI


# ── Journal Page ───────────────────────────────────────────
def page_journal():
    user = st.session_state.user
    st.markdown("<div class='page-title'>📖 Trading Journal</div>", unsafe_allow_html=True)
    st.markdown("<div class='page-sub'>Tuzhe sagale trades track kar ani analytics bagh</div>", unsafe_allow_html=True)

    try:
        res = sb.table("trades").select("*").eq("user_id", user["id"]).order("trade_date", desc=True).execute()
        trades = res.data or []
    except:
        trades = []

    closed    = [t for t in trades if t.get("result")]
    total_pnl = sum(t.get("pnl", 0) or 0 for t in closed)
    wins      = sum(1 for t in closed if t.get("result") == "WIN")
    losses    = sum(1 for t in closed if t.get("result") == "LOSS")
    wr        = round((wins / len(closed)) * 100, 1) if closed else 0
    rr_vals   = [t["r_multiple"] for t in closed if t.get("r_multiple")]
    avg_rr    = round(sum(rr_vals) / len(rr_vals), 2) if rr_vals else 0

    c1, c2, c3, c4, c5 = st.columns(5)
    with c1: st.markdown(f"<div class='metric-card'><div class='metric-label'>Total Trades</div><div class='metric-val' style='color:#00d4ff'>{len(trades)}</div></div>", unsafe_allow_html=True)
    with c2: st.markdown(f"<div class='metric-card'><div class='metric-label'>Win Rate</div><div class='metric-val' style='color:#00e676'>{wr}%</div></div>", unsafe_allow_html=True)
    with c3: st.markdown(f"<div class='metric-card'><div class='metric-label'>Wins / Losses</div><div class='metric-val' style='color:#ffd600'>{wins}/{losses}</div></div>", unsafe_allow_html=True)
    with c4: st.markdown(f"<div class='metric-card'><div class='metric-label'>Avg R:R</div><div class='metric-val' style='color:#00d4ff'>{avg_rr}</div></div>", unsafe_allow_html=True)
    with c5:
        pnl_color = "#00e676" if total_pnl >= 0 else "#ff4444"
        st.markdown(f"<div class='metric-card'><div class='metric-label'>Total P&L</div><div class='metric-val' style='color:{pnl_color}'>₹{total_pnl:,.0f}</div></div>", unsafe_allow_html=True)

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)

    with st.expander("➕ Nava Trade Add Kara", expanded=False):
        c1, c2, c3 = st.columns(3)
        with c1:
            t_date  = st.date_input("Trade Date", value=datetime.date.today(), key="t_date")
            t_sym   = st.text_input("Symbol *", placeholder="RELIANCE", key="t_sym").upper().strip()
            t_dir   = st.selectbox("Direction", ["LONG", "SHORT"], key="t_dir")
            t_qty   = st.number_input("Quantity", min_value=1, value=1, key="t_qty")
        with c2:
            t_entry = st.number_input("Entry Price *", min_value=0.0, step=0.05, format="%.2f", key="t_entry")
            t_sl    = st.number_input("Stop Loss *", min_value=0.0, step=0.05, format="%.2f", key="t_sl")
            t_tgt   = st.number_input("Target *", min_value=0.0, step=0.05, format="%.2f", key="t_tgt")
            t_exit  = st.number_input("Exit Price (optional)", min_value=0.0, step=0.05, format="%.2f", key="t_exit")
        with c3:
            t_notes = st.text_area("Notes", height=100, key="t_notes")
            if t_entry > 0 and t_sl > 0 and t_tgt > 0:
                risk   = abs(t_entry - t_sl)
                reward = abs(t_tgt - t_entry)
                rr     = round(reward / risk, 2) if risk > 0 else 0
                rr_col = "#00e676" if rr >= 2 else "#ffd600" if rr >= 1 else "#ff4444"
                st.markdown(f"""
                <div style='background:var(--bg3); border-radius:8px; padding:12px; text-align:center'>
                  <div style='font-family:JetBrains Mono; font-size:22px; font-weight:700; color:{rr_col}'>1 : {rr}</div>
                  <div style='font-size:11px; color:var(--text2)'>R:R Ratio</div>
                </div>
                """, unsafe_allow_html=True)

        if st.button("✅ Trade Save Kara", use_container_width=True, key="save_trade_btn"):
            if not t_sym or not t_entry or not t_sl or not t_tgt:
                st.error("Symbol, Entry, SL, Target required!")
            else:
                risk   = abs(t_entry - t_sl)
                result = None
                pnl    = None
                r_mult = None
                if t_exit > 0:
                    pnl    = round((t_exit - t_entry) * t_qty, 2) if t_dir == "LONG" else round((t_entry - t_exit) * t_qty, 2)
                    result = "WIN" if pnl > 0 else "LOSS"
                    r_mult = round(pnl / (risk * t_qty), 2) if risk > 0 else 0

                sb.table("trades").insert({
                    "user_id": user["id"],
                    "trade_date": t_date.isoformat(),
                    "symbol": t_sym,
                    "direction": t_dir,
                    "entry_price": t_entry,
                    "stop_loss": t_sl,
                    "target_price": t_tgt,
                    "exit_price": t_exit if t_exit > 0 else None,
                    "quantity": t_qty,
                    "result": result,
                    "pnl": pnl,
                    "r_multiple": r_mult,
                    "notes": t_notes
                }).execute()
                st.success("✅ Trade saved!")
                st.rerun()

    if not trades:
        st.info("Abhi koi trade nahi — vartil form vaparoon add kara!")
        return

    st.markdown(f"**{len(trades)} Trades**")
    for t in trades:
        result_color = "#00e676" if t.get("result") == "WIN" else "#ff4444" if t.get("result") == "LOSS" else "#ffd600"
        pnl_str      = f"₹{t['pnl']:+,.0f}" if t.get("pnl") is not None else "Open"
        col1, col2   = st.columns([10, 1])
        with col1:
            st.markdown(f"""
            <div class='trade-row'>
              <div style='display:flex; gap:16px; align-items:center; flex-wrap:wrap'>
                <div style='font-family:JetBrains Mono; font-size:16px; font-weight:700; min-width:120px'>{t['symbol']}</div>
                <div style='font-size:12px; color:var(--text2)'>{t['trade_date']}</div>
                <span class='badge {"badge-buy" if t["direction"]=="LONG" else "badge-sell"}'>{t['direction']}</span>
                <div style='font-size:12px'>Entry: <span style='font-family:JetBrains Mono'>₹{float(t['entry_price']):,.2f}</span></div>
                <div style='font-size:12px'>SL: <span style='font-family:JetBrains Mono; color:#ff4444'>₹{float(t['stop_loss']):,.2f}</span></div>
                <div style='font-size:12px'>Target: <span style='font-family:JetBrains Mono; color:#00e676'>₹{float(t['target_price']):,.2f}</span></div>
                <div style='font-size:13px; font-weight:700; color:{result_color}'>{pnl_str}</div>
                {"<span class='badge badge-buy'>WIN</span>" if t.get('result') == 'WIN' else "<span class='badge badge-sell'>LOSS</span>" if t.get('result') == 'LOSS' else "<span class='badge badge-watch'>OPEN</span>"}
              </div>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            if st.button("🗑", key=f"del_trade_{t['id']}"):
                sb.table("trades").delete().eq("id", t["id"]).execute()
                st.rerun()


# ── Risk Calculator Page ───────────────────────────────────
def page_risk():
    st.markdown("<div class='page-title'>⚡ Risk Calculator</div>", unsafe_allow_html=True)
    st.markdown("<div class='page-sub'>Position sizing based on capital risk management</div>", unsafe_allow_html=True)

    c1, c2 = st.columns([1.2, 1])
    with c1:
        st.markdown("#### 📊 Position Size Calculator")
        col1, col2 = st.columns(2)
        with col1:
            capital  = st.number_input("Capital (₹)", min_value=1000.0, value=100000.0, step=1000.0, key="rc_cap")
            risk_pct = st.number_input("Risk Per Trade (%)", min_value=0.1, max_value=10.0, value=1.0, step=0.1, key="rc_rp")
        with col2:
            entry   = st.number_input("Entry Price (₹)", min_value=0.01, value=500.0, step=0.05, key="rc_e")
            sl      = st.number_input("Stop Loss (₹)", min_value=0.01, value=485.0, step=0.05, key="rc_sl")
        target = st.number_input("Target Price (₹)", min_value=0.0, value=540.0, step=0.05, key="rc_tp")

        risk_amt  = capital * (risk_pct / 100)
        sl_points = abs(entry - sl)
        position  = int(risk_amt / sl_points) if sl_points > 0 else 0
        max_loss  = round(position * sl_points, 2)
        rr = reward = 0
        if target and sl_points > 0:
            reward_pts = abs(target - entry)
            rr     = round(reward_pts / sl_points, 2)
            reward = round(position * reward_pts, 2)

        rr_color = "#00e676" if rr >= 2 else "#ffd600" if rr >= 1 else "#ff4444"
        st.markdown(f"""
        <div style='background:var(--bg2); border:1px solid var(--border); border-radius:12px; padding:20px; margin-top:16px'>
          <div style='font-family:Syne; font-size:16px; font-weight:700; margin-bottom:16px; color:var(--text2)'>RESULTS</div>
          <div style='display:grid; grid-template-columns:1fr 1fr; gap:16px'>
            <div style='text-align:center; padding:12px; background:var(--bg3); border-radius:8px'>
              <div style='font-family:JetBrains Mono; font-size:28px; font-weight:700; color:#00d4ff'>{position}</div>
              <div style='font-size:11px; color:var(--text2); margin-top:4px'>POSITION SIZE (QTY)</div>
            </div>
            <div style='text-align:center; padding:12px; background:var(--bg3); border-radius:8px'>
              <div style='font-family:JetBrains Mono; font-size:28px; font-weight:700; color:#ff4444'>₹{max_loss:,.0f}</div>
              <div style='font-size:11px; color:var(--text2); margin-top:4px'>MAX LOSS</div>
            </div>
            <div style='text-align:center; padding:12px; background:var(--bg3); border-radius:8px'>
              <div style='font-family:JetBrains Mono; font-size:28px; font-weight:700; color:{rr_color}'>1 : {rr}</div>
              <div style='font-size:11px; color:var(--text2); margin-top:4px'>RISK : REWARD</div>
            </div>
            <div style='text-align:center; padding:12px; background:var(--bg3); border-radius:8px'>
              <div style='font-family:JetBrains Mono; font-size:28px; font-weight:700; color:#00e676'>₹{reward:,.0f}</div>
              <div style='font-size:11px; color:var(--text2); margin-top:4px'>POTENTIAL PROFIT</div>
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown("#### 📚 Risk Management Rules")
        rules = [
            ("#00e676", "1% Risk Rule", "Ekka trade madhe capital cha 1-2% peksha jast risk nako."),
            ("#00d4ff", "Min 1:2 R:R", "Pratyehi risk sathi 2x reward target kar."),
            ("#ffd600", "5% Daily Loss Limit", "Din madhe 5% loss zala tar trading band kar."),
            ("#ff4444", "Position Concentration", "Eka position madhe 25% peksha jast capital nako."),
        ]
        for color, title, desc in rules:
            st.markdown(f"""
            <div style='background:var(--bg2); border-left:3px solid {color}; border-radius:8px; padding:14px 16px; margin-bottom:10px'>
              <div style='font-weight:600; font-size:13px; color:{color}'>{title}</div>
              <div style='font-size:12px; color:var(--text2); margin-top:4px; line-height:1.5'>{desc}</div>
            </div>
            """, unsafe_allow_html=True)


# ── News Page ──────────────────────────────────────────────
def page_news():
    st.markdown("<div class='page-title'>📰 Market News</div>", unsafe_allow_html=True)
    st.markdown("<div class='page-sub'>Indian market news · Latest updates</div>", unsafe_allow_html=True)

    col1, col2 = st.columns([4, 1])
    with col2:
        if st.button("↻ Refresh News", use_container_width=True, key="refresh_news"):
            with st.spinner("News fetch hoto ahe..."):
                count = _fetch_news()
                st.success(f"✅ {count} news fetched!")
            st.rerun()

    try:
        res  = sb.table("news_cache").select("*").order("fetched_at", desc=True).limit(30).execute()
        news = res.data or []
    except:
        news = []

    # FIX: Auto fetch if empty
    if not news:
        with st.spinner("News fetch hoto ahe..."):
            _fetch_news()
        try:
            res  = sb.table("news_cache").select("*").order("fetched_at", desc=True).limit(30).execute()
            news = res.data or []
        except:
            news = []

    if not news:
        st.warning("News fetch honyat problem ahe. Refresh kara!")
        # Show fallback links
        st.markdown("""
        **Direct links:**
        - [Economic Times Markets](https://economictimes.indiatimes.com/markets)
        - [Moneycontrol](https://www.moneycontrol.com)
        - [NSE India](https://www.nseindia.com)
        """)
        return

    for item in news:
        title   = item.get("title", "")
        summary = item.get("summary", "")
        source  = item.get("source", "NEWS")
        pub_at  = str(item.get("published_at", ""))[:16]
        url     = item.get("url", "")

        summary_html = f"<div style='font-size:12px; color:var(--text2); line-height:1.5; margin-top:4px'>{summary[:250]}...</div>" if summary else ""
        link_html    = f"<a href='{url}' target='_blank' style='font-size:11px; color:#00d4ff; text-decoration:none; margin-top:6px; display:inline-block'>Read More →</a>" if url else ""

        st.markdown(f"""
        <div class='news-card'>
          <div style='display:flex; justify-content:space-between; align-items:start; margin-bottom:6px'>
            <span style='font-size:11px; color:#00d4ff; font-weight:700; background:#00d4ff22; padding:2px 8px; border-radius:20px'>{source}</span>
            <span style='font-size:11px; color:var(--text3)'>{pub_at}</span>
          </div>
          <div style='font-size:14px; font-weight:600; color:var(--text1); line-height:1.4'>{title}</div>
          {summary_html}
          {link_html}
        </div>
        """, unsafe_allow_html=True)


def _fetch_news():
    """RSS feeds varun news fetch kar — returns count."""
    count = 0
    try:
        import xml.etree.ElementTree as ET

        # FIX: Multiple RSS feeds with proper headers and timeout
        feeds = [
            ("Economic Times", "https://economictimes.indiatimes.com/markets/rssfeeds/1977021501.cms"),
            ("Moneycontrol",   "https://www.moneycontrol.com/rss/MCtopnews.xml"),
            ("LiveMint",       "https://www.livemint.com/rss/markets"),
        ]

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/rss+xml, application/xml, text/xml, */*"
        }

        now = datetime.datetime.now().isoformat()

        for source, url in feeds:
            try:
                resp = requests.get(url, timeout=8, headers=headers)
                if resp.status_code != 200:
                    continue

                root  = ET.fromstring(resp.content)
                items = root.findall(".//item")[:10]

                for item in items:
                    title = item.findtext("title", "").strip()
                    link  = item.findtext("link", "").strip()
                    desc  = item.findtext("description", "").strip()
                    pub   = item.findtext("pubDate", "").strip()

                    if not title:
                        continue

                    # Clean HTML tags from description
                    import re
                    desc_clean = re.sub(r'<[^>]+>', '', desc)[:1000] if desc else ""

                    try:
                        sb.table("news_cache").upsert({
                            "title":        title[:500],
                            "summary":      desc_clean if desc_clean else None,
                            "url":          link if link else None,
                            "source":       source,
                            "published_at": pub[:50] if pub else None,
                            "fetched_at":   now,
                        }, on_conflict="title").execute()
                        count += 1
                    except:
                        continue

            except Exception:
                continue

    except Exception:
        pass

    return count


# ── Admin Page ─────────────────────────────────────────────
def page_admin():
    st.markdown("<div class='page-title'>👑 Admin Panel</div>", unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["👥 Users", "📨 Invite User", "📋 Logs"])

    with tab1:
        try:
            users = sb.table("users").select("*").order("created_at", desc=True).execute().data or []
        except:
            users = []

        pending = [u for u in users if u["status"] == "pending"]
        if pending:
            st.warning(f"⚠️ {len(pending)} users pending approval!")

        for u in users:
            status_color = "#00e676" if u["status"] == "approved" else "#ff4444" if u["status"] == "blocked" else "#ffd600"
            col1, col2, col3, col4 = st.columns([3, 2, 2, 3])
            with col1:
                st.markdown(f"""
                <div style='padding:8px 0'>
                  <div style='font-weight:600'>{u['username']}</div>
                  <div style='font-size:12px; color:var(--text2)'>{u['email']}</div>
                </div>""", unsafe_allow_html=True)
            with col2:
                st.markdown(f"<div style='padding:12px 0; font-size:12px; color:{status_color}'>{u['status'].upper()}</div>", unsafe_allow_html=True)
            with col3:
                st.markdown(f"<div style='padding:12px 0; font-size:12px; color:var(--text2)'>{u['role']}</div>", unsafe_allow_html=True)
            with col4:
                if u["status"] == "pending":
                    if st.button("✅ Approve", key=f"approve_{u['id']}"):
                        sb.table("users").update({"status": "approved"}).eq("id", u["id"]).execute()
                        st.rerun()
                elif u["status"] == "approved":
                    if st.button("🚫 Block", key=f"block_{u['id']}"):
                        sb.table("users").update({"status": "blocked"}).eq("id", u["id"]).execute()
                        st.rerun()
                elif u["status"] == "blocked":
                    if st.button("✅ Unblock", key=f"unblock_{u['id']}"):
                        sb.table("users").update({"status": "approved"}).eq("id", u["id"]).execute()
                        st.rerun()
            st.markdown("<hr style='border-color:var(--border); margin:4px 0'>", unsafe_allow_html=True)

    # FIX: Invite User tab — admin can directly add users without approval
    with tab2:
        st.markdown("#### 📨 Nava User Invite Kara")
        st.caption("He form vaparoon directly approved user add karta yeil — email invitation nako.")

        inv_username = st.text_input("Username *", key="inv_user", placeholder="Friend cha naam")
        inv_email    = st.text_input("Email *", key="inv_email", placeholder="friend@email.com")
        inv_pass     = st.text_input("Temporary Password *", key="inv_pass", placeholder="min 6 chars")
        inv_role     = st.selectbox("Role", ["user", "admin"], key="inv_role")

        if st.button("📨 User Add Kara", use_container_width=False, key="inv_btn"):
            if not all([inv_username, inv_email, inv_pass]):
                st.error("Sagale fields bhara!")
            elif len(inv_pass) < 6:
                st.error("Password 6+ chars pahije!")
            elif get_user_by_email(inv_email):
                st.error("He email already registered ahe!")
            else:
                try:
                    sb.table("users").insert({
                        "username":      inv_username.strip(),
                        "email":         inv_email.strip().lower(),
                        "password_hash": hash_password(inv_pass),
                        "role":          inv_role,
                        "status":        "approved",
                        "created_at":    datetime.datetime.now().isoformat()
                    }).execute()
                    st.success(f"✅ {inv_username} add zala! Temporary password: **{inv_pass}**")
                    st.info("Friend la email karoon sangaa: Email, Password aani website link.")
                except Exception as e:
                    st.error(f"Error: {e}")

    with tab3:
        try:
            logs = sb.table("login_logs").select("*, users(username, email)").order("login_at", desc=True).limit(50).execute().data or []
        except:
            logs = []

        if not logs:
            st.info("Koi login logs nahi yet.")
        else:
            for log in logs:
                u_name = log.get("users", {}).get("username", "Unknown") if log.get("users") else "Unknown"
                st.markdown(f"""
                <div style='padding:8px 12px; background:var(--bg2); border-radius:6px; margin-bottom:6px; font-size:12px; display:flex; gap:16px'>
                  <span style='color:var(--accent); font-weight:600'>{u_name}</span>
                  <span style='color:var(--text2)'>{str(log.get('login_at',''))[:16]}</span>
                  <span style='color:var(--text3)'>{log.get('ip_address','')}</span>
                </div>
                """, unsafe_allow_html=True)


# ── Main App ───────────────────────────────────────────────
def main():
    if not st.session_state.user:
        show_auth()
        return

    show_sidebar()

    page = st.session_state.get("page", "scanner")
    if page == "scanner":
        page_scanner()
    elif page == "journal":
        page_journal()
    elif page == "risk":
        page_risk()
    elif page == "news":
        page_news()
    elif page == "admin" and st.session_state.user["role"] == "admin":
        page_admin()
    else:
        page_scanner()


if __name__ == "__main__":
    main()
