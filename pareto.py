import numpy as np
import pandas as pd
import plotly.express as px
from Optimizer import optimize


# =====================================================================
#                       PARETO FRONT COMPUTATION
# =====================================================================

def plot_pareto(
    inputs,
    cost_1="Total_cost",
    cost_2="Total_impact_per_passenger_per_km",
    n_points=10,
    plot=False
):
    """
    Compute a bi-objective Pareto front from the optimizer results.

    Two Pareto fronts are computed:
        Pareto 1 → minimize cost_2 within cost_1 bins
        Pareto 2 → minimize cost_1 within cost_2 bins

    Parameters
    ----------
    inputs : dict
        Optimizer input parameters.
    cost_1 : str
        First cost metric for comparison (X-axis).
    cost_2 : str
        Second cost metric for comparison (Y-axis).
    n_points : int
        Number of bins over which to compute Pareto candidates.
    plot : bool
        If True, show an interactive Plotly scatter plot.

    Returns
    -------
    pareto_1 : pd.DataFrame
        Pareto points minimizing cost_2 across cost_1 bins.
    pareto_2 : pd.DataFrame
        Pareto points minimizing cost_1 across cost_2 bins.
    """

    # -----------------------------------------------------------------
    #         1. Run optimizer and collect feasible configuration
    # -----------------------------------------------------------------
    df, _ = optimize(
        inputs,
        nb_of_pts=100,
        head=1,
        write=0,
        sort_by=cost_1
    )

    if df.empty:
        return pd.DataFrame(columns=df.columns), pd.DataFrame(columns=df.columns)

    # Bounds for grid sampling
    C_min = df[cost_1].min()
    C_max = df.loc[df[cost_2].idxmin(), cost_1]   # cost_1 at minimum cost_2

    G_min = df[cost_2].min()
    G_max = df.loc[df[cost_1].idxmin(), cost_2]   # cost_2 at minimum cost_1

    # Create linear partitions
    C_constraints = np.linspace(C_min, C_max, n_points)
    G_constraints = np.linspace(G_min, G_max, n_points)

    pareto_1 = []
    pareto_2 = []

    # =================================================================
    #                2. PRODUCE PARETO FRONT #1
    #     (Minimize cost_2 inside each cost_1 interval)
    # =================================================================
    for i in range(len(C_constraints) - 1):
        c_low  = C_constraints[i]
        c_high = C_constraints[i + 1]

        # Filter by cost_1 bin
        feasible = df[(df[cost_1] >= c_low) & (df[cost_1] < c_high)]

        if not feasible.empty:
            best = (
                feasible
                .sort_values(by=[cost_2])
                .head(1)
                .iloc[0]
            )
            best["lim_low"] = c_low
            best["lim_high"] = c_high
            pareto_1.append(best)

    # =================================================================
    #                3. PRODUCE PARETO FRONT #2
    #     (Minimize cost_1 inside each cost_2 interval)
    # =================================================================
    for i in range(len(G_constraints) - 1):
        g_low  = G_constraints[i]
        g_high = G_constraints[i + 1]

        feasible = df[(df[cost_2] >= g_low) & (df[cost_2] < g_high)]

        if not feasible.empty:
            best = (
                feasible
                .sort_values(by=[cost_1])
                .head(1)
                .iloc[0]
            )
            best["lim_low"] = g_low
            best["lim_high"] = g_high
            pareto_2.append(best)

    # Convert to DataFrames
    pareto_1 = pd.DataFrame(pareto_1)
    pareto_2 = pd.DataFrame(pareto_2)

    # =================================================================
    #                 4. OPTIONAL: INTERACTIVE PLOT
    # =================================================================
    if plot:
        fig = px.scatter(
            pareto_1,
            x=cost_1,
            y=cost_2,
            hover_data=pareto_1.columns,
            color_discrete_sequence=["red"],
            title=f"Pareto Front: {cost_1} vs {cost_2}"
        )

        fig.add_scatter(
            x=pareto_2[cost_1],
            y=pareto_2[cost_2],
            mode="markers",
            marker=dict(color="blue"),
            name="Pareto 2"
        )

        fig.show()

    return pareto_1, pareto_2

