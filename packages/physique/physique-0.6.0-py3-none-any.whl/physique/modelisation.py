# David THERINCOURT - 2022
#
# The MIT License (MIT)
#
# Copyright (c) 2014-2019 Damien P. George
# Copyright (c) 2017 Paul Sokolovsky
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

"""
Module de modélisation de courbes pour la physique

Example
-------

from physique.modelisation import ajustement_lineaire

@author: David Thérincourt
"""

import numpy as np
from scipy.stats import linregress
from scipy.optimize import curve_fit
from physique.fonctions import *
from math import log10



def _pround(x, n):
    """ Convertit un flottant en une chaîne de caractères avec n chiffres significatifs. 
    """
    x = float(x)
    x0 = abs(x)
    
    if x0<0.01:
        ch = "{:." + str(n-1) + "e}"
        x_str = ch.format(x)
        
    if 0.01<=x0<1:
        p = int(log10(x0))
        x_str = str(round(x, n-1-p))
        t = x_str.split(".")
        t = t[1].split("0")
        nx = len(t[-1])
        if nx<n:
            x_str += "0"*(n-nx)
            
    if 1<=x0<10000:
        p = int(log10(x0))
        x_str = str(round(x, n-1-p))
        t = x_str.split(".")
        if len(t[0])>=n:
            x_str = x_str[:-2]
        nx = len(t[0]+t[1])
        if nx<n:
            x_str += "0"*(n-nx)
            
    elif 10000<=x0:
        ch = "{:." + str(n-1)+"e}"
        x_str = ch.format(x)
        
    return x_str


# Ajustement suivant une fonction linéaire
def ajustement_lineaire(x, y, a_p0=1, plot_ax=None, plot_xmin=None, plot_xmax=None, plot_nb_pts=100, return_line=False):
    """
    Modélisation d'une série de points (x,y) par une fonction linéaire du type :
    y = a*x

    Paramètres :
    x (liste ou tableau Numpy) : abscisses.
    y (liste ou tableau Numpy de même dimension que x) : ordonnées.
    
    Paramètres optionnels :
    a_p0         (1)     : valeur de a aidant à la convergence du modèle.
    plot_ax      (None)  : repère (axes) dans lequel tracer la courbe.
    plot_xmin    (None)  : abscisse minimale pour le tracé.
    plot_xmax    (None)  : abscisse maximale pour le tracé.
    plot_nb_pts  (100)   : nombre de points pour le tracé.
    return_line  (False) : renvoie en plus la courbe du modèle.

    Retourne :
    a (float)
    a (float), line (matplotlib.lines.Line2D) si return_line == True
    """
    
    
    
    (a), pcov = curve_fit(fct_lineaire, x, y, p0=[a_p0])
    
    if plot_ax != None :
        if plot_xmin != None:
            x_min = plot_xmin
        else:
            x_min = x[0]
        
        if plot_xmax != None:
            x_max = plot_xmax
        else:
            x_max = x[-1]    
        
        x_mod = np.linspace(x_min, x_max, plot_nb_pts)
        y_mod = a*x_mod
        
        n = 4
        str_modele = r"$y=a\cdot x$" + r"$\qquad$"
        str_params = "a=" + _pround(a[0],n)
        line = plot_ax.plot(x_mod, y_mod, label=str_modele+str_params)
        
        if return_line==True:
            return a[0], line[0]

    return a[0]



# Ajustement suivant une fonction affine
def ajustement_affine(x, y, plot_ax=None, plot_xmin=None, plot_xmax=None, plot_nb_pts=100, return_line=False):
    """
    Modélisation d'une fonction affine de la forme :
    
        y = a*x + b

    Paramètres :
        x (liste ou tableau Numpy) : abscisses.
        y (liste ou tableau Numpy de même dimension que x) : ordonnées.
    
    Paramètres optionnels :
        plot_ax      (None)  : repère pour tracer la courbe du modèle.
        plot_xmin    (None)  : abscisse minimale  de la courbe du modèle.
        plot_xmax    (None)  : abscisse maximale de la courbe du modèle.
        plot_nb_pts  (100)   : nombre de points de la courbe du modèle.
        return_line  (False) : renvoie en plus la courbe du modèle.

    Retourne un tuple (a, b) :
        a (float), b (float)
        a (float), b (float), line (matplotlib.lines.Line2D) [si return_line == True]
    """
    a, b, _, _, _ = linregress(x,y)
    
    if plot_ax != None :
        if plot_xmin != None:
            x_min = plot_xmin
        else:
            x_min = x[0]
        if plot_xmax != None:
            x_max = plot_xmax
        else:
            x_max = x[-1]
        x_mod = np.linspace(x_min, x_max, plot_nb_pts)
        y_mod = a*x_mod + b
        
        n = 4
        str_modele = r"$y=a\cdot x + b$" + "\n"
        str_params = "a=" + _pround(a,n) + "  b=" + _pround(b,n)
        line = plot_ax.plot(x_mod, y_mod, label=str_modele+str_params)

        if return_line==True:
            return a, b, line[0]
    
    return a, b


