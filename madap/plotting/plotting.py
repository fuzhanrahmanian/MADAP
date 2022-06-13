import matplotlib
import matplotlib.pyplot as plt
import matplotlib as mpl

mpl.rcParams.update(mpl.rcParamsDefault)
matplotlib.rc('font', size=20)
matplotlib.rc('axes', titlesize=20)
plt.style.use(['nature', 'science', 'no-latex'])
plt.rcParams['text.usetex'] = False
plt.rcParams['xtick.direction'] = 'in'
plt.rcParams['ytick.direction'] = 'in'