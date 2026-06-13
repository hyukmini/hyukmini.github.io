import sqlite3
import pandas as pd
import streamlit as st
import altair as alt

DB_PATH = "lastwar.db"

st.set_page_config(page_title="LastWar Dashboard", layout="wide")

st.markdown("""
<style>
html, body, [class*="css"] {
    font-size: 18px !important;
}
[data-testid="stDataFrame"] {
    font-size: 18px !important;
}
h1 {
    font-size: 34px !important;
}
h2, h3 {
    font-size: 25px !important;
}
.filter-title {
    font-size: 18px;
    font-weight: 600;
    margin-bottom: 0.5rem;
}
</style>
""", unsafe_allow_html=True)

def format_million(value):
    return f"{value / 1_000_000:.1f}M"

def read_sql(query, params=None):
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql(query, conn, params=params or [])
    conn.close()
    return df


def remove_snapshot_column(df):
    return df.drop(columns=["snapshot_date"], errors="ignore")


def remove_player_name_column(df):
    return df.drop(columns=["player_name"], errors="ignore")


def get_column_config(df):
    config = {}

    for col in df.columns:
        if pd.api.types.is_numeric_dtype(df[col]):
            if "rate" in col.lower() or "%" in col:
                config[col] = st.column_config.NumberColumn(
                    col,
                    format="%.2f%%"
                )
            else:
                config[col] = st.column_config.NumberColumn(
                    col,
                    format="localized"
                )

    return config


def load_dates(table_name):
    df = read_sql(f"""
        SELECT DISTINCT snapshot_date
        FROM {table_name}
        ORDER BY snapshot_date
    """)
    return df["snapshot_date"].tolist()


def get_server_ids(table_name):
    df = read_sql(f"""
        SELECT DISTINCT server_id
        FROM {table_name}
        ORDER BY server_id
    """)
    return df["server_id"].tolist()
def load_table(table_name, value_column, snapshot_date):
    extra_select_inner = ""
    extra_select_outer = ""

    if table_name == "highest_hero_power":
        extra_select_inner = """
            t.highest_hero,
            t.squad_type,
        """
        extra_select_outer = """
            MAX(highest_hero) AS highest_hero,
            MAX(squad_type) AS squad_type,
        """

    return read_sql(f"""
        WITH alias_dedup AS (
            SELECT
                server_id,
                player_name,
                MAX(canonical_player_name) AS canonical_player_name
            FROM player_alias
            GROUP BY
                server_id,
                player_name
        ),
        raw AS (
            SELECT
                t.server_id,
                t.snapshot_date,
                t.rank_no,
                t.alliance_name,
                COALESCE(a.canonical_player_name, t.player_name) AS canonical_player_name,
                t.player_name,
                {extra_select_inner}
                t.{value_column} AS value
            FROM {table_name} t
            LEFT JOIN alias_dedup a
                ON t.server_id = a.server_id
               AND t.player_name = a.player_name
            WHERE t.snapshot_date = ?
        ),
        same_day_conflict AS (
            SELECT
                server_id,
                snapshot_date,
                canonical_player_name
            FROM raw
            GROUP BY
                server_id,
                snapshot_date,
                canonical_player_name
            HAVING COUNT(DISTINCT player_name) >= 2
        ),
        normalized AS (
            SELECT
                r.server_id,
                r.snapshot_date,
                r.rank_no,
                r.alliance_name,

                CASE
                    WHEN c.canonical_player_name IS NOT NULL
                    THEN r.player_name
                    ELSE r.canonical_player_name
                END AS canonical_player_name,

                r.player_name,
                {extra_select_inner.replace("t.", "r.")}
                r.value
            FROM raw r
            LEFT JOIN same_day_conflict c
                ON r.server_id = c.server_id
               AND r.snapshot_date = c.snapshot_date
               AND r.canonical_player_name = c.canonical_player_name
        )

        SELECT
            server_id,
            snapshot_date,
            MIN(rank_no) AS rank_no,
            MAX(alliance_name) AS alliance_name,
            canonical_player_name,
            MAX(player_name) AS player_name,
            {extra_select_outer}
            MAX(value) AS value
        FROM normalized
        GROUP BY
            server_id,
            snapshot_date,
            canonical_player_name
        ORDER BY
            rank_no
    """, [snapshot_date])


