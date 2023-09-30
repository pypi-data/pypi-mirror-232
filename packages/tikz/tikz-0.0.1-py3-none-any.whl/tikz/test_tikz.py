import numpy as np
import tikz

K = 1000
t = np.linspace(0, 1, K)
y = 3*np.sin(2*np.pi*t) + 0.5*np.random.randn(K)

fig = tikz.plot()
fig.add(t, y)
fig.xlabel = "Time, $t$ [s]"
fig.ylabel = "Amplitude"
fig.render("test")
