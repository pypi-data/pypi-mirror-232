# Librairie Python pour la physique au lycée

## Installation

Lancer dans un terminal :

    pip install physique

Pour une mise à jour :

```python
pip install --upgrade physique
```

---

## Dépendances

Cette librairie se base principalement sur les librairies `numpy`, `matplotlib` et `scipy`

## Module `physique.modelisation`

Fonctions pour réaliser une modélisation d'une courbe du type `y=f(x)`.

### > Bases

`ajustement_lineaire(x, y)`

`ajustement_affine(x, y)`

`ajustement_parabolique(x, y)`

`ajustement_exponentielle_croissante(x, y)`

`ajustement_exponentielle_croissante_x0(x, y)`

`ajustement_exponentielle_decroissante(x, y)`

`ajustement_exponentielle_decroissante_x0(x, y)`

### > Réponses fréquentielles

`ajustement_transmittance_ordre1_passe_bas(f, T)`

`ajustement_gain_ordre1_passe_bas(f, G)`

`ajustement_dephasage_ordre1_passe_bas(f, phi)`

`ajustement_transmittance_ordre1_passe_haut(f, T)`

`ajustement_gain_ordre1_passe_haut(f, G)`

`ajustement_dephasage_ordre1_passe_haut(f, phi)`

`ajustement_transmittance_ordre2_passe_bas(f, T)`

`ajustement_transmittance_ordre2_passe_haut(f, T)`

`ajustement_transmittance_ordre2_passe_bande(f, T)`

`ajustement_gain_ordre2_passe_bande(f, G)`

### > Exemple

```python
import matplotlib.pyplot as plt
from physique.modelisation import ajustement_parabolique

x = [0.003,0.141,0.275,0.410,0.554,0.686,0.820,0.958,1.089,1.227,1.359,1.490,1.599,1.705,1.801]
y = [0.746,0.990,1.175,1.336,1.432,1.505,1.528,1.505,1.454,1.355,1.207,1.018,0.797,0.544,0.266]

a, b, c = ajustement_parabolique(x, y, plot_ax=plt)

plt.plot(x, y, '+', label="Mesures")
plt.legend(facecolor="linen")
plt.title("Trajectoire d'un ballon")
plt.xlabel("x (m)")
plt.ylabel("y (m)")
plt.grid()
plt.show()
```

![](https://david-therincourt.fr/python/pypi-physique/exemple_1.png)

L'option `plot_ax` trace la courbe du modèle dans le repère (`axes`) indiqué. L'étiquette (`label`) du modèle donne le résultat de la modélisation dans la légende !

---

## Module `physique.csv`

Module d'importation de tableau de données au format CSV à partir des logiciels Aviméca3, Regavi, ...

#### > Fonctions disponibles

`load_txt(fileName)`

`load_avimeca3_txt(fileName)`  

`load_regavi_txt(fileName)`

`load_regressi_txt(fileName)`

`load_regressi_csv(fileName)`

`load_oscillo_csv(filename)`

`load_ltspice_csv(filename)`

`save_txt(data, fileName)`

#### > Exemple

```python
import matplotlib.pyplot as plt
from physique.csv import load_avimeca3_txt

t, x, y = load_avimeca3_txt('data.txt')

plt.plot(x,y,'.')
plt.title("Trajectoire d'un ballon")
plt.xlabel('x (m)')
plt.ylabel('y (m)')
plt.grid()
plt.show()
```

Le fichier `data.txt` a été exporté du logiciel Avimeca 3 à partir d'un exemple !

![](https://david-therincourt.fr/python/pypi-physique/exemple_2.png)

---

## Module `physique.signal`

Module Module pour le traitement des signaux.

### > Fonctions disponibles

`derive(y, t)`

`integrale(y, t, tmin, tmax)`

`spectre_amplitude(y, t, T)`

`spectre_RMS(y, t, T)`

`spectre_RMS_dBV(y, t, T)`

### > Exemple

```python
import numpy as np
import matplotlib.pyplot as plt
from physique.csv import load_oscillo_csv
from physique.signal import integrale

t, u = load_oscillo_csv('scope.csv')

f = 125
T = 1/f
aire = integrale(u, t, 0, T, plot_ax=plt)
moy = aire/T

plt.plot(t, u)
plt.axhline(moy, ls="--", color="C3")
plt.text(0.65*T, moy+0.2, "Moy = {:.2f} V".format(moy), color="C3")
plt.title("Valeur moyenne d'un signal périodique")
plt.xlabel("t (s)")
plt.ylabel("u (V)")
plt.grid()
plt.show()
```

![](https://david-therincourt.fr/python/pypi-physique/exemple_3.png)