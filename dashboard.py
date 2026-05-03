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
st.caption("Analysis as of 26 April 2026")

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
    return merged, convs, users, qtypes

df, convs, users, qtypes = load_data()

@st.cache_data
def load_ministries():
    m = pd.read_csv("ministries.csv")
    m = m.rename(columns={"English Name": "english_name", "Domain": "domain"})
    m["domain"] = m["domain"].str.strip().str.lower()
    m = m[m["domain"].notna() & (m["domain"] != "")]
    return m

@st.cache_data
def load_registered():
    reg = pd.read_csv("registered_users.csv")
    reg = reg.rename(columns={"English Name": "english_name", "Domain": "domain", "User Count": "user_count"})
    reg["user_count"] = pd.to_numeric(reg["user_count"], errors="coerce").fillna(0).astype(int)
    return reg

@st.cache_data
def load_quota_summary():
    q = pd.read_csv("ministry_quota_summary.csv")
    q["domain"] = q["domain"].str.strip().str.lower()
    q = q[~q["domain"].isin(["omandatapark.com", "otech.om", "bot.mueen.om"])]
    return q

ministries = load_ministries()
reg        = load_registered()
quota      = load_quota_summary()

# Build name map from ministries.csv (authoritative), fall back to registered_users.csv
name_map = ministries.set_index("domain")["english_name"].to_dict()
name_map.update({k: v for k, v in reg.set_index("domain")["english_name"].to_dict().items() if k not in name_map})
df["label"]  = df["ministry_domain"].map(name_map).fillna(df["ministry_domain"])
reg["label"] = reg["domain"].map(name_map).fillna(reg["domain"])

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
st.subheader("Conversations per Ministry in Last 30 Days")
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
    text="total_conversations",
)
fig_conv.update_traces(textposition="outside", texttemplate="%{x:,}")
fig_conv.update_layout(coloraxis_showscale=False, height=550, margin=dict(l=10, r=80, t=10, b=10))
st.plotly_chart(fig_conv, use_container_width=True)

st.divider()

# ── Active users per ministry — top 5 / bottom 5 ────────────────────────────
st.subheader("Active Users per Ministry in Last 30 Days")

user_sorted = df[["label", "total_users"]].sort_values("total_users", ascending=False)
user_top5   = user_sorted.head(5).sort_values("total_users", ascending=True)
user_bot5   = user_sorted[user_sorted["total_users"] > 0].tail(5).sort_values("total_users", ascending=True)

u_left, u_right = st.columns(2)

with u_left:
    st.markdown("**Top 5**")
    fig_u_top = px.bar(
        user_top5, x="total_users", y="label", orientation="h",
        labels={"total_users": "Users", "label": "Ministry"},
        color="total_users", color_continuous_scale="Greens", text="total_users",
    )
    fig_u_top.update_traces(textposition="outside", texttemplate="%{x:,}")
    fig_u_top.update_layout(coloraxis_showscale=False, height=300, margin=dict(l=10, r=80, t=10, b=10))
    st.plotly_chart(fig_u_top, use_container_width=True)

with u_right:
    st.markdown("**Bottom 5**")
    fig_u_bot = px.bar(
        user_bot5, x="total_users", y="label", orientation="h",
        labels={"total_users": "Users", "label": "Ministry"},
        color="total_users", color_continuous_scale="Greens", text="total_users",
    )
    fig_u_bot.update_traces(textposition="outside", texttemplate="%{x:,}")
    fig_u_bot.update_layout(coloraxis_showscale=False, height=300, margin=dict(l=10, r=80, t=10, b=10))
    st.plotly_chart(fig_u_bot, use_container_width=True)

st.divider()

# ── Queries per ministry — top 5 / bottom 5 ─────────────────────────────────
st.subheader("Queries per Ministry in Last 30 Days")

query_sorted = df[["label", "total_queries"]].sort_values("total_queries", ascending=False)
query_top5   = query_sorted.head(5).sort_values("total_queries", ascending=True)
query_bot5   = query_sorted[query_sorted["total_queries"] > 0].tail(5).sort_values("total_queries", ascending=True)

