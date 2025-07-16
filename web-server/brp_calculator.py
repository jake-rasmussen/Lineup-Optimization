"""
Baserunner-Dependent Net Run Production (BRP) Calculator
Calculates BRP values for 4-player batting sequences using precise statistical formulas.
"""


def calculate_brp(stats1, stats2, stats3, stats4):
    """
    Calculate Baserunner-Dependent Net Run Production (BRP) for a 4-tuple of players.
    
    Args:
        stats1, stats2, stats3, stats4: Dictionaries with player statistics containing keys:
            pa (plate appearances), h (hits), 2b (doubles), 3b (triples), hr (home runs),
            sb (stolen bases), bb (walks), hbp (hit by pitch), ibb (intentional walks)
    
    Returns:
        float: The calculated BRP value for the 4-player sequence
    """
    # Extract statistics for each player
    Apa, Ah, A2b, A3b, Ahr = stats1["pa"], stats1["h"], stats1["2b"], stats1["3b"], stats1["hr"]
    Asb, Abb, Ahbp, Aibb = stats1["sb"], stats1["bb"], stats1["hbp"], stats1["ibb"]
    
    Bpa, Bh, B2b, B3b, Bhr = stats2["pa"], stats2["h"], stats2["2b"], stats2["3b"], stats2["hr"]
    Bsb, Bbb, Bhbp, Bibb = stats2["sb"], stats2["bb"], stats2["hbp"], stats2["ibb"]
    
    Cpa, Ch, C2b, C3b, Chr = stats3["pa"], stats3["h"], stats3["2b"], stats3["3b"], stats3["hr"]
    Csb, Cbb, Chbp, Cibb = stats3["sb"], stats3["bb"], stats3["hbp"], stats3["ibb"]
    
    Dpa, Dh, D2b, D3b, Dhr = stats4["pa"], stats4["h"], stats4["2b"], stats4["3b"], stats4["hr"]
    Dsb, Dbb, Dhbp, Dibb = stats4["sb"], stats4["bb"], stats4["hbp"], stats4["ibb"]

    # Plus factors, GDP, FC, ADV Runner, Pop Up - currently using fixed values
    C4 = 0.25   # A plus factor
    C11 = 0.25  # B plus factor
    C18 = 0.2   # C plus factor
    C27 = 0.2   # D plus factor
    C5 = 0.25   # A GDP
    C12 = 0.25  # B GDP
    C19 = 0.25  # C GDP
    C28 = 0.25  # D GDP
    C6 = 0.25   # A FC
    C13 = 0.25  # B FC
    C20 = 0.25  # C FC
    C29 = 0.25  # D FC
    C7 = 0.25   # A ADV runner
    C14 = 0.25  # B ADV runner
    C21 = 0.25  # C ADV runner
    C30 = 0.25  # D ADV runner
    C8 = 0.25   # A Pop Up
    C15 = 0.25  # B Pop Up
    C22 = 0.25  # C Pop Up
    C31 = 0.25  # D Pop Up

    # Calculate rates for Player A (batter 1)
    F6 = (Apa - Ah - Abb - Ahbp - Aibb) / Apa  # Out rate
    I6 = (Ah - A2b - A3b - Ahr) / Apa          # Single rate
    I7 = I6 * C4                                # Single+
    I8 = I6 * (1 - C4)                          # Single-
    L6 = A2b / Apa                              # Double rate
    L7 = L6 * C4                                # Double+
    L8 = L6 * (1 - C4)                          # Double-
    O6 = A3b / Apa                              # Triple rate
    R6 = Ahr / Apa                              # Home run rate
    U6 = (Abb + Ahbp + Aibb) / Apa              # Walk rate
    X6 = U6 + I8                                # Steal-
    X7 = U6 + I6                                # Steal+
    AA5 = F6 * C5                               # GDP
    AA6 = F6 * C6                               # FC
    AA7 = F6 * C7                               # ADV runner
    AA8 = F6 * C8                               # Pop up

    # 0 outs batter A outcome probabilities
    I41 = R6
    J41 = F6
    K41 = (I6 + U6) * (1 - C4)
    O41 = L6 + C4 * (I6 + U6)
    P41 = O6

    # Calculate rates for Player B (batter 2)
    F13 = (Bpa - Bh - Bbb - Bhbp - Bibb) / Bpa  # Out rate
    F14 = F13 * C4                               # OutA+
    F15 = F13 * (1 - C4)                         # OutA-
    I13 = (Bh - B2b - B3b - Bhr) / Bpa           # Single rate
    I14 = I13 * C4                               # SingleA+
    I15 = I13 * (1 - C4)                         # SingleA-
    L13 = B2b / Bpa                              # Double rate
    L14 = L13 * C4                               # DoubleA+
    L15 = L13 * (1 - C4)                         # DoubleA-
    O13 = B3b / Bpa                              # Triple rate
    R13 = Bhr / Bpa                              # Home run rate
    U13 = (Bbb + Bhbp + Bibb) / Bpa              # Walk rate
    X13 = U13 + I15                              # Steal-
    X14 = U13 + I13                              # Steal+
    AA12 = F13 * C12                             # GDP
    AA13 = F13 * C13                             # FC
    AA14 = F13 * C14                             # ADV runner
    AA15 = F13 * C15                             # Pop up

    # 0 outs batter B outcome probabilities (given A's state)
    I43 = I41 * R13
    I45 = K41 * R13
    I46 = O41 * R13
    I47 = P41 * R13
    J43 = I41 * F13
    J44 = J41 * R13
    J47 = P41 * F14
    L45 = K41 * AA15
    M45 = K41 * AA14
    M46 = O41 * F15
    N46 = O41 * F14
    N47 = P41 * F15
    Q44 = J41 * F13
    Q45 = K41 * AA12
    R43 = I41 * (I13 + U13)
    R46 = O41 * I14
    R47 = P41 * I13
    S43 = I41 * L13
    S45 = K41 * L14
    S46 = O41 * L13
    S47 = P41 * L13
    T43 = I41 * O13
    T45 = K41 * O13
    T46 = O41 * O13
    T47 = P41 * O13
    U44 = J41 * (I13 + U13)
    U45 = K41 * AA13
    V44 = J41 * L13
    W44 = J41 * O13
    X45 = K41 * (I15 + U13)
    X46 = O41 * U13
    Y45 = K41 * I14
    Y46 = O41 * I15
    Y47 = P41 * U13
    Z45 = K41 * L15

    # Calculate rates for Player C (batter 3)
    F20 = (Cpa - Ch - Cbb - Chbp - Cibb) / Cpa  # Out rate
    F21 = F20 * C4                               # OutA+
    F22 = F20 * (1 - C4)                         # OutA-
    F23 = F20 * C11                              # OutB+
    F24 = F20 * (1 - C11)                        # OutB-
    I20 = (Ch - C2b - C3b - Chr) / Cpa           # Single rate
    I21 = I20 * C4                               # SingleA+
    I22 = I20 * (1 - C4)                         # SingleA-
    I23 = I20 * C11                              # SingleB+
    I24 = I20 * (1 - C11)                        # SingleB-
    L20 = C2b / Cpa                              # Double rate
    L21 = L20 * C4                               # DoubleA+
    L22 = L20 * (1 - C4)                         # DoubleA-
    L23 = L20 * C11                              # DoubleB+
    L24 = L20 * (1 - C11)                        # DoubleB-
    O20 = C3b / Cpa                              # Triple rate
    R20 = Chr / Cpa                              # Home run rate
    U20 = (Cbb + Chbp + Cibb) / Cpa              # Walk rate
    X20 = U20 + I22                              # Steal-
    X21 = U20 + I20                              # Steal+
    AA19 = F20 * C19                             # GDP
    AA20 = F20 * C20                             # FC
    AA21 = F20 * C21                             # ADV runner
    AA22 = F20 * C22                             # Pop up

    # Helper function for summing multiple values
    def SUM(*args):
        return sum(args)

    # 0 outs batter C outcome probabilities (extensive calculations based on A and B states)
    H51 = (Q44 * F20) + (Q45 * F20)
    H55 = SUM(U44, U45) * AA19
    H56 = L45 * AA19
    I49 = SUM(I43, I45, I46, I47) * R20
    I52 = (R43 + R46 + R47) * R20
    I53 = SUM(S43, S45, S46, S47) * R20
    I54 = SUM(T43, T45, T46, T47) * R20
    I61 = SUM(X45, X46) * R20
    I62 = SUM(Y45, Y46, Y47) * R20
    I63 = Z45 * R20
    J54 = SUM(T43, T45, T46, T47) * F21
    J55 = SUM(U44, U45) * R20
    J56 = L45 * R20
    J57 = (M45 + M46) * R20
    J58 = (N46 + N47) * R20
    J59 = V44 * R20
    J60 = W44 * R20
    Q50 = (J43 * F20) + (J44 * F20) + (J47 * F20)
    Q51 = (Q44 * R20) + (Q45 * R20)
    Q52 = (R43 + R46 + R47) * AA20
    Q58 = (N46 + N47) * F21
    Q60 = W44 * F21
    Q62 = SUM(Y45, Y46, Y47) * AA19
    U52 = (R43 + R46 + R47) * AA22
    V52 = (R43 + R46 + R47) * AA21
    V53 = SUM(S43, S45, S46, S47) * F24
    V62 = SUM(Y45, Y46, Y47) * AA21
    W53 = SUM(S43, S45, S46, S47) * F23
    W54 = SUM(T43, T45, T46, T47) * F22
    W63 = Z45 * F21
    AA49 = SUM(I43, I45, I46, I47) * ((1 - C18) * X21)
    AA53 = SUM(S43, S45, S46, S47) * I21
    AA54 = SUM(T43, T45, T46, T47) * I20
    AA63 = Z45 * I21
    AB49 = SUM(I43, I45, I46, I47) * (L20 + C18 * X21)
    AB52 = (R43 + R46 + R47) * L21
    AB53 = SUM(S43, S45, S47, S46) * L20
    AB54 = SUM(T43, T45, T46, T47) * L20
    AB61 = SUM(X45, X46) * L21
    AB62 = SUM(Y45, Y46, Y47) * L21
    AB63 = Z45 * L20
    AC49 = SUM(I43, I45, I46, I47) * O20
    AC52 = (R43 + R46 + R47) * O20
    AC53 = SUM(S43, S45, S46, S47) * O20
    AC54 = SUM(T43, T45, T46, T47) * O20
    AC61 = SUM(X45, X46) * O20
    AC62 = SUM(Y45, Y46, Y47) * O20
    AC63 = Z45 * O20
    AD52 = (R43 + R46 + R47) * X20
    AD53 = SUM(S43, S45, S46, S47) * U20
    AD61 = SUM(X45, X46) * I21
    AD62 = SUM(Y45, Y46, Y47) * I22
    AE52 = (R43 + R46 + R47) * I21
    AE53 = SUM(S43, S45, S46, S47) * I22
    AE54 = SUM(T43, T45, T46, T47) * U20
    AE62 = SUM(Y45, Y46, Y47) * I21
    AE63 = Z45 * I22
    AF52 = (R43 + R46 + R47) * L22
    AF61 = SUM(X45, X46) * L22
    AF62 = SUM(Y45, Y46, Y47) * L22
    AG50 = SUM(J43, J44, J47) * C18 * X21
    AG52 = (R43 + R46 + R47) * AA20
    AG57 = (M45 + M46) * I21
    AG58 = (N46 + N47) * I20
    AG59 = V44 * I21
    AG60 = W44 * I20
    AG62 = SUM(Y45, Y46, Y47) * AA20
    AH50 = SUM(J43, J44, J47) * (L20 + (1 - C18) * X21)
    AH55 = SUM(U44, U45) * L23
    AH56 = L45 * L21
    AH57 = (M45 + M46) * L20
    AH58 = (N46 + N47) * L20
    AH59 = V44 * L20
    AH60 = W44 * L20
    AI50 = SUM(J43, J44, J47) * O20
    AI55 = SUM(U44, U45) * O20
    AI56 = L45 * O20
    AI57 = (M45 + M46) * O20
    AI58 = (N46 + N47) * O20
    AI59 = V44 * O20
    AI60 = W44 * O20
    AJ55 = SUM(U44, U45) * X20
    AJ59 = V44 * U20
    AK55 = SUM(U44, U45) * I21
    AK59 = V44 * I22
    AK60 = W44 * U20
    AL55 = SUM(U44, U45) * L24
    AM51 = SUM(Q44, Q45) * (1 - C18) * X21
    AM55 = SUM(U44, U45) * AA20
    AM56 = L45 * AA20
    AN55 = SUM(U44, U45) * AA21
    AN59 = V44 * F22
    AO56 = L45 * X20
    AO57 = (M45 + M46) * U20
    AP56 = L45 * I21
    AP57 = (M45 + M46) * I22
    AP58 = (N46 + N47) * U20
    AQ56 = L45 * L22
    AR56 = L45 * AA21
    AR57 = (M45 + M46) * F22
    AS57 = (M45 + M46) * F21
    AS58 = (N46 + N47) * F22
    AT59 = V44 * F21
    AT60 = W44 * F22
    AU61 = SUM(X45, X46) * X20
    AU62 = SUM(Y45, Y46, Y47) * U20
    AU63 = Z45 * U20
    AV61 = SUM(X45, X46) * F22
    AW61 = SUM(X45, X46) * F21
    AW63 = Z45 * F22
    AX62 = SUM(Y45, Y46, Y47) * AA22
    AY51 = SUM(Q44, Q45) * (L20 + C18 * X21)
    AZ51 = SUM(Q44, Q45) * O20
    BA55 = SUM(U44, U45) * AA21
    BB56 = L45 * AA22

    # Calculate rates for Player D (batter 4)
    F29 = (Dpa - Dh - Dbb - Dhbp - Dibb) / Dpa  # Out rate
    F30 = F29 * C4                               # OutA+
    F31 = F29 * (1 - C4)                         # OutA-
    F32 = F29 * C11                              # OutB+
    F33 = F29 * (1 - C11)                        # OutB-
    F34 = F29 * C18                              # OutC+
    F35 = F29 * (1 - C18)                        # OutC-
    I29 = (Dh - D2b - D3b - Dhr) / Dpa           # Single rate
    I30 = I29 * C4                               # SingleA+
    I31 = I29 * (1 - C4)                         # SingleA-
    I32 = I29 * C11                              # SingleB+
    I33 = I29 * (1 - C11)                        # SingleB-
    I34 = I29 * C18                              # SingleC+
    I35 = I29 * (1 - C18)                        # SingleC-
    L29 = D2b / Dpa                              # Double rate
    L30 = L29 * C4                               # DoubleA+
    L31 = L29 * (1 - C4)                         # DoubleA-
    L32 = L29 * C11                              # DoubleB+
    L33 = L29 * (1 - C11)                        # DoubleB-
    L34 = L29 * C18                              # DoubleC+
    L35 = L29 * (1 - C18)                        # DoubleC-
    O29 = D3b / Dpa                              # Triple rate
    R29 = Dhr / Dpa                              # Home run rate
    U29 = (Dbb + Dhbp + Dibb) / Dpa              # Walk rate
    X29 = U29 + I31                              # Steal-
    X30 = U29 + I29                              # Steal+
    AA28 = F29 * C28                             # GDP
    AA29 = F29 * C29                             # FC
    AA30 = F29 * C30                             # ADV runner
    AA31 = F29 * C31                             # Pop up

    # 0 outs batter D outcome probabilities (extensive calculations based on A, B, and C states)
    H67 = SUM(Q50, Q51, Q52, Q58, Q60, Q62) * F29
    H71 = SUM(AG50, AG52, AG57, AG58, AG59, AG60, AG62) * F29
    H74 = SUM(AM51, AM55, AM56) * (F29 + AA29)
    H75 = AY51 * F29
    H76 = AZ51 * F29
    H77 = U52 * AA28
    H80 = BA55 * (F29 + AA29)
    H81 = SUM(AN55, AN59) * F29
    H82 = SUM(AT59, AT60) * F29
    H83 = BB56 * (F29 + AA29)
    H84 = SUM(AR56, AR57) * F29
    H85 = SUM(AS57, AS58) * F29
    H86 = AV61 * AA28
    H87 = AX62 * AA28
    H92 = SUM(AJ55, AJ59) * AA28
    H93 = SUM(AK55, AK59, AK60) * AA28
    H95 = SUM(AO56, AO57) * AA28
    H96 = SUM(AP56, AP57, AP58) * AA28

    I65 = SUM(I49, I52, I53, I54, I61, I62, I63) * R29
    I68 = SUM(AA49, AA53, AA54, AA63) * R29
    I69 = SUM(AB49, AB52, AB53, AB54, AB61, AB62, AB63) * R29
    I70 = SUM(AC49, AC52, AC53, AC54, AC61, AC62, AC63) * R29
    I89 = SUM(AD52, AD53, AD61, AD62) * R29
    I90 = SUM(AE52, AE53, AE54, AE62, AE63) * R29
    I91 = SUM(AF52, AF61, AF62) * R29
    I98 = SUM(AU61, AU62, AU63) * R29

    J65 = SUM(I49, I52, I53, I54, I61, I62, I63) * F29
    J66 = SUM(J54, J55, J56, J57, J58, J59, J60) * R29
    J70 = SUM(AC49, AC52, AC53, AC54, AC61, AC62, AC63) * F34
    J71 = SUM(AG50, AG52, AG57, AG58, AG59, AG60, AG62) * R29
    J72 = SUM(AH50, AH55, AH56, AH57, AH58, AH59, AH60) * R29
    J73 = SUM(AI50, AI55, AI56, AI57, AI58, AI59, AI60) * R29
    J77 = U52 * F29
    J78 = SUM(V52, V53, V62) * R29
    J79 = SUM(W53, W54, W63) * R29
    J86 = AV61 * R29
    J87 = AX62 * R29
    J88 = SUM(AW61, AW63) * R29
    J92 = SUM(AJ55, AJ59) * R29
    J93 = SUM(AK55, AK59, AK60) * R29
    J94 = AL55 * R29
    J95 = SUM(AO56, AO57) * R29
    J96 = SUM(AP56, AP57, AP58) * R29
    J97 = AQ56 * R29

    Q66 = SUM(J54, J55, J56, J57, J58, J59, J60) * F29
    Q67 = SUM(Q50, Q51, Q52, Q58, Q60, Q62) * R29
    Q68 = SUM(AA49, AA53, AA54, AA63) * AA29
    Q73 = SUM(AI50, AI55, AI56, AI57, AI58, AI59, AI60) * F34
    Q74 = SUM(AM51, AM55, AM56) * R29
    Q75 = AY51 * R29
    Q76 = AZ51 * R29
    Q79 = SUM(W53, W54, W63) * F32
    Q80 = BA55 * R29
    Q81 = SUM(AN55, AN59) * R29
    Q82 = SUM(AT59, AT60) * R29
    Q83 = BB56 * R29
    Q84 = SUM(AR56, AR57) * R29
    Q85 = SUM(AS57, AS58) * R29

    AG68 = SUM(AA49, AA53, AA54, AA63) * F35
    AH68 = SUM(AC49, AC52, AC53, AC54, AC61, AC62, AC63) * F34
    AH69 = SUM(AB49, AB52, AB53, AB54, AB61, AB62, AB63) * F35
    AI69 = SUM(AB49, AB52, AB53, AB54, AB61, AB62, AB63) * F34
    AI70 = SUM(AC49, AC52, AC53, AC54, AC61, AC62, AC63) * F35
    AM71 = SUM(AG50, AG52, AG57, AG58, AG59, AG60, AG62) * F35
    AN77 = U52 * F32
    AN78 = SUM(V52, V53, V62) * F33
    AN87 = AX62 * F32

    AT78 = SUM(V52, V53, V62) * F32
    AT79 = SUM(W53, W54, W63) * F33
    AT88 = SUM(AW61, AW63) * F32
    AY71 = SUM(AG50, AG52, AG57, AG58, AG59, AG60, AG62) * F34
    AY72 = SUM(AI50, AI55, AI56, AI57, AI58, AI59, AI60) * F35
    AZ72 = SUM(AH50, AH55, AH56, AH57, AH58, AH59, AH60) * F34
    AZ73 = SUM(AI50, AI55, AI56, AI57, AI58, AI59, AI60) * F35
    BA77 = U52 * F33
    BC65 = SUM(I49, I52, I53, I54, I61, I62, I63) * (I29 + U29)
    BC70 = SUM(AC49, AC52, AC53, AC54, AC61, AC62, AC63) * (I34 + U29)

    BD65 = SUM(I49, I52, I53, I54, I61, I62, I63) * L29
    BD68 = SUM(AA49, AA53, AA54, AA63) * L34
    BD69 = SUM(AB49, AB52, AB53, AB54, AB61, AB62, AB63) * L29
    BD70 = SUM(AC49, AC52, AC53, AC54, AC61, AC62, AC63) * L34
    BD89 = SUM(AD52, AD53, AD61, AD62) * L32
    BD90 = SUM(AE52, AE53, AE54, AE62, AE63) * L34
    BD91 = SUM(AF52, AF61, AF62) * L34
    BD98 = SUM(AU61, AU62, AU63) * L34

    BE65 = SUM(I49, I52, I53, I54, I61, I62, I63) * O29
    BE68 = SUM(AA49, AA53, AA54, AA63) * O29
    BE69 = SUM(AB49, AB52, AB53, AB54, AB61, AB62, AB63) * O29
    BE70 = SUM(AC49, AC52, AC53, AC54, AC61, AC62, AC63) * O29
    BE89 = SUM(AD52, AD53, AD61, AD62) * O29
    BE90 = SUM(AE52, AE53, AE54, AE62, AE63) * O29
    BE91 = SUM(AF52, AF61, AF62) * O29
    BE98 = SUM(AU61, AU62, AU63) * O29

    BF66 = SUM(J54, J55, J56, J57, J58, J59, J60) * (I29 + U29)
    BF68 = SUM(AA49, AA53, AA54, AA63) * AA29
    BF73 = SUM(AI50, AI55, AI56, AI57, AI58, AI59, AI60) * F34
    BF78 = SUM(V52, V53, V62) * I32
    BF79 = SUM(W53, W54, W63) * I32

    BG66 = SUM(J54, J55, J56, J57, J58, J59, J60) * L29
    BG77 = U52 * L32
    BG78 = SUM(V52, V53, V62) * L29
    BG79 = SUM(W53, W54, W63) * L29
    BG86 = AV61 * L30
    BG87 = AX62 * L32
    BG88 = SUM(AW61, AW63) * L29
    BG92 = SUM(AJ55, AJ59) * L34
    BG93 = SUM(AK55, AK59, AK60) * L34
    BG94 = AL55 * L34
    BG95 = SUM(AO56, AO57) * L34
    BG96 = SUM(AP56, AP57, AP58) * L34
    BG97 = AQ56 * L34

    BH66 = SUM(J54, J55, J56, J57, J58, J59, J60) * O29
    BH77 = U52 * O29
    BH78 = SUM(V52, V53, V62) * O29
    BH79 = SUM(W53, W54, W63) * O29
    BH86 = AV61 * O29
    BH87 = AX62 * O29
    BH88 = SUM(AW61, AW63) * O29
    BH92 = SUM(AJ55, AJ59) * O29
    BH93 = SUM(AK55, AK59, AK60) * O29
    BH94 = AL55 * O29
    BH95 = SUM(AO56, AO57) * O29
    BH96 = SUM(AP56, AP57, AP58) * O29
    BH97 = AQ56 * O29

    BI67 = SUM(Q50, Q51, Q52, Q58, Q60, Q62) * (I29 + U29)
    BI71 = SUM(AG50, AG52, AG57, AG58, AG59, AG60, AG62) * AA29
    BI77 = U52 * AA29
    BI81 = SUM(AN55, AN59) * I32
    BI82 = SUM(AT59, AT60) * I32
    BI85 = SUM(AS57, AS58) * I30
    BI89 = SUM(AD52, AD53, AD61, AD62) * AA28

    BJ67 = SUM(Q50, Q51, Q52, Q58, Q60, Q62) * L29
    BJ74 = SUM(AM51, AM55, AM56) * L34
    BJ75 = AY51 * L29
    BJ76 = AZ51 * L29
    BJ80 = BA55 * L32
    BJ81 = SUM(AN55, AN59) * L29
    BJ82 = SUM(AT59, AT60) * L32
    BJ83 = BB56 * L30
    BJ84 = SUM(AR56, AR57) * L30
    BJ85 = SUM(AS57, AS58) * L30

    BK67 = SUM(Q50, Q51, Q52, Q58, Q60, Q62) * O29
    BK74 = SUM(AM51, AM55, AM56) * O29
    BK75 = AY51 * O29
    BK76 = AZ51 * O29
    BK80 = BA55 * O29
    BK81 = SUM(AN55, AN59) * O29
    BK82 = SUM(AT59, AT60) * O29
    BK83 = BB56 * O29
    BK84 = SUM(AR56, AR57) * O29
    BK85 = SUM(AS57, AS58) * O29

    BO68 = SUM(AA49, AA53, AA54, AA63) * (I29 + U29)
    BO69 = SUM(AB49, AB52, AB53, AB54, AB61, AB62, AB63) * (I29 + U29)
    BP68 = SUM(AA49, AA53, AA54, AA63) * I34
    BP69 = SUM(AB49, AB52, AB53, AB54, AB61, AB62, AB63) * I34
    BP70 = SUM(AC49, AC52, AC53, AC54, AC61, AC62, AC63) * (I29 + U29)
    BQ71 = SUM(AG50, AG52, AG57, AG58, AG59, AG60, AG62) * (I29 + U29)
    BQ72 = SUM(AH50, AH55, AH56, AH57, AH58, AH59, AH60) * I35
    BR71 = SUM(AG50, AG52, AG57, AG58, AG59, AG60, AG62) * I34
    BR72 = SUM(AH50, AH55, AH56, AH57, AH58, AH59, AH60) * I34
    BR73 = SUM(AI50, AI55, AI56, AI57, AI58, AI59, AI60) * I35
    BS71 = SUM(AG50, AG52, AG57, AG58, AG59, AG60, AG62) * L29
    BT74 = SUM(AM51, AM55, AM56) * (I29 + U29)
    BT75 = AY51 * I35
    BU74 = SUM(AM51, AM55, AM56) * I34
    BU75 = AY51 * I34
    BU76 = AZ51 * I35
    BW77 = U52 * (I29 + U29)
    BW78 = SUM(V52, V53, V62) * I33
    BX77 = U52 * I32
    BX78 = SUM(V52, V53, V62) * (I29 + U29)
    BX79 = SUM(W53, W54, W63) * I33
    BX87 = AX62 * I32
    BY77 = U52 * L29
    BY78 = SUM(V52, V53, V62) * L33
    BY86 = AV61 * L29
    BY87 = AX62 * L29
    BZ80 = BA55 * (I29 + U29)
    BZ81 = SUM(AN55, AN59) * I33
    CA80 = BA55 * I32
    CA81 = SUM(AN55, AN59) * (I29 + U29)
    CA82 = SUM(AT59, AT60) * I33
    CB80 = BA55 * L29
    CB81 = SUM(AN55, AN59) * L33
    CC83 = BB56 * (I29 + U29)
    CC84 = SUM(AR56, AR57) * I31
    CD83 = BB56 * I30
    CD84 = SUM(AR56, AR57) * I30
    CD85 = SUM(AS57, AS58) * (I29 + U29)
    CE83 = BB56 * L31
    CE84 = SUM(AR56, AR57) * L29
    CF86 = AV61 * F32
    CF88 = SUM(AW61, AW63) * F29
    CG86 = AV61 * F29
    CH86 = AV61 * (I29 + U29)
    CH88 = SUM(AW61, AW63) * (I29 + U29)
    CI87 = AX62 * F29

    # RE24 Values (Run Expectancy based on base-out state)
    E106 = J104 = 0.48   # 000/0 outs
    E107 = K104 = 0.25   # 000/1 out
    E108 = L104 = 0.1    # 000/2 outs
    E109 = M104 = 0.86   # X00/0 outs
    N104 = E110 = 0.51   # X00/1 out
    O104 = E111 = 0.22   # X00/2 outs
    P104 = E112 = 1.1    # 0X0/0 outs
    Q104 = E113 = 0.66   # 0X0/1 out
    R104 = E114 = 0.32   # 0X0/2 outs
    S104 = E115 = 1.44   # XX0/0 outs
    T104 = E116 = 0.88   # XX0/1 out
    U104 = E117 = 0.43   # XX0/2 outs
    V104 = E118 = 1.35   # 00X/0 outs
    W104 = E119 = 0.95   # 00X/1 out
    X104 = E120 = 0.35   # 00X/2 outs
    Y104 = E121 = 1.78   # X0X/0 outs
    Z104 = E122 = 1.13   # X0X/1 out
    AA104 = E123 = 0.48  # X0X/2 outs
    AB104 = E124 = 1.96  # 0XX/0 outs
    AC104 = E125 = 1.38  # 0XX/1 out
    AD104 = E126 = 0.58  # 0XX/2 outs
    AE104 = E127 = 2.29  # XXX/0 outs
    AF104 = E128 = 1.54  # XXX/1 out
    AG104 = E129 = 0.75  # XXX/2 outs
    I104 = 0             # End of inning

    # BRP calculation using RE24 values
    I108 = (I104 - E108) * H67
    I110 = (I104 - E110) * SUM(H71, H77)
    I111 = (I104 - E111) * SUM(H74, H80, H83)
    I114 = (I104 - E114) * SUM(H81, H75, H84)
    I116 = (I104 - E116) * SUM(H86, H92, H95)
    I120 = (I104 - E120) * SUM(H82, H85)
    I122 = (I104 - E122) * SUM(H87, H96, H93)
    J106 = (J104 - E106 + 1) * I65
    J109 = (J104 - E109 + 2) * I68
    J112 = (J104 - E112 + 2) * I69
    J115 = (J104 - E115 + 3) * I89
    J118 = (J104 - E118 + 2) * I70
    J121 = (J104 - E121 + 3) * I90
    J124 = (J104 - E124 + 3) * I91
    J127 = (J104 - E127 + 4) * I98
    K106 = (K104 - E106) * J65
    K107 = (K104 - E107 + 1) * J66
    K110 = (K104 - E110 + 2) * SUM(J71, J78)
    K113 = (K104 - E113 + 2) * SUM(J72, J78)
    K116 = (K104 - E116 + 3) * SUM(J86, J92, J95)
    K119 = (K104 - E119 + 2) * SUM(J73, J79)
    K122 = (K104 - E122 + 3) * SUM(J87, J93, J96)
    K125 = (K104 - E125 + 3) * SUM(J88, J94, J97)
    L107 = (L104 - E107) * Q66
    L108 = (L104 - E108 + 1) * Q67
    L109 = (L104 - E109) * Q68
    L110 = (L104 - E110) * Q68
    L111 = (L104 - E111 + 2) * SUM(Q74, Q80, Q83)
    L114 = (L104 - E114 + 2) * SUM(Q75, Q81, Q84)
    L119 = (L104 - E119 + 1) * SUM(Q73, Q79)
    L120 = (L104 - E120 + 1) * SUM(Q76, Q82)
    M106 = (M104 - E106) * BC65
    N107 = (N104 - E107) * BF66
    N109 = (N104 - E109) * SUM(AG68, BF68)
    N119 = (N104 - E119 + 1) * BF73
    O107 = (O104 - E107) * Q66
    O108 = (O104 - E108) * Q67
    O110 = (O104 - E110) * SUM(AM71, BI71, BA77)
    P109 = (P104 - E109) * BO68
    P112 = (P104 - E112) * BO69
    Q110 = (Q104 - E110) * BQ71
    Q113 = (Q104 - E113) * SUM(BQ72, BW78)
    R111 = (R104 - E111) * SUM(BT74, BZ80, CC83)
    R114 = (R104 - E114) * SUM(BT75, BZ81, CC84)
    R116 = (R104 - E116 + 1) * CG86
    S106 = (S104 - E106) * BD65
    S109 = (S104 - E109 + 1) * BD68
    S112 = (S104 - E112 + 1) * BD69
    S115 = (S104 - E115 + 2) * BD89
    S121 = (S104 - E121 + 2) * BD90
    S124 = (S104 - E124 + 2) * BD91
    T107 = (T104 - E107) * BG66
    T109 = (T104 - E109 + 1) * AH68
    T110 = (T104 - E110) * AH69 + BG78
    T116 = (T104 - E116 + 2) * (BG86 + BG92 + BG95)
    T119 = (T104 - E119 + 1) * BG79
    T122 = (T104 - E122 + 2) * (BG87 + BG93)
    T125 = (T104 - E125 + 2) * (BG88 + BG94 + BG97)
    U108 = (U104 - E108) * BJ67
    U110 = (U104 - E110) * (AN77 + AY71)
    U111 = (U104 - E111) * (BJ74 + BJ80 + BJ83)
    U113 = (U104 - E113) * (AN78 + AY72)
    U120 = (U104 - E120 + 1) * (BJ76 + BJ82 + BJ85)
    U122 = (U104 - E122 + 1) * (AN87)
    V106 = (V104 - E106) * BE65
    V109 = (V104 - E109 + 1) * BE68
    V112 = (V104 - E112 + 1) * BE69
    V115 = (V104 - E115 + 2) * BE89
    V118 = (V104 - E118 + 1) * BE70
    V121 = (V104 - E121 + 2) * BE90
    V124 = (V104 - E124 + 2) * BE91
    V127 = (V104 - E127 + 3) * BE98
    W107 = (W104 - E107) * BH66
    W110 = (W104 - E110 + 1) * BH77
    W112 = (W104 - E112 + 1) * AI69
    W113 = (W104 - E113) * BH78
    W116 = (W104 - E116 + 2) * SUM(BH86, BH92, BH95)
    W118 = (W104 - E118 + 1) * AI70
    W119 = (W104 - E119 + 1) * BH79
    W122 = (W104 - E122 + 2) * SUM(BH87, BH96, BH93)
    W125 = (W104 - E125 + 2) * SUM(BH88, BH94, BH97)
    X108 = (X104 - E108) * BK67
    X111 = (X104 - E111 + 1) * (BK74 + BK80 + BK83)
    X113 = (X104 - E113 + 1) * (AT78 + AZ72)
    X114 = (X104 - E114 + 1) * (BK74 + BK81 + BK84)
    X119 = (X104 - E119 + 1) * (AT79 + AZ73)
    X120 = (X104 - E120 + 1) * (BK74 + BK81 + BK85)
    X125 = (X104 - E125 + 2) * AT88
    Y109 = (Y104 - E109) * BP68
    Y112 = (Y104 - E112) * BP69
    Y118 = (Y104 - E118) * BP70
    Z110 = (Z104 - E110) * (BR71 + BX77)
    Z113 = (Z104 - E113) * (BR72 + BX78)
    Z119 = (Z104 - E119) * (BR73 + BX79)
    AA111 = (AA104 - E111 + 1) * (BU74 + CA80)
    AA114 = (AA104 - E114 + 1) * (BU75 + CA80)
    AA120 = (AA104 - E120 + 1) * (BU76 + CA80)
    AB109 = (AB104 - E109 + 2) * BO68
    AB112 = (AB104 - E112 + 2) * BO69
    AC110 = (AC104 - E110 + 2) * (BS71 + BY77)
    AC113 = (AC104 - E113 + 2) * BY78
    AD111 = (AD104 - E111) * (CB80 + CE83)
    AD114 = (AD104 - E114) * (CB81 + CE84)
    AD116 = (AD104 - E116 + 1) * CF86
    AD125 = (AD104 - E125 + 1) * CF88
    AF116 = (AF104 - E116 + 1) * CH86
    AF125 = (AF104 - E125 + 1) * CH86

    # Final BRP calculation - sum of all situational contributions
    BRP = SUM(I108, I110, I111, I114, I116, I120, I122, J106, J109, J112, J115, J118, J121, J124, J127,
              K106, K107, K110, K113, K116, K119, K122, K125, L107, L108, L109, L110, L111, L114, L119, L120,
              M106, N107, N109, N119, O107, O108, O110, P109, P112, Q110, Q113, R111, R114, R116,
              S106, S109, S112, S115, S121, S124, T107, T109, T110, T116, T119, T122, T125,
              U108, U110, U111, U113, U120, U122, V106, V109, V112, V115, V118, V121, V124, V127,
              W107, W110, W112, W113, W116, W118, W119, W122, W125, X108, X111, X113, X114, X119, X120, X125,
              Y109, Y112, Y118, Z110, Z113, Z119, AA111, AA114, AA120, AB109, AB112, AC110, AC113,
              AD111, AD114, AD116, AD125, AF116, AF125)

    return BRP
