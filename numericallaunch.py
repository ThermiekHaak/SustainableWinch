import numpy
import scipy.integrate
from  scipy import optimize
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm





def path(x: float, wl: float, alt: float, cut_off: float) -> float:
    """Assumed sinusoid path of glider
    f(x) = A sin (B (x+C)) + D
     x: horizontal pos in [m]
     wl: winch field lenght
     alt: glider altitude at decouple
     cut_off: max angle between ground and cable
     """
    period = 2 * (wl - alt/np.tan(cut_off/180 * np.pi))
    A = alt / 2
    B = 2 * np.pi /period
    C = - period/4
    D = alt/2
    return A * np.sin(B * (x + C)) + D

def path_prime(x: float, wl: float, alt: float, cut_off: float) -> float:
    period = 2 * (wl - alt/np.tan(cut_off/180 * np.pi))
    A = alt / 2
    B = 2 * np.pi /period
    C = - period/4
    return A * B * np.cos(B * (x + C))

def path_doubleprime(x: float, wl: float, alt: float, cut_off: float) -> float:
    period = 2 * (wl - alt/np.tan(cut_off/180 * np.pi))
    A = alt / 2
    B = 2 * np.pi /period
    C = - period/4
    return -A * B**2 * np.sin(B * (x + C))

def gamma(x: float, wl: float, alt: float, cut_off: float) -> float:
    # print(f'arctan gamma {np.arctan(path_prime(x, wl, alt, cut_off))}')
    return np.arctan(path_prime(x, wl, alt, cut_off))

def gamma_prime(x: float, wl: float, alt: float, cut_off: float) -> float:
    return 1/(path_prime(x, wl, alt, cut_off)**2 + 1)

def beta(x: float, y:float,  wl: float) -> float:
    distance_to_winch = wl - x
    # print(f'arctan beta {np.arctan(y/distance_to_winch)}')
    return np.arctan2(y,distance_to_winch)

def Fc(W, V, glideratio, gamma, gamma_prime, Beta): # discontinous at x = π n + arctan(glideratio), n element Z
    m = W/9.81
    return (m * V * gamma_prime + W * np.cos(gamma))/glideratio/(np.cos(gamma + Beta) - np.sin(gamma + Beta)/glideratio)

def Rprime(x: float, wl: float, alt: float, cut_off: float, V: float):
    g = path(x, wl, alt, cut_off)
    g_prime = path_prime(x, wl, alt, cut_off)
    x_prime = np.cos(g) * V
    return (g_prime * x + g * x_prime + (wl - x) * x_prime)/np.sqrt((g**2 + (wl - x)**2))

def newCableVelocity(x,y,t,wl):
    cablelenght = np.sqrt((x - wl) ** 2 + y ** 2)
    delta = cablelenght[:-1] - cablelenght[1:]
    deltat = t[1:] - t[:-1]
    V = np.divide(delta,deltat)
    V2 = list(V)
    V2.append(V[-1])
    # V2.insert(0,V[0])
    return V2

def time(x: np.ndarray, wl: float, alt: float, cut_off: float, V: float):
    t = [0]
    def pathlenght(x, wl, alt, cut_off):
        y_prime = path_prime(x, wl, alt, cut_off)
        return np.sqrt(1 + y_prime)
    for i in x[1:]:
        l = scipy.integrate.quad(pathlenght, 0, i, args=(wl, alt, cut_off))[0]
        ti = l/V
        t.append(ti)
    return np.array(t)





if __name__ == "__main__":
    W = 826* 9.81
    V = 110/3.6
    glideratio = 42
    wl = 1000
    alt = 450
    cut_off = 80

    x_max = round(wl - alt/np.tan(8/18 * np.pi) + 1)
    x = np.arange(0, x_max, .1)
    y = path(x, wl, alt, cut_off= cut_off)
    t = time(x, wl, alt, cut_off, V)
    g = gamma(x, wl, alt, cut_off)
    g_prime = gamma_prime(x, wl, alt, cut_off)
    B = beta(x, y, wl)
    Fc = Fc(W, V, glideratio, g, g_prime, B)
    cable_vel = newCableVelocity(x,y,t,wl)
    #cable_vel = Rprime(x, wl, alt, cut_off, V)

    # plt.plot(x,y , color ='r')
    plt.plot(t,y, color ='blue')
    plt.plot(t,x, color = 'pink')
    plt.plot(t,Fc, color ='green')
    plt.plot(t,cable_vel, color = 'purple')
    # plt.plot(cable_vel*Fc, t, color = 'black')
    plt.show()










