from __future__ import annotations

import io
from datetime import date
from operator import methodcaller

import dask.dataframe as dd
import numpy as np
import pandas as pd
import pytest
from dask.dataframe.utils import tm

import ibis
import ibis.common.exceptions as com
import ibis.expr.datatypes as dt
from ibis.backends.dask import Backend
from ibis.backends.dask.execution import execute
from ibis.legacy.udf.vectorized import reduction


@pytest.fixture(scope="session")
def sort_kind():
    return "mergesort"


default = pytest.mark.parametrize("default", [ibis.NA, ibis.literal("a")])
row_offset = pytest.mark.parametrize("row_offset", list(map(ibis.literal, [-1, 1, 0])))
range_offset = pytest.mark.parametrize(
    "range_offset",
    [
        ibis.interval(days=1),
        2 * ibis.interval(days=1),
        -2 * ibis.interval(days=1),
    ],
)


@pytest.fixture
def row_window():
    return ibis.window(following=0, order_by="plain_int64")


@pytest.fixture
def range_window():
    return ibis.window(following=0, order_by="plain_datetimes_naive")


@default
@row_offset
def test_lead(t, df, row_offset, default, row_window):
    expr = t.dup_strings.lead(row_offset, default=default).over(row_window)
    result = expr.execute()
    expected = df.dup_strings.shift(execute((-row_offset).op())).compute()
    if default is not ibis.NA:
        expected = expected.fillna(execute(default.op()))
    tm.assert_series_equal(result, expected, check_names=False)


@default
@row_offset
def test_lag(t, df, row_offset, default, row_window):
    expr = t.dup_strings.lag(row_offset, default=default).over(row_window)
    result = expr.execute()
    expected = df.dup_strings.shift(execute(row_offset.op())).compute()
    if default is not ibis.NA:
        expected = expected.fillna(execute(default.op()))
    tm.assert_series_equal(result, expected, check_names=False)


@default
@range_offset
def test_lead_delta(t, df, range_offset, default, range_window):
    expr = t.dup_strings.lead(range_offset, default=default).over(range_window)
    result = expr.execute()
    expected = (
        df[["plain_datetimes_naive", "dup_strings"]]
        .set_index("plain_datetimes_naive")
        .squeeze()
        .shift(freq=execute((-range_offset).op()))
        .compute()
        .reset_index(drop=True)
    )
    if default is not ibis.NA:
        expected = expected.fillna(execute(default.op()))
    tm.assert_series_equal(result, expected, check_names=False)


@default
@range_offset
def test_lag_delta(t, df, range_offset, default, range_window):
    expr = t.dup_strings.lag(range_offset, default=default).over(range_window)
    result = expr.execute()
    expected = (
        df[["plain_datetimes_naive", "dup_strings"]]
        .set_index("plain_datetimes_naive")
        .squeeze()
        .shift(freq=execute(range_offset.op()))
        .compute()
        .reset_index(drop=True)
    )
    if default is not ibis.NA:
        expected = expected.fillna(execute(default.op()))
    tm.assert_series_equal(result, expected, check_names=False)


@pytest.mark.xfail(reason="Flaky test because of Dask #10034", strict=False)
def test_groupby_first(t, df):
    gb = t.group_by(t.dup_strings)
    expr = gb.mutate(first_value=t.plain_int64.first())
    result = expr.execute()

    df = df.compute()
    gb = df.groupby("dup_strings")
    df = df.reset_index(drop=True)

    expected = df.assign(
        first_value=gb.plain_int64.transform("first"),
    ).reset_index(drop=True)
    tm.assert_frame_equal(result, expected)


# FIXME dask issue with non deterministic groupby results.
# The issue relates to the shuffle method on a local cluster, using npartitions=1 in tests avoids it.
# https://github.com/dask/dask/issues/10034
@pytest.mark.skip(reason="dask #10034")
def test_group_by_mutate_analytic(t, df):
    gb = t.group_by(t.dup_strings)
    expr = gb.mutate(
        first_value=t.plain_int64.first(),
        last_value=t.plain_strings.last(),
        avg_broadcast=t.plain_float64 - t.plain_float64.mean(),
        delta=(t.plain_int64 - t.plain_int64.lag())
        / (t.plain_float64 - t.plain_float64.lag()),
    )
    result = expr.execute()

    df = df.compute()
    gb = df.groupby("dup_strings")
    df = df.reset_index(drop=True)
    expected = df.assign(
        first_value=gb.plain_int64.transform("first"),
        last_value=gb.plain_strings.transform("last"),
        avg_broadcast=df.plain_float64 - gb.plain_float64.transform("mean"),
        delta=(
            (df.plain_int64 - gb.plain_int64.shift(1))
            / (df.plain_float64 - gb.plain_float64.shift(1))
        ),
    ).reset_index(drop=True)

    tm.assert_frame_equal(result[expected.columns], expected)


