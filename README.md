# simulador-contagios 🚧
Proyecto personal, utilizando OpenGL para python 3, de un simulador de contagios entre dos poblaciones con aplicacion de medidas preventivas (cuarentena, distancia social y/o cierre de fronteras) en tiempo real a partir de un virus modificable (probabilidad de infeccion y muerte, radio de contagio, dias de recuperacion, etc.) durante la simulacion.
### Pre-requisitos
Para comenzar es necesario pre-instalar las siguientes librerias para python: [glfw](https://pypi.org/project/glfw/), [pyopengl](https://pypi.org/project/PyOpenGL/), [numpy](https://pypi.org/project/numpy/), [pillow](https://pypi.org/project/Pillow/), [scipy](https://pypi.org/project/scipy/), [matplotlib](https://pypi.org/project/matplotlib/)
```bash
glfw        # librería OpenGL
pyopengl    # OpenGL para python
numpy       # operación con vectores y matrices
pillow      # procesamiento de imágenes
scipy       # (stats) distribuciones de probabilidad
matplotlib  # graficos
```
### Inicio
...

```sh
> python view.py virus.json
```

```python
[
  {
    "Radius": 0.1,
    "Contagious_prob": 0.2,
    "Death_rate": 0.1,
    "Initial_population": 200,
    "Days_to_heal": 5
  }
]
```
### Controles y Funcionamiento
...
```bash
distancia social        # Key S
migrar random           # Key M
avanzar un dia          # Key Right
reiniciar simulación    # Key X
plot/terminar           # Key P
cuarentena              # Key C
vista distancia social  # Key V
seleccion               # Key 1 or 2

prob. infeccion         # set Key I
radio contagio          # set Key R
prob. muerte            # set Key D
dias para recuperarse   # set Key H
prob. distancia social  # set Key A
dias para cuarentena    # set Key Q

aumentar                # Key +
disminuir               # Key -
salir editor            # Key Escape
```
### Interfaz
...
```bash
> [2] sanos: 34, infectados: 36, muertos: 13, recuperados: 17
```
![alt text](/img/example.png)
### Estados
...
```bash
sano                  # verde
infectado             # rojo
muerto                # gris
recuperado            # azul

CON distancia social  # cian
SIN distancia social  # amarillo
```
