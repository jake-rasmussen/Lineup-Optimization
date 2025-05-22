def add_all(*args):
    total = 0
    for num in args:
        total += num
    return total
"""
example inputs: 
    A = Bryce Harper
    B = Trea Turner
    C = Juan Soto
    D = Anthony Rendon
    Stats are from the excel sheet
    This is to be changed, these stats should be taken as an argument for a method
"""
Apa = 370
Ah = 96
A2b = 18
A3b = 1
Ahr = 5
Asb = 9
Abb = 38
Ahbp = 11
Aibb = 0

Bpa = 597
Bh = 163
B2b = 44
B3b = 2
Bhr = 24
Bsb = 2
Bbb = 55
Bhbp = 5
Bibb = 5

Cpa = 385
Ch = 80
C2b = 22
C3b = 3
Chr = 6
Csb = 24
Cbb = 29
Chbp = 1
Cibb = 2

Dpa = 494
Dh = 121
D2b = 25
D3b = 1
Dhr = 22
Dsb = 5
Dbb = 79
Dhbp = 0
Dibb = 10
"""
Plus Factors, GDP, FC, ADV Runner, Pop Up TODO: find formula for all, for now using what is on excel
"""
C4 = 0.25  #A plus factor
C11 = 0.25 #B plus factor
C18 = 0.2 #C plus factor
C27 = 0.2 #D plus factor
C5 = 0.25 #A GDP
C12 = 0.25 #B GDP
C19 = 0.25 #C GDP
C28 = 0.25 #D GDP
C6 = 0.25 #A FC
C13 = 0.25 #B FC
C20 = 0.25 #C FC
C29 = 0.25 #D FC
C7 = 0.25 #A ADV runner
C14 = 0.25 #B ADV runner
C21 = 0.25 #C ADV runner
C30 = 0.25 #D ADV runner
C8 = 0.25 #A Pop Up
C15 = 0.25 #B Pop Up
C22 = 0.25 #C Pop Up
C31 = 0.25 #D Pop Up

"""
All rates for A:
"""
F6 = (Apa - Ah - Abb - Ahbp - Aibb) / Apa #Out
I6 = (Ah - A2b - A3b - Ahr) / Apa #1b
I7 = I6 * C4 #1b+
I8 = I6 * (1 - C4) #1b-
L6 = A2b / Apa #2b
L7 = L6 * C4 #2b+
L8 = L6 * (1 - C4) #2b-
O6 = A3b / Apa #3b
R6 = Ahr / Apa #hr
U6 = (Abb + Ahbp + Aibb) / Apa #walk (or equivelent)
X6 = U6 + I8 #steal-
X7 = U6+I6 #steal+
AA5 = F6 * C5 #GDP
AA6 = F6 * C6 #FC
AA7 = F6 * C7 #ADV runner
AA8 = F6 * C8 #Pop up

"""
All rates for B:
"""
F13 = (Bpa - Bh - Bbb - Bhbp - Bibb) / Bpa #Out
F14 =F13 * C4 #OutA+
F15=F13*(1-C4) #OutA-
I13 = (Bh - B2b - B3b - Bhr) / Bpa #1b
I14 = I13 * C4 #1BA+
I15 = I13 * (1 - C4) #1bA-
L13 = B2b /Bpa #2b
L14 = L13 * C4 #2BA+
L15 = L13 * (1 - C4) #2BA-
O13 = B3b / Bpa #3b
R13 = Bhr / Bpa #hr
U13 = (Bbb + Bhbp + Bibb) / Bpa #walk (or equivelent)
X13 =U13+I15 #steal-
X14 = U13+I13 #steal+
AA12 = F13 * C12 #GDP
AA13 = F13 * C13 #FC
AA14= F13 * C14 #ADV runner
AA15= F13 * C15 #Pop up

"""
All rates for C:
"""
F20 = (Cpa - Ch - Cbb - Chbp - Cibb) / Cpa #Out
F14 =F20 * C4 #OutA+
F15=F20*(1-C4) #OutA-
F23=F20*C11 #OutB+
F24=F20*(1-C11) #OutB-
I20 = (Ch - C2b - C3b - Chr) / Cpa #1b
I21 = I13 * C4 #1BA+
I15 = I13 * (1 - C4) #1bA-
L13 = B2b /Bpa #2b
L14 = L13 * C4 #2BA+
L15 = L13 * (1 - C4) #2BA-
O13 = B3b / Bpa #3b
R13 = Bhr / Bpa #hr
U13 = (Bbb + Bhbp + Bibb) / Bpa #walk (or equivelent)
X13 =U13+I15 #steal-
X14 = U13+I13 #steal+
AA12 = F13 * C12 #GDP
AA13 = F13 * C13 #FC
AA14= F13 * C14 #ADV runner
AA15= F13 * C15 #Pop up
"""
0 outs batter A:
"""
I41 = Ahr / Apa
