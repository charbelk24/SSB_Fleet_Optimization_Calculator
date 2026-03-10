# import copy
# import pandas as pd
# import plotly.graph_objects as go
# from Optimizer import optimize


# def plot_tornado_sensitivity(base_inputs, variables, metric="Total_impact_per_passenger_per_km",
#                         pct_change=0.10, nb_of_pts=20):
#     """
#     Runs tornado sensitivity analysis and plots a polished tornado chart.
#     Additionally returns:
#         - df_table: tornado summary table
#         - df_low_runs: best configurations for LOW scenarios
#         - df_high_runs: best configurations for HIGH scenarios
#     """

#     results = []
#     low_rows = []
#     high_rows = []

#     # ---- BASE RUN ----
#     df_base, best_base = optimize(base_inputs, nb_of_pts=nb_of_pts, write=0, head=1)
#     base_value = float(best_base[metric].iloc[0])

#     for var in variables:

#         low_inputs = copy.deepcopy(base_inputs)
#         high_inputs = copy.deepcopy(base_inputs)

#         low_inputs[var] = base_inputs[var] * (1 - pct_change)
#         high_inputs[var] = base_inputs[var] * (1 + pct_change)

#         # ---- LOW RUN ----
#         df_low, best_low = optimize(low_inputs, nb_of_pts=nb_of_pts, write=0, head=1)
#         low_value = float(best_low[metric].iloc[0])

#         # Store all columns for inspection
#         best_low = best_low.copy()
#         best_low["Scenario"] = "LOW"
#         best_low["Variable"] = var
#         best_low["Percent_change"] = -pct_change * 100
#         low_rows.append(best_low)

#         # ---- HIGH RUN ----
#         df_high, best_high = optimize(high_inputs, nb_of_pts=nb_of_pts, write=0, head=1)
#         high_value = float(best_high[metric].iloc[0])

#         best_high = best_high.copy()
#         best_high["Scenario"] = "HIGH"
#         best_high["Variable"] = var
#         best_high["Percent_change"] = pct_change * 100
#         high_rows.append(best_high)

#         # ---- SUMMARY TABLE ENTRY ----
#         results.append({
#             "Variable": var,
#             "Low": low_value,
#             "Base": base_value,
#             "High": high_value,
#             "% Change": pct_change * 100
#         })

#     # ------------------------
#     #   BUILD DATAFRAMES
#     # ------------------------
#     df_low_runs = pd.concat(low_rows, ignore_index=True)
#     df_high_runs = pd.concat(high_rows, ignore_index=True)

#     df = pd.DataFrame(results)
#     df["Low_delta"] = df["Low"] - df["Base"]
#     df["High_delta"] = df["High"] - df["Base"]
#     df["Range"] = df["Low_delta"].abs() + df["High_delta"].abs()

#     df = df.sort_values("Range", ascending=True)
#     y_labels = df["Variable"]

#     # ------------------------
#     #   PLOT
#     # ------------------------
#     fig = go.Figure()

#     # LOW bars
       
#     fig.add_trace(go.Bar(
#         y=y_labels,
#         x=df["Low_delta"],
#         name=f"Low (−{df['% Change'].iloc[0]:.0f}%)",
#         orientation="h",
#         marker=dict(color="rgba(220,80,60,0.85)", line=dict(width=1, color="darkred")),
#         customdata=df["Low"],
#         text=df["Low"].round(2),
#         texttemplate="%{text}",          # <-- label printed on bar
#         textposition="outside",          # <-- puts label just outside bar
#         insidetextanchor="middle",
#         hovertemplate="<b>%{y}</b><br>"
#                     "Low value: %{customdata:.3f}<br>"
#                     "Δ vs Base: %{x:.3f}<extra></extra>"
#     ))

#     # HIGH bars (right)
#     fig.add_trace(go.Bar(
#         y=y_labels,
#         x=df["High_delta"],
#         name=f"High (+{df['% Change'].iloc[0]:.0f}%)",
#         orientation="h",
#         marker=dict(color="rgba(60,120,200,0.85)", line=dict(width=1, color="darkblue")),
#         customdata=df["High"],
#         text=df["High"].round(2),
#         texttemplate="%{text}",          # <-- label printed on bar
#         textposition="outside",          # <-- avoids center-line overlap
#         insidetextanchor="middle",
#         hovertemplate="<b>%{y}</b><br>"
#                     "High value: %{customdata:.3f}<br>"
#                     "Δ vs Base: %{x:.3f}<extra></extra>"
#     ))

#     # Baseline line
#     fig.add_shape(
#     type="line",
#     x0=0, x1=0,
#     y0=-0.5, y1=len(df) - 0.5,
#     line=dict(color="rgba(0,0,0,0.4)", width=1),  # <-- thinner line
#     layer="below"
# )


#     # Baseline annotation
#     fig.add_annotation(
#         x=0, y=len(df),
#         text=f"<b>Baseline {metric}: {base_value:.3f}</b>",
#         showarrow=False, font=dict(size=15), yshift=30
#     )


