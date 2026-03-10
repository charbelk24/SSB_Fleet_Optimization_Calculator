import streamlit as st
import pandas as pd
import plotly.express as px
from Optimizer import optimize
from pareto import plot_pareto
from sensitivity import plot_tornado_sensitivity


st.set_page_config(page_title="Boat Optimizer", page_icon="🚤", layout="wide")

# --- Sidebar Inputs (Shared) ---
st.sidebar.header("Input Parameters")

distance = st.sidebar.number_input("Distance (km)", min_value=1.0, value=12.5, step=0.5)
Tmax = st.sidebar.number_input("Maximum trip time (minutes)", min_value=1.0, value=35.0)
Qpass = st.sidebar.number_input("Passenger flux (passengers/hour)", min_value=10, value=700)
t_ED = st.sidebar.number_input("Embark/Disembark + Maneuver time (minutes)", min_value=1.0, value=5.0)
n_rot = st.sidebar.number_input("Number of rotations", min_value=1, value=1)
margin = st.sidebar.number_input("Reserve margin", min_value=1.0, value=1.2)

inputs = {
    "Distance": distance,
    "Maximum time": Tmax,
    "Passenger flux": Qpass,
    "Embarking/disembarking time": t_ED,
    "Number of rotations": n_rot,
    "Reserve margin": margin
}

# --- Elegant Labels (keep identical mapping) ---
elegant_labels = {
    "Total_impact_per_passenger_per_km": "Total impact per passenger/km",
    "Total_cost": "Total cost (CHF)",
    "Total_impact": "Total impact (MJ eq or kg CO₂ eq)",
    "Trip_duration": "Trip duration (min)",
    "Length": "Length (m)",
    "Speed_in_kts": "Speed (knots)",
    "Number_of_ships": "Fleet size",
    "Trips_per_ship": "Trips per ship",
    "Passengers_per_trip": "Passengers per trip",
    "Energy_mass": "Energy mass (kg)",
    "Energy_volume": "Energy volume (m³)",
    "Energy_storage_per_boat": "Energy stored per boat (kWh)",
    "Froude_number": "Froude number",
    "Hull": "Hull type",
    "Energy_vector": "Energy vector",
    "Propuslsion": "Propulsion system",
    "Motor": "Motor type"
}
reverse_map = {v: k for k, v in elegant_labels.items()}


# --- Tabs ---
tab1, tab2, tab3 = st.tabs(["⚙️ Optimizer", "📈 Pareto Analysis", "📊 Sensitivity Analysis"])