def test_players(players, players_df):
    lagged = players.mutate(pct=lambda t: t.G - t.G.lag())
    expected = players_df.assign(
        pct=players_df.G - players_df.groupby("playerID").G.shift(1)
    )
    cols = expected.columns.tolist()
    result = lagged.execute()[cols].sort_values(cols).reset_index(drop=True)
    expected = expected.sort_values(cols).reset_index(drop=True)
    tm.assert_frame_equal(result, expected)


def test_batting_filter_mean(batting, batting_df):
    expr = batting[batting.G > batting.G.mean()]
    result = expr.execute()
    expected = (
        batting_df[batting_df.G > batting_df.G.mean()].reset_index(drop=True).compute()
    )
    tm.assert_frame_equal(result[expected.columns], expected)


def test_batting_zscore(players, players_df):
    expr = players.mutate(g_z=lambda t: (t.G - t.G.mean()) / t.G.std())

    gb = players_df.groupby("playerID")
    expected = players_df.assign(
        g_z=(players_df.G - gb.G.transform("mean")) / gb.G.transform("std")
    )
    cols = expected.columns.tolist()
    result = expr.execute()[cols].sort_values(cols).reset_index(drop=True)
    expected = expected.sort_values(cols).reset_index(drop=True)
    tm.assert_frame_equal(result, expected)


def test_batting_avg_change_in_games_per_year(players, players_df):
    expr = players.mutate(
        delta=lambda t: (t.G - t.G.lag()) / (t.yearID - t.yearID.lag())
    )

    gb = players_df.groupby("playerID")
    expected = players_df.assign(
        delta=(players_df.G - gb.G.shift(1)) / (players_df.yearID - gb.yearID.shift(1))
    )

    cols = expected.columns.tolist()
    result = expr.execute()[cols].sort_values(cols).reset_index(drop=True)
    expected = expected.sort_values(cols).reset_index(drop=True)
    tm.assert_frame_equal(result, expected)


@pytest.mark.xfail(
    raises=NotImplementedError,
    reason="Grouped and order windows not supported yet",
)
def test_batting_most_hits(players, players_df):
    expr = players.mutate(
        hits_rank=lambda t: t.H.rank().over(
            ibis.cumulative_window(order_by=ibis.desc(t.H))
        )
    )
    result = expr.execute()
    hits_rank = players_df.groupby("playerID").H.rank(method="min", ascending=False)
    expected = players_df.assign(hits_rank=hits_rank)
    tm.assert_frame_equal(result[expected.columns], expected)


@pytest.mark.xfail(
    raises=NotImplementedError,
    reason="Quantile not implemented for Dask SeriesGroupBy, Dask #9824",
)
def test_batting_quantile(players, players_df):
    expr = players.mutate(hits_quantile=lambda t: t.H.quantile(0.25))
    hits_quantile = players_df.groupby("playerID").H.transform("quantile", 0.25)
    expected = players_df.assign(hits_quantile=hits_quantile)
    cols = expected.columns.tolist()
    result = expr.execute()[cols].sort_values(cols).reset_index(drop=True)
    tm.assert_frame_equal(result, expected)


@pytest.mark.parametrize("op", ["sum", "min", "max", "mean"])
def test_batting_specific_cumulative(batting, batting_df, op, sort_kind):
    ibis_method = methodcaller(f"cum{op}")
    expr = ibis_method(batting.order_by([batting.yearID]).G)
    result = expr.execute().astype("float64")

    pandas_method = methodcaller(op)
    expected = pandas_method(
        batting_df[["G", "yearID"]]
        .sort_values("yearID", kind=sort_kind)
        .G.rolling(len(batting_df), min_periods=1)
    ).reset_index(drop=True)
    expected = expected.compute()
    tm.assert_series_equal(result, expected.rename(f"Cumulative{op.capitalize()}(G)"))


def test_batting_cumulative(batting, batting_df, sort_kind):
    expr = batting.mutate(
        more_values=lambda t: t.G.sum().over(ibis.cumulative_window(order_by=t.yearID))
    )
    result = expr.execute()

    columns = ["G", "yearID"]
    more_values = (
        batting_df[columns]
        .sort_values("yearID", kind=sort_kind)
        .G.rolling(len(batting_df), min_periods=1)
        .sum()
        .astype("int64")
    )
    expected = batting_df.assign(more_values=more_values).compute()
    tm.assert_frame_equal(result[expected.columns], expected)


