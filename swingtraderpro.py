"""
SwingTrader Pro — Single File Streamlit App
Supabase backend, no complex frameworks!
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
}

h1,h2,h3 { font-family: 'Syne', sans-serif !important; }

.stButton > button {
  background: var(--accent) !important;
  color: #000 !important;
  font-weight: 700 !important;
  border: none !important;
  border-radius: 8px !important;
  font-family: 'Syne', sans-serif !important;
}

.stButton > button:hover {
  background: #00b8d9 !important;
  transform: translateY(-1px);
}

.stTextInput > div > div > input,
.stSelectbox > div > div,
.stNumberInput > div > div > input,
.stDateInput > div > div > input {
  background: var(--bg3) !important;
  color: var(--text1) !important;
  border: 1px solid var(--border) !important;
  border-radius: 8px !important;
}

.stTextInput > label, .stSelectbox > label,
.stNumberInput > label, .stDateInput > label {
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
  font-family: 'Syne', sans-serif;
  font-size: 28px;
  font-weight: 800;
  margin: 4px 0;
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
  display: flex;
  align-items: center;
  gap: 16px;
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

/* Sidebar nav buttons */
[data-testid="stSidebar"] .stButton > button {
  background: transparent !important;
  color: var(--text2) !important;
  border: 1px solid var(--border) !important;
  width: 100%;
  text-align: left !important;
  margin-bottom: 4px;
}

[data-testid="stSidebar"] .stButton > button:hover {
  background: var(--bg3) !important;
  color: var(--accent) !important;
  border-color: var(--accent) !important;
}

.stDataFrame { background: var(--bg2) !important; }
.stAlert { border-radius: 8px !important; }

/* Hide streamlit branding */
#MainMenu, footer, header { visibility: hidden; }
.stDeployButton { display: none; }
</style>
""", unsafe_allow_html=True)


# ── Auth Helpers ───────────────────────────────────────────
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def get_user(email: str):
    res = sb.table("users").select("*").eq("email", email).execute()
    return res.data[0] if res.data else None

def create_user(username, email, password):
    try:
        sb.table("users").insert({
            "username": username,
            "email": email,
            "password_hash": hash_password(password),
            "role": "admin" if email == ADMIN_EMAIL else "user",
            "status": "approved" if email == ADMIN_EMAIL else "pending"
        }).execute()
        return True
    except:
        return False

def login_user(email, password):
    user = get_user(email)
    if not user:
        return None, "Email milala nahi!"
    if user["password_hash"] != hash_password(password):
        return None, "Password chukiche ahe!"
    if user["status"] == "pending":
        return None, "Tuzha account pending ahe — admin approval var wait kar!"
    if user["status"] == "blocked":
        return None, "Tuzha account blocked ahe!"
    sb.table("users").update({"last_login": datetime.datetime.now().isoformat()}).eq("id", user["id"]).execute()
    return user, None


# ── Session State ──────────────────────────────────────────
if "user" not in st.session_state:
    st.session_state.user = None
