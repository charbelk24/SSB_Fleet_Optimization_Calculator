import numpy as np
import pandas as pd
from Optimizer import optimize


def plot_pareto(inputs, cost_1="Total_cost", cost_2="Total_impact_per_passenger_per_km", n_points=10, plot=False):
    df, _ = optimize(inputs, nb_of_pts=100, head=1, write=0, sort_by=cost_1)

    if df.empty:
        return pd.DataFrame(columns=[cost_1, cost_2]), pd.DataFrame(columns=[cost_1, cost_2])

    df = df.copy()

    required_cols = [cost_1, cost_2]
    missing = [col for col in required_cols if col not in df.columns]
    if missing:
        raise ValueError(
            f"Missing Pareto columns: {missing}. Available columns: {list(df.columns)}"
        )

    df[cost_1] = pd.to_numeric(df[cost_1], errors="coerce")
    df[cost_2] = pd.to_numeric(df[cost_2], errors="coerce")
    df = df.dropna(subset=[cost_1, cost_2])

    if df.empty:
        return pd.DataFrame(columns=[cost_1, cost_2]), pd.DataFrame(columns=[cost_1, cost_2])

    if df[cost_1].nunique() < 2 or df[cost_2].nunique() < 2:
        return (
            df.nsmallest(1, cost_2).copy(),
            df.nsmallest(1, cost_1).copy()
        )

    C_min = df[cost_1].min()
    C_max = df[cost_1].max()

    G_min = df[cost_2].min()
    G_max = df[cost_2].max()

    if C_min == C_max or G_min == G_max:
        return (
            df.nsmallest(1, cost_2).copy(),
            df.nsmallest(1, cost_1).copy()
        )

    n_points = max(2, int(n_points))

    C_bins = np.linspace(C_min, C_max, n_points)
    G_bins = np.linspace(G_min, G_max, n_points)

    pareto_1 = []
    pareto_2 = []

    for i in range(len(C_bins) - 1):
        c_low = C_bins[i]
        c_high = C_bins[i + 1]

        if i == len(C_bins) - 2:
            feasible = df[(df[cost_1] >= c_low) & (df[cost_1] <= c_high)]
        else:
            feasible = df[(df[cost_1] >= c_low) & (df[cost_1] < c_high)]

        if not feasible.empty:
            pareto_1.append(feasible.loc[feasible[cost_2].idxmin()])

    for i in range(len(G_bins) - 1):
        g_low = G_bins[i]
        g_high = G_bins[i + 1]

        if i == len(G_bins) - 2:
            feasible = df[(df[cost_2] >= g_low) & (df[cost_2] <= g_high)]
        else:
            feasible = df[(df[cost_2] >= g_low) & (df[cost_2] < g_high)]

        if not feasible.empty:
            pareto_2.append(feasible.loc[feasible[cost_1].idxmin()])

    pareto_1 = pd.DataFrame(pareto_1)
    pareto_2 = pd.DataFrame(pareto_2)

    if pareto_1.empty:
        pareto_1 = pd.DataFrame(columns=df.columns)
    else:
        pareto_1 = pareto_1.drop_duplicates(subset=[cost_1, cost_2]).reset_index(drop=True)

    if pareto_2.empty:
        pareto_2 = pd.DataFrame(columns=df.columns)
    else:
        pareto_2 = pareto_2.drop_duplicates(subset=[cost_1, cost_2]).reset_index(drop=True)

    return pareto_1, pareto_2