def load_timeseries(table_name, value_column, canonical_player_names, server_ids):
    server_placeholders = ",".join(["?"] * len(server_ids))
    player_placeholders = ",".join(["?"] * len(canonical_player_names))

    extra_select = ""

    if table_name == "highest_hero_power":
        extra_select = """
            t.highest_hero,
            t.squad_type,
        """

    return read_sql(f"""
        SELECT
            t.server_id,
            t.snapshot_date,
            t.rank_no,
            COALESCE(a.canonical_player_name, t.player_name) AS canonical_player_name,
            t.player_name,
            {extra_select}
            t.{value_column} AS value
        FROM {table_name} t
        LEFT JOIN player_alias a
            ON t.server_id = a.server_id
           AND t.player_name = a.player_name
        WHERE COALESCE(a.canonical_player_name, t.player_name) IN ({player_placeholders})
          AND t.server_id IN ({server_placeholders})
        ORDER BY
            COALESCE(a.canonical_player_name, t.player_name),
            t.snapshot_date
    """, canonical_player_names + server_ids)


def add_growth_columns(table_name, value_column, selected_dates):
    selected_dates = sorted(selected_dates)
    compare_date = selected_dates[-1]

    compare_df = load_table(
        table_name,
        value_column,
        compare_date
    )

    if len(selected_dates) == 1:
        compare_df = compare_df.rename(columns={
            "value": compare_date
        })

        ordered_columns = [
            "server_id",
            "rank_no",
            "alliance_name",
            "canonical_player_name",
            "player_name",
            compare_date
        ]

        if table_name == "highest_hero_power":
            ordered_columns.insert(5, "highest_hero")
            ordered_columns.insert(6, "squad_type")

        compare_df = compare_df[
            [col for col in ordered_columns if col in compare_df.columns]
        ]

        return compare_df, None, compare_date

    base_date = selected_dates[0]

    base_df = load_table(
        table_name,
        value_column,
        base_date
    )

    base_df = base_df[
        [
            "server_id",
            "canonical_player_name",
            "value"
        ]
    ].rename(columns={
        "value": base_date
    })

    result_df = compare_df.merge(
        base_df,
        on=[
            "server_id",
            "canonical_player_name"
        ],
        how="left"
    )

    result_df = result_df.rename(columns={
        "value": compare_date
    })

    result_df["growth"] = (
        result_df[compare_date] - result_df[base_date]
    )

    result_df["growth_rate_%"] = (
        result_df["growth"] / result_df[base_date] * 100
    ).round(2)

    ordered_columns = [
        "server_id",
        "rank_no",
        "alliance_name",
        "canonical_player_name",
        "player_name",
        base_date,
        compare_date,
        "growth",
        "growth_rate_%"
    ]

    if table_name == "highest_hero_power":
        ordered_columns.insert(5, "highest_hero")
        ordered_columns.insert(6, "squad_type")

    result_df = result_df[
        [col for col in ordered_columns if col in result_df.columns]
    ]

    return result_df, base_date, compare_date


def render_timeseries_line_chart(ts_df, title, chart_type):
    if ts_df.empty:
        st.warning("시계열 데이터가 없습니다.")
        return

    ts_df = ts_df.copy()

    if chart_type == "Rank History":
        y_field = "rank_no"
        y_title = "Rank"
        y_scale = alt.Scale(reverse=True)
        ts_df["label_text"] = ts_df["rank_no"].apply(
            lambda x: f"#{int(x)}"
        )
    else:
        y_field = "value_m"
        y_title = f"{title} (M)"
        y_scale = alt.Scale()
        ts_df["value_m"] = ts_df["value"] / 1_000_000
        ts_df["label_text"] = ts_df["value"].apply(format_million)

    latest_date = ts_df["snapshot_date"].max()

    if chart_type == "Rank History":
        player_order = (
            ts_df[ts_df["snapshot_date"] == latest_date]
            .groupby("canonical_player_name", as_index=False)["rank_no"]
            .min()
            .sort_values("rank_no", ascending=True)
            ["canonical_player_name"]
            .tolist()
        )
    else:
        player_order = (
            ts_df[ts_df["snapshot_date"] == latest_date]
            .groupby("canonical_player_name", as_index=False)["value"]
            .max()
            .sort_values("value", ascending=False)
            ["canonical_player_name"]
            .tolist()
        )

    color_scale = alt.Scale(
        range=[
            "#FF3B30", "#007AFF", "#34C759", "#FF9500", "#AF52DE",
            "#00C7BE", "#FF2D55", "#5856D6", "#FFD60A", "#30D158",
            "#64D2FF", "#FF6482", "#BF5AF2", "#5AC8FA", "#FF9F0A",
            "#32D74B", "#FF375F", "#0A84FF", "#FFD426", "#66D4CF"
        ]
    )
    shape_scale = alt.Scale(
        range=[
            "circle",  # ●
            "square",  # ■
            "diamond",  # ◆
            "cross",  # ✕
            "triangle-up"  # ▲
        ]
    )
    tooltip_cols = [
        alt.Tooltip("server_id:N", title="서버"),
        alt.Tooltip("snapshot_date:N", title="날짜"),
        alt.Tooltip("rank_no:Q", title="랭킹"),
        alt.Tooltip("canonical_player_name:N", title="대표 ID"),
        alt.Tooltip("player_name:N", title="당시 ID"),
        alt.Tooltip("value:Q", title=title, format=",")
    ]

    if "highest_hero" in ts_df.columns:
        tooltip_cols.insert(5, alt.Tooltip("highest_hero:N", title="최강 영웅"))
        tooltip_cols.insert(6, alt.Tooltip("squad_type:N", title="군종"))

    base = alt.Chart(ts_df).encode(
        x=alt.X(
            "snapshot_date:N",
            title="날짜",
            sort=sorted(ts_df["snapshot_date"].unique().tolist())
        ),
        y=alt.Y(
            f"{y_field}:Q",
            title=y_title,
            scale=y_scale
        ),
        color=alt.Color(
            "canonical_player_name:N",
            title="플레이어",
            sort=player_order,
            scale=color_scale
        ),
        tooltip=tooltip_cols
    )

    line = base.mark_line(
        strokeWidth=4
    )

    points = base.mark_point(
        filled=True,
        size=220
    ).encode(
        shape=alt.Shape(
            "canonical_player_name:N",
            title="마커",
            sort=player_order,
            scale=shape_scale
        )
    )

    labels = base.mark_text(
        align="center",
        baseline="bottom",
        dy=-12,
        fontSize=13,
        fontWeight="bold"
    ).encode(
        text="label_text:N"
    )

    chart = (
        (line + points + labels)
        .properties(height=650)
        .interactive()
    )

    st.altair_chart(chart, use_container_width=True)