@pytest.mark.xfail(
    raises=NotImplementedError,
    reason="Grouped and order windows not supported yet.",
)
def test_batting_cumulative_partitioned(batting, batting_df, sort_kind):
    group_by = "playerID"
    order_by = "yearID"

    t = batting
    expr = t.G.sum().over(ibis.cumulative_window(order_by=order_by, group_by=group_by))
    expr = t.mutate(cumulative=expr)
    result = expr.execute()

    columns = [group_by, order_by, "G"]
    expected = (
        batting_df[columns]
        .set_index(order_by)
        .groupby(group_by)
        .G.expanding()
        .sum()
        .rename("cumulative")
    )

    tm.assert_series_equal(
        result.set_index([group_by, order_by]).sort_index().cumulative,
        expected.sort_index().astype("int64"),
    )


def test_batting_rolling(batting, batting_df, sort_kind):
    expr = batting.mutate(
        more_values=lambda t: t.G.sum().over(ibis.trailing_window(5, order_by=t.yearID))
    )
    result = expr.execute()

    columns = ["G", "yearID"]
    more_values = (
        batting_df[columns]
        .sort_values("yearID", kind=sort_kind)
        .G.rolling(6, min_periods=1)
        .sum()
        .astype("int64")
    )
    expected = batting_df.assign(more_values=more_values).compute()
    tm.assert_frame_equal(result[expected.columns], expected)


@pytest.mark.xfail(
    raises=NotImplementedError,
    reason="Grouped and order windows not supported yet",
)
def test_batting_rolling_partitioned(batting, batting_df, sort_kind):
    t = batting
    group_by = "playerID"
    order_by = "yearID"
    expr = t.G.sum().over(
        ibis.trailing_window(3, order_by=t[order_by], group_by=t[group_by])
    )
    expr = t.mutate(rolled=expr)
    result = expr.execute()

    columns = [group_by, order_by, "G"]
    expected = (
        batting_df[columns]
        .set_index(order_by)
        .groupby(group_by)
        .G.rolling(4, min_periods=1)
        .sum()
        .rename("rolled")
    ).compute()

    tm.assert_series_equal(
        result.set_index([group_by, order_by]).sort_index().rolled,
        expected.sort_index().astype("int64"),
    )


@pytest.mark.parametrize(
    "window",
    [
        pytest.param(
            ibis.window(order_by="yearID"),
            marks=pytest.mark.xfail(reason="Cumulative windows not supported"),
        ),
        pytest.param(
            ibis.window(order_by="yearID", group_by="playerID"),
            marks=pytest.mark.xfail(reason="Group and order by not implemented"),
        ),
    ],
)
def test_window_failure_mode(batting, batting_df, window):
    # can't have order by without a following value of 0
    expr = batting.mutate(more_values=batting.G.sum().over(window))
    with pytest.raises(ibis.common.exceptions.OperationNotDefinedError):
        expr.execute()


def test_scalar_broadcasting(batting, batting_df):
    expr = batting.mutate(demeaned=batting.G - batting.G.mean())
    result = expr.execute()
    expected = batting_df.assign(demeaned=batting_df.G - batting_df.G.mean())
    expected = expected.compute()

    tm.assert_frame_equal(result, expected)


def test_mutate_with_window_after_join(sort_kind, npartitions):
    left_df = dd.from_pandas(
        pd.DataFrame(
            {
                "ints": [0, 1, 2],
                "strings": ["a", "b", "c"],
                "dates": pd.date_range("20170101", periods=3),
            }
        ),
        npartitions=npartitions,
    )
    right_df = dd.from_pandas(
        pd.DataFrame(
            {
                "group": [0, 1, 2] * 3,
                "value": [0, 1, np.nan, 3, 4, np.nan, 6, 7, 8],
            }
        ),
        npartitions=npartitions,
    )
    con = Backend().connect({"left": left_df, "right": right_df})
    left, right = map(con.table, ("left", "right"))

    joined = left.outer_join(right, left.ints == right.group)
    proj = joined[left, right.value]
    expr = proj.group_by("ints").mutate(sum=proj.value.sum())
    result = expr.execute()
    result = result.sort_values(["dates", "ints", "value"]).reset_index(drop=True)
    expected = (
        pd.DataFrame(
            {
                "dates": dd.concat([left_df.dates] * 3)
                .compute()
                .sort_values(kind=sort_kind)
                .reset_index(drop=True),
                "ints": [0] * 3 + [1] * 3 + [2] * 3,
                "strings": ["a"] * 3 + ["b"] * 3 + ["c"] * 3,
                "value": [0.0, 3.0, 6.0, 1.0, 4.0, 7.0, np.nan, np.nan, 8.0],
                "sum": [9.0] * 3 + [12.0] * 3 + [8.0] * 3,
            }
        )
        .sort_values(["dates", "ints", "value"])
        .reset_index(drop=True)
    )

    tm.assert_frame_equal(result[expected.columns], expected)