if "page" not in st.session_state:
    st.session_state.page = "scanner"


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

        tab1, tab2 = st.tabs(["🔐 Login", "📝 Register"])

        with tab1:
            email    = st.text_input("Email", key="li_email")
            password = st.text_input("Password", type="password", key="li_pass")
            if st.button("Login →", key="login_btn", use_container_width=True):
                if email and password:
                    user, err = login_user(email, password)
                    if user:
                        st.session_state.user = user
                        st.success(f"Welcome back, {user['username']}! 🎉")
                        st.rerun()
                    else:
                        st.error(err)
                else:
                    st.warning("Email ani password bhara!")

        with tab2:
            username = st.text_input("Username", key="reg_user")
            email2   = st.text_input("Email", key="reg_email")
            pass2    = st.text_input("Password", type="password", key="reg_pass")
            pass3    = st.text_input("Confirm Password", type="password", key="reg_pass2")
            if st.button("Register →", key="reg_btn", use_container_width=True):
                if not all([username, email2, pass2, pass3]):
                    st.warning("Sagale fields bhara!")
                elif pass2 != pass3:
                    st.error("Passwords match nahi!")
                elif len(pass2) < 6:
                    st.error("Password 6+ characters pahije!")
                elif get_user(email2):
                    st.error("He email already registered ahe!")
                else:
                    if create_user(username, email2, pass2):
                        if email2 == ADMIN_EMAIL:
                            st.success("Admin account tayar! Login kara.")
                        else:
                            st.success("Registration zali! Admin approval nantar login karta yeil.")
                    else:
                        st.error("Registration failed — try again!")


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
            active = st.session_state.page == page_key
            if st.button(f"{icon}  {label}", key=f"nav_{page_key}",
                        use_container_width=True):
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

    # Fetch today's scans
    today = datetime.date.today().isoformat()
    res = sb.table("scan_results").select("*").eq("scan_date", today).order("created_at", desc=True).execute()
    results = res.data or []

    # Stats
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
                sym    = st.text_input("Symbol *", placeholder="e.g. RELIANCE").upper().strip()
                signal = st.selectbox("Signal", ["BUY", "SELL", "WATCH"])
                cmp    = st.number_input("CMP / Price (₹)", min_value=0.0, step=0.05)
            with c2:
                entry  = st.number_input("Entry Price (₹) *", min_value=0.0, step=0.05)
                sl     = st.number_input("Stop Loss (₹) *", min_value=0.0, step=0.05)
                tp     = st.number_input("Target (₹) *", min_value=0.0, step=0.05)
            with c3:
                notes  = st.text_input("Notes / Setup", placeholder="VCP Breakout, EMA Cross...")
                # Live RR
                if entry > 0 and sl > 0 and tp > 0:
                    risk   = abs(entry - sl)
                    reward = abs(tp - entry)
                    rr     = round(reward / risk, 2) if risk > 0 else 0
                    color  = "#00e676" if rr >= 2 else "#ffd600" if rr >= 1 else "#ff4444"
                    st.markdown(f"""
                    <div style='background:var(--bg3); border-radius:8px; padding:12px; margin-top:20px; text-align:center'>
                      <div style='font-family:JetBrains Mono; font-size:24px; font-weight:700; color:{color}'>1 : {rr}</div>
                      <div style='font-size:11px; color:var(--text2)'>Risk:Reward Ratio</div>
                      <div style='font-size:12px; color:var(--text2); margin-top:4px'>Risk ₹{round(risk,2)} · Reward ₹{round(reward,2)}</div>
                    </div>
                    """, unsafe_allow_html=True)

            if st.button("✅ Stock Add Kara", use_container_width=True):
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
                            "price": cmp,
                            "entry": entry,
                            "sl": sl,
                            "tp": tp,
                            "notes": notes,
                            "added_by": user["id"]
                        }).execute()
                        st.success(f"✅ {sym} added! Users la disel ata.")
                        # Send email notification
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
          <div style='color:var(--text2); font-size:13px; margin-top:8px'>Daily 4:30 PM IST la auto-scan hoto.</div>
        </div>
        """, unsafe_allow_html=True)
        return

    # Stock Cards — 3 per row
    cols = st.columns(3)
    for i, r in enumerate(results):
        signal_class = "badge-buy" if r["signal"] == "BUY" else "badge-sell" if r["signal"] == "SELL" else "badge-watch"
        rr_html = ""
        if r.get("entry") and r.get("sl") and r.get("tp"):
            risk   = abs(r["entry"] - r["sl"])
            reward = abs(r["tp"] - r["entry"])
            rr     = round(reward / risk, 2) if risk > 0 else 0
            rr_col = "#00e676" if rr >= 2 else "#ffd600" if rr >= 1 else "#ff4444"
            rr_html = f"<div style='font-size:12px; color:{rr_col}; font-family:JetBrains Mono; margin-top:4px'>R:R = 1:{rr}</div>"

        with cols[i % 3]:
            st.markdown(f"""
            <div class='stock-card'>
              <div style='display:flex; justify-content:space-between; align-items:start'>
                <div style='font-family:JetBrains Mono; font-size:18px; font-weight:700'>{r["symbol"]}</div>
                <span class='badge {signal_class}'>{r["signal"]}</span>
              </div>
              {"<div style='font-family:JetBrains Mono; font-size:13px; color:var(--text2); margin-top:6px'>CMP: <span style='color:var(--text1)'>₹{r['price']}</span></div>" if r.get("price") else ""}
              {"<div style='margin-top:10px; font-size:12px; display:flex; flex-direction:column; gap:3px'><div style='display:flex;justify-content:space-between'><span style='color:var(--text3)'>Entry</span><span style='font-family:JetBrains Mono; color:#00d4ff'>₹" + str(r['entry']) + "</span></div><div style='display:flex;justify-content:space-between'><span style='color:var(--text3)'>SL</span><span style='font-family:JetBrains Mono; color:#ff4444'>₹" + str(r['sl']) + "</span></div><div style='display:flex;justify-content:space-between'><span style='color:var(--text3)'>Target</span><span style='font-family:JetBrains Mono; color:#00e676'>₹" + str(r['tp']) + "</span></div></div>" if r.get("entry") else ""}
              {rr_html}
              {"<div style='font-size:11px; color:var(--text3); margin-top:8px'>" + str(r['notes']) + "</div>" if r.get("notes") else ""}
            </div>
            """, unsafe_allow_html=True)

            if user["role"] == "admin":
                if st.button(f"🗑 Remove", key=f"del_{r['id']}"):
                    sb.table("scan_results").delete().eq("id", r["id"]).execute()
                    st.rerun()


def _notify_users_new_stock(symbol, signal, entry, sl, tp, notes):
    """Email pathav saglya approved users la."""
    try:
        smtp_user = st.secrets.get("SMTP_USER", "")
        smtp_pass = st.secrets.get("SMTP_PASS", "")
        smtp_host = st.secrets.get("SMTP_HOST", "smtp.gmail.com")
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
  <h2 style="color:#00d4ff; font-size:24px">📈 New Algo Signal</h2>
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
</body></html>
"""
        server = smtplib.SMTP(smtp_host, int(st.secrets.get("SMTP_PORT", 587)))
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
        st.warning(f"Email send nahi zala: {e}")