# Ajustement suivant une fonction parabolique
def ajustement_parabolique(x, y, plot_ax=None, plot_xmin=None, plot_xmax=None, plot_nb_pts=100, return_line=False):
    """
    Modélisation d'une fonction parabolique du type :
    
        y = a*x**2 + b*x + c

    Paramètres :
        x (liste ou tableau Numpy) : abscisses.
        y (liste ou tableau Numpy de même dimension que x) : ordonnées.
    
    Paramètres optionnels :
        plot_ax        (None)  : repère pour tracer la courbe du modèle.
        plot_xmin      (None)  : abscisse minimale  de la courbe du modèle.
        plot_xmax      (None)  : abscisse maximale de la courbe du modèle.
        plot_nb_pts    (100)   : nombre de points de la courbe du modèle.
        return_line    (False) : renvoie en plus la courbe du modèle.


    Retourne :
        a (float), b (float), c (float)
        a (float), b (float), c (float), line (matplotlib.lines.Line2D) [si return_line == True]
    """
    
    a, b, c = np.polyfit(x, y, 2)
    
    if plot_ax != None :
        if plot_xmin != None:
            x_min = plot_xmin
        else:
            x_min = x[0]
        if plot_xmax != None:
            x_max = plot_xmax
        else:
            x_max = x[-1]
            
        x_mod = np.linspace(x_min, x_max, plot_nb_pts)
        y_mod = a*x_mod**2 + b*x_mod + c
        
        n = 4
        str_modele = r"$y=a \cdot x^2 + b\cdot x + c$" + "\n"
        str_params = "a=" + _pround(a,n) + "  b=" + _pround(b,n) + "  c=" + _pround(c,n) 
        line = plot_ax.plot(x_mod, y_mod, label=str_modele+str_params)

        if return_line==True:
            return a, b, c, line[0]
    
    return a, b, c


# Ajustement suivant une fonction exponentielle croissante
def ajustement_exponentielle_croissante(x, y, A_p0=1, tau_p0=1, plot_ax=None, plot_xmin=None, plot_xmax=None, plot_nb_pts=100, return_line=False) :
    """
    Modélisation d'une série de points (x,y) par une fonction exponentielle croissante
    du type :
    
        y = A*(1-exp(-x/tau))

    Paramètres :
        x (liste ou tableau Numpy) : abscisses.
        y (liste ou tableau Numpy de même dimension que x) : ordonnées.

    Paramètres optionnels :
        A_p0         (1)     : valeur de la limite à l'infini aidant à la convergence du modèle.
        tau_p0       (1)     : valeur de la constante de temps aidant à la convergence du modèle.
        plot_ax      (None)  : repère pour tracer la courbe du modèle.
        plot_xmin    (None)  : abscisse minimale  de la courbe du modèle.
        plot_xmax    (None)  : abscisse maximale de la courbe du modèle.
        plot_nb_pts  (100)   : nombre de points de la courbe du modèle.
        return_line  (False) : renvoie en plus la courbe du modèle.

    Retourne :
        A (float), tau (float)
        A (float), tau (float), line (matplotlib.lines.Line2D) [si return_line == True]
    """
    (A,tau), pcov = curve_fit(fct_exponentielle_croissante, x, y, p0=[A_p0, tau_p0])

    if plot_ax != None :
        if plot_xmin != None:
            x_min = plot_xmin
        else:
            x_min = x[0]
        if plot_xmax != None:
            x_max = plot_xmax
        else:
            x_max = x[-1]
            
        x_mod = np.linspace(x_min, x_max, plot_nb_pts)
        y_mod = fct_exponentielle_croissante(x_mod, A, tau)
        
        n = 4
        str_modele = r"$y = A(1-e^{-\dfrac{x}{\tau}})$" + "\n"
        str_params = r"$A=$" + _pround(A,n) + r"  $\tau$=" + _pround(tau,n)
        line = plot_ax.plot(x_mod, y_mod, label=str_modele+str_params)


        if return_line==True:
            return A, tau , line[0]

    return A, tau

# Ajustement suivant une fonction exponentielle croissante avec décalage
def ajustement_exponentielle_croissante_x0(x, y, A_p0=1, tau_p0=1, x0_p0=0, plot_ax=None, plot_xmin=None, plot_xmax=None, plot_nb_pts=100, return_line=False) :
    """
    Modélisation d'une série de points (x,y) par une fonction exponentielle croissante
    décalée suivant l'abscisse du type :
    
        y = A*(1-exp(-(x-xo)/tau))

    Paramètres :
        x (liste ou tableau Numpy) : abscisses.
        y (liste ou tableau Numpy de même dimension que x) : ordonnées.

    Paramètres optionnels :
        A_p0         (1)     : valeur de la limite à l'infini aidant à la convergence du modèle.
        tau_p0       (1)     : valeur de la constante de temps aidant à la convergence du modèle.
        x0_p0        (0)     : valeur du retard aidant à la convergence du modèle.
        plot_ax      (None)  : repère pour tracer la courbe du modèle.
        plot_xmin    (None)  : abscisse minimale  de la courbe du modèle.
        plot_xmax    (None)  : abscisse maximale de la courbe du modèle.
        plot_nb_pts  (100)   : nombre de points de la courbe du modèle.
        return_line  (False) : renvoie en plus la courbe du modèle.

    Retourne :
        A (float), tau (float), x0 (float)
        A (float), tau (float), x0 (float), line (matplotlib.lines.Line2D) [si return_line == True]
    """
    (A,tau,x0), pcov = curve_fit(fct_exponentielle_croissante, x, y, p0=[A_p0, tau_p0, x0_p0])

    if plot_ax != None :
        if plot_xmin != None:
            x_min = plot_xmin
        else:
            x_min = x[0]
        if plot_xmax != None:
            x_max = plot_xmax
        else:
            x_max = x[-1]
            
        x_mod = np.linspace(x_min, x_max, plot_nb_pts)
        y_mod = fct_exponentielle_croissante(x_mod, A, tau, x0=x0)
        
        n = 4
        str_modele = r"$y = A(1-e^{-\dfrac{x-x_0}{\tau}})$" + "\n"
        str_params = r"$A=$" + _pround(A,n) + r"  $\tau$=" + _pround(tau,n) + r"  $x_0$=" + _pround(x0,n)
        line = plot_ax.plot(x_mod, y_mod, label=str_modele+str_params)


        if return_line==True:
            return A, tau, x0 , line[0]

    return A, tau, x0


