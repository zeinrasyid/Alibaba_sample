import itertools
from io import BytesIO
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def render(
    df: pd.DataFrame,
    chart_type: str,
    x_column: str,
    y_columns: list[str],
    colors: list[str],
    show_values: bool,
    show_legend: bool,
    title: str,
    figsize: tuple[int, int],
) -> BytesIO:
    """Render chart to a PNG buffer.

    Raises:
        ValueError: If chart_type is unsupported or y columns can't be converted to numeric.
    """
    if chart_type not in _DRAW_DISPATCH:
        raise ValueError(
            f"Unsupported chart type '{chart_type}'. "
            f"Valid types: {', '.join(_DRAW_DISPATCH)}"
        )

    # Attempt numeric conversion for y columns
    for col in y_columns:
        if col in df.columns:
            converted = pd.to_numeric(df[col], errors="coerce")
            if converted.isna().all():
                raise ValueError(f"Column '{col}' cannot be converted to numeric values.")
            df[col] = converted

    fig, ax = plt.subplots(figsize=figsize)
    try:
        _DRAW_DISPATCH[chart_type](ax, df, x_column, y_columns, colors, show_values, show_legend)

        if title:
            ax.set_title(title, fontsize=14, fontweight="bold", pad=12)

        buf = BytesIO()
        fig.savefig(buf, format="png", dpi=150, bbox_inches="tight")
        buf.seek(0)
        return buf
    finally:
        plt.close(fig)




# ---------------------------------------------------------------------------
# Private draw functions
# ---------------------------------------------------------------------------

def _draw_bar(ax, df, x_col, y_cols, colors, show_values, show_legend):
    color_cycle = itertools.cycle(colors)
    x = np.arange(len(df))
    width = 0.8 / max(len(y_cols), 1)

    for i, col in enumerate(y_cols):
        c = next(color_cycle)
        offset = (i - len(y_cols) / 2 + 0.5) * width
        bars = ax.bar(x + offset, df[col], width=width, label=col, color=c)
        if show_values:
            for bar in bars:
                h = bar.get_height()
                ax.annotate(
                    f"{h:g}", xy=(bar.get_x() + bar.get_width() / 2, h),
                    ha="center", va="bottom", fontsize=8,
                )

    ax.set_xticks(x)
    ax.set_xticklabels(df[x_col].astype(str), rotation=45, ha="right")
    ax.set_xlabel(x_col)
    if show_legend and len(y_cols) > 1:
        ax.legend()


def _draw_horizontal_bar(ax, df, x_col, y_cols, colors, show_values, show_legend):
    color_cycle = itertools.cycle(colors)
    y = np.arange(len(df))
    height = 0.8 / max(len(y_cols), 1)

    for i, col in enumerate(y_cols):
        c = next(color_cycle)
        offset = (i - len(y_cols) / 2 + 0.5) * height
        bars = ax.barh(y + offset, df[col], height=height, label=col, color=c)
        if show_values:
            for bar in bars:
                w = bar.get_width()
                ax.annotate(
                    f"{w:g}", xy=(w, bar.get_y() + bar.get_height() / 2),
                    ha="left", va="center", fontsize=8,
                )

    ax.set_yticks(y)
    ax.set_yticklabels(df[x_col].astype(str))
    ax.set_ylabel(x_col)
    if show_legend and len(y_cols) > 1:
        ax.legend()


def _draw_stacked_bar(ax, df, x_col, y_cols, colors, show_values, show_legend):
    color_cycle = itertools.cycle(colors)
    x = np.arange(len(df))
    bottom = np.zeros(len(df))

    for col in y_cols:
        c = next(color_cycle)
        vals = df[col].values.astype(float)
        bars = ax.bar(x, vals, bottom=bottom, label=col, color=c)
        if show_values:
            for bar, b in zip(bars, bottom):
                h = bar.get_height()
                ax.annotate(
                    f"{h:g}", xy=(bar.get_x() + bar.get_width() / 2, b + h / 2),
                    ha="center", va="center", fontsize=8,
                )
        bottom += vals

    ax.set_xticks(x)
    ax.set_xticklabels(df[x_col].astype(str), rotation=45, ha="right")
    ax.set_xlabel(x_col)
    if show_legend and len(y_cols) > 1:
        ax.legend()


def _draw_line(ax, df, x_col, y_cols, colors, show_values, show_legend):
    color_cycle = itertools.cycle(colors)
    for col in y_cols:
        c = next(color_cycle)
        ax.plot(df[x_col].astype(str), df[col], marker="o", label=col, color=c)
        if show_values:
            for i, v in enumerate(df[col]):
                ax.annotate(f"{v:g}", (i, v), ha="center", va="bottom", fontsize=8)

    ax.set_xlabel(x_col)
    ax.tick_params(axis="x", rotation=45)
    if show_legend and len(y_cols) > 1:
        ax.legend()


