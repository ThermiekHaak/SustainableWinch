import scipy.integrate
import numpy as np
import matplotlib.pyplot as plt

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

def path_xprime(x: float, wl: float, alt: float, cut_off: float) -> float:
    "slope : path derivative with respect to horizontal component x"
    period = 2 * (wl - alt/np.tan(cut_off/180 * np.pi))
    A = alt / 2
    B = 2 * np.pi /period
    C = - period/4
    return A * B * np.cos(B * (x + C))


def path_doubleprime(x: float, wl: float, alt: float, cut_off: float) -> float:
    """change in slope: second derivative of the path with respect to horizontal component x """
    period = 2 * (wl - alt/np.tan(cut_off/180 * np.pi))
    A = alt / 2
    B = 2 * np.pi /period
    C = - period/4
    return -A * B**2 * np.sin(B * (x + C))

def gamma(x: float, wl: float, alt: float, cut_off: float) -> float:
    """pitch angle is between 0 and pi/2 thus pitch = arctan(slope)"""
    return np.arctan(path_xprime(x, wl, alt, cut_off))

def gamma_prime(x: float, x_prime: float, wl: float, alt: float, cut_off: float) -> float:
    """pitchrate : first derrivative of the pitch with respect to time """
    f = path_doubleprime(x, wl, alt, cut_off)
    return x_prime/(path_xprime(x, wl, alt, cut_off)**2 + 1) * f

def beta(x: float, y:float,  wl: float) -> float:
    """"Angle between horizon and winch cable
    Assumes cable without mass (no sack) """
    distance_to_winch = wl - x
    return np.arctan2(y,distance_to_winch)

def Fc(W, V, glideratio, gamma, gamma_prime, Beta): # discontinous at x = π n + arctan(glideratio), n element Z
    """Cable Force, computed with the assumption that the Velocity change is zero
    Glider flies at max L/D to minimise required cable force / max climb angle"""
    m = W/9.81
    A = (W * np.sin(gamma) * glideratio )/(np.cos(Beta + gamma)*glideratio - np.sin(Beta + gamma))
    B = ( m * V * np.sin(gamma_prime))/(np.cos(Beta + gamma)*glideratio - np.sin(Beta + gamma))
    Bgp = np.sin(gamma_prime)
    C = (W * np.cos(gamma))/(np.cos(Beta + gamma)*glideratio - np.sin(Beta + gamma))
    Fc = (W * np.sin(gamma) * glideratio + m * V * np.sin(gamma_prime) + W * np.cos(gamma))/(np.cos(Beta + gamma)*glideratio - np.sin(Beta + gamma))
    return Fc

def Rprime(x: float,  wl: float, alt: float, cut_off: float, V: float):
    g = gamma(x, wl, alt, cut_off)
    x_prime = np.cos(g) * V
    y = path(x, wl, alt, cut_off)
    y_prime = path_xprime(x, wl, alt, cut_off) * x_prime
    return (-(wl-x)*x_prime + y * y_prime)/np.sqrt((wl- x)**2 + y**2)

def CableVelocity(x: float,  wl: float, alt: float, cut_off: float, V: float):
    return - Rprime(x, wl, alt, cut_off, V)


def time(x: np.ndarray, wl: float, alt: float, cut_off: float, V: float):
    t = [0]
    def pathlenght(x, wl, alt, cut_off):
        y_prime = path_xprime(x, wl, alt, cut_off)
        return np.sqrt(1 + y_prime)
    for i in x[1:]:
        l = scipy.integrate.quad(pathlenght, 0, i, args=(wl, alt, cut_off))[0]
        ti = l/V
        t.append(ti)
    return np.array(t)





if __name__ == "__main__":
    W = 600* 9.81
    V = 110/3.6
    glideratio = 42
    wl = 1000
    alt = 400
    cut_off = 80

    x_max = round(wl - alt/np.tan(8/18 * np.pi) + 1)
    x = np.arange(0, x_max, .1)
    y = path(x, wl, alt, cut_off= cut_off)
    R = np.sqrt((wl -x)**2 + y**2)
    t = time(x, wl, alt, cut_off, V)

    g = gamma(x, wl, alt, cut_off)
    g_prime = gamma_prime(x, np.cos(g)*V, wl, alt, cut_off)
    B = beta(x, y, wl)

    Fc = Fc(W, V, glideratio, g, g_prime, B)
    cable_vel = CableVelocity(x, wl, alt, cut_off, V)


    plt.plot(t, cable_vel)
    plt.plot(t, Fc)
    plt.plot(t, cable_vel*Fc, color = 'black')
    plt.show()










