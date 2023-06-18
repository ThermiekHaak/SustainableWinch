import scipy.integrate
import numpy as np
import matplotlib.pyplot as plt
import warnings
# FLying Phase ____________________________________________________________________________________
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

def Fc(x: float, wl: float, alt: float, cut_off: float, W: float, V: float, glideratio:float):
    # discontinous at x = π n + arctan(glideratio), n element Z
    """Cable Force, computed with the assumption that the Velocity change is zero
    Glider flies at max L/D to minimise required cable force / max climb angle"""
    y = path(x, wl, alt, cut_off)
    g = gamma(x, wl, alt, cut_off)
    x_prime = V * np.cos(g)
    g_prime = gamma_prime(x, x_prime, wl, alt, cut_off)
    B = beta(x,y,wl)
    m = W/9.81
    # A = (W * np.sin(g) * glideratio )/(np.cos(B + g)*glideratio - np.sin(B + g))
    #B = ( m * V * np.sin(g_prime))/(np.cos(B + g)*glideratio - np.sin(B + g))
    # Bgp = np.sin(g_prime)
    # C = (W * np.cos(g))/(np.cos(B + g)*glideratio - np.sin(B + g))
    Fc = (W * np.sin(g) * glideratio + m * V * np.sin(g_prime) + W * np.cos(g))/(np.cos(B + g)*glideratio - np.sin(B + g))
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

def launch_time(x: np.ndarray, wl: float, alt: float, cut_off: float, V: float):
    def pathlenght(x, wl, alt, cut_off):
        y_prime = path_xprime(x, wl, alt, cut_off)
        return np.sqrt(1 + y_prime)
    l = scipy.integrate.quad(pathlenght, 0, x, args=(wl, alt, cut_off))[0]
    return l/V


def Power_profile(wl:float, alt: float, cut_off: float, mass: float, glideratio: float, V: float, max_force):
    # ground roll
    lossfactor = 0.95
    Fc_roll = min(0.9 * max_force * 1000,5000)
    a = Fc_roll/mass * lossfactor
    if a/9.81 > 2:  # if launch is more than 2 g's
        a = 2 * 9.81
        Fc_roll = a * mass / lossfactor

    tend = V / a
    t_roll = np.linspace(0,tend,10)
    V_roll = a*t_roll
    P_roll = Fc_roll * V_roll
    P_maxroll = max(P_roll)
    Energy_roll = scipy.integrate.simpson(P_roll,t_roll)

    # airborne phase
    unfeasible = True
    while unfeasible:
        x_max = wl - alt / np.tan(cut_off / 180 * np.pi)  # horizontal distance traveled [m] before decoupling
        x = np.linspace(0, x_max, 1000)
        t_air = time(x, wl, alt, cut_off, V)
        t_max = launch_time(x_max, wl, alt, cut_off,V)  # Time [s] it takes to launch a glider
        V_c = CableVelocity(x, wl, alt, cut_off, V)  # Cable velocity [m/s]
        W = mass * 9.81
        F_c = Fc(x, wl, alt, cut_off, W, V, glideratio)
        F_cairborn_max = max(F_c)
        if F_cairborn_max < max_force * 1000:
            unfeasible = False
        else:
            alt -= 10
            warnings.warn(f'The desired altitude gain is unfeasible with the given field lenght and glider'
                          f'altitude gain is set to {alt}')


    P_l = V_c * F_c
    Pmax_launch = max(P_l)
    Energy_launch = scipy.integrate.simpson(P_l,t_air)

    Pmax = max(P_maxroll,Pmax_launch)
    if Fc_roll > F_cairborn_max:
        Vmaxf = V
    else:
        Vmaxf = V_c[np.where(F_c == F_cairborn_max)[0]][0]
    Fcmax = max(Fc_roll, F_cairborn_max)
    Vcmax = V
    t_total = tend + t_max
    P_average = (Energy_roll + Energy_launch)/(tend+t_max)
    dict = {'Force': Fcmax,
            'Vmaxforce': Vmaxf,
            'Vmax': Vcmax,
            'maxPower': Pmax,
            'avgPower': P_average,
            'time': t_total
            }
    return dict



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
    mass = W/9.81
    glideratio

    # g = gamma(x, wl, alt, cut_off)
    # g_prime = gamma_prime(x, np.cos(g)*V, wl, alt, cut_off)
    # B = beta(x, y, wl)
    Fc1 = Fc(x, wl, alt, cut_off, W, V, glideratio)
    cable_vel = CableVelocity(x, wl, alt, cut_off, V)
    plt.plot(t, cable_vel)
    plt.plot(t, Fc1)
    plt.plot(t, cable_vel*Fc1, color = 'black')
    plt.show()
    max_force = 10
    abc = Power_profile(wl, alt, cut_off, mass, glideratio, V, max_force)
    print(abc)










