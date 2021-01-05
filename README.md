# simulador-contagios 🚧
Proyecto personal, utilizando OpenGL para python 3, de un simulador de contagios entre dos poblaciones con aplicación de medidas preventivas (cuarentena, distancia social y/o cierre de fronteras) en tiempo real a partir de un virus modificable (probabilidad de infección y muerte, radio de contagio, dias de recuperacion, etc.) durante la simulación.
## Pre-requisitos
Para comenzar es necesario pre-instalar las siguientes librerias para python: [glfw](https://pypi.org/project/glfw/), [pyopengl](https://pypi.org/project/PyOpenGL/), [numpy](https://pypi.org/project/numpy/), [pillow](https://pypi.org/project/Pillow/), [scipy](https://pypi.org/project/scipy/), [matplotlib](https://pypi.org/project/matplotlib/)
```bash
glfw        # librería OpenGL
pyopengl    # OpenGL para python
numpy       # operación con vectores y matrices
pillow      # procesamiento de imágenes
scipy       # (stats) distribuciones de probabilidad
matplotlib  # gráficos
```
## Inicio
Para iniciar, es necesario introducir como argumento adicional (al llamado del simulador view.py) la ruta de un archivo .json que contiene los parámetros de un virus a simular. Esto es:
```sh
> python view.py ruta
```
por comodidad se recomienda usar ruta=virus.json y modificar dicho archivo con los valores deseados.

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
donde "Radius" es el radio de contagio, "Contagious_prob" la probabilidad de contagio cuando existe interacción a distancia menor que "Radius", "Death_rate" probabilidad de muerte por infección, "Initial_population" población total inicial (para un desempeño fluido se recomienda menor o igual 200) y "Days_to_heal" días necesarios para recuperarse de la infección.

Ahora bien, cada parámetro posee cotas y tipos de variables, estas son:
```python
0 <= "Radius"(float) <= 0.2
0 <= "Contagious_prob"(float) <= 1
0 <= "Death_rate"(float) <= 1
0 <= "Initial_population"(int) <= 300
0 <= "Days_to_heal"(int) <= 14
```
## Lógica
Se basa en el conjunto de dos poblaciones que conforman un sistema comunicado. Cada poblacion tiene un comportamiento alejado de la otra, donde en algunos casos se puede considerar un grado de comunicacion, como los viajes entre poblaciones de individuos (autos, aviones o barcos). En general, por cuanto es de infeccioso un virus se considera una zona de cuarentena o aislacion de casos activos (infectados) para asi prevenir nuevos contagios. Ahora bien, dado este sistema general cada individuo de la poblacion distribuye con estados, esto es:

### Estados
Esta simulacion se basa en un sistema de individuos con estado variable. El estado por defecto de un individuo es "sano" (saludable o no infectado). En el contexto de un virus podemos considerar un porcentaje (o caso cero) de la poblacion que esta infectada con el virus a simular, con esto se considera el estado "infectado" (contagiado). Una de las caracteristicas de un virus es su capacidad de contagio o cuan infeccioso es el virus, y de un radio para el cual la probabilidad de contagio es suficiente para infectar a un individuo sano. Ademas un virus posee letalidad relacionada por cuanto es de mortal el virus para un individuo que lo posee considerando un nuevo estado "muerto", en algunos casos el mismo individuo tiene la capacidad de recuperarse (o ser tratado) dependiendo del virus con estado "recuperado". Por simplicidad se supone sin perdida de generalidad que un individuo recuperado no puede volver a infectarse ni infectar a otros.
```bash
sano                  # verde
infectado             # rojo
muerto                # gris
recuperado            # azul

CON distancia social  # cian
SIN distancia social  # amarillo
```

## Controles y Funcionamiento
Para la activación de parámetros basta presionar la tecla correspondiente de activación y para modificar los valores de los parámetros es necesario presionar la tecla correspondiente de modificación donde con tecla + para aumentar el valor, - para disminuir y Escape para deseleccionar la modificación:
```bash
aumentar                # Key +
disminuir               # Key -
salir editor            # Key Escape
```
El mecanismo de la simulación se define por tres bloques de parámetros modificables: medidas preventivas, valores del virus y globales. Definidos como siguen:
### Medidas Preventivas
Para este modelo de simulación se eligen como medidas clave la aplicación de la distancia social, cuarentena y cierre de fronteras.

Primero, una distancia social corresponde al distanciamiento individual del resto de individuos cuando se decide ser aplicada, donde además existe una probabilidad de responsabilidad individual por ser aplicada. Además, la distancia social queda definida por el radio de contagio de tal forma que su aplicación impida el contagio. Con esto, para la activación de distancia social hay que usar tecla S y modificación de probabilidad la tecla A. Además se considera un modo que visualiza quien realiza la distancia con tecla V.
```bash
distancia social        # Key S
prob. distancia social  # set Key A
vista distancia social  # Key V
```
Segundo, una cuarentena corresponde al aislamiento social de personas contagiadas cuando se decide ser aplicada, donde en general dicha medida se gestiona con un examen que determina si un individuo está contagiado, entonces dicha aplicación posee una cantidad de días de aplicación individual desde el día en que se contagió el individuo. Con esto, para la activación de cuarentena hay que usar tecla C y modificación de días de aplicación individual la tecla Q.
```bash
cuarentena              # Key C
días para cuarentena    # set Key Q
```
Tercero, un cierre de fronteras corresponde al aislamiento de una población de otras cuando se decide ser aplicada, donde un libre desplazamiento de individuos entre poblaciones con cierta probabilidad provoca reinfección de una población pese a no tener casos activos. Con esto, por defecto una población tendrá denegado el libre tránsito entre poblaciones, donde para la activación hay que usar tecla M y modificación de la probabilidad de tránsito (un individuo cambia de población) con tecla N.
```bash
migrar random           # Key M
prob. migrar            # set Key N
```
Es importante notar que la aplicación de las medidas se realizan de manera separada de acuerdo a la población seleccionada. Para elegir una población basta presionar 1 o 2 según corresponda.
```bash
población 1             # Key 1
población 2             # Key 2
```
### Valores del Virus
Para este modelo de simulación se consideran como parámetros modificables clave la probabilidad de infección, radio de contagio, probabilidad de muerte por infección y días para recuperarse.

Primero, la probabilidad de contagio está definida como la probabilidad que tiene un individuo sano de contagiarse cuando un individuo infectado está a distancia menor o igual al radio de contagio relacionada por cuanto es infeccioso el virus. Con esto, para modificar tal probabilidad hay que usar tecla I.
```bash
prob. infección         # set Key I
```
Segundo, el radio de contagio corresponde a la distancia suficiente para que un individuo sano pueda ser contagiado por un infectado. Así, para modificar dicho radio hay que usar tecla R.
```bash
radio contagio          # set Key R
```
Tercero, la probabilidad de muerte por infección está definida como la probabilidad que tiene un individuo infectado de morir por el virus relacionada con la letalidad del virus. Con esto, para modificar hay que usar tecla D.
```bash
prob. muerte            # set Key D
```
Cuarto, días para recuperarse corresponde a la cantidad de días suficientes para que un individuo infectado pueda recuperarse del virus. Así, para modificar la cantidad de días hay que usar tecla H.
```bash
días para recuperarse   # set Key H
```
Es importante notar que la modificación de los valores del virus son independientes de la población seleccionada, por lo que el nuevo desempeño del virus se aplica sobre el conjunto de poblaciones.
### Globales
Finalmente, se considerar la posibilidad de adelantar un día desde el tiempo actual con tecla derecha, reiniciar la simulación de la población seleccionada con tecla X y graficar el comportamiento de la simulación por población con tecla P.
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

