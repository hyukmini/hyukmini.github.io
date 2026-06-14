import sqlite3
import pandas as pd
import streamlit as st
import altair as alt

DB_PATH = "lastwar.db"

TEXT = {
    "ko": {
        "page_title": "LastWar Dashboard",
        "language": "Language",
        "menu": "메뉴",
        "server_analysis": "서버 전체 분석",
        "player_analysis": "플레이어 분석",

        "tab_server_summary": "서버 요약",
        "tab_total_hero_power": "총 영웅 전투력 (Top 200)",
        "tab_highest_hero_power": "최강 영웅 전투력 (Top 100)",
        "tab_enemy_kills": "적 처치 (Top 100)",

        "total_hero_power": "총 영웅 전투력",
        "highest_hero_power": "최강 영웅 전투력",
        "enemy_kills": "적 처치",

        "server_filter": "서버 필터 / 최대 2개",
        "alliance_filter": "연맹 필터 / 최대 3개",
        "date": "날짜",
        "date_filter": "날짜 범위 필터 / (시작, 끝)",

        "select_server": "서버를 선택하세요.",
        "select_date": "날짜를 선택하세요.",
        "no_common_dates": "3개 지표에 공통으로 존재하는 날짜가 없습니다.",
        "no_data": "{title} 데이터가 없습니다.",
        "no_timeseries": "시계열 데이터가 없습니다.",
        "no_scatter": "산점도 데이터가 없습니다.",
        "no_players": "선택한 조건에 해당하는 플레이어가 없습니다.",
        "select_player": "플레이어를 선택하세요.",
        "summary_only": "서버 요약은 서버 전체 분석 메뉴에서만 표시됩니다.",

        "server": "서버",
        "alliance": "연맹",
        "rank": "랭킹",
        "normalized_id": "정규화 ID",
        "player_name": "당시 ID",
        "growth": "성장값",
        "growth_rate": "성장률",
        "member_count": "인원수",
        "ratio": "비율",
        "total": "합계",
        "avg": "평균",

        "strongest_hero": "최강 영웅",
        "squad_type": "군종",
        "marker": "마커",
        "player": "플레이어",

        "total_hero_power_sum": "총영투 합계",
        "total_hero_power_ratio": "총영투 비율",
        "total_hero_power_member": "총영투 인원수",

        "highest_hero_power_sum": "최강영웅 합계",
        "highest_hero_power_ratio": "최강영웅 비율",
        "highest_hero_power_member": "최강영웅 인원수",

        "enemy_kills_sum": "적처치 합계",
        "enemy_kills_ratio": "적처치 비율",
        "enemy_kills_member": "적처치 인원수",

        "total_hero_power_short": "총영투",
        "highest_hero_power_short": "최강 영웅",
        "enemy_kills_short": "적 처치",

        "total_hero_power_ratio_title": "총영투 비율",
        "highest_hero_power_ratio_title": "최강 영웅 비율",
        "enemy_kills_ratio_title": "적 처치 비율",

        "select_player_mode": "플레이어 선택 방식",
        "manual_select": "직접 선택",
        "top5": "상위 5",
        "top10": "상위 10",
        "top20": "상위 20",
        "player_select": "플레이어 선택 / 최대 20명",

        "chart_type": "그래프 유형",
        "power_history": "Power History",
        "rank_history": "Rank History",

        "timeseries": "시계열",
        "timeseries_data": "시계열 데이터",

        "highlight_users": "유저 하이라이트",
        "highlight_help": "모든 테이블에 해당 유저를 강조하여 표현합니다. (tiki, migration 입력 가능)",

        "summary_title": "{title} 랭킹 / 서버: {server} / 연맹: {alliance} / 날짜: {date}",
        "server_summary_title": "서버 요약 / 서버: {server} / 날짜: {date}",
        "timeseries_title": "{title} 시계열 / 서버: {server} / 플레이어: {players}",

        "all": "전체",
        "others": "Others",
        "summary_column_error": "요약 기준 컬럼을 찾을 수 없습니다: {column}",
        "current_columns": "현재 컬럼 목록:",
    },
    "en": {
        "page_title": "LastWar Dashboard",
        "language": "Language",
        "menu": "Menu",
        "server_analysis": "Server Analysis",
        "player_analysis": "Player Analysis",

        "tab_server_summary": "Server Summary",
        "tab_total_hero_power": "Total Hero Power (Top 200)",
        "tab_highest_hero_power": "Highest Hero Power (Top 100)",
        "tab_enemy_kills": "Enemy Kills (Top 100)",

        "total_hero_power": "Total Hero Power",
        "highest_hero_power": "Highest Hero Power",
        "enemy_kills": "Enemy Kills",

        "server_filter": "Server Filter / Max 2",
        "alliance_filter": "Alliance Filter / Max 3",
        "date": "Date",
        "date_filter": "Date Range Filter / (Start-date, End-date)",

        "select_server": "Please select a server.",
        "select_date": "Please select a date.",
        "no_common_dates": "No common date exists across the 3 metrics.",
        "no_data": "No {title} data available.",
        "no_timeseries": "No time series data available.",
        "no_scatter": "No scatter plot data available.",
        "no_players": "No players match the selected conditions.",
        "select_player": "Please select a player.",
        "summary_only": "Server Summary is only available in Server Analysis mode.",

        "server": "Server",
        "alliance": "Alliance",
        "rank": "Rank",
        "normalized_id": "Normalized ID",
        "player_name": "Player Name at That Time",
        "growth": "Growth",
        "growth_rate": "Growth Rate",
        "member_count": "Member Count",
        "ratio": "Ratio",
        "total": "Total",
        "avg": "Average",

        "strongest_hero": "Strongest Hero",
        "squad_type": "Squad Type",
        "marker": "Marker",
        "player": "Player",

        "total_hero_power_sum": "Total Hero Power Sum",
        "total_hero_power_ratio": "Total Hero Power Ratio",
        "total_hero_power_member": "Total Hero Power Members",

        "highest_hero_power_sum": "Highest Hero Power Sum",
        "highest_hero_power_ratio": "Highest Hero Power Ratio",
        "highest_hero_power_member": "Highest Hero Power Members",

        "enemy_kills_sum": "Enemy Kills Sum",
        "enemy_kills_ratio": "Enemy Kills Ratio",
        "enemy_kills_member": "Enemy Kills Members",

        "total_hero_power_short": "Total Hero Power",
        "highest_hero_power_short": "Highest Hero",
        "enemy_kills_short": "Enemy Kills",

        "total_hero_power_ratio_title": "Total Hero Power Ratio",
        "highest_hero_power_ratio_title": "Highest Hero Ratio",
        "enemy_kills_ratio_title": "Enemy Kills Ratio",

        "select_player_mode": "Player Selection Mode",
        "manual_select": "Manual Select",
        "top5": "Top 5",
        "top10": "Top 10",
        "top20": "Top 20",
        "player_select": "Player Select / Max 20",

        "chart_type": "Chart Type",
        "power_history": "Power History",
        "rank_history": "Rank History",

        "timeseries": "Time Series",
        "timeseries_data": "Time Series Data",

        "highlight_users": "Highlight Users",
        "highlight_help": "Highlights the specified user across all tables. (e.g., 'tiki', 'migration' can be entered)",

        "summary_title": "{title} Ranking / Server: {server} / Alliance: {alliance} / Date: {date}",
        "server_summary_title": "Server Summary / Server: {server} / Date: {date}",
        "timeseries_title": "{title} Time Series / Server: {server} / Player: {players}",

        "all": "All",
        "others": "Others",
        "summary_column_error": "Summary base column not found: {column}",
        "current_columns": "Current columns:",
    }
}