# Ajustement suivant une fonction exponentielle décroissante
def ajustement_exponentielle_decroissante(x, y, A_p0=1, tau_p0=1, plot_ax=None, plot_xmin=None, plot_xmax=None, plot_nb_pts=100, return_line=False):
    """
    Modélisation d'une série de points (x,y) par une fonction exponentielle décroissante
    du type :
    
        y = A*exp(-x/tau)

    Paramètres :
        x (liste ou tableau Numpy) : abscisses.
        y (liste ou tableau Numpy de même dimension que x) : ordonnées.

    Paramètres optionnels :
        A_p0         (1)     : valeur de la limite à l'infini aidant à la convergence du modèle.
        tau_p0       (1)     : valeur de la constante de temps aidant à la convergence du modèle.
        x0_p0        (0)     : valeur du retard aidant à la convergence du modèle.
        plot_ax      (None)  : repère pour tracer la courbe du modèle.
        plot_xmin    (None)  : abscisse minimale  de la courbe du modèle.
        plot_xmax    (None)  : abscisse maximale de la courbe du modèle.
        plot_nb_pts  (100)   : nombre de points de la courbe du modèle.
        return_line  (False) : renvoie en plus la courbe du modèle.

    Retourne :
        A (float), tau (float),
        A (float), tau (float), line (matplotlib.lines.Line2D) [si return_line == True]
    """
    (A,tau), pcov = curve_fit(fct_exponentielle_decroissante, x, y, p0=[A_p0, tau_p0])

    if plot_ax != None :
        if plot_xmin != None:
            x_min = plot_xmin
        else:
            x_min = x[0]
        if plot_xmax != None:
            x_max = plot_xmax
        else:
            x_max = x[-1]
            
        x_mod = np.linspace(x_min, x_max, plot_nb_pts)
        y_mod = fct_exponentielle_decroissante(x_mod, A, tau)

        n = 4
        str_modele = r"$y = A \cdot e^{-\dfrac{x}{\tau}}$" + "\n"
        str_params = r"$A=$" + _pround(A,n) + r"  $\tau$=" + _pround(tau,n)
        line = plot_ax.plot(x_mod, y_mod, label=str_modele+str_params)
        

        if return_line==True:
            return A, tau , line[0]

    return A, tau


# Ajustement suivant une fonction exponentielle décroissante avec décalage
def ajustement_exponentielle_decroissante_x0(x, y, A_p0=1, tau_p0=1, x0_p0=1, plot_ax=None, plot_xmin=None, plot_xmax=None, plot_nb_pts=100, return_line=False) :
    """
    Modélisation d'une série de points (x,y) par une fonction exponentielle décroissante
    du type :
    
        y = A*exp(-(x-x0)/tau)

    Paramètres :
        x (liste ou tableau Numpy) : abscisses.
        y (liste ou tableau Numpy de même dimension que x) : ordonnées.

    Paramètres optionnels :
        A_p0         (1)     : valeur de la limite à l'infini aidant à la convergence du modèle.
        tau_p0       (1)     : valeur de la constante de temps aidant à la convergence du modèle.
        plot_ax      (None)  : repère pour tracer la courbe du modèle.
        plot_xmin    (None)  : abscisse minimale  de la courbe du modèle.
        plot_xmax    (None)  : abscisse maximale de la courbe du modèle.
        plot_nb_pts  (100)   : nombre de points de la courbe du modèle.
        return_line  (False) : renvoie en plus la courbe du modèle.

    Retourne :
        A (float), tau (float), x0 (float)
        A (float), tau (float), x0 (float), line (matplotlib.lines.Line2D) [si return_line == True]
    """
    (A,tau, x0), pcov = curve_fit(fct_exponentielle_decroissante, x, y, p0=[A_p0, tau_p0, x0_p0])

    if plot_ax != None :
        if plot_xmin != None:
            x_min = plot_xmin
        else:
            x_min = x[0]
        if plot_xmax != None:
            x_max = plot_xmax
        else:
            x_max = x[-1]
            
        x_mod = np.linspace(x_min, x_max, plot_nb_pts)
        y_mod = fct_exponentielle_decroissante(x_mod, A, tau, x0=x0)

        n = 4
        str_modele = r"$y = A \cdot e^{-\dfrac{x-x_0}{\tau}}$" + "\n"
        str_params = r"$A=$" + _pround(A,n) + r"  $\tau$=" + _pround(tau,n) + r"  $x_0$=" + _pround(x0,n)
        line = plot_ax.plot(x_mod, y_mod, label=str_modele+str_params)

        if return_line==True:
            return A, tau, x0, line[0]

    return A, tau, x0





