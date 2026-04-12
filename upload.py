import streamlit as st
import pandas as pd
import sqlite3
from database import get_connection


def render_upload(username):
    # ── Page header ──────────────────────────────────────────────────────────
    st.markdown("""
    <div class="page-header">
        <div class="page-header-title">📤 Import CSV</div>
        <div class="page-header-sub">Bulk-upload your bank/wallet transaction history in seconds</div>
    </div>
    """, unsafe_allow_html=True)

    # ── Upload zone ───────────────────────────────────────────────────────────
    st.markdown("""
    <div class="upload-zone">
        <span class="upload-icon">☁️</span>
        <div style="font-size:1rem; font-weight:600; color:#94a3b8; margin-bottom:6px; font-family:'Outfit',sans-serif;">
            Drop your CSV file here
        </div>
        <div class="upload-text">Supports bank exports, Splitwise, Walnut · Max 50 MB</div>
    </div>
    """, unsafe_allow_html=True)

    file = st.file_uploader(
        label="Choose CSV file",
        type=["csv"],
        label_visibility="collapsed"
    )

    st.write("")

    # ── Format reference ──────────────────────────────────────────────────────
    st.markdown("""
    <div class="chart-card">
        <div class="chart-title">📋 Expected CSV Format</div>
    """, unsafe_allow_html=True)

    format_df = pd.DataFrame([
        {"Column": "date",        "Type": "YYYY-MM-DD", "Example": "2026-04-09", "Required": "✅ Yes"},
        {"Column": "description", "Type": "string",     "Example": "Swiggy Order", "Required": "✅ Yes"},
        {"Column": "category",    "Type": "string",     "Example": "Food",         "Required": "✅ Yes"},
        {"Column": "amount",      "Type": "float",      "Example": "840.00",       "Required": "✅ Yes"},
        {"Column": "notes",       "Type": "string",     "Example": "Optional note","Required": "⬜ No"},
    ])
    st.dataframe(format_df, hide_index=True, use_container_width=True)

    st.markdown("""
    <div style="margin-top:0.75rem; font-size:0.8rem; color:#475569; font-family:'Inter',sans-serif;">
        💡 <b style="color:#64748b;">Tip:</b> Column headers must match exactly (lowercase). 
        Category values can be anything — they'll be used as-is for analysis.
    </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # ── Process upload ────────────────────────────────────────────────────────
    if file is not None:
        st.write("")
        try:
            df = pd.read_csv(file)
            df.columns = df.columns.str.strip().str.lower()

            # Preview
            st.markdown("""
            <div class="chart-card">
                <div class="chart-title">👁️ Data Preview</div>
            """, unsafe_allow_html=True)
            st.dataframe(df.head(10), hide_index=True, use_container_width=True)
            st.markdown(f"""
            <div style="font-size:0.8rem; color:#475569; margin-top:0.5rem; font-family:'Inter',sans-serif;">
                Showing 10 of <b style="color:#64748b;">{len(df)}</b> rows detected
            </div>
            """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

            st.write("")
            col_l, col_btn, col_r = st.columns([2, 1, 2])
            with col_btn:
                process = st.button("⚡ Process & Import", type="primary", use_container_width=True)

            if process:
                if "date" in df.columns and "amount" in df.columns and "category" in df.columns:
                    try:
                        conn = get_connection()
                        cur  = conn.cursor()
                        count = 0
                        for _, row in df.iterrows():
                            desc = str(row.get("description", ""))
                            note = str(row.get("notes", ""))
                            cur.execute(
                                "INSERT INTO expenses (username, date, category, amount, note) VALUES (?, ?, ?, ?, ?)",
                                (username, str(row['date']), str(row['category']),
                                 float(row['amount']), note if note else desc)
                            )
                            count += 1
                        conn.commit()
                        conn.close()
                        st.success(f"✅ Successfully imported **{count}** records! Head to Overview to see your dashboard.")
                    except Exception as e:
                        st.error(f"❌ Error while importing: {e}")
                else:
                    st.error("❌ Missing required columns: **date**, **amount**, **category**. Check that headers match exactly.")
        except Exception as e:
            st.error(f"❌ Could not read file: {e}")
