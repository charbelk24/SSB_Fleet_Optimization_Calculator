
import math
import numpy as np
import pandas as pd

from functions import (
    get_speed_boundaries, get_ship_length, get_ship_draft, get_ship_beam, get_ship_impact, get_prop_efficiency,
    get_ship_cost, get_res_from_Froude, get_ship_TDW, get_ship_GT, get_ship_power, get_res_ratio, get_energy_from_res, get_ratio,
    volume_from_GT, schedule, time_convert, unpack
)
from Data import hulls, propulsion, motor_energy

def optimize(inputs,name="results",nb_of_pts=50,head=5,write=1, sort_by = "Total_impact_per_passenger_per_km"):
    """
    Main optimization routine to evaluate all feasible combinations of:
    - Hull types
    - Passenger capacity per trip
    - Ship speed
    - Propulsion systems
    - Motor + energy storage pairs

    Produces a dataframe of all feasible boat configurations and
    optionally writes CSV files.

    Parameters
    ----------
    inputs : dict
        User-defined inputs (distance [km], T_max [min], passenger flux[pax/h], Embarking/disembarking time [min], number of rotations, reserve margin)
    name : str
        Prefix for CSV output files
    nb_of_pts : int
        Number of sampling points for capacities and speeds
    head : int
        Number of best rows per hull to keep in "best_per_hull"
    write : int (0 or 1)
        If 1 → write CSVs
    sort_by : str
        Column name used to rank configurations

    Returns
    -------
    df : pd.DataFrame
        All feasible configurations
    best_per_hull : pd.DataFrame
        Top configurations per hull
    """
    
    g   = 9.81             
    mps_to_kn = 1.943844    # 1 m/s = 1.943844 kn

    records=[]
    lifetime_coef = 30 *292 *12 #Assuming 30 years of lifetime, 292 days of operation per year, 12 hours per day

    #Unpack inputs as separate variables
    D, T_max, Q_pass, t_ED, number_of_rot, reserve_margin = unpack(inputs)
    
    #Conversion to kms and seconds
    D=1000*D #[m]
    T_max = 60*T_max #[s]
    t_ED = 60*t_ED #[s]

    
    #Start iterating over each type of hull
    for hull in hulls:
        #Generating range of passenger capacities C [pax]
        C_range = np.linspace(Q_pass/nb_of_pts, 1.5*Q_pass, nb_of_pts)
        
        for c in C_range:
            C=math.ceil(c)

            #For each capacity, compute the ship dimensions
            L= get_ship_length(hull, C) #Length [m]
            B = get_ship_beam(hull,L) #Beam [m]
            Dr= get_ship_draft(hull,L) #Draft [m]

            TDW = get_ship_TDW(hull,L)

            #Compute the sspeed boundaries from the Froude range of each hull regime
            Vmin, Vmax = get_speed_boundaries(hull, L)  #in [m/s]
            #Ensure Vmin is enough to travel distance in less than Tmax
            Vmin = max(Vmin, D/T_max)
            #Generate a range of speeds to optimize over
            

            #Iteration over each type of motor energy pairing
            for prop in propulsion:
                Vmin = max(Vmin,prop.Vmin)
                Vmax = min(Vmax,prop.Vmax)
                V_range = np.linspace(Vmin,Vmax, nb_of_pts)
                for V in V_range:
                    Flag_time=0  #Used to detect cases where the trip duration is larger than the maximum (if needed)

                    #Compute Froude number and trip duration
                    Fn = V/math.sqrt(g*L)
                    T_travel = D/V + t_ED #in [s]
                    T_round_trip = 2*T_travel #in [s]
                    #Remove cases where trip duration exceeds maximum (first feasibility check)
                    if T_travel > T_max: 
                        Flag_time=1
                        continue
                    
                    #Compute fleet size and number of trips needed in function of inputs
                    N_trips, Q, N_fleet, N_trips_per_ship, H = schedule(Q_pass, C, T_round_trip/3600)

                    #Compute the impact and cost of the fleet
                    impact_Ship = N_fleet * T_round_trip* get_ship_impact(hull,TDW)/lifetime_coef  #[g CO2]
                    cost_Ship = N_fleet * T_round_trip * get_ship_cost(hull,L)/lifetime_coef   #[M CHF]   
                    
                    #Iteration over each type of motor energy pairing
                    for motor,energy in motor_energy:
                        flag_mass=0  #Flags used to detect volume and mass limit violations (if needed)
                        flag_vol=0
                        
                        P_installed = get_ship_power(hull,L,V*mps_to_kn)
                        P = 0.8* P_installed
                        P_motor = P*motor.efficiency
                        EKW = P_motor * get_prop_efficiency(prop,V)
                        Rt = EKW/V
                        res_over_w = get_res_ratio(hull, Fn)
                        W =Rt/res_over_w
                        Disp=W/g
                        
                        E = P * T_round_trip/3600 * number_of_rot
                        E_storage = E * N_trips_per_ship * reserve_margin #[kWh]
                        
                        GT = get_ship_GT(hull,L)
                        Vol = volume_from_GT(GT)
                        
                        #Calculate mass [kg], volume [m3], impact [g CO2], and cost [CHF] of energy stored
                        E_mass = E_storage * energy.mass_per_kWh
                        E_vol =  E_storage * energy.vol_per_kWh
                        E_impact =  E_storage * energy.impact_per_kWh * N_fleet 
                        E_cost = E_storage * energy.cost_per_kWh * N_fleet

                        #Compute mass and volume limits for feasibility checks and remove cases that violate the constraints
                        mass_limit = 0.1*TDW*1000
                        vol_limit = 0.1*Vol*1000
                        if E_mass>mass_limit:
                            # flag_mass=1
                            continue
                        if E_vol>vol_limit:
                            flag_vol=1
                            continue
                            
                        #Add feasible results to records
                        records.append({"Hull": hull.name,
                    "Energy_vector": energy.name,
                    "Propuslsion": prop.name,
                    "Motor": motor.name,
                    "Length": round(L,2), #[m]
                    # "Beam": round(B,2), #[m]
                    # "Draft" : round(Dr,2), #[m]
                    "Number_of_ships": N_fleet,
                    "Trips_per_ship": N_trips_per_ship,
                    "Trip_duration":time_convert(T_travel),# [min]
                    # "RoundTrip_duration":time_convert(T_round_trip),
                    "Passengers_per_trip": C,  #[pax]
                    # "Speed": round(V,2),
                    "Speed_in_kts": round (V*mps_to_kn,3),  #[kts]
                    "Froude_number": round(Fn,2),
                    # "Displacement":round(Disp,2),  #[tons]
                    # "Resistance": round(Rt,2),
                    "Power": round(P, 2),   #[kW]
                    # "Time flag": Flag_time,
                    # "Mass_Flag": flag_mass,
                    # "Vol_flag": flag_vol,
                    "Energy_storage_per_boat": round(E_storage,2),  #[kWh]
                    # "Energy_mass": round(E_mass,2),
                    # "Limit M": round(mass_limit,2),
                    # "Energy_volume": round(E_vol,2),
                    # "Limit V": round(vol_limit,2),
                    # "Impact_construction": round(impact_Ship,2),
                    # "Impact_energy": round(E_impact,2),
                    # "Total_impact": round(impact_Ship + E_impact,2),
                    "Total_impact_per_passenger_per_km": round((impact_Ship + E_impact) / (D/1000 * Q_pass),2),  #[g CO2 / km / pax]
                    # "Ship cost": round(cost_Ship,2), #[M CHF]
                    # "Energy_cost": round(E_cost,2), #[CHF]
                    "Total_cost": round((E_cost + cost_Ship*1000000)/(D/1000 * Q_pass),2)  #[CHF / km /pax]
                    })
                    
                        
    
    #Transform records into datafram                  
    df = pd.DataFrame.from_records(records)
    if df.empty:
        return pd.DataFrame(), pd.DataFrame()
    
    # df["Trip_duration"] = pd.to_timedelta(df["Trip_duration"])
    # df["RoundTrip_duration"] = pd.to_timedelta(df["RoundTrip_duration"])

    #Sort dataframe according to chosen cost
    if not df.empty:
        df.sort_values(by=[sort_by], inplace=True, ascending=True)
    
    #Save to csv
    out_path = "./"+name+"_optimizer.csv"
    if write:
        df.to_csv(out_path, index=False)

    # Isolate optimal solutions by hull in separate dataframe
    best_per_hull = (df
                 .sort_values(by=[sort_by])
                 .groupby(["Hull"], as_index=False)
                 .head(head))

    best_path = "./" +name+"_best_per_hull.csv"
    if write: 
        best_per_hull.to_csv(best_path, index=False) 
        
    print("Success")
    return df, best_per_hull