def load_all_players():
    df = read_sql("""
        SELECT DISTINCT canonical_player_name
        FROM (
            SELECT COALESCE(a.canonical_player_name, t.player_name) AS canonical_player_name
            FROM total_hero_power t
            LEFT JOIN player_alias a
                ON t.server_id = a.server_id
               AND t.player_name = a.player_name

            UNION

            SELECT COALESCE(a.canonical_player_name, h.player_name) AS canonical_player_name
            FROM highest_hero_power h
            LEFT JOIN player_alias a
                ON h.server_id = a.server_id
               AND h.player_name = a.player_name

            UNION

            SELECT COALESCE(a.canonical_player_name, e.player_name) AS canonical_player_name
            FROM enemy_kills e
            LEFT JOIN player_alias a
                ON e.server_id = a.server_id
               AND e.player_name = a.player_name
        )
        ORDER BY canonical_player_name
    """)
    return df["canonical_player_name"].dropna().tolist()

def highlight_selected_users(row):
    if (
        "canonical_player_name" in row.index
        and row["canonical_player_name"] in highlight_players
    ):
        return [
            "background-color: #fff3b0; font-weight: bold;"
            for _ in row
        ]

    return ["" for _ in row]

def render_scatter_chart(df, title, compare_date):
    if df.empty:
        st.warning("산점도 데이터가 없습니다.")
        return

    y_col = compare_date

    tooltip_cols = [
        alt.Tooltip("server_id:N", title="서버"),
        alt.Tooltip("rank_no:Q", title="랭킹"),
        alt.Tooltip("alliance_name:N", title="연맹"),
        alt.Tooltip("canonical_player_name:N", title="대표 ID"),
        alt.Tooltip(f"{y_col}:Q", title=title, format=",")
    ]

    if "growth" in df.columns:
        tooltip_cols.append(
            alt.Tooltip("growth:Q", title="성장값", format=",")
        )

    if "growth_rate_%" in df.columns:
        tooltip_cols.append(
            alt.Tooltip("growth_rate_%:Q", title="성장률", format=".2f")
        )

    chart = (
        alt.Chart(df)
        .mark_circle(size=80, opacity=0.75)
        .encode(
            x=alt.X(
                "rank_no:Q",
                title="랭킹",
                scale=alt.Scale(reverse=True)
            ),
            y=alt.Y(
                f"{y_col}:Q",
                title=title,
                scale=alt.Scale(zero=False)
            ),
            color=alt.Color("alliance_name:N", title="연맹"),
            tooltip=tooltip_cols
        )
        .properties(height=650)
        .interactive()
    )

    st.altair_chart(chart, use_container_width=True)