#################################################################
#                                                               #
#                  Réponses fréquentielles                      #
#                                                               #
#################################################################


# Ajustement suivant une fonction de transmittance d'un système d'ordre 1 passe-bas
def ajustement_transmittance_ordre1_passe_bas(f, T, T0_p0=1, f0_p0=1, plot_ax=None, plot_fmin=None, plot_fmax=None, plot_xlog=True, plot_nb_pts=100, return_line=False):
    """
    Modélisation d'une série de points (f,T) par une fonction de transmittance
    d'un système d'ordre 1 passe-bas :
    
        T = T0/sqrt(1+(f/f0)**2)
    
    Paramètres :
        f (liste ou tableau Numpy) : fréquence.
        T (liste ou tableau Numpy de même dimension que f) : transmittance.

    Paramètres optionnels :
        T0_p0        (1)    : valeur de T0 aidant à la convergence du modèle.
        f0_p0        (1)    : valeur de f0 aidant à la convergence du modèle.
        plot_ax      (None) : repère pour tracer le modèle.
        plot_fmin    (None) : fréquence minimale  pour le tracé de modèle.
        plot_fmax    (None) : fréquence maximale pour le tracé de modèle.
        plot_xlog    (True) : fréquences sur une échelle logarithmique
        plot_nb_pts  (100)  : nombre de points.
        return_line  (False) : renvoie en plus la courbe du modèle.

    Retourne :
        T0 (float), f0 (float)
        T0 (float), f0 (float), line (matplotlib.lines.Line2D) [si return_line == True]
    """
    (T0, f0), pcov = curve_fit(transmittance_ordre1_passe_bas, f, T, p0=[T0_p0, f0_p0])
    
    if plot_fmin != None:
        f_min = fmin
    else:
        f_min = f[0]
        
    if plot_fmax != None:
        f_max = fmax
    else:
        f_max = f[-1]
        
    if (plot_ax != None):
        if plot_xlog==True:
            f_mod = np.logspace(np.log10(f_min), np.log10(f_max), plot_nb_pts)
        else:
            f_mod = np.linspace(f_min, f_max, plot_nb_pts)
    
        T_mod = transmittance_ordre1_passe_bas(f_mod, T0, f0)

        n = 4
        str_modele = r"$T = \dfrac{T_0}{\sqrt{1+(\dfrac{f}{f_0})^2}}$" + "\n"
        str_params = r"$T_0=$" + _pround(T0,n) + r"  $f_0$=" + _pround(f0,n)
        line = plot_ax.plot(f_mod, T_mod, label=str_modele+str_params)


        if return_line==True:
            return T0, f0, line[0]
        
    return T0, f0


# Ajustement suivant le gain d'un système d'ordre 1 passe-bas
def ajustement_gain_ordre1_passe_bas(f, G, G0_p0=0, f0_p0=1, plot_ax=None, plot_fmin=None, plot_fmax=None, plot_xlog=True, plot_nb_pts=100, return_line=False):
    """
    Modélisation d'une série de points (f,G) par une fonction de gain
    d'un système d'ordre 1 passe-bas :
    
        G = G0 - 20*log(sqrt(1+(f/f0)**2))
    

    Paramètres :
        f (liste ou tableau Numpy) : fréquence.
        T (liste ou tableau Numpy de même dimension que f) : transmittance.

    Paramètres optionnels :
        T0_p0        (1)    : valeur de T0 aidant à la convergence du modèle.
        f0_p0        (1)    : valeur de f0 aidant à la convergence du modèle.
        plot_ax      (None) : repère pour tracer le modèle.
        plot_fmin    (None) : fréquence minimale  pour le tracé de modèle.
        plot_fmax    (None) : fréquence maximale pour le tracé de modèle.
        plot_xlog    (True) : fréquences sur une échelle logarithmique
        plot_nb_pts  (100)  : nombre de points.
        return_line  (False) : renvoie en plus la courbe du modèle.
    
    Retourne :
        G0 (float), f0 (float)
        G0 (float), f0 (float), line (matplotlib.lines.Line2D) [si return_line == True]
    """

    (G0, f0), pcov = curve_fit(gain_ordre1_passe_bas, f, G, p0=[G0_p0, f0_p0])
    
    if plot_fmin != None:
        f_min = fmin
    else:
        f_min = f[0]
        
    if plot_fmax != None:
        f_max = fmax
    else:
        f_max = f[-1]
        
    if (plot_ax != None):
        if plot_xlog==True:
            f_mod = np.logspace(np.log10(f_min), np.log10(f_max), plot_nb_pts)
        else:
            f_mod = np.linspace(f_min, f_max, plot_nb_pts)
    
        G_mod = gain_ordre1_passe_bas(f_mod, G0, f0)

        n = 4
        str_modele = r"$G = G_0 - 20\cdot\log(\sqrt{1+(\dfrac{f}{f_0})^2})$" + "\n"
        str_params = r"$G_0=$" + _pround(G0,n) + r"  $f_0$=" + _pround(f0,n)
        line = plot_ax.plot(f_mod, G_mod, label=str_modele+str_params)

        if return_line==True:
            return G0, f0, line[0]
               
    return G0, f0




