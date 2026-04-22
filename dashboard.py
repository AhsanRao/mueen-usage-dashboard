import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="Ministry Usage Dashboard",
    page_icon="🏛️",
    layout="wide",
)

st.title("🏛️ Ministry Usage Dashboard")

# ── Load data ────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    convs  = pd.read_csv("total_conversations.csv")
    users  = pd.read_csv("total_users.csv")
    qtypes = pd.read_csv("question_types.csv")
    merged = (
        convs
        .merge(users,  on="ministry_domain", how="outer")
        .merge(qtypes, on="ministry_domain", how="outer")
        .fillna(0)
    )
    # Pretty label: strip common suffixes for display
    merged["label"] = merged["ministry_domain"].str.replace(
        r"\.(gov\.om|edu\.om|om|co)$", "", regex=True
    ).str.upper()
    return merged, convs, users, qtypes

df, convs, users, qtypes = load_data()

@st.cache_data
def load_registered():
    reg = pd.read_csv("registered_users.csv")
    reg["label"] = reg["domain"].str.replace(
        r"\.(gov\.om|edu\.om|om|co)$", "", regex=True
    ).str.upper()
    return reg

reg = load_registered()

# ── KPI cards ────────────────────────────────────────────────────────────────
total_ministries   = df["ministry_domain"].nunique()
total_users        = int(users["total_users"].sum())
total_convs        = int(convs["total_conversations"].sum())
total_messages     = int(convs["total_messages"].sum())
total_registered   = int(reg["user_count"].sum())
reg_ministries     = reg["domain"].nunique()

k1, k2, k3, k4, k5, k6 = st.columns(6)
k1.metric("Total Active Ministries",        total_ministries)
k2.metric("Total Active Users",      f"{total_users:,}")
k3.metric("Total Conversations",     f"{total_convs:,}")
k4.metric("Total Messages",          f"{total_messages:,}")
k5.metric("Registered Ministries",   reg_ministries)
k6.metric("Registered Users",        f"{total_registered:,}")

st.divider()

# ── Conversations per ministry ───────────────────────────────────────────────
st.subheader("Conversations per Ministry")
conv_df = (
    df[["label", "total_conversations"]]
    .sort_values("total_conversations", ascending=True)
)
fig_conv = px.bar(
    conv_df,
    x="total_conversations",
    y="label",
    orientation="h",
    labels={"total_conversations": "Conversations", "label": "Ministry"},
    color="total_conversations",
    color_continuous_scale="Blues",
)
fig_conv.update_layout(coloraxis_showscale=False, height=550, margin=dict(l=10, r=10, t=10, b=10))
st.plotly_chart(fig_conv, use_container_width=True)

st.divider()

# ── Users & total queries per ministry (side-by-side) ───────────────────────
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("Users per Ministry")
    user_df = (
        df[["label", "total_users"]]
        .sort_values("total_users", ascending=True)
    )
    fig_users = px.bar(
        user_df,
        x="total_users",
        y="label",
        orientation="h",
        labels={"total_users": "Users", "label": "Ministry"},
        color="total_users",
        color_continuous_scale="Greens",
    )
    fig_users.update_layout(coloraxis_showscale=False, height=550, margin=dict(l=10, r=10, t=10, b=10))
    st.plotly_chart(fig_users, use_container_width=True)

with col_right:
    st.subheader("Total Queries per Ministry")
    query_df = (
        df[["label", "total_queries"]]
        .sort_values("total_queries", ascending=True)
    )
    fig_queries = px.bar(
        query_df,
        x="total_queries",
        y="label",
        orientation="h",
        labels={"total_queries": "Total Queries", "label": "Ministry"},
        color="total_queries",
        color_continuous_scale="Oranges",
    )
    fig_queries.update_layout(coloraxis_showscale=False, height=550, margin=dict(l=10, r=10, t=10, b=10))
    st.plotly_chart(fig_queries, use_container_width=True)

st.divider()

# ── Query type breakdown ─────────────────────────────────────────────────────
# st.subheader("Usage Breakdown by Query Type")

# query_type_cols = ["translation", "summarization", "content_generation", "question_answer", "other"]
# breakdown_df = (
#     df[["label"] + query_type_cols]
#     .sort_values("question_answer", ascending=False)
#     .head(15)          # top 15 by Q&A volume for readability
#     .melt(id_vars="label", var_name="Query Type", value_name="Count")
# )

# fig_stack = px.bar(
#     breakdown_df,
#     x="label",
#     y="Count",
#     color="Query Type",
#     barmode="stack",
#     labels={"label": "Ministry", "Count": "Queries"},
#     color_discrete_sequence=px.colors.qualitative.Set2,
# )
# fig_stack.update_layout(height=420, margin=dict(l=10, r=10, t=10, b=10), xaxis_tickangle=-30)
# st.plotly_chart(fig_stack, use_container_width=True)

# st.divider()

# ── Registered users per ministry ───────────────────────────────────────────
st.subheader("Registered Users per Ministry")
reg_sorted = reg.sort_values("user_count", ascending=True)
fig_reg = px.bar(
    reg_sorted,
    x="user_count",
    y="label",
    orientation="h",
    labels={"user_count": "Registered Users", "label": "Ministry"},
    color="user_count",
    color_continuous_scale="Purples",
)
fig_reg.update_layout(coloraxis_showscale=False, height=600, margin=dict(l=10, r=10, t=10, b=10))
st.plotly_chart(fig_reg, use_container_width=True)

st.divider()

# ── Raw data table ───────────────────────────────────────────────────────────
with st.expander("View raw data"):
    display_cols = {
        "ministry_domain": "Domain",
        "total_users": "Users",
        "total_conversations": "Conversations",
        "total_messages": "Messages",
        "avg_messages_per_user": "Avg Msgs/User",
        "total_queries": "Total Queries",
        # "translation": "Translation",
        # "summarization": "Summarization",
        # "content_generation": "Content Gen",
        # "question_answer": "Q&A",
        # "other": "Other",
    }
    st.dataframe(
        df[list(display_cols.keys())].rename(columns=display_cols).sort_values("Conversations", ascending=False),
        use_container_width=True,
        hide_index=True,
    )
