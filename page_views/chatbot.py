"""
PyChamp AI Finance Chatbot — Streamlit Page
============================================
Interactive chat UI that wraps the chatbot engine in a beautiful, premium interface.
"""

import streamlit as st
import time
from database import load_expenses
from utils.chatbot import get_chatbot_response

# ─── Suggested Quick-Action Questions ──────────────────────────────────────
QUICK_PROMPTS = [
    ("💰", "How much did I spend?"),
    ("🏆", "What's my top spending category?"),
    ("📊", "Analyze my spending pattern"),
    ("✂️", "How can I reduce expenses?"),
    ("💡", "Give me a savings plan"),
    ("🏥", "What's my financial health score?"),
]

BOT_AVATAR = "⚡"
USER_AVATAR = "👤"


def inject_chat_css():
    st.markdown("""
    <style>
    /* === Chat Container === */
    .chat-wrapper {
        display: flex;
        flex-direction: column;
        gap: 1rem;
        padding: 0.5rem 0;
    }

    /* === Message Bubbles === */
    .msg-row {
        display: flex;
        align-items: flex-start;
        gap: 0.75rem;
        animation: slideUp 0.35s ease-out;
    }
    .msg-row.user {
        flex-direction: row-reverse;
    }
    @keyframes slideUp {
        from { opacity: 0; transform: translateY(12px); }
        to   { opacity: 1; transform: translateY(0); }
    }

    .msg-avatar {
        width: 36px;
        height: 36px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1rem;
        flex-shrink: 0;
        margin-top: 2px;
    }
    .avatar-bot  { background: linear-gradient(135deg, #00e599, #0ea5e9); }
    .avatar-user { background: linear-gradient(135deg, #6366f1, #8b5cf6); }

    .msg-bubble {
        max-width: 78%;
        padding: 0.9rem 1.2rem;
        border-radius: 16px;
        font-size: 0.92rem;
        line-height: 1.65;
        font-family: 'Inter', sans-serif;
    }
    .bubble-bot {
        background: rgba(14, 165, 233, 0.08);
        border: 1px solid rgba(14, 165, 233, 0.18);
        border-top-left-radius: 4px;
        color: #e2e8f0;
    }
    .bubble-user {
        background: rgba(99, 102, 241, 0.15);
        border: 1px solid rgba(99, 102, 241, 0.25);
        border-top-right-radius: 4px;
        color: #f1f5f9;
        text-align: right;
    }

    /* === Quick Prompts === */
    .quick-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 0.6rem;
        margin-bottom: 1rem;
    }
    .quick-btn {
        background: rgba(30, 41, 59, 0.5);
        border: 1px solid rgba(255,255,255,0.07);
        border-radius: 10px;
        padding: 0.55rem 0.8rem;
        font-size: 0.8rem;
        color: #94a3b8;
        cursor: pointer;
        text-align: center;
        transition: all 0.2s ease;
    }
    .quick-btn:hover {
        background: rgba(14, 165, 233, 0.12);
        border-color: rgba(14, 165, 233, 0.3);
        color: #e2e8f0;
    }

    /* === Typing indicator === */
    .typing-dots {
        display: inline-flex;
        align-items: center;
        gap: 4px;
        padding: 0.6rem 1rem;
    }
    .dot {
        width: 7px; height: 7px;
        border-radius: 50%;
        background: #0ea5e9;
        animation: bounce 1.2s infinite;
    }
    .dot:nth-child(2) { animation-delay: 0.2s; }
    .dot:nth-child(3) { animation-delay: 0.4s; }
    @keyframes bounce {
        0%, 80%, 100% { transform: scale(0.6); opacity: 0.4; }
        40%            { transform: scale(1.0); opacity: 1;   }
    }

    /* === Chat Input Overrides === */
    .stChatInput textarea {
        background: rgba(30, 41, 59, 0.6) !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        border-radius: 12px !important;
        color: #f1f5f9 !important;
        font-size: 0.92rem !important;
    }
    .stChatInput textarea:focus {
        border-color: rgba(14, 165, 233, 0.4) !important;
        box-shadow: 0 0 0 2px rgba(14, 165, 233, 0.1) !important;
    }

    /* === Header Gradient === */
    .chat-header {
        background: linear-gradient(135deg, rgba(0, 229, 153, 0.07), rgba(14, 165, 233, 0.07));
        border: 1px solid rgba(0, 229, 153, 0.15);
        border-radius: 16px;
        padding: 1.4rem 1.8rem;
        margin-bottom: 1.5rem;
        display: flex;
        align-items: center;
        gap: 1rem;
    }
    .chat-header-icon {
        font-size: 2.2rem;
        line-height: 1;
    }
    .chat-header-title {
        font-size: 1.4rem;
        font-weight: 700;
        color: #f8fafc;
        margin: 0;
    }
    .chat-header-sub {
        font-size: 0.85rem;
        color: #64748b;
        margin: 0;
    }

    /* === Status Badge === */
    .status-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: rgba(16,185,129,0.1);
        border: 1px solid rgba(16,185,129,0.2);
        border-radius: 20px;
        padding: 4px 12px;
        font-size: 0.75rem;
        color: #10b981;
        font-weight: 600;
        margin-left: auto;
    }
    .status-dot {
        width: 6px; height: 6px;
        background: #10b981;
        border-radius: 50%;
        animation: pulse 2s infinite;
    }
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50%       { opacity: 0.4; }
    }
    </style>
    """, unsafe_allow_html=True)