# Ajustement suivant le déphasage d'un système d'ordre 1 passe-bas
def ajustement_dephasage_ordre1_passe_bas(f, phi, f0_p0=1, plot_ax=None, plot_fmin=None, plot_fmax=None, plot_xlog=True, plot_nb_pts=100, return_line=False):
    """
    Modélisation d'une série de points (f,T) par une fonction de transmittance
    d'un système d'ordre 1 passe-bas :
    
        phi = - arctan(f/f0)

    Paramètres :
        f (liste ou tableau Numpy) : fréquence.
        T (liste ou tableau Numpy de même dimension que f) : transmittance.

    Paramètres optionnels :
        f0_p0        (1)     : valeur de f0 aidant à la convergence du modèle.
        plot_ax      (None)  : repère pour tracer le modèle.
        plot_fmin    (None)  : fréquence minimale  pour le tracé de modèle.
        plot_fmax    (None)  : fréquence maximale pour le tracé de modèle.
        plot_xlog    (True)  : fréquences sur une échelle logarithmique
        plot_nb_pts  (100)   : nombre de points.
        return_line  (False) : renvoie en plus la courbe du modèle.

    Retourne un tuple (T0, f0) :
        f0 (float) : fréquence propre
    """
    (f0), pcov = curve_fit(dephasage_ordre1_passe_bas, f, phi, p0=[f0_p0])
    
    if plot_fmin != None:
        f_min = fmin
    else:
        f_min = f[0]
        
    if plot_fmax != None:
        f_max = fmax
    else:
        f_max = f[-1]
        
    if (plot_ax != None):
        if plot_xlog==True:
            f_mod = np.logspace(np.log10(f_min), np.log10(f_max), plot_nb_pts)
        else:
            f_mod = np.linspace(f_min, f_max, plot_nb_pts)
    
        phi_mod = dephasage_ordre1_passe_bas(f_mod, f0)

        n = 4
        str_modele = r"$\varphi = -\arctan(\dfrac{f}{f_0})$" + "\n"
        str_params = r"$f_0$=" + _pround(f0[0],n)
        line = plot_ax.plot(f_mod, phi_mod, label=str_modele+str_params)

        if return_line==True:
            return f0[0], line[0]
               
    return f0[0]


######################################
#      Ordre 1 - Passe haut          #
######################################

def ajustement_transmittance_ordre1_passe_haut(f, T, T0_p0=1, f0_p0=1, plot_ax=None, plot_fmin=None, plot_fmax=None, plot_xlog=True, plot_nb_pts=100, return_line=False) :
    """
    Modélisation d'une série de points (x,y) par une fonction de transmittance
    d'un système d'ordre 1 passe-bas :
    
        T = T0*(f/f0)/sqrt(1+(f/f0)**2)

    Paramètres :
        f (liste ou tableau Numpy) : fréquence.
        T (liste ou tableau Numpy de même dimension que x) : transmittance.

    Paramètres optionnels :
        T0_p0        (1)     : valeur de T0 aidant à la convergence du modèle.
        f0_p0        (1)     : valeur de f0 aidant à la convergence du modèle.
        plot_ax      (None)  : repère pour tracer le modèle.
        fmin         (None)  : fréquence minimale  pour le tracé de modèle.
        fmax         (None)  : fréquence maximale pour le tracé de modèle.
        xlog         (True)  : fréquences sur une échelle logarithmique
        plot_nb_pts  (100)   : nombre de points.
        return_line  (False) : renvoie en plus la courbe du modèle.

    Retourne :
        T0 (float), f0 (float)
        T0 (float), f0 (float), line (matplotlib.lines.Line2D) [si return_line == True]
    """
    (T0, f0), pcov = curve_fit(transmittance_ordre1_passe_haut, f, T, p0=[T0_p0, f0_p0])

    if plot_fmin != None:
        f_min = fmin
    else:
        f_min = f[0]
        
    if plot_fmax != None:
        f_max = fmax
    else:
        f_max = f[-1]
        
    if (plot_ax != None):
        if plot_xlog==True:
            f_mod = np.logspace(np.log10(f_min), np.log10(f_max), plot_nb_pts)
        else:
            f_mod = np.linspace(f_min, f_max, plot_nb_pts)
    
        T_mod = transmittance_ordre1_passe_haut(f_mod, T0, f0)

        n = 4
        str_modele = r"$T = \dfrac{T_0\cdot\dfrac{f}{f_0}}{\sqrt{1+(\dfrac{f}{f_0})^2}}$" + "\n"
        str_params = r"$T_0=$" + _pround(T0,n) + r"  $f_0$=" + _pround(f0,n)
        line = plot_ax.plot(f_mod, T_mod, label=str_modele+str_params)

        if return_line==True:
            return T0, f0, line[0]

    return T0, f0


