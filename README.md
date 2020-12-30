# simulador-contagios 🚧
### Pre-requisitos
Para comenzar es necesario pre-instalar las siguientes librerias para python: [glfw](https://pypi.org/project/glfw/), [pyopengl](https://pypi.org/project/PyOpenGL/), [numpy](https://pypi.org/project/numpy/), [pillow](https://pypi.org/project/Pillow/), [scipy](https://pypi.org/project/scipy/)
```bash
glfw      # librería OpenGL
pyopengl  # OpenGL para python
numpy     # operación con vectores y matrices
pillow    # procesamiento de imágenes
scipy     # distribuciones de probabilidad
```
### Controles
...
```bash
distancia social    # Key S
avanzar un dia      # Key Right
restart simulation  # Key R
info                # Key P
seleccion           # Press Key 1 or 2

prob infeccion      # set Key I
radius              # set Key R
death rate          # set Key D
days to heal        # set Key H

aumentar            $ Key +
disminuir           # Key -
```
### Inicio
...
```python
b = Builder()
pop1 = Population(b, size=100, social_distance=False, groups=2, view_center=(0.7, 0.5))
pop2 = Population(b, size=100, social_distance=False, groups=2, view_center=(0.7, -0.5))
```
### Interfaz (Terminal)
...
```bash
> [2] sanos: 34, infectados: 36, muertos: 13, recuperados: 17
```
### Estados
...
```bash
sano        # verde
infectado   # rojo
muerto      # gris
recuperado  # azul
```