def render_filter_result_title(
        title,
        selected_server_ids,
        selected_alliances,
        base_date,
        compare_date
):
    if base_date:
        date_filter_text = f"{base_date} → {compare_date}"
    else:
        date_filter_text = compare_date

    server_filter_text = ", ".join(map(str, selected_server_ids))

    if "전체" in selected_alliances:
        alliance_filter_text = "전체"
    else:
        alliance_filter_text = ", ".join(selected_alliances)

    st.markdown(
        f"""
        <div class="filter-title">
            {title} 랭킹 / 서버: {server_filter_text} / 연맹: {alliance_filter_text} / 날짜: {date_filter_text}
        </div>
        """,
        unsafe_allow_html=True
    )


def render_summary_page(title, table_name, value_column):
    dates = load_dates(table_name)

    if not dates:
        st.warning(f"{title} 데이터가 없습니다.")
        return

    server_ids = get_server_ids(table_name)

    selected_server_ids = st.multiselect(
        "서버 필터 / 최대 2개",
        server_ids,
        default=server_ids[:1],
        max_selections=2,
        key=f"{table_name}_summary_server"
    )

    if not selected_server_ids:
        st.warning("서버를 선택하세요.")
        return

    latest_df_for_filter = load_table(
        table_name,
        value_column,
        dates[-1]
    )

    latest_df_for_filter = latest_df_for_filter[
        latest_df_for_filter["server_id"].isin(selected_server_ids)
    ]

    alliances = ["전체"] + sorted(
        latest_df_for_filter["alliance_name"]
        .dropna()
        .unique()
        .tolist()
    )

    selected_alliances = st.multiselect(
        "연맹 필터 / 최대 3개",
        alliances,
        default=["전체"],
        max_selections=3,
        key=f"{table_name}_summary_alliance"
    )

    selected_dates = st.multiselect(
        "날짜 필터 / 최대 2개",
        dates,
        default=[dates[-1]],
        max_selections=2,
        key=f"{table_name}_summary_dates"
    )

    if not selected_dates:
        st.warning("날짜를 선택하세요.")
        return

    selected_dates = sorted(selected_dates)

    df, base_date, compare_date = add_growth_columns(
        table_name,
        value_column,
        selected_dates
    )

    df = df[df["server_id"].isin(selected_server_ids)]

    if "전체" not in selected_alliances:
        df = df[df["alliance_name"].isin(selected_alliances)]

    df = df.sort_values(["server_id", "rank_no"], ascending=True)
    df = df.reset_index(drop=True)

    display_df = remove_snapshot_column(df)
    display_df = remove_player_name_column(display_df)

    render_filter_result_title(
        title,
        selected_server_ids,
        selected_alliances,
        base_date,
        compare_date
    )

    col1, col2 = st.columns([2, 1])

    with col1:
        st.dataframe(
            display_df.style.apply(
                highlight_selected_users,
                axis=1
            ),
            use_container_width=True,
            height=650,
            column_config=get_column_config(display_df)
        )

    with col2:
        render_scatter_chart(
            df,
            title,
            compare_date
        )


def render_user_detail_page(title, table_name, value_column):
    dates = load_dates(table_name)

    if not dates:
        st.warning(f"{title} 데이터가 없습니다.")
        return

    server_ids = get_server_ids(table_name)

    selected_server_ids = st.multiselect(
        "서버 필터 / 최대 2개",
        server_ids,
        default=server_ids[:1],
        max_selections=2,
        key=f"{table_name}_detail_server"
    )

    if not selected_server_ids:
        st.warning("서버를 선택하세요.")
        return

    latest_date = dates[-1]

    latest_df = load_table(
        table_name,
        value_column,
        latest_date
    )

    latest_df = latest_df[
        latest_df["server_id"].isin(selected_server_ids)
    ]

    alliances = ["전체"] + sorted(
        latest_df["alliance_name"].dropna().unique().tolist()
    )

    selected_alliances = st.multiselect(
        "연맹 필터 / 최대 3개",
        alliances,
        default=["전체"],
        max_selections=3,
        key=f"{table_name}_detail_alliance"
    )

    if "전체" not in selected_alliances:
        latest_df = latest_df[
            latest_df["alliance_name"].isin(selected_alliances)
        ]

    players = (
        latest_df["canonical_player_name"]
        .dropna()
        .unique()
        .tolist()
    )

    if not players:
        st.warning("선택한 조건에 해당하는 플레이어가 없습니다.")
        return

    select_mode = st.radio(
        "플레이어 선택 방식",
        [
            "직접 선택",
            "상위 5",
            "상위 10",
            "상위 20"
        ],
        horizontal=True,
        key=f"{table_name}_detail_select_mode"
    )

    latest_df = latest_df.sort_values("rank_no", ascending=True)

    if select_mode == "상위 5":
        selected_players = latest_df["canonical_player_name"].dropna().head(5).tolist()

    elif select_mode == "상위 10":
        selected_players = latest_df["canonical_player_name"].dropna().head(10).tolist()

    elif select_mode == "상위 20":
        selected_players = latest_df["canonical_player_name"].dropna().head(20).tolist()

    else:
        selected_players = st.multiselect(
            "플레이어 선택 / 최대 20명",
            players,
            default=players[:1],
            max_selections=20,
            key=f"{table_name}_detail_players"
        )

    if not selected_players:
        st.warning("플레이어를 선택하세요.")
        return

    chart_type = st.selectbox(
        "그래프 유형",
        [
            "Power History",
            "Rank History"
        ],
        key=f"{table_name}_detail_chart_type"
    )



    ts_df = load_timeseries(
        table_name,
        value_column,
        selected_players,
        selected_server_ids
    )

    st.markdown(
        f"""
        <div class="filter-title">
            {title} 시계열 / 서버: {", ".join(map(str, selected_server_ids))} / 플레이어: {", ".join(selected_players)}
        </div>
        """,
        unsafe_allow_html=True
    )

    render_timeseries_line_chart(
        ts_df,
        title,
        chart_type
    )
    st.markdown(
        """
        <div class="filter-title">
            시계열 데이터
        </div>
        """,
        unsafe_allow_html=True
    )

    display_ts_df = ts_df.copy()

    st.dataframe(
        display_ts_df.style.apply(
            highlight_selected_users,
            axis=1
        ),
        use_container_width=True,
        column_config=get_column_config(display_ts_df)
    )