def ajustement_gain_ordre1_passe_haut(f, G, G0_p0=0, f0_p0=1, plot_ax=None, plot_fmin=None, plot_fmax=None, plot_xlog=True, plot_nb_pts=100, return_line=False):
    """
    Modélisation d'une série de points (f,G) par une fonction de gain
    d'un système d'ordre 1 passe-bas :
    
        G = G0 - 20*log((f/f0)/(sqrt(1+(f/f0)**2))
    

    Paramètres :
        f (liste ou tableau Numpy) : fréquence.
        T (liste ou tableau Numpy de même dimension que f) : transmittance.

    Paramètres optionnels :
        T0_p0        (1)     : valeur de T0 aidant à la convergence du modèle.
        f0_p0        (1)     : valeur de f0 aidant à la convergence du modèle.
        plot_ax      (None)  : repère pour tracer le modèle.
        plot_fmin    (None)  : fréquence minimale  pour le tracé de modèle.
        plot_fmax    (None)  : fréquence maximale pour le tracé de modèle.
        plot_xlog    (True)  : fréquences sur une échelle logarithmique
        plot_nb_pts  (100)   : nombre de points.
        return_line  (False) : renvoie en plus la courbe du modèle.
    
    Retourne :
        G0 (float), f0 (float)
        G0 (float), f0 (float), line (matplotlib.lines.Line2D) [si return_line == True]
    """

    (G0, f0), pcov = curve_fit(gain_ordre1_passe_haut, f, G, p0=[G0_p0, f0_p0])
    
    if plot_fmin != None:
        f_min = fmin
    else:
        f_min = f[0]
        
    if plot_fmax != None:
        f_max = fmax
    else:
        f_max = f[-1]
        
    if (plot_ax != None):
        if plot_xlog==True:
            f_mod = np.logspace(np.log10(f_min), np.log10(f_max), plot_nb_pts)
        else:
            f_mod = np.linspace(f_min, f_max, plot_nb_pts)
    
        G_mod = gain_ordre1_passe_haut(f_mod, G0, f0)

        n = 4
        str_modele = r"$G = G_0 - 20\cdot\log(\dfrac{\dfrac{f}{f_0}}{\sqrt{1+(\dfrac{f}{f_0})^2}})$" + "\n"
        str_params = r"$G_0=$" + _pround(G0,n) + r"  $f_0$=" + _pround(f0,n)
        line = plot_ax.plot(f_mod, G_mod, label=str_modele+str_params)

        if return_line==True:
            return G0, f0, line[0]
               
    return G0, f0




# Ajustement suivant le déphasage d'un système d'ordre 1 passe-bas
def ajustement_dephasage_ordre1_passe_haut(f, phi, f0_p0=1, plot_ax=None, plot_fmin=None, plot_fmax=None, plot_xlog=True, plot_nb_pts=100, return_line=False):
    """
    Modélisation d'une série de points (f,T) par une fonction de transmittance
    d'un système d'ordre 1 passe-bas :
    
        phi = 90 - arctan(f/f0)

    Paramètres :
        f (liste ou tableau Numpy) : fréquence.
        T (liste ou tableau Numpy de même dimension que f) : transmittance.

    Paramètres optionnels :
        f0_p0        (1)    : valeur de f0 aidant à la convergence du modèle.
        plot_ax    (None) : repère pour tracer le modèle.
        plot_fmin    (None) : fréquence minimale  pour le tracé de modèle.
        plot_fmax    (None) : fréquence maximale pour le tracé de modèle.
        plot_xlog    (True) : fréquences sur une échelle logarithmique
        plot_nb_pts  (100)  : nombre de points.
        return_line  (False) : renvoie en plus la courbe du modèle.

    Retourne un tuple (T0, f0) :
        f0 (float) : fréquence propre
    """
    (f0), pcov = curve_fit(dephasage_ordre1_passe_haut, f, phi, p0=[f0_p0])
    
    if plot_fmin != None:
        f_min = fmin
    else:
        f_min = f[0]
        
    if plot_fmax != None:
        f_max = fmax
    else:
        f_max = f[-1]
        
    if (plot_ax != None):
        if plot_xlog==True:
            f_mod = np.logspace(np.log10(f_min), np.log10(f_max), plot_nb_pts)
        else:
            f_mod = np.linspace(f_min, f_max, plot_nb_pts)
    
        phi_mod = dephasage_ordre1_passe_haut(f_mod, f0)

        n = 4
        str_modele = r"$\varphi = 90-\arctan(\dfrac{f}{f_0})$" + "\n"
        str_params = r"$f_0$=" + _pround(f0[0],n)
        line = plot_ax.plot(f_mod, phi_mod, label=str_modele+str_params)

        if return_line==True:
            return f0[0], line[0]
               
    return f0[0]



######################################
#      Ordre 2 - Passe bas           #
######################################