# ── Journal Page ───────────────────────────────────────────
def page_journal():
    user = st.session_state.user
    st.markdown("<div class='page-title'>📖 Trading Journal</div>", unsafe_allow_html=True)
    st.markdown("<div class='page-sub'>Tuzhe sagale trades track kar ani analytics baghh</div>", unsafe_allow_html=True)

    # Fetch trades
    res = sb.table("trades").select("*").eq("user_id", user["id"]).order("trade_date", desc=True).execute()
    trades = res.data or []

    # Analytics
    closed = [t for t in trades if t.get("result")]
    total_pnl = sum(t.get("pnl", 0) or 0 for t in closed)
    wins  = sum(1 for t in closed if t.get("result") == "WIN")
    losses= sum(1 for t in closed if t.get("result") == "LOSS")
    wr    = round((wins / len(closed)) * 100, 1) if closed else 0
    rr_vals = [t["r_multiple"] for t in closed if t.get("r_multiple")]
    avg_rr  = round(sum(rr_vals) / len(rr_vals), 2) if rr_vals else 0

    c1, c2, c3, c4, c5 = st.columns(5)
    with c1: st.markdown(f"<div class='metric-card'><div class='metric-label'>Total Trades</div><div class='metric-val' style='color:#00d4ff'>{len(trades)}</div></div>", unsafe_allow_html=True)
    with c2: st.markdown(f"<div class='metric-card'><div class='metric-label'>Win Rate</div><div class='metric-val' style='color:#00e676'>{wr}%</div></div>", unsafe_allow_html=True)
    with c3: st.markdown(f"<div class='metric-card'><div class='metric-label'>Wins / Losses</div><div class='metric-val' style='color:#ffd600'>{wins}/{losses}</div></div>", unsafe_allow_html=True)
    with c4: st.markdown(f"<div class='metric-card'><div class='metric-label'>Avg R:R</div><div class='metric-val' style='color:#00d4ff'>{avg_rr}</div></div>", unsafe_allow_html=True)
    with c5:
        pnl_color = "#00e676" if total_pnl >= 0 else "#ff4444"
        st.markdown(f"<div class='metric-card'><div class='metric-label'>Total P&L</div><div class='metric-val' style='color:{pnl_color}'>₹{total_pnl:,.0f}</div></div>", unsafe_allow_html=True)

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)

    # Add Trade
    with st.expander("➕ Nava Trade Add Kara", expanded=False):
        c1, c2, c3 = st.columns(3)
        with c1:
            t_date  = st.date_input("Trade Date", value=datetime.date.today())
            t_sym   = st.text_input("Symbol *", placeholder="RELIANCE").upper().strip()
            t_dir   = st.selectbox("Direction", ["LONG", "SHORT"])
            t_qty   = st.number_input("Quantity", min_value=1, value=1)
        with c2:
            t_entry = st.number_input("Entry Price *", min_value=0.0, step=0.05)
            t_sl    = st.number_input("Stop Loss *", min_value=0.0, step=0.05)
            t_tgt   = st.number_input("Target *", min_value=0.0, step=0.05)
            t_exit  = st.number_input("Exit Price (optional)", min_value=0.0, step=0.05)
        with c3:
            t_notes = st.text_area("Notes", height=100)
            # Auto P&L preview
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

        if st.button("✅ Trade Save Kara", use_container_width=True):
            if not t_sym or not t_entry or not t_sl or not t_tgt:
                st.error("Symbol, Entry, SL, Target required!")
            else:
                risk = abs(t_entry - t_sl)
                result = None
                pnl = None
                r_mult = None

                if t_exit > 0:
                    if t_dir == "LONG":
                        pnl = round((t_exit - t_entry) * t_qty, 2)
                    else:
                        pnl = round((t_entry - t_exit) * t_qty, 2)
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

    # Trade List
    if not trades:
        st.info("Abhi koi trade nahi — vartil form vaparoon add kara!")
        return

    st.markdown(f"**{len(trades)} Trades**")
    for t in trades:
        result_color = "#00e676" if t.get("result") == "WIN" else "#ff4444" if t.get("result") == "LOSS" else "#ffd600"
        pnl_str = f"₹{t['pnl']:+,.0f}" if t.get("pnl") is not None else "Open"
        col1, col2 = st.columns([10, 1])
        with col1:
            st.markdown(f"""
            <div class='trade-row'>
              <div style='font-family:JetBrains Mono; font-size:16px; font-weight:700; min-width:120px'>{t['symbol']}</div>
              <div style='font-size:12px; color:var(--text2)'>{t['trade_date']}</div>
              <span class='badge {"badge-buy" if t["direction"]=="LONG" else "badge-sell"}'>{t['direction']}</span>
              <div style='font-size:12px'>Entry: <span style='font-family:JetBrains Mono'>₹{t['entry_price']}</span></div>
              <div style='font-size:12px'>SL: <span style='font-family:JetBrains Mono; color:#ff4444'>₹{t['stop_loss']}</span></div>
              <div style='font-size:12px'>Target: <span style='font-family:JetBrains Mono; color:#00e676'>₹{t['target_price']}</span></div>
              <div style='font-size:13px; font-weight:700; color:{result_color}'>{pnl_str}</div>
              {f"<span class='badge {\"badge-buy\" if t[\"result\"]==\"WIN\" else \"badge-sell\"}'>{t['result']}</span>" if t.get('result') else ""}
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
            capital  = st.number_input("Capital (₹)", min_value=1000.0, value=100000.0, step=1000.0)
            risk_pct = st.number_input("Risk Per Trade (%)", min_value=0.1, max_value=10.0, value=1.0, step=0.1)
        with col2:
            entry   = st.number_input("Entry Price (₹)", min_value=0.01, value=500.0, step=0.05)
            sl      = st.number_input("Stop Loss (₹)", min_value=0.01, value=485.0, step=0.05)
        target = st.number_input("Target Price (₹) — optional", min_value=0.0, value=540.0, step=0.05)

        # Calculate
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
            ("#00e676", "1% Risk Rule", "Ekka trade madhe capital cha 1-2% peksha jast risk nako. Drawdown madhe capital protect hote."),
            ("#00d4ff", "Min 1:2 R:R", "Pratyehi risk sathi 2x reward target kar. 40% win rate madhe pan profitable hote."),
            ("#ffd600", "5% Daily Loss Limit", "Din madhe 5% loss zala tar trading band kar. Revenge trading avoid kar."),
            ("#ff4444", "Position Concentration", "Eka position madhe 25% peksha jast capital nako. Sectors madhe diversify kar."),
        ]
        for color, title, desc in rules:
            st.markdown(f"""
            <div style='background:var(--bg2); border-left:3px solid {color}; border-radius:8px; padding:14px 16px; margin-bottom:10px'>
              <div style='font-weight:600; font-size:13px; color:{color}'>{title}</div>
              <div style='font-size:12px; color:var(--text2); margin-top:4px; line-height:1.5'>{desc}</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("#### Win Rate vs R:R Matrix")
        matrix_data = [
            ("1:1", "50%", "#ffd600", "Marginal"),
            ("1:2", "33%", "#00e676", "Good"),
            ("1:3", "25%", "#00e676", "Great"),
            ("1:4", "20%", "#00d4ff", "Excellent"),
        ]
        for rr_val, min_wr, color, label in matrix_data:
            st.markdown(f"""
            <div style='display:flex; justify-content:space-between; align-items:center; padding:8px 12px; background:var(--bg2); border-radius:6px; margin-bottom:6px'>
              <span style='font-family:JetBrains Mono; font-size:13px'>{rr_val}</span>
              <span style='font-family:JetBrains Mono; font-size:13px'>{min_wr}</span>
              <span style='color:{color}; font-size:12px; font-weight:700'>{label}</span>
            </div>
            """, unsafe_allow_html=True)


# ── News Page ──────────────────────────────────────────────
def page_news():
    st.markdown("<div class='page-title'>📰 Market News</div>", unsafe_allow_html=True)
    st.markdown("<div class='page-sub'>Indian market news · Auto-refresh every 30 min</div>", unsafe_allow_html=True)

    col1, col2 = st.columns([4, 1])
    with col2:
        if st.button("↻ Refresh News", use_container_width=True):
            _fetch_news()
            st.rerun()

    # Fetch cached news
    res = sb.table("news_cache").select("*").order("fetched_at", desc=True).limit(30).execute()
    news = res.data or []

    if not news:
        _fetch_news()
        st.rerun()

    # News cards
    for item in news:
        st.markdown(f"""
        <div class='news-card'>
          <div style='display:flex; justify-content:space-between; align-items:start; margin-bottom:6px'>
            <span style='font-size:11px; color:#00d4ff; font-weight:700; background:#00d4ff22; padding:2px 8px; border-radius:20px'>{item.get('source','NEWS')}</span>
            <span style='font-size:11px; color:var(--text3)'>{str(item.get('published_at',''))[:16]}</span>
          </div>
          <div style='font-size:14px; font-weight:600; color:var(--text1); line-height:1.4; margin-bottom:6px'>{item['title']}</div>
          {"<div style='font-size:12px; color:var(--text2); line-height:1.5'>" + item['summary'][:200] + "...</div>" if item.get('summary') else ""}
          {"<a href='" + item['url'] + "' target='_blank' style='font-size:11px; color:#00d4ff; text-decoration:none; margin-top:6px; display:inline-block'>Read More →</a>" if item.get('url') else ""}
        </div>
        """, unsafe_allow_html=True)


def _fetch_news():
    """RSS feeds varun news fetch kar."""
    try:
        import xml.etree.ElementTree as ET
        feeds = [
            ("Economic Times", "https://economictimes.indiatimes.com/markets/rssfeeds/1977021501.cms"),
            ("Moneycontrol",   "https://www.moneycontrol.com/rss/MCtopnews.xml"),
        ]
        for source, url in feeds:
            try:
                req = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
                root = ET.fromstring(req.content)
                items = root.findall(".//item")[:10]
                for item in items:
                    title = item.findtext("title", "").strip()
                    link  = item.findtext("link", "").strip()
                    desc  = item.findtext("description", "").strip()
                    pub   = item.findtext("pubDate", "").strip()
                    if title:
                        sb.table("news_cache").upsert({
                            "title": title[:500],
                            "summary": desc[:1000] if desc else None,
                            "url": link,
                            "source": source,
                            "published_at": pub[:50] if pub else None,
                        }, on_conflict="title").execute()
            except:
                continue
    except:
        pass


# ── Admin Page ─────────────────────────────────────────────
def page_admin():
    st.markdown("<div class='page-title'>👑 Admin Panel</div>", unsafe_allow_html=True)
    st.markdown("<div class='page-sub'>User management aani platform control</div>", unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["👥 Users", "📋 Login Logs"])

    with tab1:
        users = sb.table("users").select("*").order("created_at", desc=True).execute().data or []

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
                </div>
                """, unsafe_allow_html=True)
            with col2:
                st.markdown(f"<div style='padding:8px 0; font-size:12px; color:{status_color}'>{u['status'].upper()}</div>", unsafe_allow_html=True)
            with col3:
                st.markdown(f"<div style='padding:8px 0; font-size:12px; color:var(--text2)'>{u['role']}</div>", unsafe_allow_html=True)
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

    with tab2:
        logs = sb.table("login_logs").select("*, users(username, email)").order("login_at", desc=True).limit(50).execute().data or []
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

    page = st.session_state.page
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


if __name__ == "__main__":
    main()