def _draw_area(ax, df, x_col, y_cols, colors, show_values, show_legend):
    color_cycle = itertools.cycle(colors)
    x_vals = np.arange(len(df))
    for col in y_cols:
        c = next(color_cycle)
        ax.fill_between(x_vals, df[col], alpha=0.4, label=col, color=c)
        ax.plot(x_vals, df[col], color=c)
        if show_values:
            for i, v in enumerate(df[col]):
                ax.annotate(f"{v:g}", (i, v), ha="center", va="bottom", fontsize=8)

    ax.set_xticks(x_vals)
    ax.set_xticklabels(df[x_col].astype(str), rotation=45, ha="right")
    ax.set_xlabel(x_col)
    if show_legend and len(y_cols) > 1:
        ax.legend()


def _draw_pie(ax, df, x_col, y_cols, colors, show_values, show_legend):
    col = y_cols[0]
    labels = df[x_col].astype(str)
    values = df[col].values.astype(float)
    color_list = list(itertools.islice(itertools.cycle(colors), len(values)))

    autopct = "%1.1f%%" if show_values else None
    wedges, texts, *autotexts = ax.pie(
        values, colors=color_list, autopct=autopct, startangle=90,
        pctdistance=0.8,
    )
    if autotexts:
        for t in autotexts[0]:
            t.set_fontsize(7)
    ax.set_aspect("equal")
    if show_legend:
        ax.legend(wedges, labels, loc="center left", bbox_to_anchor=(1, 0.5), fontsize=8)


def _draw_donut(ax, df, x_col, y_cols, colors, show_values, show_legend):
    col = y_cols[0]
    labels = df[x_col].astype(str)
    values = df[col].values.astype(float)
    color_list = list(itertools.islice(itertools.cycle(colors), len(values)))

    autopct = "%1.1f%%" if show_values else None
    wedges, texts, *autotexts = ax.pie(
        values, colors=color_list, autopct=autopct,
        startangle=90, pctdistance=0.75, wedgeprops={"width": 0.4},
    )
    if autotexts:
        for t in autotexts[0]:
            t.set_fontsize(7)
    ax.set_aspect("equal")
    if show_legend:
        ax.legend(wedges, labels, loc="center left", bbox_to_anchor=(1, 0.5), fontsize=8)


def _draw_scatter(ax, df, x_col, y_cols, colors, show_values, show_legend):
    color_cycle = itertools.cycle(colors)
    for col in y_cols:
        c = next(color_cycle)
        ax.scatter(df[x_col], df[col], label=col, color=c, alpha=0.7)
        if show_values:
            for i in range(len(df)):
                ax.annotate(
                    f"{df[col].iloc[i]:g}",
                    (df[x_col].iloc[i], df[col].iloc[i]),
                    ha="center", va="bottom", fontsize=8,
                )

    ax.set_xlabel(x_col)
    if show_legend and len(y_cols) > 1:
        ax.legend()


def _draw_histogram(ax, df, x_col, y_cols, colors, show_values, show_legend):
    color_cycle = itertools.cycle(colors)
    for col in y_cols:
        c = next(color_cycle)
        n, bins, patches = ax.hist(df[col], bins="auto", label=col, color=c, alpha=0.7)
        if show_values:
            for count, patch in zip(n, patches):
                if count > 0:
                    ax.annotate(
                        f"{int(count)}",
                        xy=(patch.get_x() + patch.get_width() / 2, count),
                        ha="center", va="bottom", fontsize=8,
                    )

    ax.set_xlabel(y_cols[0] if y_cols else x_col)
    ax.set_ylabel("Frequency")
    if show_legend and len(y_cols) > 1:
        ax.legend()


def _draw_box(ax, df, x_col, y_cols, colors, show_values, show_legend):
    data = [df[col].dropna().values for col in y_cols]
    bp = ax.boxplot(data, labels=y_cols, patch_artist=True)

    color_cycle = itertools.cycle(colors)
    for patch in bp["boxes"]:
        patch.set_facecolor(next(color_cycle))

    if show_values:
        for i, col in enumerate(y_cols):
            median = df[col].median()
            ax.annotate(
                f"{median:g}", xy=(i + 1, median),
                ha="center", va="bottom", fontsize=8,
            )


def _draw_heatmap(ax, df, x_col, y_cols, colors, show_values, show_legend):
    numeric_df = df[y_cols].apply(pd.to_numeric, errors="coerce")
    data = numeric_df.values

    im = ax.imshow(data, aspect="auto", cmap="YlOrRd")
    ax.figure.colorbar(im, ax=ax)

    ax.set_xticks(np.arange(len(y_cols)))
    ax.set_xticklabels(y_cols, rotation=45, ha="right")
    ax.set_yticks(np.arange(len(df)))
    ax.set_yticklabels(df[x_col].astype(str))

    if show_values:
        for i in range(len(df)):
            for j in range(len(y_cols)):
                val = data[i, j]
                if not np.isnan(val):
                    ax.text(j, i, f"{val:g}", ha="center", va="center", fontsize=8)


# Dispatch table — defined after all draw functions exist
_DRAW_DISPATCH = {
    "bar": _draw_bar,
    "horizontal_bar": _draw_horizontal_bar,
    "stacked_bar": _draw_stacked_bar,
    "line": _draw_line,
    "area": _draw_area,
    "pie": _draw_pie,
    "donut": _draw_donut,
    "scatter": _draw_scatter,
    "histogram": _draw_histogram,
    "box": _draw_box,
    "heatmap": _draw_heatmap,
}