def test_mutate_scalar_with_window_after_join(npartitions):
    left_df = dd.from_pandas(pd.DataFrame({"ints": range(3)}), npartitions=npartitions)
    right_df = dd.from_pandas(
        pd.DataFrame(
            {
                "group": [0, 1, 2] * 3,
                "value": [0, 1, np.nan, 3, 4, np.nan, 6, 7, 8],
            }
        ),
        npartitions=npartitions,
    )
    con = Backend().connect({"left": left_df, "right": right_df})
    left, right = map(con.table, ("left", "right"))

    joined = left.outer_join(right, left.ints == right.group)
    proj = joined[left, right.value]
    expr = proj.mutate(sum=proj.value.sum(), const=1)
    result = expr.execute()
    result = result.sort_values(["ints", "value"]).reset_index(drop=True)
    expected = (
        pd.DataFrame(
            {
                "ints": [0] * 3 + [1] * 3 + [2] * 3,
                "value": [0.0, 3.0, 6.0, 1.0, 4.0, 7.0, np.nan, np.nan, 8.0],
                "sum": [29.0] * 9,
                "const": np.ones(9, dtype="int8"),
            }
        )
        .sort_values(["ints", "value"])
        .reset_index(drop=True)
    )

    tm.assert_frame_equal(result[expected.columns], expected)


def test_project_scalar_after_join(npartitions):
    left_df = dd.from_pandas(pd.DataFrame({"ints": range(3)}), npartitions=npartitions)
    right_df = dd.from_pandas(
        pd.DataFrame(
            {
                "group": [0, 1, 2] * 3,
                "value": [0, 1, np.nan, 3, 4, np.nan, 6, 7, 8],
            }
        ),
        npartitions=npartitions,
    )
    con = ibis.dask.connect({"left": left_df, "right": right_df})
    left, right = map(con.table, ("left", "right"))

    joined = left.outer_join(right, left.ints == right.group)
    proj = joined[left, right.value]
    expr = proj[proj.value.sum().name("sum"), ibis.literal(1).name("const")]
    result = expr.execute()
    expected = pd.DataFrame(
        {
            "sum": [29.0] * 9,
            "const": np.ones(9, dtype="int8"),
        }
    )
    tm.assert_frame_equal(result[expected.columns], expected)


@pytest.mark.xfail(
    raises=ibis.common.exceptions.OperationNotDefinedError,
    reason="MultiQuantile not implemented",
)
def test_project_list_scalar(npartitions):
    df = dd.from_pandas(pd.DataFrame({"ints": range(3)}), npartitions=npartitions)
    con = ibis.dask.connect({"df": df})
    table = con.table("df")
    expr = table.mutate(res=table.ints.quantile([0.5, 0.95]))
    result = expr.execute()

    expected = pd.Series([[1.0, 1.9] for _ in range(3)], name="res")
    tm.assert_series_equal(result.res, expected)


@pytest.mark.xfail(
    raises=NotImplementedError, reason="Group and order by not implemented"
)
def test_window_with_mlb(npartitions):
    index = pd.date_range("20170501", "20170507")
    data = np.random.randn(len(index), 3)
    df = (
        pd.DataFrame(data, columns=list("abc"), index=index)
        .rename_axis("time")
        .reset_index(drop=False)
    )
    df = dd.from_pandas(df, npartitions=npartitions)
    client = ibis.dask.connect({"df": df})
    t = client.table("df")
    rows_with_mlb = ibis.rows_with_max_lookback(5, ibis.interval(days=10))
    expr = t.mutate(
        sum=lambda df: df.a.sum().over(
            ibis.trailing_window(rows_with_mlb, order_by="time", group_by="b")
        )
    )
    result = expr.execute()
    expected = df.set_index("time")
    gb_df = (
        expected.groupby(["b"])["a"]
        .rolling("10d", closed="both")
        .apply(lambda s: s.iloc[-5:].sum(), raw=False)
        .sort_index(level=["time"])
        .reset_index(drop=True)
    )
    expected = expected.reset_index(drop=False).assign(sum=gb_df)
    tm.assert_frame_equal(result, expected)

    rows_with_mlb = ibis.rows_with_max_lookback(5, 10)
    with pytest.raises(com.IbisInputError):
        t.mutate(
            sum=lambda df: df.a.sum().over(
                ibis.trailing_window(rows_with_mlb, order_by="time")
            )
        )


