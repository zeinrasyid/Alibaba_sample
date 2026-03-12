import json
import matplotlib.pyplot as plt
import pandas as pd
from typing import Literal
from strands import tool, ToolContext
from src.core import logger
from src.tools.chart import chart_renderer, storage_manager


PALETTES: dict[str, list[str]] = {
    "default": ["#4C72B0", "#55A868", "#C44E52", "#8172B3", "#CCB974", "#64B5CD"],
    "warm": ["#E74C3C", "#E67E22", "#F1C40F", "#D35400", "#C0392B", "#F39C12"],
    "cool": ["#3498DB", "#1ABC9C", "#9B59B6", "#2980B9", "#16A085", "#8E44AD"],
    "pastel": ["#AEC6CF", "#FFB347", "#B39EB5", "#FF6961", "#77DD77", "#FDFD96"],
    "corporate": ["#2C3E50", "#34495E", "#7F8C8D", "#95A5A6", "#BDC3C7", "#ECF0F1"],
}


@tool(context=True)
def generate_chart(
    data: str,
    chart_type: Literal[
        "bar", "horizontal_bar", "stacked_bar", "line", "area",
        "pie", "donut", "scatter", "histogram", "box", "heatmap"
    ],
    x_column: str,
    y_columns: str,
    title: str = "",
    color_palette: Literal["default", "warm", "cool", "pastel", "corporate"] = "default",
    show_values: bool = True,
    show_legend: bool = True,
    figsize_width: int = 10,
    figsize_height: int = 6,
    tool_context=ToolContext
) -> str:
    """Generate a PNG chart from JSON data and save it to storage.

    Args:
        data: JSON string — canonical array format: [{"column": "value"}, ...].
        chart_type: Chart type — bar, horizontal_bar, stacked_bar, line, area,
            pie, donut, scatter, histogram, box, heatmap.
        x_column: Column name for x-axis / labels.
        y_columns: Column name(s) for y-axis, comma-separated (e.g. "sales,profit").
        title: Chart title.
        color_palette: Color scheme — default, warm, cool, pastel, corporate.
        show_values: Display data values on chart elements.
        show_legend: Show legend when multiple series exist.
        figsize_width: Chart width in inches.
        figsize_height: Chart height in inches.

    Returns:
        JSON string with chart_url, chart_type, title, data_points, columns, and summary.
    """
    logger.info(f"generate_chart: type={chart_type}, x={x_column}, y={y_columns}")

    user_id = tool_context.agent.state.get("user_id") if tool_context else ""
    session_id = tool_context.agent.state.get("session_id") if tool_context else ""
    if not user_id or not session_id:
        raise ValueError("Missing user_id or session_id in agent state")

    try:
        parsed = json.loads(data)

        # Strict validation: must be array of objects
        if not isinstance(parsed, list) or not all(isinstance(row, dict) for row in parsed):
            raise ValueError(
                f"Invalid data format. Must use canonical array: [{{\"x_column\": value, \"y_columns\": value}}, ...]. Your input: {data}"
            )

        df = pd.DataFrame(parsed)
        if df.empty:
            raise ValueError("No data to visualize.")

        y_cols = [c.strip() for c in y_columns.split(",") if c.strip()]
        colors = PALETTES.get(color_palette)

        buf = chart_renderer.render(
            df, chart_type, x_column, y_cols, colors,
            show_values, show_legend, title, (figsize_width, figsize_height),
        )

        chart_url = storage_manager.save_chart(buf, session_id, user_id)
        chart_title = title or f"{chart_type.replace('_', ' ').title()} Chart"
        logger.info(f"Chart saved: {chart_url}")

        # Store in agent state so telegram webhook can pick it up (lives only per-invocation)
        pending = tool_context.agent.state.get("pending_charts") or []
        pending.append({"url": chart_url, "title": chart_title})
        tool_context.agent.state.set("pending_charts",pending)

        return json.dumps({
            "chart_url": chart_url,
            "chart_type": chart_type,
            "title": chart_title,
            "data_points": len(df),
            "columns": {"x": x_column, "y": y_cols},
        })
    except Exception as e:
        logger.error(f"Chart generation error: {e}")
        raise
    finally:
        plt.close("all")