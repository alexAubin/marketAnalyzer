from matplotlib import pyplot as plotting
import numpy as math

plotting.clf()
plotting.hold(1)

x = math.linspace(0, 30, 100)
y = math.sin(x) * 0.5
plotting.plot(x, y, '--k')


x = math.linspace(0, 30, 30)
y = math.sin(x/6*math.pi)
error = math.random.normal(0.1, 0.02, size=y.shape) +.1
y += math.random.normal(0, 0.1, size=y.shape)

plotting.plot(x, y, 'k', color='#CC4F1B')
plotting.fill_between(x, y-error, y+error,
    alpha=0.5, edgecolor='#CC4F1B', facecolor='#FF9848')

y = math.cos(x/6*math.pi)    
error = math.random.rand(len(y)) * 0.5
y += math.random.normal(0, 0.1, size=y.shape)
plotting.plot(x, y, 'k', color='#1B2ACC')
plotting.fill_between(x, y-error, y+error,
    alpha=0.2, edgecolor='#1B2ACC', facecolor='#089FFF',
    linewidth=4, linestyle='dashdot', antialiased=True)



y = math.cos(x/6*math.pi)  + math.sin(x/3*math.pi)  
error = math.random.rand(len(y)) * 0.5
y += math.random.normal(0, 0.1, size=y.shape)
plotting.plot(x, y, 'k', color='#3F7F4C')
plotting.fill_between(x, y-error, y+error,
    alpha=1, edgecolor='#3F7F4C', facecolor='#7EFF99',
    linewidth=0)



plotting.show()
