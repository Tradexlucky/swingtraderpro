"""
SwingTrader Pro — Clean Fixed Version
Fixes: sidebar, numbers display, forgot password, CMP, invite user, news
"""
import streamlit as st
import hashlib
import datetime
import requests
import re
from supabase import create_client

st.set_page_config(
    page_title="SwingTrader Pro",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
ADMIN_EMAIL  = st.secrets["ADMIN_EMAIL"]

@st.cache_resource
def get_supabase():
    return create_client(SUPABASE_URL, SUPABASE_KEY)
sb = get_supabase()

st.markdown("""
<style>
html, body, [data-testid="stAppViewContainer"] {
  background: #080c14 !important;
  color: #f0f4ff !important;
  font-family: Arial, sans-serif !important;
}
[data-testid="stSidebar"] {
  background: #0d1220 !important;
  border-right: 1px solid #1e2a3a !important;
}
.stButton > button {
  background: #00d4ff !important;
  color: #000 !important;
  font-weight: 700 !important;
  border: none !important;
  border-radius: 8px !important;
}
.stButton > button:hover { background: #00b8d9 !important; }
[data-testid="stSidebar"] .stButton > button {
  background: transparent !important;
  color: #8899bb !important;
  border: 1px solid #1e2a3a !important;
  text-align: left !important;
  margin-bottom: 4px !important;
  width: 100% !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
  background: #111827 !important;
  color: #00d4ff !important;
  border-color: #00d4ff !important;
}
.stTextInput > div > div > input,
.stSelectbox > div > div > div,
.stNumberInput > div > div > input,
.stTextArea > div > div > textarea {
  background: #111827 !important;
  color: #f0f4ff !important;
  border: 1px solid #1e2a3a !important;
  border-radius: 8px !important;
}
.stock-card {
  background: #0d1220; border: 1px solid #1e2a3a;
  border-radius: 12px; padding: 16px; margin-bottom: 12px;
}
.news-card {
  background: #0d1220; border: 1px solid #1e2a3a;
  border-left: 3px solid #00d4ff; border-radius: 8px;
  padding: 14px 16px; margin-bottom: 10px;
}
.trade-row {
  background: #0d1220; border: 1px solid #1e2a3a;
  border-radius: 8px; padding: 12px 16px; margin-bottom: 8px;
}
.badge { display:inline-block; padding:3px 10px; border-radius:20px; font-size:11px; font-weight:700; }
.badge-buy  { background:#00e67622; color:#00e676; border:1px solid #00e67644; }
.badge-sell { background:#ff444422; color:#ff4444; border:1px solid #ff444444; }
.badge-watch{ background:#ffd60022; color:#ffd600; border:1px solid #ffd60044; }
.page-title { font-size:26px; font-weight:800; color:#f0f4ff; margin-bottom:4px; }
.page-sub   { font-size:13px; color:#8899bb; margin-bottom:20px; }
#MainMenu, footer, header { visibility: hidden; }
.stDeployButton { display: none; }
</style>
""", unsafe_allow_html=True)

# ── Session State ──────────────────────────────────────────
if "user"     not in st.session_state: st.session_state.user     = None
if "page"     not in st.session_state: st.session_state.page     = "scanner"
if "auth_tab" not in st.session_state: st.session_state.auth_tab = "login"

# ── Auth Helpers ───────────────────────────────────────────
def hash_pw(p): return hashlib.sha256(p.encode()).hexdigest()

def get_user(email):
    try:
        r = sb.table("users").select("*").eq("email", email.strip().lower()).execute()
        return r.data[0] if r.data else None
    except: return None

def create_user(username, email, password, role="user", status="pending"):
    try:
        is_admin = email.strip().lower() == ADMIN_EMAIL.strip().lower()
        sb.table("users").insert({
            "username": username.strip(),
            "email":    email.strip().lower(),
            "password_hash": hash_pw(password),
            "role":   "admin" if is_admin else role,
            "status": "approved" if (is_admin or status == "approved") else "pending",
            "created_at": datetime.datetime.now().isoformat()
        }).execute()
        return True
    except: return False

def login_user(email, password):
    u = get_user(email)
    if not u:                              return None, "Email milala nahi!"
    if u["password_hash"] != hash_pw(password): return None, "Password chukiche ahe!"
    if u["status"] == "pending":           return None, "Account pending — admin approval var wait kar!"
    if u["status"] == "blocked":           return None, "Account blocked ahe!"
    try: sb.table("users").update({"last_login": datetime.datetime.now().isoformat()}).eq("id", u["id"]).execute()
    except: pass
    return u, None

def reset_password(email, new_pw):
    try:
        sb.table("users").update({"password_hash": hash_pw(new_pw)}).eq("email", email.strip().lower()).execute()
        return True
    except: return False

# ── AUTH PAGE ─────────────────────────────────────────────
def show_auth():
    _, col, _ = st.columns([1, 1.2, 1])
    with col:
        st.markdown("""
        <div style='text-align:center; padding:40px 0 24px'>
          <div style='font-size:40px; font-weight:800; color:#00d4ff'>📈 SwingTrader Pro</div>
          <div style='color:#8899bb; font-size:14px; margin-top:6px'>Professional Swing Trading · Indian Markets</div>
        </div>""", unsafe_allow_html=True)

        b1, b2, b3 = st.columns(3)
        with b1:
            if st.button("🔐 Login",    use_container_width=True, key="ab1"):
                st.session_state.auth_tab = "login";    st.rerun()
        with b2:
            if st.button("📝 Register", use_container_width=True, key="ab2"):
                st.session_state.auth_tab = "register"; st.rerun()
        with b3:
            if st.button("🔓 Forgot",   use_container_width=True, key="ab3"):
                st.session_state.auth_tab = "forgot";   st.rerun()

        st.markdown("---")
        tab = st.session_state.auth_tab

        if tab == "login":
            st.markdown("#### 🔐 Login")
            email = st.text_input("Email", key="li_e", placeholder="your@email.com")
            pw    = st.text_input("Password", type="password", key="li_p")
            if st.button("Login →", use_container_width=True, key="li_btn"):
                if email and pw:
                    u, err = login_user(email, pw)
                    if u:
                        st.session_state.user = u
                        st.session_state.page = "scanner"
                        st.success(f"Welcome, {u['username']}!")
                        st.rerun()
                    else: st.error(err)
                else: st.warning("Email ani password bhara!")

        elif tab == "register":
            st.markdown("#### 📝 Register")
            uname = st.text_input("Username", key="re_u")
            email = st.text_input("Email",    key="re_e")
            pw1   = st.text_input("Password", type="password", key="re_p1")
            pw2   = st.text_input("Confirm",  type="password", key="re_p2")
            if st.button("Register →", use_container_width=True, key="re_btn"):
                if not all([uname, email, pw1, pw2]): st.warning("Sagale fields bhara!")
                elif pw1 != pw2:   st.error("Passwords match nahi!")
                elif len(pw1) < 6: st.error("Password 6+ chars pahije!")
                elif get_user(email): st.error("Email already registered!")
                else:
                    if create_user(uname, email, pw1):
                        if email.strip().lower() == ADMIN_EMAIL.strip().lower():
                            st.success("Admin account tayar! Login kara.")
                        else:
                            st.success("Registration zali! Admin approval nantar login hoin.")
                    else: st.error("Failed — try again!")

        elif tab == "forgot":
            st.markdown("#### 🔓 Reset Password")
            email = st.text_input("Registered Email", key="fp_e")
            pw1   = st.text_input("New Password",     type="password", key="fp_p1")
            pw2   = st.text_input("Confirm Password", type="password", key="fp_p2")
            if st.button("Reset →", use_container_width=True, key="fp_btn"):
                if not all([email, pw1, pw2]): st.warning("Sagale fields bhara!")
                elif pw1 != pw2:   st.error("Passwords match nahi!")
                elif len(pw1) < 6: st.error("6+ chars pahije!")
                elif not get_user(email): st.error("Email registered nahi!")
                else:
                    if reset_password(email, pw1):
                        st.success("Password reset zala! Login kara.")
                        st.session_state.auth_tab = "login"; st.rerun()
                    else: st.error("Failed — try again!")

# ── SIDEBAR ───────────────────────────────────────────────
def show_sidebar():
    u = st.session_state.user
    with st.sidebar:
        role_color = "#00e676" if u["role"] == "admin" else "#ffd600"
        role_label = "👑 Admin" if u["role"] == "admin" else "👤 User"
        st.markdown(f"""
        <div style='padding:12px 0 16px; border-bottom:1px solid #1e2a3a; margin-bottom:12px'>
          <div style='font-size:20px; font-weight:800; color:#00d4ff'>📈 SwingTrader</div>
          <div style='font-size:12px; color:#8899bb; margin-top:4px'>
            {u['username']} · <span style='color:{role_color}'>{role_label}</span>
          </div>
        </div>""", unsafe_allow_html=True)

        pages = [
            ("📊", "scanner", "Algo Scanner"),
            ("📖", "journal", "Trading Journal"),
            ("⚡", "risk",    "Risk Calculator"),
            ("📰", "news",    "Market News"),
        ]
        if u["role"] == "admin":
            pages.append(("👑", "admin", "Admin Panel"))

        for icon, pg, label in pages:
            if st.button(f"{icon}  {label}", key=f"nav_{pg}", use_container_width=True):
                st.session_state.page = pg; st.rerun()

        st.markdown("---")
        if st.button("🚪 Logout", use_container_width=True, key="logout"):
            st.session_state.user = None
            st.session_state.page = "scanner"
            st.rerun()

# ── SCANNER PAGE ──────────────────────────────────────────
def page_scanner():
    u     = st.session_state.user
    today = datetime.date.today().isoformat()

    st.markdown("<div class='page-title'>📊 Algo Scanner</div>", unsafe_allow_html=True)
    st.markdown("<div class='page-sub'>Today's swing trading opportunities · Indian Markets</div>", unsafe_allow_html=True)

    try:
        res     = sb.table("scan_results").select("*").eq("scan_date", today).order("created_at", desc=True).execute()
        results = res.data or []
    except: results = []

    buys  = sum(1 for r in results if r["signal"] == "BUY")
    sells = sum(1 for r in results if r["signal"] == "SELL")

    c1, c2, c3, c4 = st.columns(4)
    with c1: st.metric("📊 Total Signals", len(results))
    with c2: st.metric("🟢 Buy Signals",   buys)
    with c3: st.metric("🔴 Sell Signals",  sells)
    with c4: st.metric("📅 Scan Date",     today)

    st.markdown("---")

    if u["role"] == "admin":
        with st.expander("➕ Nava Stock Add Kara", expanded=False):
            c1, c2, c3 = st.columns(3)
            with c1:
                sym    = st.text_input("Symbol *", placeholder="RELIANCE", key="sc_s").upper().strip()
                signal = st.selectbox("Signal", ["BUY","SELL","WATCH"], key="sc_sig")
                cmp    = st.number_input("CMP (₹)", min_value=0.0, step=0.05, format="%.2f", key="sc_cmp")
            with c2:
                entry = st.number_input("Entry (₹) *",    min_value=0.0, step=0.05, format="%.2f", key="sc_e")
                sl    = st.number_input("Stop Loss (₹) *", min_value=0.0, step=0.05, format="%.2f", key="sc_sl")
                tp    = st.number_input("Target (₹) *",   min_value=0.0, step=0.05, format="%.2f", key="sc_tp")
            with c3:
                notes = st.text_input("Setup Notes", placeholder="VCP Breakout...", key="sc_n")
                if entry > 0 and sl > 0 and tp > 0:
                    risk   = abs(entry - sl)
                    reward = abs(tp - entry)
                    rr     = round(reward/risk, 2) if risk > 0 else 0
                    col    = "🟢" if rr >= 2 else "🟡" if rr >= 1 else "🔴"
                    st.metric("R:R Ratio", f"{col} 1:{rr}")

            if st.button("✅ Add Stock", use_container_width=True, key="sc_add"):
                if not sym:          st.error("Symbol required!")
                elif entry <= 0 or sl <= 0 or tp <= 0: st.error("Entry, SL, Target required!")
                else:
                    try:
                        sb.table("scan_results").insert({
                            "scan_date": today, "symbol": sym, "signal": signal,
                            "price": float(cmp) if cmp > 0 else None,
                            "entry": float(entry), "sl": float(sl), "tp": float(tp),
                            "notes": notes, "added_by": u["id"]
                        }).execute()
                        st.success(f"✅ {sym} added!")
                        _notify_users(sym, signal, entry, sl, tp, notes)
                        st.rerun()
                    except Exception as e: st.error(f"Error: {e}")

    if not results:
        st.info("📭 Aajache scan pending — admin ne stocks add kelya ki ithech disel.")
        return

    cols = st.columns(3)
    for i, r in enumerate(results):
        sig_cls = "badge-buy" if r["signal"]=="BUY" else "badge-sell" if r["signal"]=="SELL" else "badge-watch"
        cmp_val = r.get("price")
        cmp_html = f"<div style='color:#8899bb; font-size:13px; margin-top:6px'>CMP: <b style='color:#fff'>₹{float(cmp_val):,.2f}</b></div>" if cmp_val and float(cmp_val) > 0 else ""

        rr_html = ""
        if r.get("entry") and r.get("sl") and r.get("tp"):
            risk   = abs(float(r["entry"]) - float(r["sl"]))
            reward = abs(float(r["tp"])    - float(r["entry"]))
            rr     = round(reward/risk, 2) if risk > 0 else 0
            rc     = "#00e676" if rr >= 2 else "#ffd600" if rr >= 1 else "#ff4444"
            rr_html = f"<div style='color:{rc}; font-size:13px; font-weight:700; margin-top:6px'>R:R = 1:{rr}</div>"

        price_html = ""
        if r.get("entry"):
            price_html = f"""
            <div style='margin-top:10px; font-size:13px; display:flex; flex-direction:column; gap:4px'>
              <div style='display:flex; justify-content:space-between'>
                <span style='color:#8899bb'>Entry</span>
                <span style='color:#00d4ff; font-weight:700'>₹{float(r['entry']):,.2f}</span>
              </div>
              <div style='display:flex; justify-content:space-between'>
                <span style='color:#8899bb'>SL</span>
                <span style='color:#ff4444; font-weight:700'>₹{float(r['sl']):,.2f}</span>
              </div>
              <div style='display:flex; justify-content:space-between'>
                <span style='color:#8899bb'>Target</span>
                <span style='color:#00e676; font-weight:700'>₹{float(r['tp']):,.2f}</span>
              </div>
            </div>"""

        notes_html = f"<div style='color:#4a5568; font-size:11px; margin-top:8px'>{r['notes']}</div>" if r.get("notes") else ""

        with cols[i % 3]:
            st.markdown(f"""
            <div class='stock-card'>
              <div style='display:flex; justify-content:space-between; align-items:center'>
                <div style='font-size:20px; font-weight:800; color:#f0f4ff'>{r['symbol']}</div>
                <span class='badge {sig_cls}'>{r['signal']}</span>
              </div>
              {cmp_html}{price_html}{rr_html}{notes_html}
            </div>""", unsafe_allow_html=True)

            if u["role"] == "admin":
                if st.button("🗑 Remove", key=f"del_{r['id']}"):
                    sb.table("scan_results").delete().eq("id", r["id"]).execute(); st.rerun()

def _notify_users(symbol, signal, entry, sl, tp, notes):
    try:
        su = st.secrets.get("SMTP_USER",""); sp = st.secrets.get("SMTP_PASS","")
        if not su or not sp: return
        users = sb.table("users").select("email,username").eq("status","approved").execute()
        if not users.data: return
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        body = f"""<html><body style='font-family:Arial;background:#080c14;color:#f0f4ff;padding:20px'>
<div style='max-width:500px;margin:0 auto;background:#0d1220;border-radius:12px;padding:24px'>
  <h2 style='color:#00d4ff'>📈 New Signal: {symbol} {signal}</h2>
  <p>Entry: ₹{entry} | SL: ₹{sl} | Target: ₹{tp}</p>
  {"<p>" + notes + "</p>" if notes else ""}
</div></body></html>"""
        server = smtplib.SMTP(st.secrets.get("SMTP_HOST","smtp.gmail.com"), int(st.secrets.get("SMTP_PORT",587)))
        server.starttls(); server.login(su, sp)
        for u2 in users.data:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = f"📈 {symbol} {signal} — SwingTrader Pro"
            msg["From"] = f"SwingTrader <{su}>"; msg["To"] = u2["email"]
            msg.attach(MIMEText(body, "html"))
            server.sendmail(su, u2["email"], msg.as_string())
        server.quit()
    except: pass

# ── JOURNAL PAGE ──────────────────────────────────────────
def page_journal():
    u = st.session_state.user
    st.markdown("<div class='page-title'>📖 Trading Journal</div>", unsafe_allow_html=True)
    st.markdown("<div class='page-sub'>Tuzhe sagale trades track kar ani analytics bagh</div>", unsafe_allow_html=True)

    try:
        res    = sb.table("trades").select("*").eq("user_id", u["id"]).order("trade_date", desc=True).execute()
        trades = res.data or []
    except: trades = []

    closed    = [t for t in trades if t.get("result")]
    total_pnl = sum(t.get("pnl", 0) or 0 for t in closed)
    wins      = sum(1 for t in closed if t.get("result") == "WIN")
    losses    = sum(1 for t in closed if t.get("result") == "LOSS")
    wr        = round((wins/len(closed))*100, 1) if closed else 0
    rr_vals   = [t["r_multiple"] for t in closed if t.get("r_multiple")]
    avg_rr    = round(sum(rr_vals)/len(rr_vals), 2) if rr_vals else 0

    c1,c2,c3,c4,c5 = st.columns(5)
    with c1: st.metric("📊 Trades",  len(trades))
    with c2: st.metric("🎯 Win Rate", f"{wr}%")
    with c3: st.metric("✅ Wins",    wins)
    with c4: st.metric("❌ Losses",  losses)
    with c5: st.metric("💰 P&L",    f"₹{total_pnl:+,.0f}")

    st.markdown("---")

    with st.expander("➕ Nava Trade Add Kara", expanded=False):
        c1,c2,c3 = st.columns(3)
        with c1:
            t_date = st.date_input("Date", value=datetime.date.today(), key="td")
            t_sym  = st.text_input("Symbol *", placeholder="RELIANCE", key="ts").upper().strip()
            t_dir  = st.selectbox("Direction", ["LONG","SHORT"], key="tdir")
            t_qty  = st.number_input("Quantity", min_value=1, value=1, key="tq")
        with c2:
            t_entry = st.number_input("Entry *",       min_value=0.0, step=0.05, format="%.2f", key="te")
            t_sl    = st.number_input("Stop Loss *",   min_value=0.0, step=0.05, format="%.2f", key="tsl")
            t_tgt   = st.number_input("Target *",      min_value=0.0, step=0.05, format="%.2f", key="tt")
            t_exit  = st.number_input("Exit (optional)", min_value=0.0, step=0.05, format="%.2f", key="tex")
        with c3:
            t_notes = st.text_area("Notes", height=100, key="tn")
            if t_entry > 0 and t_sl > 0 and t_tgt > 0:
                risk = abs(t_entry - t_sl)
                rr   = round(abs(t_tgt - t_entry)/risk, 2) if risk > 0 else 0
                rc   = "🟢" if rr >= 2 else "🟡" if rr >= 1 else "🔴"
                st.metric("R:R", f"{rc} 1:{rr}")

        if st.button("✅ Save Trade", use_container_width=True, key="save_t"):
            if not t_sym or t_entry <= 0 or t_sl <= 0 or t_tgt <= 0:
                st.error("Symbol, Entry, SL, Target required!")
            else:
                risk = abs(t_entry - t_sl); result = pnl = r_mult = None
                if t_exit > 0:
                    pnl    = round((t_exit-t_entry)*t_qty, 2) if t_dir=="LONG" else round((t_entry-t_exit)*t_qty, 2)
                    result = "WIN" if pnl > 0 else "LOSS"
                    r_mult = round(pnl/(risk*t_qty), 2) if risk > 0 else 0
                sb.table("trades").insert({
                    "user_id": u["id"], "trade_date": t_date.isoformat(),
                    "symbol": t_sym, "direction": t_dir, "entry_price": t_entry,
                    "stop_loss": t_sl, "target_price": t_tgt,
                    "exit_price": t_exit if t_exit > 0 else None,
                    "quantity": t_qty, "result": result, "pnl": pnl,
                    "r_multiple": r_mult, "notes": t_notes
                }).execute()
                st.success("✅ Trade saved!"); st.rerun()

    if not trades:
        st.info("Abhi koi trade nahi!"); return

    for t in trades:
        rc  = "#00e676" if t.get("result")=="WIN" else "#ff4444" if t.get("result")=="LOSS" else "#ffd600"
        pls = f"₹{t['pnl']:+,.0f}" if t.get("pnl") is not None else "Open"
        c1, c2 = st.columns([11,1])
        with c1:
            badge = "<span class='badge badge-buy'>WIN</span>" if t.get("result")=="WIN" else "<span class='badge badge-sell'>LOSS</span>" if t.get("result")=="LOSS" else "<span class='badge badge-watch'>OPEN</span>"
            dir_badge = f"<span class='badge {'badge-buy' if t['direction']=='LONG' else 'badge-sell'}'>{t['direction']}</span>"
            st.markdown(f"""
            <div class='trade-row'>
              <div style='display:flex; gap:14px; align-items:center; flex-wrap:wrap'>
                <b style='font-size:16px; min-width:100px'>{t['symbol']}</b>
                <span style='color:#8899bb; font-size:12px'>{t['trade_date']}</span>
                {dir_badge}
                <span style='font-size:12px'>Entry <b>₹{float(t['entry_price']):,.2f}</b></span>
                <span style='font-size:12px; color:#ff4444'>SL ₹{float(t['stop_loss']):,.2f}</span>
                <span style='font-size:12px; color:#00e676'>Tgt ₹{float(t['target_price']):,.2f}</span>
                <b style='color:{rc}'>{pls}</b>
                {badge}
              </div>
            </div>""", unsafe_allow_html=True)
        with c2:
            if st.button("🗑", key=f"del_t_{t['id']}"):
                sb.table("trades").delete().eq("id", t["id"]).execute(); st.rerun()

# ── RISK CALCULATOR ───────────────────────────────────────
def page_risk():
    st.markdown("<div class='page-title'>⚡ Risk Calculator</div>", unsafe_allow_html=True)
    st.markdown("<div class='page-sub'>Position sizing · Capital risk management</div>", unsafe_allow_html=True)

    c1, c2 = st.columns([1.2, 1])
    with c1:
        col1, col2 = st.columns(2)
        with col1:
            capital  = st.number_input("Capital (₹)", min_value=1000.0, value=100000.0, step=1000.0, key="rc_c")
            risk_pct = st.number_input("Risk %", min_value=0.1, max_value=10.0, value=1.0, step=0.1, key="rc_r")
        with col2:
            entry = st.number_input("Entry (₹)",    min_value=0.01, value=500.0, step=0.05, key="rc_e")
            sl    = st.number_input("Stop Loss (₹)", min_value=0.01, value=485.0, step=0.05, key="rc_sl")
        target = st.number_input("Target (₹)", min_value=0.0, value=540.0, step=0.05, key="rc_t")

        risk_amt = capital * (risk_pct/100)
        sl_pts   = abs(entry - sl)
        position = int(risk_amt/sl_pts) if sl_pts > 0 else 0
        max_loss = round(position * sl_pts, 2)
        rr = reward = 0
        if target and sl_pts > 0:
            rr     = round(abs(target-entry)/sl_pts, 2)
            reward = round(position * abs(target-entry), 2)

        st.markdown("---")
        m1,m2,m3,m4 = st.columns(4)
        with m1: st.metric("Position Size", f"{position} qty")
        with m2: st.metric("Max Loss",      f"₹{max_loss:,.0f}")
        with m3: st.metric("R:R",           f"1:{rr}")
        with m4: st.metric("Potential Profit", f"₹{reward:,.0f}")

    with c2:
        st.markdown("#### 📚 Risk Rules")
        rules = [
            ("#00e676", "1% Risk Rule",          "Capital cha 1-2% peksha jast risk nako."),
            ("#00d4ff", "Min 1:2 R:R",           "Pratyehi risk sathi 2x reward target kar."),
            ("#ffd600", "5% Daily Loss Limit",    "5% loss zala tar trading band kar."),
            ("#ff4444", "Position Concentration", "Eka position madhe 25% peksha jast nako."),
        ]
        for color, title, desc in rules:
            st.markdown(f"""
            <div style='background:#0d1220; border-left:3px solid {color}; border-radius:8px; padding:12px 14px; margin-bottom:10px'>
              <div style='font-weight:700; color:{color}'>{title}</div>
              <div style='font-size:12px; color:#8899bb; margin-top:3px'>{desc}</div>
            </div>""", unsafe_allow_html=True)

# ── NEWS PAGE ─────────────────────────────────────────────
def page_news():
    st.markdown("<div class='page-title'>📰 Market News</div>", unsafe_allow_html=True)
    st.markdown("<div class='page-sub'>Indian market news · Latest updates</div>", unsafe_allow_html=True)

    c1, c2 = st.columns([4,1])
    with c2:
        if st.button("↻ Refresh", use_container_width=True, key="ref_news"):
            with st.spinner("Fetching..."):
                n = _fetch_news()
            st.success(f"{n} news fetched!"); st.rerun()

    try:
        res  = sb.table("news_cache").select("*").order("fetched_at", desc=True).limit(30).execute()
        news = res.data or []
    except: news = []

    if not news:
        with st.spinner("News load hoto ahe..."):
            _fetch_news()
        try:
            res  = sb.table("news_cache").select("*").order("fetched_at", desc=True).limit(30).execute()
            news = res.data or []
        except: news = []

    if not news:
        st.warning("News fetch honyat problem ahe!")
        st.markdown("**Direct links:** [ET Markets](https://economictimes.indiatimes.com/markets) · [Moneycontrol](https://www.moneycontrol.com) · [NSE](https://www.nseindia.com)")
        return

    for item in news:
        title   = item.get("title","")
        summary = item.get("summary","")
        source  = item.get("source","NEWS")
        pub_at  = str(item.get("published_at",""))[:16]
        url     = item.get("url","")
        sum_html  = f"<div style='font-size:12px; color:#8899bb; margin-top:5px'>{summary[:220]}...</div>" if summary else ""
        link_html = f"<a href='{url}' target='_blank' style='font-size:11px; color:#00d4ff; margin-top:6px; display:inline-block'>Read More →</a>" if url else ""
        st.markdown(f"""
        <div class='news-card'>
          <div style='display:flex; justify-content:space-between; margin-bottom:5px'>
            <span style='font-size:11px; color:#00d4ff; font-weight:700; background:#00d4ff22; padding:2px 8px; border-radius:20px'>{source}</span>
            <span style='font-size:11px; color:#4a5568'>{pub_at}</span>
          </div>
          <div style='font-size:14px; font-weight:600; line-height:1.4'>{title}</div>
          {sum_html}{link_html}
        </div>""", unsafe_allow_html=True)

def _fetch_news():
    count = 0
    try:
        import xml.etree.ElementTree as ET
        feeds = [
            ("Economic Times", "https://economictimes.indiatimes.com/markets/rssfeeds/1977021501.cms"),
            ("Moneycontrol",   "https://www.moneycontrol.com/rss/MCtopnews.xml"),
            ("LiveMint",       "https://www.livemint.com/rss/markets"),
        ]
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36", "Accept": "*/*"}
        now = datetime.datetime.now().isoformat()
        for source, url in feeds:
            try:
                resp = requests.get(url, timeout=8, headers=headers)
                if resp.status_code != 200: continue
                root  = ET.fromstring(resp.content)
                items = root.findall(".//item")[:10]
                for item in items:
                    title = item.findtext("title","").strip()
                    link  = item.findtext("link","").strip()
                    desc  = re.sub(r'<[^>]+>', '', item.findtext("description",""))[:800]
                    pub   = item.findtext("pubDate","").strip()
                    if not title: continue
                    try:
                        sb.table("news_cache").upsert({
                            "title": title[:500], "summary": desc or None,
                            "url": link or None, "source": source,
                            "published_at": pub[:50] if pub else None,
                            "fetched_at": now
                        }, on_conflict="title").execute()
                        count += 1
                    except: continue
            except: continue
    except: pass
    return count

# ── ADMIN PAGE ────────────────────────────────────────────
def page_admin():
    st.markdown("<div class='page-title'>👑 Admin Panel</div>", unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["👥 Users", "📨 Invite User", "📋 Logs"])

    with tab1:
        try: users = sb.table("users").select("*").order("created_at", desc=True).execute().data or []
        except: users = []
        pending = [x for x in users if x["status"] == "pending"]
        if pending: st.warning(f"⚠️ {len(pending)} users pending approval!")
        for x in users:
            sc = "#00e676" if x["status"]=="approved" else "#ff4444" if x["status"]=="blocked" else "#ffd600"
            c1,c2,c3,c4 = st.columns([3,2,2,3])
            with c1:
                st.markdown(f"<div style='padding:8px 0'><b>{x['username']}</b><br><span style='font-size:12px; color:#8899bb'>{x['email']}</span></div>", unsafe_allow_html=True)
            with c2:
                st.markdown(f"<div style='padding:14px 0; font-size:12px; color:{sc}'>{x['status'].upper()}</div>", unsafe_allow_html=True)
            with c3:
                st.markdown(f"<div style='padding:14px 0; font-size:12px; color:#8899bb'>{x['role']}</div>", unsafe_allow_html=True)
            with c4:
                if x["status"] == "pending":
                    if st.button("✅ Approve", key=f"app_{x['id']}"):
                        sb.table("users").update({"status":"approved"}).eq("id",x["id"]).execute(); st.rerun()
                elif x["status"] == "approved":
                    if st.button("🚫 Block", key=f"blk_{x['id']}"):
                        sb.table("users").update({"status":"blocked"}).eq("id",x["id"]).execute(); st.rerun()
                elif x["status"] == "blocked":
                    if st.button("✅ Unblock", key=f"ublk_{x['id']}"):
                        sb.table("users").update({"status":"approved"}).eq("id",x["id"]).execute(); st.rerun()
            st.markdown("<hr style='border-color:#1e2a3a; margin:4px 0'>", unsafe_allow_html=True)

    with tab2:
        st.markdown("#### 📨 Directly User Add Kara")
        st.caption("He form vaparoon admin directly approved user add karta yeil — email invitation nako.")
        iu = st.text_input("Username *",         key="iu_u", placeholder="FriendName")
        ie = st.text_input("Email *",            key="iu_e", placeholder="friend@email.com")
        ip = st.text_input("Temp Password *",    key="iu_p", type="password")
        ir = st.selectbox("Role", ["user","admin"], key="iu_r")
        if st.button("➕ Add User", key="iu_btn"):
            if not all([iu, ie, ip]): st.warning("Sagale fields bhara!")
            elif len(ip) < 6:         st.error("Password 6+ chars!")
            elif get_user(ie):        st.error("Email already exists!")
            else:
                if create_user(iu, ie, ip, role=ir, status="approved"):
                    st.success(f"✅ {iu} add zala! Password: **{ip}**")
                    st.info("Friend la email kar — Email, Password ani website link.")
                else: st.error("Failed — try again!")

    with tab3:
        try: logs = sb.table("login_logs").select("*, users(username)").order("login_at", desc=True).limit(50).execute().data or []
        except: logs = []
        if not logs: st.info("Koi logs nahi.")
        else:
            for log in logs:
                uname = log.get("users",{}).get("username","?") if log.get("users") else "?"
                st.markdown(f"<div style='padding:6px 10px; background:#0d1220; border-radius:6px; margin-bottom:5px; font-size:12px; display:flex; gap:14px'><span style='color:#00d4ff'>{uname}</span><span style='color:#8899bb'>{str(log.get('login_at',''))[:16]}</span></div>", unsafe_allow_html=True)

# ── MAIN ──────────────────────────────────────────────────
def main():
    if not st.session_state.user:
        show_auth(); return

    show_sidebar()
    page = st.session_state.get("page","scanner")

    if   page == "scanner": page_scanner()
    elif page == "journal": page_journal()
    elif page == "risk":    page_risk()
    elif page == "news":    page_news()
    elif page == "admin" and st.session_state.user["role"] == "admin": page_admin()
    else: page_scanner()

if __name__ == "__main__":
    main()
