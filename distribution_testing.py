from fitter import Fitter
import pandas as pd
import os
import numpy as np


# file = pd.ExcelFile("Teams/Cardinals/WRs/DeAndre Hopkins.xlsx")
# df = file.parse("Game logs")
# yards = df["YDS"]
# print(yards.value_counts(dropna=False))

# f = Fitter(yards)
# f.fit()
# print(f.get_best())

L = np.array([1, 3, 4, 7, 9])
print(1/4 * np.sum((L-np.mean(L))**2))
print(np.std(L))