#     fig.update_layout(
#     title=f"<b>Tornado Sensitivity Chart</b><br><sup>Metric: {metric}</sup>",
#     template="plotly_white",
#     barmode="overlay",
#     height=750,
#     margin=dict(l=180, r=60, t=120, b=60),
#     xaxis_title=f"Change from Baseline {metric}",
#     yaxis_title="Variable"
# )

#     return fig, df, df_low_runs, df_high_runs




import copy
import pandas as pd
import plotly.graph_objects as go
from Optimizer import optimize


def plot_tornado_sensitivity(base_inputs, variables, metric="Total_impact_per_passenger_per_km",
                        pct_change=0.10, nb_of_pts=20):

    results = []
    low_rows = []
    high_rows = []

    # ---- BASE RUN ----
    df_base, best_base = optimize(base_inputs, nb_of_pts=nb_of_pts, write=0, head=1)

    if best_base.empty or metric not in best_base.columns:
        return None, pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

    base_value = float(best_base[metric].iloc[0])

    for var in variables:
        low_inputs = copy.deepcopy(base_inputs)
        high_inputs = copy.deepcopy(base_inputs)

        low_inputs[var] = base_inputs[var] * (1 - pct_change)
        high_inputs[var] = base_inputs[var] * (1 + pct_change)

        # ---- LOW RUN ----
        df_low, best_low = optimize(low_inputs, nb_of_pts=nb_of_pts, write=0, head=1)

        if best_low.empty or metric not in best_low.columns:
            low_value = None
        else:
            low_value = float(best_low[metric].iloc[0])
            best_low = best_low.copy()
            best_low["Scenario"] = "LOW"
            best_low["Variable"] = var
            best_low["Percent_change"] = -pct_change * 100
            low_rows.append(best_low)

        # ---- HIGH RUN ----
        df_high, best_high = optimize(high_inputs, nb_of_pts=nb_of_pts, write=0, head=1)

        if best_high.empty or metric not in best_high.columns:
            high_value = None
        else:
            high_value = float(best_high[metric].iloc[0])
            best_high = best_high.copy()
            best_high["Scenario"] = "HIGH"
            best_high["Variable"] = var
            best_high["Percent_change"] = pct_change * 100
            high_rows.append(best_high)

        results.append({
            "Variable": var,
            "Low": low_value,
            "Base": base_value,
            "High": high_value,
            "% Change": pct_change * 100
        })

    df_low_runs = pd.concat(low_rows, ignore_index=True) if low_rows else pd.DataFrame()
    df_high_runs = pd.concat(high_rows, ignore_index=True) if high_rows else pd.DataFrame()

    df = pd.DataFrame(results)

    if df.empty:
        return None, df, df_low_runs, df_high_runs

    # keep only rows where both scenarios worked
    df = df.dropna(subset=["Low", "High"])

    if df.empty:
        return None, df, df_low_runs, df_high_runs

    df["Low_delta"] = df["Low"] - df["Base"]
    df["High_delta"] = df["High"] - df["Base"]
    df["Range"] = df["Low_delta"].abs() + df["High_delta"].abs()

    df = df.sort_values("Range", ascending=True)
    y_labels = df["Variable"]

    fig = go.Figure()

    fig.add_trace(go.Bar(
        y=y_labels,
        x=df["Low_delta"],
        name=f"Low (−{df['% Change'].iloc[0]:.0f}%)",
        orientation="h",
        marker=dict(color="rgba(220,80,60,0.85)", line=dict(width=1, color="darkred")),
        customdata=df["Low"],
        text=df["Low"].round(2),
        texttemplate="%{text}",
        textposition="outside",
        insidetextanchor="middle",
        hovertemplate="<b>%{y}</b><br>"
                      "Low value: %{customdata:.3f}<br>"
                      "Δ vs Base: %{x:.3f}<extra></extra>"
    ))

    fig.add_trace(go.Bar(
        y=y_labels,
        x=df["High_delta"],
        name=f"High (+{df['% Change'].iloc[0]:.0f}%)",
        orientation="h",
        marker=dict(color="rgba(60,120,200,0.85)", line=dict(width=1, color="darkblue")),
        customdata=df["High"],
        text=df["High"].round(2),
        texttemplate="%{text}",
        textposition="outside",
        insidetextanchor="middle",
        hovertemplate="<b>%{y}</b><br>"
                      "High value: %{customdata:.3f}<br>"
                      "Δ vs Base: %{x:.3f}<extra></extra>"
    ))

    fig.add_shape(
        type="line",
        x0=0, x1=0,
        y0=-0.5, y1=len(df) - 0.5,
        line=dict(color="rgba(0,0,0,0.4)", width=1),
        layer="below"
    )

    fig.add_annotation(
        x=0, y=len(df),
        text=f"<b>Baseline {metric}: {base_value:.3f}</b>",
        showarrow=False, font=dict(size=15), yshift=30
    )

    fig.update_layout(
        title=f"<b>Tornado Sensitivity Chart</b><br><sup>Metric: {metric}</sup>",
        template="plotly_white",
        barmode="overlay",
        height=750,
        margin=dict(l=180, r=60, t=120, b=60),
        xaxis_title=f"Change from Baseline {metric}",
        yaxis_title="Variable"
    )

    return fig, df, df_low_runs, df_high_runs