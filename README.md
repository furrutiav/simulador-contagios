# simulador-contagios 🚧
Proyecto personal, utilizando OpenGL para python 3, de un simulador de contagios entre dos poblaciones con aplicacion de medidas preventivas (cuarentena, distancia social y/o cierre de fronteras) en tiempo real a partir de un virus modificable (probabilidad de infeccion y muerte, radio de contagio, dias de recuperacion, etc.) durante la simulacion.
## Pre-requisitos
Para comenzar es necesario pre-instalar las siguientes librerias para python: [glfw](https://pypi.org/project/glfw/), [pyopengl](https://pypi.org/project/PyOpenGL/), [numpy](https://pypi.org/project/numpy/), [pillow](https://pypi.org/project/Pillow/), [scipy](https://pypi.org/project/scipy/), [matplotlib](https://pypi.org/project/matplotlib/)
```bash
glfw        # librería OpenGL
pyopengl    # OpenGL para python
numpy       # operación con vectores y matrices
pillow      # procesamiento de imágenes
scipy       # (stats) distribuciones de probabilidad
matplotlib  # graficos
```
## Inicio
Para iniciar, es necesario introducir como argumento adicional (al llamado del simulador view.py) la ruta de un archivo .json que contiene los parametros de un virus a simular. Esto es:
```sh
> python view.py ruta
```
por comondidad se recomienda usar ruta=virus.json y modificar dicho archivo con los valores deseados.

Un ejemplo del contenido de virus.json se define como sigue:
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
donde "Radius" es el radio de contagio, "Contagious_prob" la probabilidad de contagio cuando existe interaccion a distancia menor que "Radius", "Death_rate" probabilidad de muerte por infeccion, "Initial_population" poblacion total inicial (para un desempeño fluido se recomienda menor o igual 200) y "Days_to_heal" dias necesarios para recuperarse de la infeccion.

Ahora bien, cada parametro posee cotas y tipos de variables, estas son:
```python
0 <= "Radius"(float) <= 0.2
0 <= "Contagious_prob"(float) <= 1
0 <= "Death_rate"(float) <= 1
0 <= "Initial_population"(int) <= 300
0 <= "Days_to_heal"(int) <= 14
```
## Logica
...
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

## Controles y Funcionamiento
Para la activacion de parametros basta presionar la tecla correspondiente de activacion y para modificar los valores de los parametros es necesario presionar la tecla correspondiente de modificacion donde con tecla + para aumentar el valor, - para disminuir y Escape para deseleccionar la modificacion:
```bash
aumentar                # Key +
disminuir               # Key -
salir editor            # Key Escape
```
El mecanismo de la simulacion se define por tres bloques de parametros modificables: medidas preventivas, valores del virus y globales. Definidos como siguen:
### Medidas Preventivas
Para este modelo de simulacion se eligen como medidas clave la aplicacion de la distancia social, cuarentena y cierre de fronteras.

Primero, una distancia social corresponde al distanciamiento indiviudal del resto de individuos cuando se decide ser aplicada, donde ademas existe una probabilidad de responsabilidad individual por ser aplicada. Ademas, la distancia social queda definida por el radio de contagio de tal forma que su aplicacion impida el contagio. Con esto, para la activacion de distancia social hay que usar tecla S y modificacion de probabilidad la tecla A. Ademas se considerar un modo que visualiza quien realiza la distancia con tecla V.
```bash
distancia social        # Key S
prob. distancia social  # set Key A
vista distancia social  # Key V
```
Segundo, una cuarentena corresponde al aislamiento social de personas contagiadas cuando se decide ser aplicada, donde en general dicha medida se gestiona con un examen que determina si un individuo esta contagiado, entonces dicha aplicacion posee una cantidad de dias de aplicacion indiviudal desde el dia en que se contagio el individuo. Con esto, para la activacion de cuarentena hay que usar tecla C y modificacion de dias de aplicacion individual la tecla Q.
```bash
cuarentena              # Key C
dias para cuarentena    # set Key Q
```
Tercero, un cierre de fronteras corresponde al aislamiento de una poblacion de otras cuando se decide ser aplicada, donde un libre desplazamiento de indiviudos entre poblaciones con cierta probabilidad provoca reinfeccion de una poblacion pese a no tener casos activos. Con esto, por defecto una poblacion tendra denegado el libre transito entre poblaciones, donde para la activacion hay que usar tecla M y modificacion de la probabilidad de transito (un individuo cambia de poblacion) con tecla N.
```bash
migrar random           # Key M
prob. migrar            # set Key N
```
Es importante notar que la aplicacion de las medidas se realizan de manera separada de acuerdo a la poblacion seleccionada. Para elegir una poblacion basta presionar 1 o 2 segun corresponda.
```bash
poblacion 1             # Key 1
poblacion 2             # Key 2
```
### Valores del Virus
Para este modelo de simulacion se consideran como parametros modificables clave la probabilidad de infeccion, radio de contagio, probabilidad de muerte por infeccion y dias para recuperarse.

Primero, la probabilidad de contagio esta definida como la probabilidad que tiene un individuo sano de contagiarse cuando un individuo infectado esta a distancia menor o igual al radio de contagio relacionada por cuanto es de infeccioso el virus. Con esto, para modificar tal probabilidad hay que usar tecla I.
```bash
prob. infeccion         # set Key I
```
Segundo, el radio de contagio corresponde a la distancia suficiente para que un individuo sano pueda ser contagiado por un infectado. Asi, para modificar dicho radio hay que usar tecla R.
```bash
radio contagio          # set Key R
```
Tercero, la probabilidad de muerte por infeccion esta definida como la probabilidad que tiene un individuo infectado de morir por el virus relacionada con la letalidad del virus. Con esto, para modificar hay que usar tecla D.
```bash
prob. muerte            # set Key D
```
Cuarto, dias para recuperarse corresponde a la cantidad de dias suficientes para que un individuo infectado pueda recuperarse del virus. Asi, para modificar la cantidad de dias hay que usar tecla H.
```bash
dias para recuperarse   # set Key H
```
Es importante notar la modificacion de los valores del virus son independientes de la poblacion selecciondado, por lo que el nuevo desempeño del virus se aplica sobre el conjunto de poblaciones.
### Globales
Finalmente, se considerar la posibilidad de adelantar un dia desde el tiempo actual con tecla derecha, reiniciar la simulacion de la poblacion seleccionada con tecla X y graficar el comportamiento de la simulacion por poblacion con tecla P.
```bash
avanzar un dia          # Key Right
reiniciar simulación    # Key X
terminar/plot           # Key P
```
## Interfaz
...
```bash
> [2] sanos: 34, infectados: 36, muertos: 13, recuperados: 17
```
![alt text](/img/example.png)