st.set_page_config(page_title=TEXT["ko"]["page_title"], layout="wide")

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


lang = st.sidebar.selectbox(
    TEXT["en"]["language"],
    ["en", "ko"],
    index=0,
    format_func=lambda x: "English" if x == "en" else "한국어"
)


def t(key):
    return TEXT[lang].get(key, key)


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

    label_map = {
        "server_id": t("server"),
        "rank_no": t("rank"),
        "alliance_name": t("alliance"),
        "normalized_player_name": t("normalized_id"),
        "player_name": t("player_name"),
        "highest_hero": t("strongest_hero"),
        "squad_type": t("squad_type"),
        "growth": t("growth"),
        "growth_rate_%": t("growth_rate"),
    }

    for col in df.columns:
        display_name = label_map.get(col, col)

        if pd.api.types.is_numeric_dtype(df[col]):
            if "rate" in col.lower() or "%" in col:
                config[col] = st.column_config.NumberColumn(
                    display_name,
                    format="%.2f%%"
                )
            else:
                config[col] = st.column_config.NumberColumn(
                    display_name,
                    format="localized"
                )
        else:
            config[col] = st.column_config.TextColumn(display_name)

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
        WITH raw AS (
            SELECT
                t.server_id,
                t.snapshot_date,
                t.rank_no,
                t.alliance_name,
                COALESCE(a.normalized_player_name, t.player_name) AS normalized_player_name,
                t.player_name,
                {extra_select_inner}
                t.{value_column} AS value
            FROM {table_name} t
            LEFT JOIN player_alias a
                ON a.id = (
                    SELECT a2.id
                    FROM player_alias a2
                    WHERE a2.server_id = t.server_id
                      AND a2.player_name = t.player_name
                      AND a2.updated_date <= t.snapshot_date
                    ORDER BY a2.updated_date DESC, a2.id DESC
                    LIMIT 1
                )
            WHERE t.snapshot_date = ?
        ),
        same_day_conflict AS (
            SELECT
                server_id,
                snapshot_date,
                normalized_player_name
            FROM raw
            GROUP BY
                server_id,
                snapshot_date,
                normalized_player_name
            HAVING COUNT(DISTINCT player_name) >= 2
        ),
        normalized AS (
            SELECT
                r.server_id,
                r.snapshot_date,
                r.rank_no,
                r.alliance_name,

                CASE
                    WHEN c.normalized_player_name IS NOT NULL
                    THEN r.player_name
                    ELSE r.normalized_player_name
                END AS normalized_player_name,

                r.player_name,
                {extra_select_inner.replace("t.", "r.")}
                r.value
            FROM raw r
            LEFT JOIN same_day_conflict c
                ON r.server_id = c.server_id
               AND r.snapshot_date = c.snapshot_date
               AND r.normalized_player_name = c.normalized_player_name
        )

        SELECT
            server_id,
            snapshot_date,
            MIN(rank_no) AS rank_no,
            MAX(alliance_name) AS alliance_name,
            normalized_player_name,
            MAX(player_name) AS player_name,
            {extra_select_outer}
            MAX(value) AS value
        FROM normalized
        GROUP BY
            server_id,
            snapshot_date,
            normalized_player_name
        ORDER BY
            rank_no
    """, [snapshot_date])


def load_timeseries(table_name, value_column, normalized_player_names, server_ids):
    server_placeholders = ",".join(["?"] * len(server_ids))
    player_placeholders = ",".join(["?"] * len(normalized_player_names))

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
            COALESCE(a.normalized_player_name, t.player_name) AS normalized_player_name,
            t.player_name,
            {extra_select}
            t.{value_column} AS value
        FROM {table_name} t
        LEFT JOIN player_alias a
            ON a.id = (
                SELECT a2.id
                FROM player_alias a2
                WHERE a2.server_id = t.server_id
                  AND a2.player_name = t.player_name
                  AND a2.updated_date <= t.snapshot_date
                ORDER BY a2.updated_date DESC, a2.id DESC
                LIMIT 1
            )
        WHERE COALESCE(a.normalized_player_name, t.player_name) IN ({player_placeholders})
          AND t.server_id IN ({server_placeholders})
        ORDER BY
            COALESCE(a.normalized_player_name, t.player_name),
            t.snapshot_date
    """, normalized_player_names + server_ids)


