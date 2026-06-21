"""Authentication module for CareGradients AI.

Provides a database-backed login/registration system with Gmail OTP
email verification. Admin credentials are auto-seeded on first run.
SMTP settings are read from Streamlit secrets (.streamlit/secrets.toml).
"""

import hashlib
import random
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import streamlit as st

from src.database import (
    #init_users_db,
    create_user,
    get_user_by_username,
    get_user_by_email,
    update_last_login,
)


# ==========================================
# HELPERS
# ==========================================

def _hash_password(password: str) -> str:
    """SHA-256 hash of the given password string."""
    return hashlib.sha256(password.encode()).hexdigest()


def _generate_otp() -> str:
    """Generate a random 6-digit OTP code."""
    return str(random.randint(100000, 999999))


def _send_otp_email(recipient_email: str, otp_code: str) -> bool:
    """Send an OTP verification email via SMTP.

    Returns True on success, False on failure.
    SMTP credentials are read from st.secrets["email"].
    """
    try:
        email_cfg = st.secrets.get("email", {})
        smtp_server = email_cfg.get("smtp_server", "smtp.gmail.com")
        smtp_port = int(email_cfg.get("smtp_port", 587))
        sender_email = email_cfg.get("sender_email", "")
        smtp_username = email_cfg.get("smtp_username", sender_email)
        app_password = email_cfg.get("app_password", "")

        if not sender_email or not app_password:
            st.error("⚠️ Email SMTP not configured. Please set up `.streamlit/secrets.toml` with your SMTP Key.")
            return False

        # Build the email
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"🔐 CareGradients AI — Your Verification Code: {otp_code}"
        msg["From"] = f"CareGradients AI <{sender_email}>"
        msg["To"] = recipient_email

        html_body = f"""
        <div style="font-family: 'Segoe UI', Arial, sans-serif; max-width: 480px; margin: 0 auto;
                    background: linear-gradient(145deg, #0f172a, #1e293b); border-radius: 16px;
                    padding: 40px 32px; color: #e2e8f0; border: 1px solid #334155;">
            <div style="text-align: center; margin-bottom: 24px;">
                <span style="font-size: 36px;">🩺</span>
                <h2 style="margin: 8px 0 4px 0; background: linear-gradient(135deg, #6366f1, #a78bfa);
                           -webkit-background-clip: text; -webkit-text-fill-color: transparent;
                           font-size: 24px;">CareGradients AI</h2>
                <p style="color: #64748b; font-size: 13px; margin: 0;">Clinical Decision Support Engine</p>
            </div>
            <div style="background: rgba(99, 102, 241, 0.08); border: 1px solid rgba(99, 102, 241, 0.2);
                        border-radius: 12px; padding: 24px; text-align: center; margin: 20px 0;">
                <p style="color: #94a3b8; font-size: 14px; margin: 0 0 12px 0;">Your verification code is:</p>
                <div style="font-size: 36px; font-weight: 800; letter-spacing: 8px; color: #a78bfa;
                            text-shadow: 0 0 10px rgba(167, 139, 250, 0.3);">{otp_code}</div>
            </div>
            <p style="color: #64748b; font-size: 12px; text-align: center; margin-top: 20px;">
                This code expires in 10 minutes. If you didn't request this, please ignore this email.
            </p>
            <div style="text-align: center; margin-top: 24px; padding-top: 16px;
                        border-top: 1px solid #1e293b;">
                <p style="color: #475569; font-size: 11px; margin: 0;">
                    © 2026 CareGradients AI · Built by Dheeraj Tiwari
                </p>
            </div>
        </div>
        """

        plain_text = f"Your CareGradients AI verification code is: {otp_code}. This code expires in 10 minutes."

        msg.attach(MIMEText(plain_text, "plain"))
        msg.attach(MIMEText(html_body, "html"))

        # Send via SMTP
        context = ssl.create_default_context()
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.ehlo()
            server.starttls(context=context)
            server.ehlo()
            server.login(smtp_username, app_password)
            server.sendmail(sender_email, recipient_email, msg.as_string())

        return True

    except smtplib.SMTPAuthenticationError:
        st.error("❌ SMTP Authentication failed. Please check your SMTP credentials in `secrets.toml`.")
        return False
    except Exception as e:
        st.error(f"❌ Failed to send OTP email. Error: {e}")
        return False


