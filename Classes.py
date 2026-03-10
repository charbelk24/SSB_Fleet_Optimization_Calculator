# =====================================================================
#                           HULL CLASS
# =====================================================================

class Hull(object):
    """
    Represents a hull type with:
    - Froude speed limits
    - Geometric scaling relations (length, beam, draft)
    - Weight / displacement equation
    - Resistance polynomial curve (4th-order)
    - Cost scaling relations
    - Energy-density ratio adjustment for Diesel / H2 / Battery

    All mathematical relations come directly from the Excel dataset.
    """

    def __init__(
        self, name, Fmin, Fmax, impact_slope,
        cost_coef, cost_power,
        length_int, length_slope,
        beam_int, beam_slope,
        draft_int, draft_slope,
        TDW_coef,TDW_power,
        GT_coef,GT_power,
        power_coef, power_Length_term, power_V_term,
        res_4, res_3, res_2, res_1, res_int,
        ratio_to_Diesel, ratio_to_H2, ratio_to_NMC_batteries
    ):
        # --- Identification ---
        self.name = name

        # --- Operational Froude limits ---
        self.Fmin = Fmin
        self.Fmax = Fmax

        # --- Length scaling L = a + b*C ---
        self.length_int = length_int
        self.length_slope = length_slope

        # --- Beam scaling B = a + b*L ---
        self.beam_int = beam_int
        self.beam_slope = beam_slope

        # --- Draft scaling T = a + b*L ---
        self.draft_int = draft_int
        self.draft_slope = draft_slope

        self.TDW_coef = TDW_coef
        self.TDW_power = TDW_power

        self.GT_coef = GT_coef
        self.GT_power = GT_power

        self.power_coef = power_coef
        self.power_Length_term = power_Length_term
        self.power_V_term = power_V_term    
        # --- Resistance polynomial coefficients ---
        self.res_4 = res_4
        self.res_3 = res_3
        self.res_2 = res_2
        self.res_1 = res_1
        self.res_int = res_int

        # --- Environmental impact of construction ---
        self.impact_slope = impact_slope

        # --- Cost scaling: cost = a * L^b ---
        self.cost_coef = cost_coef
        self.cost_power = cost_power

        # --- Energy-density (mass/volume) correction factors ---
        self.ratio = {
            "ratio_to_Diesel": ratio_to_Diesel,
            "ratio_to_H2": ratio_to_H2,
            "ratio_to_NMC_batteries": ratio_to_NMC_batteries
        }

    def calculate_length(self, C):
        """Return ship length L (m) based on passenger capacity C."""
        return self.length_int + self.length_slope * C

    def calculate_beam(self, L):
        """Return ship beam B (m) based on length L."""
        return self.beam_int + self.beam_slope * L

    def calculate_draft(self, L):
        """Return ship draft T (m) based on length L."""
        return self.draft_int + self.draft_slope * L

    
    def calculate_TDW(self,L):
        return self.TDW_coef * pow(L,self.TDW_power)
    
    def calculate_GT(self,L):
        return self.GT_coef * pow(L,self.GT_power)
    
    def calculate_power(self, L, V):
        return self.power_coef * pow(L, self.power_Length_term) * pow(V, self.power_V_term)


    def calculate_res(self, Fn, W):
        """
        Compute total resistance from polynomial in Froude number:

        Rt = (a + b*Fn + c*Fn^2 + d*Fn^3 + e*Fn^4) * W
        """
        return (
            self.res_int
            + self.res_1 * Fn
            + self.res_2 * (Fn ** 2)
            + self.res_3 * (Fn ** 3)
            + self.res_4 * (Fn ** 4)
        ) * W

    def calculate_impact(self, TDW):
        """Return construction cost using cost = coef * L^power."""
        return self.impact_slope * TDW
    
    def calculate_cost(self, L):
        """Return construction cost using cost = coef * L^power."""
        return self.cost_coef * pow(L, self.cost_power)


    def __str__(self):
        return self.name


# =====================================================================
#                         MOTOR CLASS
# =====================================================================

class Motor(object):
    """
    Represents a motor type with a given efficiency.
    Used mainly in the power conversion chain:
        Effective power → Shaft power → Motor power → Energy
    """

    def __init__(self, name, efficiency):
        self.name = name
        self.efficiency = efficiency

    def __str__(self):
        return f"{self.name}{self.efficiency}"


# =====================================================================
#                       PROPULSION CLASS
# =====================================================================

class Propulsion(object):
    """
    Represents a propulsion system (propeller or waterjet)
    with a given mechanical-to-shaft efficiency.
    """

    def __init__(self, name, Vmin, Vmax, eff_4, eff_3, eff_2, eff_1, eff_int):
        self.name = name
        self.Vmin = Vmin
        self.Vmax = Vmax
        self.eff_4 = eff_4
        self.eff_3 = eff_3
        self.eff_2 = eff_2
        self.eff_1 = eff_1
        self.eff_int = eff_int

    def calculate_efficiency(self, V):
        return self.eff_int + self.eff_1 * V + self.eff_2 * pow(V,2) +self.eff_3 * pow(V,3) + self.eff_4 * pow(V,4)


    def __str__(self):
        return f"{self.name}"


# =====================================================================
#                        ENERGY STORAGE CLASS
# =====================================================================

class Energies(object):
    """
    Represents an energy vector (Diesel, H2, Battery) with:
    - Mass per kWh stored
    - Volume per kWh stored
    - Environmental impact per kWh
    - Cost per kWh

    Used to compute:
    - Storage mass & volume constraints
    - Environmental footprint of energy
    - Storage cost
    """

    def __init__(self, name, mass_per_kWh, vol_per_kWh, impact_per_kWh, cost_per_kWh):
        self.name = name
        self.mass_per_kWh = mass_per_kWh
        self.vol_per_kWh = vol_per_kWh
        self.impact_per_kWh = impact_per_kWh
        self.cost_per_kWh = cost_per_kWh

    def __str__(self):
        return self.name