def _render_message(role: str, content: str):
    """Render a single chat message bubble."""
    if role == "assistant":
        st.markdown(f"""
        <div class="msg-row bot">
            <div class="msg-avatar avatar-bot">{BOT_AVATAR}</div>
            <div class="msg-bubble bubble-bot">{content}</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="msg-row user">
            <div class="msg-avatar avatar-user">{USER_AVATAR}</div>
            <div class="msg-bubble bubble-user">{content}</div>
        </div>
        """, unsafe_allow_html=True)


def _typing_indicator():
    return st.markdown("""
    <div class="msg-row bot">
        <div class="msg-avatar avatar-bot">⚡</div>
        <div class="msg-bubble bubble-bot">
            <div class="typing-dots">
                <div class="dot"></div>
                <div class="dot"></div>
                <div class="dot"></div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_chatbot(username: str):
    inject_chat_css()

    # ── Load expense data ──────────────────────────────────────────────────
    df = load_expenses(username)
    data_status = "📊 Data Loaded" if not df.empty else "📭 No Data"
    record_count = len(df) if not df.empty else 0

    # ── Header ─────────────────────────────────────────────────────────────
    st.markdown(f"""
    <div class="chat-header">
        <div class="chat-header-icon">⚡</div>
        <div>
            <p class="chat-header-title">PyChamp Finance Advisor</p>
            <p class="chat-header-sub">AI-powered • {record_count} transactions analyzed</p>
        </div>
        <div class="status-badge">
            <div class="status-dot"></div>
            Online
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Initialize session state ───────────────────────────────────────────
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    if "chat_initialized" not in st.session_state:
        welcome = (
            f"👋 Hi **{username.capitalize()}**! I'm your **PyChamp AI Finance Advisor**.\n\n"
            f"I've analyzed **{record_count} transactions** from your account. "
            + (
                f"You've spent a total of **₹{df['amount'].sum():,.0f}**. "
                if not df.empty else
                "I don't see any expense data yet — add transactions first for personalized insights. "
            )
            + "\n\nAsk me anything about your finances — spending, savings, or investment advice!"
        )
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": welcome
        })
        st.session_state.chat_initialized = True

    # ── Quick prompt buttons ────────────────────────────────────────────────
    st.markdown("**💬 Quick Questions:**")
    cols = st.columns(3)
    quick_input = None
    for idx, (emoji, label) in enumerate(QUICK_PROMPTS):
        with cols[idx % 3]:
            if st.button(f"{emoji} {label}", key=f"quick_{idx}", use_container_width=True):
                quick_input = label

    st.markdown("<hr style='border-color: rgba(255,255,255,0.05); margin: 1rem 0;'>", unsafe_allow_html=True)

    # ── Render existing messages ────────────────────────────────────────────
    # Use native st.chat_message for proper streaming + native look
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"], avatar="⚡" if msg["role"] == "assistant" else "👤"):
            st.markdown(msg["content"])

    # ── Handle quick prompt ─────────────────────────────────────────────────
    if quick_input:
        _process_message(quick_input, df)

    # ── Chat input ─────────────────────────────────────────────────────────
    user_msg = st.chat_input(
        placeholder="Ask me about your spending, savings, or any finance question...",
    )

    if user_msg:
        _process_message(user_msg, df)

    # ── Clear chat button ───────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    col_l, col_r = st.columns([4, 1])
    with col_r:
        if st.button("🗑️ Clear Chat", key="clear_chat", use_container_width=True):
            st.session_state.chat_history = []
            st.session_state.chat_initialized = False
            st.rerun()


def _process_message(user_msg: str, df):
    """Append user message, generate bot response, and rerun."""

    # Add user message
    st.session_state.chat_history.append({"role": "user", "content": user_msg})

    # Display immediately (without waiting for bot)
    with st.chat_message("user", avatar="👤"):
        st.markdown(user_msg)

    # Simulate AI thinking with a short delay then respond
    with st.chat_message("assistant", avatar="⚡"):
        with st.spinner("Analyzing your finances..."):
            time.sleep(0.6)  # brief "thinking" pause for UX
            bot_response = get_chatbot_response(user_msg, df)

        st.markdown(bot_response)

    # Store bot response
    st.session_state.chat_history.append({"role": "assistant", "content": bot_response})