# =====================================================
# ⚙️ TAB 1 — OPTIMIZER
# =====================================================
with tab1:
    st.title("🚤 Boat Fleet Optimizer")

    # --- Advanced Options ---
    with st.sidebar.expander("⚙️ Advanced Options", expanded=False):
        nb_of_pts = st.number_input("Number of Points", min_value=10, value=20, step=10)
        head = st.number_input("Best Configurations to Keep", min_value=1, value=1, step=1)
        sort_display = st.selectbox(
            "Sort results according to",
            list(elegant_labels.values()),
            index=0
        )
        sort_by = reverse_map[sort_display]

    # --- Run Optimizer ---
    if st.button("Run Optimization"):
        with st.spinner("Running optimizer... please wait ⏳"):
            df, best_df = optimize(inputs, nb_of_pts=nb_of_pts, head=head, sort_by=sort_by, write=0)
            st.session_state["optimizer_df"] = df
            st.session_state["best_df"] = best_df

            

    # --- Load DataFrames ---
    if "optimizer_df" in st.session_state and "best_df" in st.session_state:
        df = st.session_state["optimizer_df"]
        best_df = st.session_state["best_df"]

        if df.empty:
            st.error("No feasible solutions found. Try relaxing some parameters.")
        else:           
            st.success(f"✅ {len(df)} feasible configurations found")

            # ===== KPI SUMMARY =====
            min_duration_min = float(df["Trip_duration"].min())

            min_impact = float(df["Total_impact_per_passenger_per_km"].min())
            max_speed_kts = float(df["Speed_in_kts"].max())
            min_cost = float(df["Total_cost"].min())

            k1, k2, k3, k4 = st.columns(4)
            with k1:
                st.metric("Lowest impact", f"{min_impact:.3g} / pax / km")
            with k2:
                st.metric("Shortest trip", f"{min_duration_min:.1f} min" if min_duration_min else "–")
            with k3:
                st.metric("Lowest cost", f"{min_cost:,.0f} CHF")
            with k4:
                st.metric("Fastest speed", f"{max_speed_kts:.1f} kn")


            # --- BEST RESULTS ---
            with st.expander("🏆 Best Configurations per Hull", expanded=True):
                st.markdown("<hr style='border:1px solid #bbb; border-radius:5px; margin:10px 0;'>", unsafe_allow_html=True)
                st.dataframe(best_df, use_container_width=True)

            # --- Divider Line ---
            st.markdown("<div style='border-top:2px solid #ccc; margin:25px 0 20px 0;'></div>", unsafe_allow_html=True)

            # --- FILTERABLE RESULTS ---
            with st.expander("🔍 Filter All Results", expanded=True):

                # Scoped CSS for slider spacing
                st.markdown("""
                    <style>
                    div[data-testid="stVerticalBlock"] div[data-testid="stHorizontalBlock"] > div:first-child {padding-right: 15px;}
                    div[data-testid="stVerticalBlock"] div[data-testid="stHorizontalBlock"] > div:last-child {padding-left: 15px;}
                    </style>
                """, unsafe_allow_html=True)

                # --- Row 1: Impact & Duration ---
                col1, col2 = st.columns(2)
                with col1:
                    impact_min, impact_max = st.slider(
                        "Total impact per passenger/km",
                        float(df["Total_impact_per_passenger_per_km"].min()),
                        float(df["Total_impact_per_passenger_per_km"].max()),
                        (float(df["Total_impact_per_passenger_per_km"].min()),
                         float(df["Total_impact_per_passenger_per_km"].max()))
                    )
                with col2:
                    duration_min, duration_max = st.slider(
                        "Trip duration (minutes)",
                        float(df["Trip_duration"].min()),
                        float(df["Trip_duration"].max()),
                        (float(df["Trip_duration"].min()), float(df["Trip_duration"].max()))
                    )

                # --- Row 2: Length & Speed ---
                col3, col4 = st.columns(2)
                with col3:
                    length_min, length_max = st.slider(
                        "Length (m)",
                        float(df["Length"].min()), float(df["Length"].max()),
                        (float(df["Length"].min()), float(df["Length"].max()))
                    )
                with col4:
                    speed_min, speed_max = st.slider(
                        "Speed (knots)",
                        float(df["Speed_in_kts"].min()), float(df["Speed_in_kts"].max()),
                        (float(df["Speed_in_kts"].min()), float(df["Speed_in_kts"].max()))
                    )

                # --- Row 3: Fleet size & Trips per ship ---
                col5, col6 = st.columns(2)
                with col5:
                    ships_lo = int(df["Number_of_ships"].min())
                    ships_hi = int(df["Number_of_ships"].max())

                    if ships_lo == ships_hi:
                        ships_hi = ships_lo + 1
                        default_range = (ships_lo, ships_lo)
                    else:
                        default_range = (ships_lo, ships_hi)

                    ships_min, ships_max = st.slider(
                        "Fleet size (Number of ships)",
                        min_value=ships_lo,
                        max_value=ships_hi,
                        value=default_range
                    )
                with col6:
                    trips_lo = int(df["Trips_per_ship"].min())
                    trips_hi = int(df["Trips_per_ship"].max())

                    if trips_lo == trips_hi:
                        trips_hi = trips_lo + 1
                        default_range = (trips_lo, trips_lo)
                    else:
                        default_range = (trips_lo, trips_hi)

                    trips_min, trips_max = st.slider(
                        "Trips per ship",
                        min_value=trips_lo,
                        max_value=trips_hi,
                        value=default_range
                    )

                # Hull & Energy filters
                hulls = st.multiselect(
                    "Select Hull Types",
                    sorted(df["Hull"].unique()),
                    default=sorted(df["Hull"].unique())
                )
                energies = st.multiselect(
                    "Select Energy Vectors",
                    sorted(df["Energy_vector"].unique()),
                    default=sorted(df["Energy_vector"].unique())
                )

                # Apply Filters
                filtered_df = df[
                    (df["Total_impact_per_passenger_per_km"].between(impact_min, impact_max))
                    & (df["Trip_duration"].between(duration_min, duration_max))
                    & (df["Length"].between(length_min, length_max))
                    & (df["Speed_in_kts"].between(speed_min, speed_max))
                    & (df["Number_of_ships"].between(ships_min, ships_max))
                    & (df["Trips_per_ship"].between(trips_min, trips_max))
                    & (df["Hull"].isin(hulls))
                    & (df["Energy_vector"].isin(energies))
                ]

                st.markdown("<hr style='border:1px dashed #aaa; margin:10px 0;'>", unsafe_allow_html=True)
                st.write(f"### Filtered Results ({len(filtered_df)} rows)")
                st.dataframe(filtered_df, use_container_width=True)

            # --- Visualization ---
            with st.expander("📊 Visualization", expanded=True):
                if not filtered_df.empty:
                    numeric_columns = [c for c in filtered_df.columns if pd.api.types.is_numeric_dtype(filtered_df[c])]
                    categorical_options = [c for c in ["Hull", "Energy_vector", "Number_of_ships", "Trips_per_ship"] if c in filtered_df.columns]

                    x_axis = st.selectbox("X-axis", numeric_columns, index=numeric_columns.index("Speed_in_kts"))
                    y_axis = st.selectbox("Y-axis", numeric_columns, index=numeric_columns.index("Total_impact_per_passenger_per_km"))
                    color_by = st.selectbox("Color by", categorical_options, index=0)
                    symbol_by = st.selectbox("Symbol by", categorical_options, index=1)

                    # Custom hover
                    def format_duration(duration_min):
                        h = int(duration_min // 60)
                        m = int(duration_min % 60)
                        return f"{h} hr {m} min" if h > 0 else f"{m} min"

                    hover_text = []
                    for _, row in filtered_df.iterrows():
                        hover_text.append(
                            f"Hull={row['Hull']}<br>"
                            f"Energy_vector={row['Energy_vector']}<br>"
                            f"Speed_in_kts={row['Speed_in_kts']:.1f} kn<br>"
                            f"Trip_duration={format_duration(row['Trip_duration'])}<br>"
                            f"Total_impact_per_passenger_per_km={row['Total_impact_per_passenger_per_km']:.2f} /pax/km<br>"
                            f"Length={row['Length']:.1f} m<br>"
                            f"Passengers_per_trip={int(row['Passengers_per_trip'])}<br>"
                            f"Number_of_ships={int(row['Number_of_ships'])} ships<br>"
                            f"Trips_per_ship={int(row['Trips_per_ship'])} trips"
                        )

                    fig = px.scatter(
                        filtered_df,
                        x=x_axis,
                        y=y_axis,
                        color=color_by,
                        symbol=symbol_by,
                        hover_name=None,
                        hover_data=None,
                        title=f"{elegant_labels.get(y_axis, y_axis)} vs {elegant_labels.get(x_axis, x_axis)}"
                    )
                
                    fig.update_traces(
                        hovertemplate="%{customdata}",
                        customdata=hover_text,
                        marker=dict(line=dict(width=0.5, color="black"))
                    )
                    fig.update_layout(template="plotly_white", height=520)
                    st.plotly_chart(fig, use_container_width=True)

# =====================================================
# 📈 TAB 2 — PARETO ANALYSIS
# =====================================================
with tab2:
    st.title("📈 Pareto Front Analysis")

    # --- Use elegant labels for user interface ---
    cost_options = [
        "Total_cost",
        "Total_impact_per_passenger_per_km",
        "Trip_duration"
    ]

    # Convert to human-readable options
    display_options = [elegant_labels.get(opt, opt) for opt in cost_options]

    # --- Dropdowns using elegant labels ---
    cost1_display = st.selectbox("Select X-axis (Cost/Impact 1)", display_options, index=0)
    cost2_display = st.selectbox("Select Y-axis (Cost/Impact 2)", display_options, index=1)

    # Map back to internal column names
    cost1 = reverse_map.get(cost1_display, cost1_display)
    cost2 = reverse_map.get(cost2_display, cost2_display)

    # --- Slider for number of Pareto points ---
    n_points = st.slider("Number of Pareto points", min_value=5, max_value=50, value=10, step=5)


    # --- Run Pareto Analysis ---
    if st.button("Run Pareto Analysis"):
        with st.spinner("Computing Pareto front..."):
            pareto_1, pareto_2 = plot_pareto(inputs, cost_1=cost1, cost_2=cost2, n_points=n_points, plot=False)

            if pareto_1.empty or pareto_2.empty:
                st.error("No feasible Pareto points were found for the selected inputs.")
            else:
                st.success(f"✅ Computed {len(pareto_1)} + {len(pareto_2)} Pareto points")

                x_label = elegant_labels.get(cost1, cost1)
                y_label = elegant_labels.get(cost2, cost2)

                # ---- Build shared hover text ----
                hover_cols = [
                    "Hull", "Energy_vector", "Propuslsion", "Motor",
                    "Length", "Speed_in_kts", "Trip_duration",
                    "Number_of_ships", "Trips_per_ship", "Passengers_per_trip",
                    "Energy_mass", "Energy_volume", "Total_impact_per_passenger_per_km", "Total_cost"
                ]
                hover_cols = [col for col in hover_cols if col in pareto_1.columns]

                def build_hover(df):
                    hover_text = []
                    for _, row in df.iterrows():
                        lines = [f"<b>{x_label}:</b> {row[cost1]:,.2f}",
                                f"<b>{y_label}:</b> {row[cost2]:,.2f}"]
                        for col in hover_cols:
                            if col not in (cost1, cost2):
                                lines.append(f"<b>{elegant_labels.get(col, col)}:</b> {row[col]}")
                        hover_text.append("<br>".join(lines))
                    return hover_text

                hover_text_1 = build_hover(pareto_1)
                hover_text_2 = build_hover(pareto_2)

                # ---- Red Pareto 1 ----
                fig = px.scatter(
                    pareto_1,
                    x=cost1,
                    y=cost2,
                    color_discrete_sequence=["red"],
                    title=f"Pareto Front: {x_label} vs {y_label}"
                )
                fig.update_traces(
                    name=f"Minimize {y_label}",
                    showlegend=True,
                    hovertemplate="%{customdata}",
                    customdata=hover_text_1,
                    marker=dict(size=8, line=dict(width=0.5, color="black"))
                )

                # ---- Blue Pareto 2 ----
                fig.add_scatter(
                    x=pareto_2[cost1],
                    y=pareto_2[cost2],
                    mode="markers",
                    marker=dict(color="blue", size=8, line=dict(width=0.5, color="black")),
                    name=f"Minimize {x_label}",
                    showlegend=True,
                    hovertemplate="%{customdata}",
                    customdata=hover_text_2
                )

                # ---- Layout tweaks ----
                fig.update_layout(
                    template="plotly_white",
                    height=700,
                    width=950,
                    margin=dict(l=60, r=60, t=80, b=60),
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=-0.25,
                        xanchor="center",
                        x=0.5,
                        font=dict(size=12)
                    ),
                    xaxis_title=x_label,
                    yaxis_title=y_label,
                )

                st.plotly_chart(fig, use_container_width=False)