# ==========================================
# LOGIN PAGE STYLES
# ==========================================

def _inject_auth_styles():
    """Inject premium CSS for the login/register page."""
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap');

        [data-testid="stAppViewContainer"] {
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #0f172a 100%);
        }

        html, body, [class*="css"], .stApp {
            font-family: 'Outfit', sans-serif;
        }

        .auth-header {
            text-align: center;
            padding: 3vh 0 2vh 0;
        }

        .auth-icon {
            font-size: 3.2rem;
            margin-bottom: 8px;
        }

        .auth-title {
            font-size: 2.2rem;
            font-weight: 800;
            background: linear-gradient(135deg, #6366f1, #a78bfa, #38bdf8);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 4px;
        }

        .auth-subtitle {
            color: #64748b;
            font-size: 0.9rem;
        }

        .auth-card {
            background: rgba(30, 41, 59, 0.8);
            border: 1px solid rgba(99, 102, 241, 0.25);
            border-radius: 20px;
            padding: 2rem 1.5rem;
            backdrop-filter: blur(20px);
            box-shadow: 0 25px 50px rgba(0,0,0,0.5), 0 0 0 1px rgba(99,102,241,0.1);
        }

        .otp-display {
            text-align: center;
            margin: 16px 0;
        }

        .otp-label {
            color: #94a3b8;
            font-size: 13px;
            margin-bottom: 6px;
        }

        .otp-email-highlight {
            display: inline-block;
            background: rgba(99, 102, 241, 0.12);
            border: 1px solid rgba(99, 102, 241, 0.25);
            border-radius: 8px;
            padding: 6px 14px;
            color: #a78bfa;
            font-weight: 600;
            font-size: 14px;
            margin-top: 4px;
        }

        .auth-error {
            background: rgba(239, 68, 68, 0.12);
            border: 1px solid rgba(239, 68, 68, 0.3);
            border-radius: 10px;
            padding: 10px 16px;
            color: #fca5a5;
            font-size: 13px;
            text-align: center;
            margin-top: 8px;
        }

        .auth-success {
            background: rgba(46, 196, 182, 0.12);
            border: 1px solid rgba(46, 196, 182, 0.3);
            border-radius: 10px;
            padding: 10px 16px;
            color: #2ec4b6;
            font-size: 13px;
            text-align: center;
            margin-top: 8px;
        }

        /* Style for the confidentiality text (keeps its natural flow) */
        .auth-footer-1 {
            text-align: center;
            color: #475569;
            font-size: 0.78rem;
            margin-top: 2rem;
            margin-bottom: 1rem;
        }
        
        /* Style to force the creators' names to the absolute bottom */
        .auth-footer-2 {
            position: fixed;
            left: 0;
            bottom: 10px; /* Distance from the very bottom edge */
            width: 100%;
            text-align: center;
            color: #475569;
            font-size: 0.78rem;
            z-index: 999; /* Keeps it visible above background elements */
        }

        /* Hide sidebar on auth page */
        [data-testid="stSidebar"] { display: none; }
        </style>
        """,
        unsafe_allow_html=True,
    )


# ==========================================
# RENDER AUTH PAGE
# ==========================================

def render_login_page() -> None:
    """Render a premium login/register page with OTP verification."""
    _inject_auth_styles()

    # Ensure users table exists
    from src.database import init_users_db
    init_users_db()

    # Header
    st.markdown(
        """
        <div class="auth-header">
            <div class="auth-icon">🔐</div>
            <div class="auth-title">CareGradients AI</div>
            <div class="auth-subtitle">Clinical Decision Support — Secure Access Portal</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Center the form
    col_l, col_c, col_r = st.columns([1, 2, 1])

    with col_c:
        # Check if we're in OTP verification step
        if st.session_state.get("otp_step", False):
            _render_otp_verification()
            return

        # Login / Register tabs
        tab_login, tab_register = st.tabs(["🔑 Sign In", "📝 Register"])

        with tab_login:
            _render_login_form()

        with tab_register:
            _render_register_form()

        st.markdown(
            '<p class="auth-footer-1">🔒 All patient records are protected under clinical confidentiality.</p>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<p class="auth-footer-2">    Made by Dheeraj.</p>',
            unsafe_allow_html=True,
        )


def _render_login_form():
    """Render the sign-in form."""
    with st.form("login_form", clear_on_submit=False):
        username = st.text_input("👤 Username", placeholder="Enter your username", key="login_user")
        password = st.text_input("🔒 Password", type="password", placeholder="Enter your password", key="login_pass")
        login_btn = st.form_submit_button("Sign In →", use_container_width=True, type="primary")

        if login_btn:
            if not username or not password:
                st.markdown('<div class="auth-error">❌ Please fill in both fields.</div>', unsafe_allow_html=True)
                return

            user = get_user_by_username(username.strip())
            hashed = _hash_password(password)

            if user and user["password_hash"] == hashed:
                update_last_login(username.strip())
                st.session_state["authenticated"] = True
                st.session_state["current_user"] = username.strip()
                st.session_state["user_role"] = user["role"]
                st.session_state["user_fullname"] = user["full_name"]
                st.rerun()
            else:
                st.markdown(
                    '<div class="auth-error">❌ Invalid username or password. Please try again.</div>',
                    unsafe_allow_html=True,
                )


def _render_register_form():
    """Render the registration form (Step 1: collect details, send OTP)."""
    with st.form("register_form", clear_on_submit=False):
        reg_name = st.text_input("👤 Full Name", placeholder="e.g. Dheeraj Tiwari", key="reg_name")
        reg_email = st.text_input("✉️ Email Address", placeholder="e.g. dheerajtiwari.pandit@gmail.com", key="reg_email")
        reg_user = st.text_input("🏷️ Choose Username", placeholder="e.g. dheerajtiwari123", key="reg_user")
        reg_pass = st.text_input("🔒 Create Password", type="password", placeholder="Min 6 characters", key="reg_pass")
        reg_pass_confirm = st.text_input("🔒 Confirm Password", type="password", placeholder="Re-enter password", key="reg_pass2")
        reg_btn = st.form_submit_button("Send OTP →", use_container_width=True, type="primary")

        if reg_btn:
            # Validate inputs
            if not all([reg_name, reg_email, reg_user, reg_pass, reg_pass_confirm]):
                st.markdown('<div class="auth-error">❌ Please fill in all fields.</div>', unsafe_allow_html=True)
                return

            if len(reg_pass) < 6:
                st.markdown('<div class="auth-error">❌ Password must be at least 6 characters.</div>', unsafe_allow_html=True)
                return

            if reg_pass != reg_pass_confirm:
                st.markdown('<div class="auth-error">❌ Passwords do not match.</div>', unsafe_allow_html=True)
                return

            if "@" not in reg_email or "." not in reg_email:
                st.markdown('<div class="auth-error">❌ Please enter a valid email address.</div>', unsafe_allow_html=True)
                return

            # Check if username/email already taken
            if get_user_by_username(reg_user.strip()):
                st.markdown('<div class="auth-error">❌ Username is already taken. Choose another.</div>', unsafe_allow_html=True)
                return

            if get_user_by_email(reg_email.strip()):
                st.markdown('<div class="auth-error">❌ This email is already registered.</div>', unsafe_allow_html=True)
                return

            # Generate and send OTP
            otp = _generate_otp()
            sent = _send_otp_email(reg_email.strip(), otp)

            if sent:
                # Store registration data in session for OTP step
                st.session_state["otp_step"] = True
                st.session_state["otp_code"] = otp
                st.session_state["reg_data"] = {
                    "full_name": reg_name.strip(),
                    "email": reg_email.strip(),
                    "username": reg_user.strip(),
                    "password_hash": _hash_password(reg_pass),
                }
                st.rerun()


def _render_otp_verification():
    """Render the OTP verification step (Step 2)."""
    reg_data = st.session_state.get("reg_data", {})
    email = reg_data.get("email", "")

    st.markdown(
        f"""
        <div class="otp-display">
            <div class="otp-label">A 6-digit verification code has been sent to:</div>
            <div class="otp-email-highlight">✉️ {email}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.form("otp_form", clear_on_submit=False):
        otp_input = st.text_input(
            "🔢 Enter 6-Digit OTP",
            placeholder="e.g. 482917",
            max_chars=6,
            key="otp_input",
        )
        col_verify, col_cancel = st.columns(2)
        with col_verify:
            verify_btn = st.form_submit_button("✅ Verify & Create Account", use_container_width=True, type="primary")
        with col_cancel:
            cancel_btn = st.form_submit_button("← Back to Register", use_container_width=True)

        if cancel_btn:
            # Clear OTP state and go back
            st.session_state.pop("otp_step", None)
            st.session_state.pop("otp_code", None)
            st.session_state.pop("reg_data", None)
            st.rerun()

        if verify_btn:
            stored_otp = st.session_state.get("otp_code", "")
            if otp_input.strip() == stored_otp:
                # OTP verified — create the account
                success = create_user(
                    username=reg_data["username"],
                    full_name=reg_data["full_name"],
                    email=reg_data["email"],
                    password_hash=reg_data["password_hash"],
                )
                if success:
                    # Clear OTP state
                    st.session_state.pop("otp_step", None)
                    st.session_state.pop("otp_code", None)
                    st.session_state.pop("reg_data", None)
                    st.session_state["registration_success"] = True
                    st.rerun()
                else:
                    st.markdown(
                        '<div class="auth-error">❌ Account creation failed. Username or email may already exist.</div>',
                        unsafe_allow_html=True,
                    )
            else:
                st.markdown(
                    '<div class="auth-error">❌ Invalid OTP. Please check your email and try again.</div>',
                    unsafe_allow_html=True,
                )

    # Resend OTP button (outside the form)
    if st.button("🔄 Resend OTP", use_container_width=True):
        new_otp = _generate_otp()
        sent = _send_otp_email(email, new_otp)
        if sent:
            st.session_state["otp_code"] = new_otp
            st.success("✅ New OTP sent! Check your inbox.")


# ==========================================
# AUTH GATE & LOGOUT
# ==========================================

def require_auth() -> bool:
    """Check if the user is authenticated.

    If not, render the login/register page and halt the app.
    Returns True if already authenticated.
    """
    if st.session_state.get("authenticated", False):
        return True

    # Show success message if just registered
    if st.session_state.pop("registration_success", False):
        st.success("🎉 Account created successfully! You can now sign in.")

    render_login_page()
    st.stop()
    return False


def render_logout_button() -> None:
    """Render user info and logout button in the sidebar."""
    user = st.session_state.get("current_user", "User")
    role = st.session_state.get("user_role", "user")
    fullname = st.session_state.get("user_fullname", user)

    role_badge = "🛡️ Admin" if role == "admin" else "👤 User"

    st.sidebar.markdown("---")
    st.sidebar.markdown(
        f"<small style='color:#64748b;'>Signed in as <b style='color:#a78bfa;'>{fullname}</b>"
        f" <span style='background:rgba(99,102,241,0.15);color:#a78bfa;padding:2px 8px;"
        f"border-radius:12px;font-size:11px;font-weight:600;'>{role_badge}</span></small>",
        unsafe_allow_html=True,
    )
    if st.sidebar.button("🚪 Sign Out", use_container_width=True):
        for key in ["authenticated", "current_user", "user_role", "user_fullname"]:
            st.session_state.pop(key, None)
        st.rerun()


def is_admin() -> bool:
    """Return True if the current user has the admin role."""
    return st.session_state.get("user_role", "user") == "admin"