BESTIE_KEYWORDS = ["juhong", "kaisar", "dobby", "dori"]
def search_players_by_keyword(keyword):
    keyword = keyword.strip().lower()

    if not keyword:
        return []

    # bestie special keyword
    if keyword == "bestie":
        keywords = BESTIE_KEYWORDS
        search_column = "player_name"

    # migration special keyword
    elif keyword == "migration":
        df = read_sql("""
            SELECT DISTINCT canonical_player_name
            FROM player_alias
            WHERE migration_yn = 'Y'
            ORDER BY canonical_player_name
        """)

        return (
            df["canonical_player_name"]
            .dropna()
            .tolist()
        )

    # normal keyword search
    else:
        keywords = [keyword]
        search_column = "player_name"

    conditions = []
    params = []

    for kw in keywords:
        conditions.append(f"""
            LOWER({search_column}) LIKE ?
        """)
        params.append(f"%{kw.lower()}%")

    where_sql = " OR ".join(conditions)

    df = read_sql(f"""
        SELECT DISTINCT canonical_player_name
        FROM player_alias
        WHERE {where_sql}
        ORDER BY canonical_player_name
    """, params)

    return (
        df["canonical_player_name"]
        .dropna()
        .tolist()
    )



menu = st.sidebar.radio(
    "메뉴",
    [
        "서버 전체 분석",
        "유저 상세 분석"
    ]
)

all_players = load_all_players()

raw_highlight_players = st.sidebar.multiselect(
    "하이라이트 유저",
    options=all_players,
    default=[],
    accept_new_options=True,
    help="bestie, migration 입력 가능"
)

highlight_players = []

for item in raw_highlight_players:

    # 기존 플레이어 선택
    if item in all_players:
        highlight_players.append(item)

    # 신규 입력(bestie, juhong 등)
    else:
        matched_players = search_players_by_keyword(item)

        for player in matched_players:
            if player not in highlight_players:
                highlight_players.append(player)

#highlight_players = highlight_players[:10]


tab1, tab2, tab3 = st.tabs([
    "총 영웅 전투력",
    "최강 영웅 전투력",
    "적 처치"
])

with tab1:
    if menu == "서버 전체 분석":
        render_summary_page(
            "총 영웅 전투력",
            "total_hero_power",
            "total_hero_power"
        )
    else:
        render_user_detail_page(
            "총 영웅 전투력",
            "total_hero_power",
            "total_hero_power"
        )

with tab2:
    if menu == "서버 전체 분석":
        render_summary_page(
            "최강 영웅 전투력",
            "highest_hero_power",
            "highest_hero_power"
        )
    else:
        render_user_detail_page(
            "최강 영웅 전투력",
            "highest_hero_power",
            "highest_hero_power"
        )

with tab3:
    if menu == "서버 전체 분석":
        render_summary_page(
            "적 처치",
            "enemy_kills",
            "enemy_kills"
        )
    else:
        render_user_detail_page(
            "적 처치",
            "enemy_kills",
            "enemy_kills"
        )