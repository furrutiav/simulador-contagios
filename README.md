# simulador-contagios 🚧(en contrucción)
### Pre-requisitos
Para comenzar es necesario pre-instalar las siguientes librerias para python: [glfw](https://pypi.org/project/glfw/), [pyopengl](https://pypi.org/project/PyOpenGL/), [numpy](https://pypi.org/project/numpy/), [pillow](https://pypi.org/project/Pillow/), [scipy](https://pypi.org/project/scipy/)
```bash
glfw      # librería OpenGL
pyopengl  # OpenGL para python
numpy     # operación con vectores y matrices
pillow    # procesamiento de imágenes
scipy     # software para matematica, ciencia e ingenieria
```
### Controles
...
```bash
distancia social    # Key S
avanzar un dia      # Key Right
restart simulation  # Key R
```
### Inicio
...
```python
p = Population(size=100, social_distance=False, groups=2)
```
### Interfaz (Terminal)
...
```bash
> sanos: 19, infectados: 1, muertos: 46, recuperados: 34
```
### Estados
...
```bash
sano        # verde
infectado   # rojo
muerto      # gris
recuperado  # azul
```
