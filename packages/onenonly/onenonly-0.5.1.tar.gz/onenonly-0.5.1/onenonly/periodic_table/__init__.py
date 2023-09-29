import pandas as pd

def table():
    return (r"""
        1  2  3   4  5  6  7  8  9  10 11 12 13 14 15 16 17 18
    1   H                                                   He
    2   Li Be                                B  C  N  O  F  Ne
    3   Na Mg                                Al Si P  S  Cl Ar
    4   K  Ca Sc  Ti V  Cr Mn Fe Co Ni Cu Zn Ga Ge As Se Br Kr
    5   Rb Sr Y   Zr Nb Mo Tc Ru Rh Pd Ag Cd In Sn Sb Te I  Xe
    6   Cs Be La- Hf Ta W  Re Os Ir Pt Au Hg Tl Pd Bi Po At Rn
    7   Fr Ra Ac- Rf Db Sg Bh Hs Mt Ds Rg Cn Nh Fl Mc Lv Ts Og

                 -Ce Pr Nd Pm Sm Eu Gd Tb Dy Ho Er Tm Yb Lu
                 -Th Pa U  Np Pu Am Cm Bk Cf Es Fm Md No Lr
        """)

def getInfo(of,via="symbol"):
    data = pd.read_csv("https://raw.githubusercontent.com/Sahil-Rajwar-2004/Datasets/master/elements.csv")
    if via == "symbol":
        position = data.index[data["Symbol"] == of].tolist()[0]
        return data.iloc[position]
    elif via == "number":
        return data.iloc[of-1]
    elif via == "name":
        position = data.index[data["Element"].str.lower() == of.lower()].tolist()[0]
        return data.iloc[position]
    else:
        raise ValueError(f"invalid argument")
