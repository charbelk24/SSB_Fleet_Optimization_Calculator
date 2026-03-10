import math
import mpmath as mp

def get_speed_boundaries(hull, L):
    """ Returns the minimum and maximum feasible ship speed based on Froude limits."""
    V_min = hull.Fmin * math.sqrt(9.81*L)
    V_max = hull.Fmax * math.sqrt(9.81*L)
    return V_min,V_max

def get_ship_beam(hull, L):
    """Return ship beam based on length."""
    return hull.calculate_beam(L)

def get_ship_length(hull,C):
    """Return ship length based on passenger capacity C."""
    return hull.calculate_length(C)

def get_ship_draft(hull,L):
    """Return ship draft based on length."""
    return hull.calculate_draft(L)

def get_ship_weight(hull,L):
    """Return ship displacement weight."""
    return hull.calculate_weight(L)

def get_ship_impact(hull,L):
    """Return ship displacement weight."""
    return hull.calculate_impact(L)

def get_ship_TDW(hull,L):
    """Return ship displacement weight."""
    return hull.calculate_TDW(L)

def get_ship_GT(hull,L):
    """Return ship displacement weight."""
    return hull.calculate_GT(L)

def get_ship_power(hull,L,V):
    """Return ship displacement weight."""
    return hull.calculate_power(L,V)

def get_res_ratio(hull, Fn):
    """Compute total resistance based on Froude number and hull displacement."""
    return hull.calculate_res(Fn,1)

def get_res_from_Froude(hull, Fn, W):
    """Compute total resistance based on Froude number and hull displacement."""
    return hull.calculate_res(Fn, W)

def get_energy_from_res(EKW, prop, motor, T_total, number_of_rot):
    """
    Convert effective power to shaft power, motor power, and energy required.

    Parameters
    ----------
    EKW : float
        Effective power = V * Resistance
    prop : Propulsion
        Propulsion system (efficiency)
    motor : Motor
        Motor (efficiency)
    T_total : float
        Duration of one round trip (hours)
    number_of_rot : int
        Number of rotations before refuel/recharge.

    Returns
    -------
    P : float
        Motor shaft power (kW)
    E : float
        Energy consumed per round-trip (kWh)
    """
    # Shaft power after propeller losses
    SKW = EKW / prop.efficiency

    # Motor input power after motor losses
    P = SKW / motor.efficiency
    P = P / 1000   # Convert W → kW

    # Energy consumption for the rotation cycle
    E = P * T_total * number_of_rot
    return P, E

# def volume_from_GT(GT):
#     f = lambda V: V * (0.2 + 0.02 * math.log10(V)) - GT
#     return mp.findroot(f, 5 * GT)   # initial guess: 5×GT

def volume_from_GT(GT, tol=1e-8, max_iter=200):
    if GT <= 0:
        raise ValueError(f"GT must be positive, got {GT}")

    def f(V):
        return V * (0.2 + 0.02 * math.log10(V)) - GT

    low = 1e-9
    high = max(1.0, 10.0 * GT)

    while f(high) < 0:
        high *= 2
        if high > 1e12:
            raise ValueError(f"Could not bracket solution for GT={GT}")

    for _ in range(max_iter):
        mid = (low + high) / 2
        val = f(mid)

        if abs(val) < tol:
            return mid

        if val < 0:
            low = mid
        else:
            high = mid

    return (low + high) / 2

def get_ratio(hull, energy):
    """Return hull-to-energy scaling factor for displacement (mass/volume effects)."""
    return hull.ratio.get(f"ratio_to_{energy.name}", 1)

def get_ship_cost(hull,L):
    """Return cost of ship based on scaling law."""
    return hull.calculate_cost(L)

def get_prop_efficiency(prop, V):
    """Return propulsion efficiency based on speed."""
    return prop.calculate_efficiency(V)

def schedule(Q_pass, C, T):

    N_trips = math.ceil(Q_pass/C)
    Q = C/T
    N_fleet = math.ceil(Q_pass/Q)

    N_trips_per_ship = math.ceil(N_trips/N_fleet)
    H = 60/N_trips

    return N_trips, Q, N_fleet, N_trips_per_ship, H

def time_convert(T):
    return int(T/60)
    # h=int(T/3600)
    # m=(T/3600-h)*60
    # m=int(m)
    # return(str(h)+":"+str(m)+":00")

def unpack(inputs):
    """ Extract inputs from dictionary while applying default values."""
    D = 12.5
    T_max = 35
    Q_pass = 700
    t_ED = 5
    number_of_rot = 1
    reserve_margin = 1.2

    if "Distance" in inputs.keys():
        D= inputs["Distance"]
    if "Maximum time" in inputs.keys():
        T_max= inputs["Maximum time"]
    if "Passenger flux" in inputs.keys():
        Q_pass= inputs["Passenger flux"]
    if "Embarking/disembarking time" in inputs.keys():
        t_ED= inputs["Embarking/disembarking time"]
    if "Number of rotations" in inputs.keys():
        number_of_rot= inputs["Number of rotations"]
    if "Reserve margin" in inputs.keys():
        reserve_margin= inputs["Reserve margin"]

    return D, T_max, Q_pass, t_ED, number_of_rot, reserve_margin