def test_window_grouping_key_has_scope(t, df):
    param = ibis.param(dt.string)
    window = ibis.window(group_by=t.dup_strings + param)
    expr = t.plain_int64.mean().over(window)
    result = expr.execute(params={param: "a"})
    expected = df.groupby(df.dup_strings + "a").plain_int64.transform("mean").compute()

    tm.assert_series_equal(
        result, expected.sort_index().reset_index(drop=True), check_names=False
    )


@pytest.mark.xfail(
    raises=NotImplementedError,
    reason="Grouped and order windows not supported yet",
)
def test_window_on_and_by_key_as_window_input(t, df):
    order_by = "plain_int64"
    group_by = "dup_ints"
    control = "plain_float64"

    row_window = ibis.trailing_window(order_by=order_by, group_by=group_by, preceding=1)

    # Test built-in function

    tm.assert_series_equal(
        t[order_by].count().over(row_window).execute(),
        t[control].count().over(row_window).execute(),
        check_names=False,
    )

    tm.assert_series_equal(
        t[group_by].count().over(row_window).execute(),
        t[control].count().over(row_window).execute(),
        check_names=False,
    )

    # Test UDF

    @reduction(input_type=[dt.int64], output_type=dt.int64)
    def count(v):
        return len(v)

    @reduction(input_type=[dt.int64, dt.int64], output_type=dt.int64)
    def count_both(v1, v2):
        return len(v1)

    tm.assert_series_equal(
        count(t[order_by]).over(row_window).execute(),
        t[control].count().over(row_window).execute(),
        check_names=False,
    )

    tm.assert_series_equal(
        count(t[group_by]).over(row_window).execute(),
        t[control].count().over(row_window).execute(),
        check_names=False,
    )

    tm.assert_series_equal(
        count_both(t[group_by], t[order_by]).over(row_window).execute(),
        t[control].count().over(row_window).execute(),
        check_names=False,
    )


@pytest.fixture
def events(npartitions) -> dd.DataFrame:
    df = pd.DataFrame(
        {
            "event_id": [1] * 4 + [2] * 6 + [3] * 2,
            "measured_on": map(
                pd.Timestamp,
                map(
                    date,
                    [2021] * 12,
                    [6] * 4 + [5] * 6 + [7] * 2,
                    range(1, 13),
                ),
            ),
            "measurement": np.nan,
        }
    )
    df.at[1, "measurement"] = 5.0
    df.at[4, "measurement"] = 42.0
    df.at[5, "measurement"] = 42.0
    df.at[7, "measurement"] = 11.0
    return dd.from_pandas(df, npartitions=npartitions)


@pytest.mark.xfail(
    raises=NotImplementedError, reason="Group and order by not implemented"
)
def test_bfill(events):
    con = ibis.dask.connect({"t": events})
    t = con.table("t")

    win = ibis.window(
        group_by=t.event_id, order_by=ibis.desc(t.measured_on), following=0
    )
    grouped = t.mutate(grouper=t.measurement.count().over(win))

    expr = (
        grouped.group_by([grouped.event_id, grouped.grouper])
        .mutate(bfill=grouped.measurement.max())
        .order_by("measured_on")
    )
    result = expr.execute().reset_index(drop=True)

    expected_raw = """\
event_id measured_on  measurement  grouper  bfill
       2  2021-05-05         42.0        3   42.0
       2  2021-05-06         42.0        2   42.0
       2  2021-05-07          NaN        1   11.0
       2  2021-05-08         11.0        1   11.0
       2  2021-05-09          NaN        0    NaN
       2  2021-05-10          NaN        0    NaN
       1  2021-06-01          NaN        1    5.0
       1  2021-06-02          5.0        1    5.0
       1  2021-06-03          NaN        0    NaN
       1  2021-06-04          NaN        0    NaN
       3  2021-07-11          NaN        0    NaN
       3  2021-07-12          NaN        0    NaN"""
    expected = pd.read_csv(
        io.StringIO(expected_raw),
        sep=r"\s+",
        header=0,
        parse_dates=["measured_on"],
    )
    tm.assert_frame_equal(result, expected)