# =====================================================
# 📊 TAB 3 — TORNADO SENSITIVITY ANALYSIS
# =====================================================
with tab3:
    st.title("📊 Sensitivity Analysis")

    st.markdown(
        """
        This analysis evaluates how sensitive the **optimal solution**
        is to ± percentage changes in key input parameters.
        
        Each variable is perturbed independently while all others remain fixed.
        """
    )

    # -------------------------
    # Variable selection
    # -------------------------
    variables_to_test = st.multiselect(
        "Select variables to include in sensitivity analysis",
        [
            "Distance",
            "Maximum time",
            "Passenger flux",
            "Embarking/disembarking time",
            "Number of rotations",
            "Reserve margin",
        ],
        default=[
            "Distance",
            "Maximum time",
            "Passenger flux",
            "Reserve margin",
        ]
    )

    col1, col2 = st.columns(2)
    with col1:
        pct_change = st.slider(
            "Percentage variation (±)",
            min_value=5,
            max_value=50,
            value=10,
            step=5
        )
    with col2:
        nb_of_pts = st.number_input(
            "Optimizer sampling points per run",
            min_value=10,
            value=20,
            step=5
        )

    metric_display = st.selectbox(
        "Sensitivity metric",
        [
            "Total impact per passenger/km",
            "Total cost (CHF)",
            "Trip duration (min)"
        ],
        index=0
    )

    metric_map = {
        "Total impact per passenger/km": "Total_impact_per_passenger_per_km",
        "Total cost (CHF)": "Total_cost",
        "Trip duration (min)": "Trip_duration"
    }
    metric = metric_map[metric_display]

    st.markdown("<hr>", unsafe_allow_html=True)

    # -------------------------
    # Run Tornado Analysis
    # -------------------------
    if st.button("Run Sensitivity Analysis"):
        with st.spinner("Running sensitivity analysis... please wait ⏳"):
            if not variables_to_test:
                st.warning("Please select at least one variable.")
            else:
                
                fig, summary_df, low_df, high_df = plot_tornado_sensitivity(
                    base_inputs=inputs,
                    variables=variables_to_test,
                    metric=metric,
                    pct_change=pct_change / 100,
                    nb_of_pts=nb_of_pts
                )

                if fig is None or summary_df.empty:
                    st.error("No feasible sensitivity results were found for the selected inputs.")
                else:
                    st.success("✅ Sensitivity analysis completed")
                    st.plotly_chart(fig, use_container_width=True)

                    st.subheader("📋 Sensitivity Summary Table")
                    st.dataframe(summary_df, use_container_width=True)

                    with st.expander("⬇️ Best configurations — LOW scenarios"):
                        st.dataframe(low_df, use_container_width=True)

                    with st.expander("⬆️ Best configurations — HIGH scenarios"):
                        st.dataframe(high_df, use_container_width=True)
