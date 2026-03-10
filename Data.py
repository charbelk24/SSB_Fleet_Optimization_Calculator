import pandas as pd
from Classes import Hull, Propulsion, Motor, Energies

# ---------- Helper ----------
def make_lambda(formula: str, vars: str):
    """Convert text like '0.0674*C+15.526' to a lambda."""
    return eval(f"lambda {vars}: {formula}")

# ---------- Load Excel ----------
file_path = "Data.xlsx"  # <--- update path if needed

hull_df = pd.read_excel(file_path, sheet_name="Hulls")
prop_df = pd.read_excel(file_path, sheet_name="Propulsion")
motor_df = pd.read_excel(file_path, sheet_name="Motors")
energy_df = pd.read_excel(file_path, sheet_name="Energies")
pair_df = pd.read_excel(file_path, sheet_name="Motor-Energy")

# ---------- Create objects ----------
hulls = [
    Hull(
        name=row["Name"],
        Fmin=row["Fmin"],
        Fmax=row["Fmax"],
        impact_slope=row["Impact Slope"],
        cost_coef = row["Cost Coefficient"],
        cost_power = row["Cost Power"],
        length_int = row["Length Intercept"],
        length_slope = row["Length Slope"], 
        beam_int = row["Beam Intercept"], 
        beam_slope = row["Beam Slope"],
        draft_int = row["Draft Intercept"], 
        draft_slope = row["Draft Slope"], 
        TDW_coef = row["TDW Coefficient"],
        TDW_power = row["TDW Power"],
        GT_coef = row["GT Coefficient"],
        GT_power = row["GT Power"],
        power_coef = row["Power Coefficient"],
        power_V_term = row["Power Speed Term"],
        power_Length_term = row["Power Length Term"], 
        res_4 = row["Rt Order 4"],
        res_3 = row["Rt Order 3"],
        res_2 = row["Rt Order 2"],
        res_1 = row["Rt Order 1"],
        res_int = row["Rt Intercept"],
        ratio_to_Diesel=row["ratio_to_Diesel"],
        ratio_to_H2=row["ratio_to_H2"],         
        ratio_to_NMC_batteries=row["ratio_to_NMC_batteries"]
    )
    for _, row in hull_df.iterrows()
]
propulsion = [
    Propulsion(
        name=row["Name"],
        Vmin=row["Vmin"],
        Vmax=row["Vmax"],
        eff_4 = row["Efficiency Order 4"],
        eff_3 = row["Efficiency Order 3"],
        eff_2 = row["Efficiency Order 2"],
        eff_1 = row["Efficiency Order 1"],
        eff_int = row["Efficiency Intercept"] 
    )
    for _, row in prop_df.iterrows()
]

motors = [Motor(row["Name"], row["Efficiency"]) for _, row in motor_df.iterrows()]
energies = [
    Energies(row["Name"], row["mass_per_kWh"], row["vol_per_kWh"], row["impact_per_kWh"], row["cost_per_kWh"])
    for _, row in energy_df.iterrows()
]

# ---------- Create motor–energy pairs from sheet ----------
motor_energy = []
for _, row in pair_df.iterrows():
    motor_name = row["Motor"]
    energy_name = row["Energy"]

    motor = next((m for m in motors if m.name == motor_name), None)
    energy = next((e for e in energies if e.name == energy_name), None)

    if motor and energy:
        motor_energy.append((motor, energy))
    else:
        print(f"⚠️ Warning: could not find match for {motor_name} + {energy_name}")

# ---------- Summary ----------
print(f"✅ Loaded {len(hulls)} hulls, {len(propulsion)} propulsion systems, "
      f"{len(motors)} motors, {len(energies)} energies, "
      f"{len(motor_energy)} motor–energy pairs.")