def add_growth_columns(table_name, value_column, selected_dates):
    selected_dates = sorted(selected_dates)
    compare_date = selected_dates[-1]

    compare_df = load_table(table_name, value_column, compare_date)

    if len(selected_dates) == 1:
        compare_df = compare_df.rename(columns={
            "value": compare_date
        })

        ordered_columns = [
            "server_id",
            "rank_no",
            "alliance_name",
            "normalized_player_name",
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

    base_df = load_table(table_name, value_column, base_date)

    base_df = base_df[
        [
            "server_id",
            "normalized_player_name",
            "value"
        ]
    ].rename(columns={
        "value": base_date
    })

    result_df = compare_df.merge(
        base_df,
        on=[
            "server_id",
            "normalized_player_name"
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
        "normalized_player_name",
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


def build_alliance_summary(df, value_column_name):
    if df.empty:
        return pd.DataFrame()

    value_column_name = str(value_column_name)

    df = df.copy()
    df.columns = df.columns.map(str)

    if value_column_name not in df.columns:
        st.error(t("summary_column_error").format(column=value_column_name))
        st.write(t("current_columns"), df.columns.tolist())
        return pd.DataFrame()

    summary_df = (
        df.groupby("alliance_name", as_index=False)
        .agg(
            member_count=("normalized_player_name", "nunique"),
            total_value=(value_column_name, "sum"),
            avg_value=(value_column_name, "mean")
        )
    )

    total_sum = summary_df["total_value"].sum()

    if total_sum == 0:
        summary_df["value_ratio_%"] = 0
    else:
        summary_df["value_ratio_%"] = (
            summary_df["total_value"] / total_sum * 100
        ).round(2)

    summary_df["total_value_m"] = (
        summary_df["total_value"] / 1_000_000
    ).round(1)

    summary_df["avg_value_m"] = (
        summary_df["avg_value"] / 1_000_000
    ).round(1)

    return summary_df.sort_values(
        "total_value",
        ascending=False
    ).reset_index(drop=True)


def build_top7_others_pie_df(summary_df, value_col):
    if summary_df.empty:
        return pd.DataFrame()

    df = summary_df.copy()
    df = df.sort_values(value_col, ascending=False).reset_index(drop=True)

    total_value = df[value_col].sum()

    top_df = df.head(7).copy()
    others_df = df.iloc[7:].copy()

    if not others_df.empty:
        others_row = {
            "alliance_name": t("others"),
            value_col: others_df[value_col].sum(),
            "member_count": others_df["member_count"].sum()
        }
        top_df = pd.concat([top_df, pd.DataFrame([others_row])], ignore_index=True)

    top_df = top_df.sort_values(value_col, ascending=False).reset_index(drop=True)

    if total_value == 0:
        top_df["ratio_%"] = 0
    else:
        top_df["ratio_%"] = (top_df[value_col] / total_value * 100).round(2)

    top_df["pie_label"] = top_df.apply(
        lambda row: f"{row['ratio_%']:.0f}%"
        if row["ratio_%"] >= 10
        else "",
        axis=1
    )

    return top_df


def render_metric_pie_chart(summary_df, value_col, title, value_title, value_format=","):
    if summary_df.empty:
        st.warning(t("no_data").format(title=title))
        return

    pie_df = build_top7_others_pie_df(
        summary_df,
        value_col
    )

    pie_df = pie_df.sort_values(
        value_col,
        ascending=False
    ).reset_index(drop=True)

    sort_order = pie_df["alliance_name"].tolist()

    rank_color_scale = alt.Scale(
        domain=sort_order,
        range=[
            "#FF3B30",
            "#FF9500",
            "#FFCC00",
            "#34C759",
            "#00C7BE",
            "#64D2FF",
            "#5856D6",
            "#C7C7CC",
        ]
    )

    chart = (
        alt.Chart(pie_df)
        .mark_arc(
            innerRadius=45,
            outerRadius=155
        )
        .encode(
            theta=alt.Theta(
                f"{value_col}:Q",
                title=value_title
            ),
            color=alt.Color(
                "alliance_name:N",
                title=t("alliance"),
                sort=sort_order,
                scale=rank_color_scale
            ),
            order=alt.Order(
                f"{value_col}:Q",
                sort="descending"
            ),
            tooltip=[
                alt.Tooltip("alliance_name:N", title=t("alliance")),
                alt.Tooltip(f"{value_col}:Q", title=value_title, format=value_format),
                alt.Tooltip("ratio_%:Q", title=t("ratio"), format=".2f"),
                alt.Tooltip("member_count:Q", title=t("member_count")),
            ]
        )
        .properties(height=360)
    )

    st.altair_chart(
        chart,
        use_container_width=True
    )


def render_metric_bar_chart(summary_df, metric_col, title, x_title, value_format=","):
    if summary_df.empty:
        st.warning(t("no_data").format(title=title))
        return

    chart_df = summary_df.copy()
    chart_df = chart_df.sort_values(metric_col, ascending=False).reset_index(drop=True)

    chart = (
        alt.Chart(chart_df)
        .mark_bar()
        .encode(
            x=alt.X(
                f"{metric_col}:Q",
                title=x_title
            ),
            y=alt.Y(
                "alliance_name:N",
                title=t("alliance"),
                sort=chart_df["alliance_name"].tolist()
            ),
            tooltip=[
                alt.Tooltip("alliance_name:N", title=t("alliance")),
                alt.Tooltip(f"{metric_col}:Q", title=x_title, format=value_format),
                alt.Tooltip("member_count:Q", title=t("member_count")),
                alt.Tooltip("value_ratio_%:Q", title=t("ratio"), format=".2f"),
            ]
        )
        .properties(height=360)
        .interactive()
    )

    st.altair_chart(chart, use_container_width=True)


def render_timeseries_line_chart(ts_df, title, chart_type):
    if ts_df.empty:
        st.warning(t("no_timeseries"))
        return

    ts_df = ts_df.copy()

    if chart_type == t("rank_history"):
        y_field = "rank_no"
        y_title = t("rank")
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

    if chart_type == t("rank_history"):
        player_order = (
            ts_df[ts_df["snapshot_date"] == latest_date]
            .groupby("normalized_player_name", as_index=False)["rank_no"]
            .min()
            .sort_values("rank_no", ascending=True)
            ["normalized_player_name"]
            .tolist()
        )
    else:
        player_order = (
            ts_df[ts_df["snapshot_date"] == latest_date]
            .groupby("normalized_player_name", as_index=False)["value"]
            .max()
            .sort_values("value", ascending=False)
            ["normalized_player_name"]
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
            "circle",
            "square",
            "diamond",
            "cross",
            "triangle-up"
        ]
    )

    tooltip_cols = [
        alt.Tooltip("server_id:N", title=t("server")),
        alt.Tooltip("snapshot_date:N", title=t("date")),
        alt.Tooltip("rank_no:Q", title=t("rank")),
        alt.Tooltip("normalized_player_name:N", title=t("normalized_id")),
        alt.Tooltip("player_name:N", title=t("player_name")),
        alt.Tooltip("value:Q", title=title, format=",")
    ]

    if "highest_hero" in ts_df.columns:
        tooltip_cols.insert(5, alt.Tooltip("highest_hero:N", title=t("strongest_hero")))
        tooltip_cols.insert(6, alt.Tooltip("squad_type:N", title=t("squad_type")))

    base = alt.Chart(ts_df).encode(
        x=alt.X(
            "snapshot_date:N",
            title=t("date"),
            sort=sorted(ts_df["snapshot_date"].unique().tolist())
        ),
        y=alt.Y(
            f"{y_field}:Q",
            title=y_title,
            scale=y_scale
        ),
        color=alt.Color(
            "normalized_player_name:N",
            title=t("player"),
            sort=player_order,
            scale=color_scale
        ),
        tooltip=tooltip_cols
    )

    line = base.mark_line(strokeWidth=4)

    points = base.mark_point(
        filled=True,
        size=220
    ).encode(
        shape=alt.Shape(
            "normalized_player_name:N",
            title=t("marker"),
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
        SELECT DISTINCT normalized_player_name
        FROM (
            SELECT COALESCE(a.normalized_player_name, t.player_name) AS normalized_player_name
            FROM total_hero_power t
            LEFT JOIN player_alias a
                ON a.id = (
                    SELECT a2.id
                    FROM player_alias a2
                    WHERE a2.server_id = t.server_id
                      AND a2.player_name = t.player_name
                      AND a2.updated_date <= t.snapshot_date
                    ORDER BY a2.updated_date DESC, a2.id DESC
                    LIMIT 1
                )

            UNION

            SELECT COALESCE(a.normalized_player_name, h.player_name) AS normalized_player_name
            FROM highest_hero_power h
            LEFT JOIN player_alias a
                ON a.id = (
                    SELECT a2.id
                    FROM player_alias a2
                    WHERE a2.server_id = h.server_id
                      AND a2.player_name = h.player_name
                      AND a2.updated_date <= h.snapshot_date
                    ORDER BY a2.updated_date DESC, a2.id DESC
                    LIMIT 1
                )

            UNION

            SELECT COALESCE(a.normalized_player_name, e.player_name) AS normalized_player_name
            FROM enemy_kills e
            LEFT JOIN player_alias a
                ON a.id = (
                    SELECT a2.id
                    FROM player_alias a2
                    WHERE a2.server_id = e.server_id
                      AND a2.player_name = e.player_name
                      AND a2.updated_date <= e.snapshot_date
                    ORDER BY a2.updated_date DESC, a2.id DESC
                    LIMIT 1
                )
        )
        ORDER BY normalized_player_name
    """)
    return df["normalized_player_name"].dropna().tolist()


def highlight_selected_users(row):
    if (
        "normalized_player_name" in row.index
        and row["normalized_player_name"] in highlight_players
    ):
        return [
            "background-color: #fff3b0; font-weight: bold;"
            for _ in row
        ]

    return ["" for _ in row]


def render_scatter_chart(df, title, compare_date):
    if df.empty:
        st.warning(t("no_scatter"))
        return

    y_col = compare_date

    tooltip_cols = [
        alt.Tooltip("server_id:N", title=t("server")),
        alt.Tooltip("rank_no:Q", title=t("rank")),
        alt.Tooltip("alliance_name:N", title=t("alliance")),
        alt.Tooltip("normalized_player_name:N", title=t("normalized_id")),
        alt.Tooltip(f"{y_col}:Q", title=title, format=",")
    ]

    if "growth" in df.columns:
        tooltip_cols.append(
            alt.Tooltip("growth:Q", title=t("growth"), format=",")
        )

    if "growth_rate_%" in df.columns:
        tooltip_cols.append(
            alt.Tooltip("growth_rate_%:Q", title=t("growth_rate"), format=".2f")
        )

    chart = (
        alt.Chart(df)
        .mark_circle(size=80, opacity=0.75)
        .encode(
            x=alt.X(
                "rank_no:Q",
                title=t("rank"),
                scale=alt.Scale(reverse=True)
            ),
            y=alt.Y(
                f"{y_col}:Q",
                title=title,
                scale=alt.Scale(zero=False)
            ),
            color=alt.Color("alliance_name:N", title=t("alliance")),
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

    if t("all") in selected_alliances:
        alliance_filter_text = t("all")
    else:
        alliance_filter_text = ", ".join(selected_alliances)

    st.markdown(
        f"""
        <div class="filter-title">
            {t("summary_title").format(
                title=title,
                server=server_filter_text,
                alliance=alliance_filter_text,
                date=date_filter_text
            )}
        </div>
        """,
        unsafe_allow_html=True
    )


def render_server_summary_page():
    total_dates = load_dates("total_hero_power")
    highest_dates = load_dates("highest_hero_power")
    kills_dates = load_dates("enemy_kills")

    common_dates = sorted(
        list(set(total_dates) & set(highest_dates) & set(kills_dates))
    )

    if not common_dates:
        st.warning(t("no_common_dates"))
        return

    server_ids = get_server_ids("total_hero_power")

    selected_server_ids = st.multiselect(
        t("server_filter"),
        server_ids,
        default=server_ids[:1],
        max_selections=2,
        key="server_summary_server"
    )

    if not selected_server_ids:
        st.warning(t("select_server"))
        return

    selected_date = st.selectbox(
        t("date"),
        common_dates,
        index=len(common_dates) - 1,
        key="server_summary_date"
    )

    total_df = load_table(
        "total_hero_power",
        "total_hero_power",
        selected_date
    )

    highest_df = load_table(
        "highest_hero_power",
        "highest_hero_power",
        selected_date
    )

    kills_df = load_table(
        "enemy_kills",
        "enemy_kills",
        selected_date
    )

    total_df = total_df[total_df["server_id"].isin(selected_server_ids)]
    highest_df = highest_df[highest_df["server_id"].isin(selected_server_ids)]
    kills_df = kills_df[kills_df["server_id"].isin(selected_server_ids)]

    total_summary = build_alliance_summary(
        total_df.rename(columns={"value": "total_hero_power"}),
        "total_hero_power"
    )

    highest_summary = build_alliance_summary(
        highest_df.rename(columns={"value": "highest_hero_power"}),
        "highest_hero_power"
    )

    kills_summary = build_alliance_summary(
        kills_df.rename(columns={"value": "enemy_kills"}),
        "enemy_kills"
    )

    total_part = total_summary[
        [
            "alliance_name",
            "member_count",
            "total_value",
            "avg_value",
            "value_ratio_%"
        ]
    ].rename(columns={
        "member_count": "total_member_count",
        "total_value": "total_hero_power_sum",
        "avg_value": "total_hero_power_avg",
        "value_ratio_%": "total_hero_power_ratio_%"
    })

    highest_part = highest_summary[
        [
            "alliance_name",
            "member_count",
            "total_value",
            "avg_value",
            "value_ratio_%"
        ]
    ].rename(columns={
        "member_count": "highest_member_count",
        "total_value": "highest_hero_power_sum",
        "avg_value": "highest_hero_power_avg",
        "value_ratio_%": "highest_hero_power_ratio_%"
    })

    kills_part = kills_summary[
        [
            "alliance_name",
            "member_count",
            "total_value",
            "avg_value",
            "value_ratio_%"
        ]
    ].rename(columns={
        "member_count": "kills_member_count",
        "total_value": "enemy_kills_sum",
        "avg_value": "enemy_kills_avg",
        "value_ratio_%": "enemy_kills_ratio_%"
    })

    merged_summary = (
        total_part
        .merge(highest_part, on="alliance_name", how="outer")
        .merge(kills_part, on="alliance_name", how="outer")
        .fillna(0)
    )

    merged_summary = merged_summary.sort_values(
        "total_hero_power_sum",
        ascending=False
    ).reset_index(drop=True)

    st.markdown(
        f"""
        <div class="filter-title">
            {t("server_summary_title").format(
                server=", ".join(map(str, selected_server_ids)),
                date=selected_date
            )}
        </div>
        """,
        unsafe_allow_html=True
    )

    kpi1, kpi2, kpi3 = st.columns(3)

    kpi1.metric(
        t("total_hero_power"),
        format_million(merged_summary["total_hero_power_sum"].sum())
    )

    kpi2.metric(
        t("highest_hero_power"),
        format_million(merged_summary["highest_hero_power_sum"].sum())
    )

    kpi3.metric(
        t("enemy_kills"),
        f"{int(merged_summary['enemy_kills_sum'].sum()):,}"
    )

    display_df = merged_summary[
        [
            "alliance_name",

            "total_member_count",
            "total_hero_power_sum",
            "total_hero_power_ratio_%",

            "highest_member_count",
            "highest_hero_power_sum",
            "highest_hero_power_ratio_%",

            "kills_member_count",
            "enemy_kills_sum",
            "enemy_kills_ratio_%"
        ]
    ]

    chart_col1, chart_col2, chart_col3 = st.columns(3)

    with chart_col1:
        render_metric_pie_chart(
            total_summary,
            "total_value",
            t("total_hero_power_ratio_title"),
            t("total_hero_power_short"),
            ".1f"
        )

    with chart_col2:
        render_metric_pie_chart(
            highest_summary,
            "total_value",
            t("highest_hero_power_ratio_title"),
            t("highest_hero_power_short"),
            ".1f"
        )

    with chart_col3:
        render_metric_pie_chart(
            kills_summary,
            "total_value",
            t("enemy_kills_ratio_title"),
            t("enemy_kills_short"),
            ","
        )

    st.dataframe(
        display_df,
        use_container_width=True,
        height=380,
        column_config={
            "alliance_name": st.column_config.TextColumn(t("alliance")),

            "total_member_count": st.column_config.NumberColumn(t("total_hero_power_member"), format="%d"),
            "total_hero_power_sum": st.column_config.NumberColumn(t("total_hero_power_sum"), format="localized"),
            "total_hero_power_ratio_%": st.column_config.NumberColumn(t("total_hero_power_ratio"), format="%.2f%%"),

            "highest_member_count": st.column_config.NumberColumn(t("highest_hero_power_member"), format="%d"),
            "highest_hero_power_sum": st.column_config.NumberColumn(t("highest_hero_power_sum"), format="localized"),
            "highest_hero_power_ratio_%": st.column_config.NumberColumn(t("highest_hero_power_ratio"), format="%.2f%%"),

            "kills_member_count": st.column_config.NumberColumn(t("enemy_kills_member"), format="%d"),
            "enemy_kills_sum": st.column_config.NumberColumn(t("enemy_kills_sum"), format="localized"),
            "enemy_kills_ratio_%": st.column_config.NumberColumn(t("enemy_kills_ratio"), format="%.2f%%"),
        }
    )


def render_summary_page(title, table_name, value_column):
    dates = load_dates(table_name)

    if not dates:
        st.warning(t("no_data").format(title=title))
        return

    server_ids = get_server_ids(table_name)

    selected_server_ids = st.multiselect(
        t("server_filter"),
        server_ids,
        default=server_ids[:1],
        max_selections=2,
        key=f"{table_name}_summary_server"
    )

    if not selected_server_ids:
        st.warning(t("select_server"))
        return

    latest_df_for_filter = load_table(
        table_name,
        value_column,
        dates[-1]
    )

    latest_df_for_filter = latest_df_for_filter[
        latest_df_for_filter["server_id"].isin(selected_server_ids)
    ]

    alliances = [t("all")] + sorted(
        latest_df_for_filter["alliance_name"]
        .dropna()
        .unique()
        .tolist()
    )

    selected_alliances = st.multiselect(
        t("alliance_filter"),
        alliances,
        default=[t("all")],
        max_selections=3,
        key=f"{table_name}_summary_alliance"
    )

    selected_dates = st.multiselect(
        t("date_filter"),
        dates,
        default=[dates[-1]],
        max_selections=2,
        key=f"{table_name}_summary_dates"
    )

    if not selected_dates:
        st.warning(t("select_date"))
        return

    selected_dates = sorted(selected_dates)

    df, base_date, compare_date = add_growth_columns(
        table_name,
        value_column,
        selected_dates
    )

    df = df[df["server_id"].isin(selected_server_ids)]

    if t("all") not in selected_alliances:
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
        st.warning(t("no_data").format(title=title))
        return

    server_ids = get_server_ids(table_name)

    selected_server_ids = st.multiselect(
        t("server_filter"),
        server_ids,
        default=server_ids[:1],
        max_selections=2,
        key=f"{table_name}_detail_server"
    )

    if not selected_server_ids:
        st.warning(t("select_server"))
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

    alliances = [t("all")] + sorted(
        latest_df["alliance_name"].dropna().unique().tolist()
    )

    selected_alliances = st.multiselect(
        t("alliance_filter"),
        alliances,
        default=[t("all")],
        max_selections=3,
        key=f"{table_name}_detail_alliance"
    )

    if t("all") not in selected_alliances:
        latest_df = latest_df[
            latest_df["alliance_name"].isin(selected_alliances)
        ]

    players = (
        latest_df["normalized_player_name"]
        .dropna()
        .unique()
        .tolist()
    )

    if not players:
        st.warning(t("no_players"))
        return

    select_mode = st.radio(
        t("select_player_mode"),
        [
            t("manual_select"),
            t("top5"),
            t("top10"),
            t("top20")
        ],
        horizontal=True,
        key=f"{table_name}_detail_select_mode"
    )

    latest_df = latest_df.sort_values("rank_no", ascending=True)

    if select_mode == t("top5"):
        selected_players = latest_df["normalized_player_name"].dropna().head(5).tolist()

    elif select_mode == t("top10"):
        selected_players = latest_df["normalized_player_name"].dropna().head(10).tolist()

    elif select_mode == t("top20"):
        selected_players = latest_df["normalized_player_name"].dropna().head(20).tolist()

    else:
        selected_players = st.multiselect(
            t("player_select"),
            players,
            default=players[:1],
            max_selections=20,
            key=f"{table_name}_detail_players"
        )

    if not selected_players:
        st.warning(t("select_player"))
        return

    chart_type = st.selectbox(
        t("chart_type"),
        [
            t("power_history"),
            t("rank_history")
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
            {t("timeseries_title").format(
                title=title,
                server=", ".join(map(str, selected_server_ids)),
                players=", ".join(selected_players)
            )}
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
        f"""
        <div class="filter-title">
            {t("timeseries_data")}
        </div>
        """,
        unsafe_allow_html=True
    )

    display_ts_df = ts_df.copy()
    display_ts_df = display_ts_df.sort_values(
        ["snapshot_date", "rank_no"],
        ascending=[False, True]
    ).reset_index(drop=True)


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

    if keyword == "bestie":
        keywords = BESTIE_KEYWORDS
        search_column = "player_name"

    elif keyword == "migration":
        df = read_sql("""
            SELECT DISTINCT normalized_player_name
            FROM player_alias
            WHERE migration_yn = 'Y'
            ORDER BY normalized_player_name
        """)

        return (
            df["normalized_player_name"]
            .dropna()
            .tolist()
        )

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
        SELECT DISTINCT normalized_player_name
        FROM player_alias
        WHERE {where_sql}
        ORDER BY normalized_player_name
    """, params)

    return (
        df["normalized_player_name"]
        .dropna()
        .tolist()
    )


menu = st.sidebar.radio(
    t("menu"),
    [
        t("server_analysis"),
        t("player_analysis")
    ]
)

all_players = load_all_players()

raw_highlight_players = st.sidebar.multiselect(
    t("highlight_users"),
    options=all_players,
    default=[],
    accept_new_options=True,
    help=t("highlight_help")
)

highlight_players = []

for item in raw_highlight_players:
    if item in all_players:
        highlight_players.append(item)
    else:
        matched_players = search_players_by_keyword(item)

        for player in matched_players:
            if player not in highlight_players:
                highlight_players.append(player)


tab0, tab1, tab2, tab3 = st.tabs([
    t("tab_server_summary"),
    t("tab_total_hero_power"),
    t("tab_highest_hero_power"),
    t("tab_enemy_kills")
])

with tab0:
    if menu == t("server_analysis"):
        render_server_summary_page()
    else:
        st.info(t("summary_only"))

with tab1:
    if menu == t("server_analysis"):
        render_summary_page(
            t("total_hero_power"),
            "total_hero_power",
            "total_hero_power"
        )
    else:
        render_user_detail_page(
            t("total_hero_power"),
            "total_hero_power",
            "total_hero_power"
        )

with tab2:
    if menu == t("server_analysis"):
        render_summary_page(
            t("highest_hero_power"),
            "highest_hero_power",
            "highest_hero_power"
        )
    else:
        render_user_detail_page(
            t("highest_hero_power"),
            "highest_hero_power",
            "highest_hero_power"
        )

with tab3:
    if menu == t("server_analysis"):
        render_summary_page(
            t("enemy_kills"),
            "enemy_kills",
            "enemy_kills"
        )
    else:
        render_user_detail_page(
            t("enemy_kills"),
            "enemy_kills",
            "enemy_kills"
        )