q_left, q_right = st.columns(2)

with q_left:
    st.markdown("**Top 5**")
    fig_q_top = px.bar(
        query_top5, x="total_queries", y="label", orientation="h",
        labels={"total_queries": "Queries", "label": "Ministry"},
        color="total_queries", color_continuous_scale="Oranges", text="total_queries",
    )
    fig_q_top.update_traces(textposition="outside", texttemplate="%{x:,}")
    fig_q_top.update_layout(coloraxis_showscale=False, height=300, margin=dict(l=10, r=80, t=10, b=10))
    st.plotly_chart(fig_q_top, use_container_width=True)

with q_right:
    st.markdown("**Bottom 5**")
    fig_q_bot = px.bar(
        query_bot5, x="total_queries", y="label", orientation="h",
        labels={"total_queries": "Queries", "label": "Ministry"},
        color="total_queries", color_continuous_scale="Oranges", text="total_queries",
    )
    fig_q_bot.update_traces(textposition="outside", texttemplate="%{x:,}")
    fig_q_bot.update_layout(coloraxis_showscale=False, height=300, margin=dict(l=10, r=80, t=10, b=10))
    st.plotly_chart(fig_q_bot, use_container_width=True)

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
st.subheader("Total Registered Users per Ministry")
reg_sorted = reg.sort_values("user_count", ascending=True)
fig_reg = px.bar(
    reg_sorted,
    x="user_count",
    y="label",
    orientation="h",
    labels={"user_count": "Registered Users", "label": "Ministry"},
    color="user_count",
    color_continuous_scale="Purples",
    text="user_count",
)
fig_reg.update_traces(textposition="outside", texttemplate="%{x:,}")
fig_reg.update_layout(coloraxis_showscale=False, height=1200, margin=dict(l=10, r=80, t=10, b=10))
st.plotly_chart(fig_reg, use_container_width=True)

st.divider()

# ── Registered vs. Quota ─────────────────────────────────────────────────────
st.subheader("Registered vs. Quota per Ministry")

quota_plot = quota[["domain", "ministry_code", "quota_limit", "keycloak_active_users"]].copy()
quota_plot["label"] = quota_plot["domain"].map(name_map).fillna(quota_plot["ministry_code"].str.strip())
quota_plot = quota_plot.rename(columns={"keycloak_active_users": "user_count"})
quota_plot["quota_used_pct"] = (quota_plot["user_count"] / quota_plot["quota_limit"].replace(0, float("nan")) * 100).round(1).fillna(0)
quota_plot = quota_plot.sort_values("quota_used_pct", ascending=True)

qc1, qc2 = st.columns([3, 2])

with qc1:
    st.markdown("**Registered vs. Quota**")
    fig_quota = go.Figure()
    fig_quota.add_trace(go.Bar(
        y=quota_plot["label"],
        x=quota_plot["quota_limit"],
        name="Quota",
        orientation="h",
        marker_color="lightsteelblue",
        text=quota_plot["quota_limit"],
        textposition="outside",
        textangle=0,
        cliponaxis=False,
        textfont=dict(color="steelblue"),
    ))
    # Bars wide enough to hold inside text (>= 20 % of quota): label inside white
    # Bars too thin (< 20 % of quota): label outside dark — avoids overlap in both cases
    ratio = quota_plot["user_count"] / quota_plot["quota_limit"].replace(0, float("nan"))
    large = ratio >= 0.20
    fig_quota.add_trace(go.Bar(
        y=quota_plot["label"],
        x=quota_plot["user_count"].where(large),
        name="Registered",
        orientation="h",
        marker_color="steelblue",
        text=quota_plot["user_count"].where(large),
        textposition="inside",
        insidetextanchor="end",
        textangle=0,
        textfont=dict(color="white"),
    ))
    fig_quota.add_trace(go.Bar(
        y=quota_plot["label"],
        x=quota_plot["user_count"].where(~large),
        name="Registered",
        showlegend=False,
        orientation="h",
        marker_color="steelblue",
        text=quota_plot["user_count"].where(~large),
        textposition="outside",
        textangle=0,
        cliponaxis=False,
        textfont=dict(color="steelblue"),
    ))
    fig_quota.update_layout(
        barmode="overlay",
        height=max(600, len(quota_plot) * 24),
        margin=dict(l=10, r=80, t=10, b=10),
        legend=dict(orientation="h", yanchor="bottom", y=1.01, xanchor="left", x=0),
        xaxis_title="Users",
    )
    st.plotly_chart(fig_quota, use_container_width=True)

