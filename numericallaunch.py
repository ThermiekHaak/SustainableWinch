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


if __name__ == "__main__":
    W = 826* 9.81
    V = 110/3.6
    glideratio = 42
    wl = 1000
    alt = 510
    cut_off = 80

    x_max = round(wl - alt/np.tan(8/18 * np.pi) + 1)
    x = np.arange(0, x_max, .1)
    y = path(x, wl, alt, cut_off= cut_off)
    g = gamma(x, wl, alt, cut_off)
    g_prime = gamma_prime(x, wl, alt, cut_off)
    B = beta(x, y, wl)
    Fc = Fc(W, V, glideratio, g, g_prime, B)
    #plt.plot(x, path(x, 1500, 500, 80))
    plus = g + B
    dis = (plus - np.arctan(glideratio))%np.pi
    # plt.plot(x, B , color = 'r')
    # plt.plot(x, g+B - np.arctan(glideratio), color = 'purple')
    # plt.plot(x, g, color = 'pink')
    # plt.plot(dis, B, color = 'b')

    plt.plot(x, Fc, color = 'r')
    plt.show()





