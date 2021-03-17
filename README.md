# simulador-contagios
Proyecto personal, utilizando OpenGL para python 3, de un simulador de contagios entre dos poblaciones con aplicación de medidas preventivas (cuarentena, distancia social y/o cierre de fronteras) en tiempo real a partir de un virus modificable (probabilidad de infección y muerte, radio de contagio, dias de recuperacion, etc.) durante la simulación.
### Identificación del Documento
```bash
Curso: CC3501 - Primavera 2020, Fecha: 04/01/2021, Alumno: Felipe Urrutia Vargas
```
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
Se basa en el conjunto de dos poblaciones que conforman un sistema comunicativo. Cada población tiene un comportamiento alejado de la otra, donde en algunos casos se puede considerar un grado de comunicación, como los viajes entre poblaciones de individuos (autos, aviones o barcos). En general, por cuanto es infeccioso un virus se considera una zona de cuarentena o aislamiento de casos activos (infectados) para así prevenir nuevos contagios. Ahora bien, dado este sistema general cada individuo de la población distribuye con estados, esto es:

### Estados
Esta simulación se basa en un sistema de individuos con estado variable. El estado por defecto de un individuo es "sano" (saludable o no infectado). En el contexto de un virus podemos considerar un porcentaje (o caso cero) de la población que está infectada con el virus a simular, con esto se considera el estado "infectado" (contagiado). Una de las características de un virus es su capacidad de contagio o cuan infeccioso es el virus, y de un radio para el cual la probabilidad de contagio es necesaria para infectar a un individuo sano. Además un virus posee letalidad relacionada por cuanto es mortal el virus para un individuo que lo posee considerando un nuevo estado "muerto", en algunos casos el mismo individuo tiene la capacidad de recuperarse (o ser tratado) dependiendo del virus con estado "recuperado". Por simplicidad se supone sin pérdida de generalidad que un individuo recuperado no puede volver a infectarse ni infectar a otros.
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
La simulación posee una interfaz sencilla y guiada de visualización y control (editor).
### Visualización
Se compone de dos escenas principales cuadradas con borde celeste donde en cada extremo de la pantalla con un conjunto de puntos verde y rojo que conforman cada población ya definidas (#1 izquierda y #2 derecha). Además, entre ellas existe una tercera escena cuadrada con borde rojo que representa la zona de cuarentena la cual ya se definió como ser activada. Luego, existe un rectángulo grande en el extremo inferior izquierdo donde se dibuja un gráfico de línea con OpenGL del comportamiento hasta el momento de la población seleccionada la cual ya se explico como activar.
### Editor
Además, en la parte izquierda junto al cuadrado de la población #1 existen cuatro gráficos desde barra que representan la distribución de individuos por estado para la población seleccionada, esto es "sano", "infectado", "muerto" y "recuperado", respectivamente de arriba hacia abajo. Así mismo, en la parte derecha junto al cuadrado de la población #2 están el conjunto de gráficos de barras modificables junto al indicador de activación para los parámetros "distancia social", "cuarentena" y "migración (viajes)", respectivamente desde arriba hacia abajo. Es fácil notar que en la parte central superior existe una barra que representa el tiempo, el cual avanza hacia la derecha como una barra blanca que al completarse representa un día (50 iteraciones).

Finalmente, en la parte inferior derecha junto al rectángulo donde se dibuja el gráfico señalado se ubican los parámetros que modifican el virus, esto es "prob. infección", "radio de contagio", "prob. muerte" y "dias de recuperacion", respectivamente de arriba hacia abajo. Junto a ellos hay un conjunto de indicaciones adicionales con teclas "+: aumentar", "-: disminuir", "P: terminar/plot", "V: vista distancia social", "X: reiniciar simulación"(por población) y "Esc: salir editor", en general sobre cada parámetro modificable viene acompañada un tecla que referencia lo detallado anteriormente en el módulo "Controles".
```bash
> [2] sanos: 34, infectados: 36, muertos: 13, recuperados: 17
```
![https://github.com/furrutiav/simulador-contagios/blob/main/img/example.png](/img/example.png)