with qc2:
    st.markdown("**Quota Used (%)**")
    fig_pct = px.bar(
        quota_plot,
        x="quota_used_pct",
        y="label",
        orientation="h",
        labels={"quota_used_pct": "% Used", "label": "Ministry"},
        color="quota_used_pct",
        color_continuous_scale="RdYlGn_r",
        range_x=[0, max(quota_plot["quota_used_pct"].max() * 1.15, 110)],
        text="quota_used_pct",
    )
    fig_pct.add_vline(x=100, line_dash="dash", line_color="red", line_width=1)
    fig_pct.update_traces(textposition="outside", texttemplate="%{x:.1f}%", textangle=0, cliponaxis=False)
    fig_pct.update_layout(
        coloraxis_showscale=False,
        height=max(600, len(quota_plot) * 24),
        margin=dict(l=10, r=80, t=10, b=10),
    )
    st.plotly_chart(fig_pct, use_container_width=True)

with st.expander("View quota table"):
    quota_table = quota_plot[["label", "domain", "user_count", "quota_limit", "quota_used_pct"]].rename(columns={
        "label":          "Ministry",
        "domain":         "Domain",
        "user_count":     "Registered",
        "quota_limit":    "Quota",
        "quota_used_pct": "% Used",
    }).sort_values("% Used", ascending=False)
    st.dataframe(quota_table.reset_index(drop=True), use_container_width=True, hide_index=True)

st.divider()

# ── Active utilization vs. quota ─────────────────────────────────────────────
st.subheader("Active Utilization (Last 30 Days) vs. Quota per Ministry")

active_df = (
    quota_plot[["domain", "label", "quota_limit", "user_count"]]
    .rename(columns={"user_count": "registered"})
    .merge(
        users.rename(columns={"ministry_domain": "domain"})[["domain", "total_users"]],
        on="domain", how="left",
    )
    .fillna(0)
)
active_df["total_users"] = active_df["total_users"].astype(int)
active_df["registered"]  = active_df["registered"].astype(int)
active_df = active_df.sort_values("registered", ascending=True)

active_cat = active_df["label"].tolist()

fig_active = go.Figure()
fig_active.add_trace(go.Bar(
    y=active_df["label"],
    x=active_df["quota_limit"],
    name="Quota",
    orientation="h",
    marker_color="lightsteelblue",
    text=active_df["quota_limit"],
    textposition="outside",
    textangle=0,
    cliponaxis=False,
))
fig_active.add_trace(go.Bar(
    y=active_df["label"],
    x=active_df["registered"],
    name="Registered",
    orientation="h",
    marker_color="steelblue",
    text=active_df["registered"],
    textposition="outside",
    textangle=0,
    cliponaxis=False,
))
fig_active.add_trace(go.Bar(
    y=active_df["label"],
    x=active_df["total_users"],
    name="Active Users",
    orientation="h",
    marker_color="mediumseagreen",
    text=active_df["total_users"],
    textposition="outside",
    textangle=0,
    cliponaxis=False,
))
fig_active.update_layout(
    barmode="group",
    height=max(600, len(active_df) * 60),
    margin=dict(l=10, r=80, t=10, b=10),
    legend=dict(orientation="h", yanchor="bottom", y=1.01, xanchor="left", x=0),
    xaxis_title="Users",
    yaxis=dict(categoryorder="array", categoryarray=active_cat),
    bargap=0.15,
    bargroupgap=0.05,
)
st.plotly_chart(fig_active, use_container_width=True)