# Ajustement suivante une fonction de transmittance d'un système d'ordre 2 passe-bas
def ajustement_transmittance_ordre2_passe_bas(f, T, T0_p0=1, f0_p0=1, m_p0=1, plot_ax=None, plot_fmin=None, plot_fmax=None, plot_xlog=True, plot_nb_pts=100, return_line=False) :
    """
    Modélisation d'une série de points (f,T) par une fonction de transmittance
    d'un système d'ordre 2 passe-bas :
    
        T = T0/np.sqrt((1-(f/f0)**2)**2+(2*m*f/f0)**2)

    Paramètres :
        f (liste ou tableau Numpy) : fréquence.
        T (liste ou tableau Numpy de même dimension que x) : transmittance.

    Paramètres optionnels :
        T0_p0 (1 par défaut) : valeur de T0 aidant à la convergence du modèle.
        f0_p0 (1 par défaut) : valeur de f0 aidant à la convergence du modèle.
        m_p0 (1 par défaut)  : valeur de m  aidant à la convergence du modèle.
        plot_ax    (None) : repère pour tracer le modèle.
        plot_fmin    (None) : fréquence minimale  pour le tracé de modèle.
        plot_fmax    (None) : fréquence maximale pour le tracé de modèle.
        plot_xlog    (True) : fréquences sur une échelle logarithmique
        plot_nb_pts  (100)  : nombre de points.
        return_line  (False) : renvoie en plus la courbe du modèle.

    Retourne :
        T0 (float), f0 (float), m (float)
        T0 (float), f0 (float), m (float), line (matplotlib.lines.Line2D) [si return_line == True]
    """
    (T0, f0, m), pcov = curve_fit(transmittance_ordre2_passe_bas, f, T, p0=[T0_p0, f0_p0, m_p0])

    if plot_fmin != None:
        f_min = fmin
    else:
        f_min = f[0]
        
    if plot_fmax != None:
        f_max = fmax
    else:
        f_max = f[-1]
        
    if (plot_ax != None):
        if plot_xlog==True:
            f_mod = np.logspace(np.log10(f_min), np.log10(f_max), plot_nb_pts)
        else:
            f_mod = np.linspace(f_min, f_max, plot_nb_pts)
    
        T_mod = transmittance_ordre2_passe_bas(f_mod, T0, f0, m)

        n = 4
        str_modele = r"$T = \dfrac{T_0\cdot\dfrac{f}{f_0}}{\sqrt{1+(\dfrac{f}{f_0})^2}}$" + "\n"
        str_params = r"$T_0=$" + _pround(T0,n) + r"  $f_0$=" + _pround(f0,n) + r"  $m$=" + _pround(m,n)
        line = plot_ax.plot(f_mod, T_mod, label=str_modele+str_params)

        if return_line==True:
            return T0, f0, m, line[0]

    return T0, f0, m


######################################
#      Ordre 2 - Passe haut          #
######################################


# Ajustement suivante une fonction de transmittance d'un système d'ordre 2 passe-haut
def ajustement_transmittance_ordre2_passe_haut(f, T, T0_p0=1, f0_p0=1, m_p0=1, plot_ax=None, plot_fmin=None, plot_fmax=None, plot_xlog=True, plot_nb_pts=100, return_line=False) :
    """
    Modélisation d'une série de points (f,T) par une fonction de transmittance
    d'un système d'ordre 2 passe-haut : T = -T0*(f/f0)**2/np.sqrt((1-(f/f0)**2)**2+(2*m*f/f0)**2)

    Paramètres :
        f (liste ou tableau Numpy) : fréquence.
        T (liste ou tableau Numpy de même dimension que x) : transmittance.

    Paramètres optionnels :
        T0_p0        (1)    : valeur de T0 aidant à la convergence du modèle.
        f0_p0        (1)    : valeur de f0 aidant à la convergence du modèle.
        m_p0         (1)    : valeur de m  aidant à la convergence du modèle.
        plot_ax      (None) : repère pour tracer le modèle.
        plot_fmin    (None) : fréquence minimale  pour le tracé de modèle.
        plot_fmax    (None) : fréquence maximale pour le tracé de modèle.
        plot_xlog    (True) : fréquences sur une échelle logarithmique
        plot_nb_pts  (100)  : nombre de points.
        return_line  (False) : renvoie en plus la courbe du modèle.

    Retourne :
        T0 (float), f0 (float), m (float)
        T0 (float), f0 (float), m (float), line (matplotlib.lines.Line2D) [si return_line == True]
    """
    (T0, f0, m), pcov = curve_fit(transmittance_ordre2_passe_haut, f, T, p0=[T0_p0, f0_p0, m_p0])

    if plot_fmin != None:
        f_min = fmin
    else:
        f_min = f[0]
        
    if plot_fmax != None:
        f_max = fmax
    else:
        f_max = f[-1]
        
    if (plot_ax != None):
        if plot_xlog==True:
            f_mod = np.logspace(np.log10(f_min), np.log10(f_max), plot_nb_pts)
        else:
            f_mod = np.linspace(f_min, f_max, plot_nb_pts)
    
        T_mod = transmittance_ordre2_passe_haut(f_mod, T0, f0, m)
        
        n = 4
        str_modele = r"$T = \dfrac{T_0\cdot\dfrac{f}{f_0}}{\sqrt{1+(\dfrac{f}{f_0})^2}}$" + "\n"
        str_params = r"$T_0=$" + _pround(T0,n) + r"  $f_0$=" + _pround(f0,n) + r"  $m$=" + _pround(m,n)
        line = plot_ax.plot(f_mod, T_mod, label=str_modele+str_params)

        if return_line==True:
            return T0, f0, m, line[0]
    
    return T0, f0, m


######################################
#      Ordre 2 - Passe bande         #
######################################