st.divider()

# ── Utilization & frequency ──────────────────────────────────────────────────
st.subheader("Utilization & Frequency per Ministry in Last 30 Days")

util_df = (
    reg[["domain", "user_count", "label"]]
    .merge(
        users.rename(columns={"ministry_domain": "domain"}),
        on="domain", how="left",
    )
    .merge(
        convs[["ministry_domain", "total_conversations", "avg_messages_per_user"]]
        .rename(columns={"ministry_domain": "domain"}),
        on="domain", how="left",
    )
    .fillna(0)
)
util_df["active_pct"]     = (util_df["total_users"] / util_df["user_count"] * 100).clip(upper=100).round(1)
util_df["convs_per_user"] = (
    util_df["total_conversations"]
    .div(util_df["total_users"].replace(0, float("nan")))
    .round(2)
    .fillna(0)
)

uc1, uc2 = st.columns(2)

with uc1:
    st.markdown("**% of Registered Users Who Are Active**")
    pct_df = util_df[util_df["active_pct"] > 0].sort_values("active_pct", ascending=True)
    fig_pct = px.bar(
        pct_df,
        x="active_pct",
        y="label",
        orientation="h",
        labels={"active_pct": "Active Users (%)", "label": "Ministry"},
        color="active_pct",
        color_continuous_scale="Teal",
        range_x=[0, 100],
        text="active_pct",
    )
    fig_pct.update_traces(textposition="outside", texttemplate="%{x:.1f}%")
    fig_pct.update_layout(coloraxis_showscale=False, height=550, margin=dict(l=10, r=80, t=10, b=10))
    st.plotly_chart(fig_pct, use_container_width=True)

with uc2:
    st.markdown("**Conversations per Active User (Frequency)**")
    freq_df = util_df[util_df["convs_per_user"] > 0].sort_values("convs_per_user", ascending=True)
    fig_freq = px.bar(
        freq_df,
        x="convs_per_user",
        y="label",
        orientation="h",
        labels={"convs_per_user": "Conversations / User", "label": "Ministry"},
        color="convs_per_user",
        color_continuous_scale="Reds",
        text="convs_per_user",
    )
    fig_freq.update_traces(textposition="outside", texttemplate="%{x:.2f}")
    fig_freq.update_layout(coloraxis_showscale=False, height=550, margin=dict(l=10, r=80, t=10, b=10))
    st.plotly_chart(fig_freq, use_container_width=True)

with st.expander("View utilization table"):
    show_util = (
        util_df[["label", "user_count", "total_users", "active_pct", "total_conversations", "convs_per_user", "avg_messages_per_user"]]
        .rename(columns={
            "label":                 "Ministry",
            "user_count":            "Registered Users",
            "total_users":           "Active Users",
            "active_pct":            "% Active",
            "total_conversations":   "Conversations",
            "convs_per_user":        "Conv / User",
            "avg_messages_per_user": "Avg Msgs / User",
        })
        .sort_values("% Active", ascending=False)
    )
    st.table(show_util.reset_index(drop=True))

st.divider()

# ── Raw data table ───────────────────────────────────────────────────────────
with st.expander("View raw data from last 30 days"):
    raw_df = df.copy()
    raw_df["english_name"] = raw_df["ministry_domain"].map(name_map).fillna("")
    display_cols = {
        "english_name": "Ministry",
        "ministry_domain": "Domain",
        "total_users": "Users",
        "total_conversations": "Conversations",
        "total_messages": "Messages",
        "avg_messages_per_user": "Avg Msgs/User",
        "total_queries": "Total Queries",
    }
    st.dataframe(
        raw_df[list(display_cols.keys())].rename(columns=display_cols).sort_values("Conversations", ascending=False),
        use_container_width=True,
        hide_index=True,
    )