def ajustement_transmittance_ordre2_passe_bande(f, T, T0_p0=1, f0_p0=1, m_p0=1, plot_ax=None, plot_fmin=None, plot_fmax=None, plot_xlog=True, plot_nb_pts=100, return_line=False) :
    """
    Modélisation d'une série de points (f,T) par une fonction de transmittance
    d'un système d'ordre 2 passe-bande :
    T = T0*2*m*(f/f0)/np.sqrt((1-(f/f0)**2)**2+(2*m*f/f0)**2)

    Paramètres :
        f (liste ou tableau Numpy) : fréquence.
        T (liste ou tableau Numpy de même dimension que x) : transmittance.

    Paramètres optionnels :
        T0_p0         (1)    : valeur de T0 aidant à la convergence du modèle.
        f0_p0         (1)    : valeur de f0 aidant à la convergence du modèle.
        m_p0          (1)    : valeur de m  aidant à la convergence du modèle.
        plot_ax      (None)  : repère pour tracer le modèle.
        plot_fmin    (None)  : fréquence minimale  pour le tracé de modèle.
        plot_fmax    (None)  : fréquence maximale pour le tracé de modèle.
        plot_xlog    (True)  : fréquences sur une échelle logarithmique
        plot_nb_pts  (100)   : nombre de points.
        return_line  (False) : renvoie en plus la courbe du modèle.

    Retourne :
        T0 (float), f0 (float), m (float)
        T0 (float), f0 (float), m (float), line (matplotlib.lines.Line2D) [si return_line == True]
    """
    (T0, f0, m), pcov = curve_fit(transmittance_ordre2_passe_bande, f, T, p0=[T0_p0, f0_p0, m_p0])

    if plot_fmin != None:
        f_min = fmin
    else:
        f_min = f[0]
        
    if plot_fmax != None:
        f_max = fmax
    else:
        f_max = f[-1]
        
    if (plot_ax != None):
        if plot_xlog==True:
            f_mod = np.logspace(np.log10(f_min), np.log10(f_max), plot_nb_pts)
        else:
            f_mod = np.linspace(f_min, f_max, plot_nb_pts)
    
        T_mod = transmittance_ordre2_passe_bande(f_mod, T0, f0, m)

        n = 4
        str_modele = r"$T = T_0\times\dfrac{2m\dfrac{f}{f_0}}{\sqrt{(1-\dfrac{f^2}{f_0^2})^2+(2m\dfrac{f}{f_0})^2}}$" + "\n"
        str_params = r"$T_0=$" + _pround(T0,n) + r"  $f_0$=" + _pround(f0,n) + r"  $m$=" + _pround(m,n)
        line = plot_ax.plot(f_mod, T_mod, label=str_modele+str_params)

 

        if return_line==True:
            return T0, f0, m, line[0]

    return T0, f0, m


def ajustement_gain_ordre2_passe_bande(f, G, G0_p0=1, f0_p0=1, m_p0=1, plot_ax=None, plot_fmin=None, plot_fmax=None, plot_xlog=True, plot_nb_pts=100, return_line=False) :
    """
    Modélisation d'une série de points (f,T) par une fonction de transmittance
    d'un système d'ordre 2 passe-bande :
    T = T0*2*m*(f/f0)/np.sqrt((1-(f/f0)**2)**2+(2*m*f/f0)**2)

    Paramètres :
        f (liste ou tableau Numpy) : fréquence.
        T (liste ou tableau Numpy de même dimension que x) : transmittance.

    Paramètres optionnels :
        T0_p0         (1)    : valeur de T0 aidant à la convergence du modèle.
        f0_p0         (1)    : valeur de f0 aidant à la convergence du modèle.
        m_p0          (1)    : valeur de m  aidant à la convergence du modèle.
        plot_ax      (None)  : repère pour tracer le modèle.
        plot_fmin    (None)  : fréquence minimale  pour le tracé de modèle.
        plot_fmax    (None)  : fréquence maximale pour le tracé de modèle.
        plot_xlog    (True)  : fréquences sur une échelle logarithmique
        plot_nb_pts  (100)   : nombre de points.
        return_line  (False) : renvoie en plus la courbe du modèle.

    Retourne :
        G0 (float), f0 (float), m (float)
        G0 (float), f0 (float), m (float), line (matplotlib.lines.Line2D) [si return_line == True]
    """
    (G0, f0, m), pcov = curve_fit(gain_ordre2_passe_bande, f, G, p0=[G0_p0, f0_p0, m_p0])

    if plot_fmin != None:
        f_min = fmin
    else:
        f_min = f[0]
        
    if plot_fmax != None:
        f_max = fmax
    else:
        f_max = f[-1]
        
    if (plot_ax != None):
        if plot_xlog==True:
            f_mod = np.logspace(np.log10(f_min), np.log10(f_max), plot_nb_pts)
        else:
            f_mod = np.linspace(f_min, f_max, plot_nb_pts)
    
        G_mod = gain_ordre2_passe_bande(f_mod, G0, f0, m)

        n = 4
        str_modele = r"$G = G_0 + 20\log(2m\dfrac{f}{f_0})- 20\log(\sqrt{(1-\dfrac{f^2}{f_0^2})^2+(2m\dfrac{f}{f_0})^2}$" + "\n"
        str_params = r"$G_0=$" + _pround(G0,n) + r"  $f_0$=" + _pround(f0,n) + r"  $m$=" + _pround(m,n)
        line = plot_ax.plot(f_mod, G_mod, label=str_modele+str_params)



        if return_line==True:
            return G0, f0, m, line[0]

    return G0, f0, m





