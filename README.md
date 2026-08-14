# BATALLA NAVAL VECTORIAL
### *Aprende Álgebra Lineal, Pitágoras y Proyecciones Jugando*

Un videojuego educativo desarrollado en **Python** con una **interfaz gráfica
unificada** (tkinter + Matplotlib) que dibuja los vectores sobre el eje
cartesiano con fidelidad matemática. Diseñado especialmente para estudiantes de
secundaria, profesores de matemáticas/física e ingenieros.

Toda la lógica del juego (álgebra vectorial, batalla por turnos, tutorial,
laboratorio y manual) vive en módulos **puros** dentro del paquete `juego_naval/`
y es comprobable con `unittest` sin abrir ventanas; las pantallas solo la
presentan.

---

## Inicio Rápido

### 1. Requisitos Previos
* Python 3.8 o superior.
* `tkinter` (ya viene con Python en Windows; en Linux:
  `sudo apt install python3-tk`).
* Librería `matplotlib` (y `pillow`, que requiere en algunos entornos):
  ```bash
  pip install -r requirements.txt
  ```

### 2. Ejecutar el Juego
```bash
python3 main.py
```

El menú principal ofrece cuatro pantallas:
1. **Batalla vs IA:** campaña por turnos contra el *Almirante Vector* (energía,
   viento, 5 habilidades vectoriales, victoria/derrota).
2. **Tutorial:** 3 misiones didácticas con historia, pistas y desglose
   matemático paso a paso.
3. **Manual:** diccionario de vectores y catálogo de habilidades con su
   fundamento matemático.
4. **Laboratorio:** espacio libre con depuración visual en tiempo real para
   experimentar sumas, restas, escalares, módulo, distancia, producto punto y
   proyecciones, además del simulador de disparo P + V.

> Si matplotlib no está instalado, el juego **no se rompe**: las pantallas que
> lo necesitan muestran las instrucciones de instalación y permiten volver al
> menú.

### 3. Ejecutar las Pruebas Unitarias Automatizadas
```bash
python3 -m unittest discover -s . -p "test_*.py"
```

### 4. Empaquetar un Ejecutable (cualquier máquina Linux o Windows)

Para distribuir el juego como un único ejecutable que incluye tkinter y
matplotlib (sin que los alumnos instalen nada), se usa **PyInstaller**:

* **Linux** (genera `dist/BatallaNavalVectorial`):
  ```bash
  bash build_linux.sh
  ```
* **Windows** (genera `dist\BatallaNavalVectorial.exe`):
  ```bat
  build_windows.bat
  ```

El ejecutable sirve en cualquier máquina del mismo sistema operativo, tenga o
no Python instalado. En Windows, `tkinter` ya viene con Python; en Linux, el
script pide `sudo apt install python3-tk` solo en la máquina de compilación.

---

# PARTE 1: GUÍA PARA ESTUDIANTES DE SECUNDARIA

¡Hola, Almirante! Bienvenido al mando de tu flota. Para ganar esta batalla no necesitas disparar a ciegas: vas a utilizar el poder de los **vectores** para calcular tus tiros con exactitud matemática.

---

### 1. El Plano Cartesiano: Tu Mapa de Batalla
El mar es un plano de coordenadas $10 \times 10$:
* **Eje X (Horizontal):** Va de izquierda a derecha ($0$ al $9$).
* **Eje Y (Vertical):** Va de abajo hacia arriba ($0$ al $9$).
* **Origen $(0, 0)$:** Es la esquina inferior izquierda.

Un punto o posición se escribe como $(x, y)$. Por ejemplo, si tu fragata está en $(2, 3)$, significa que avanzó $2$ casillas a la derecha y $3$ casillas hacia arriba.

---

### 2. ¿Qué es un Vector y Cómo Funciona?
Un vector es una flecha que te dice **cuánto moverte y hacia dónde**:
* $\vec{v} = (3, 2)$ significa: "avanza $3$ casillas a la derecha en $X$, y sube $2$ casillas en $Y$".

---

### 2.0 Diccionario de Vectores: ¿Qué significa cada uno?

En el juego vas a ver distintos tipos de vectores. Esta es la "traducción" de cada uno en lenguaje sencillo:

| Vector | Símbolo | ¿Qué significa en el juego? | Ejemplo |
| :---: | :---: | :--- | :--- |
| **Posición del barco** | $\vec{P}_{\text{barco}}$ | **Dónde está** tu navío. Es el punto de partida de todos tus disparos. | Fragata en $(2, 3)$ |
| **Vector de tiro** | $\vec{V}_{\text{tiro}}$ | **Cuánto y hacia dónde** quieres que viaje el proyectil. Se suma a la posición del barco. | $(3, 2)$ = "3 a la derecha, 2 arriba" |
| **Punto de impacto** | $\vec{P}_{\text{impacto}}$ | **Dónde cae** la bala. Resultado de la suma $\vec{P}_{\text{barco}} + \vec{V}_{\text{tiro}}$. | $(2,3) + (3,2) = (5,5)$ |
| **Vector de viento** | $\vec{V}_{\text{viento}}$ | La fuerza que **empuja y desvía** tu proyectil. Debes restarlo o compensarlo para acertar. | $(1,-1)$ sopla "derecha y abajo" |
| **Dirección base** | $\vec{u}_{\text{dir}}$ | La **orientación pura** del torpedo (sin potencia). Suele ser corto como $(1,0)$ u $(1,1)$. | $(1,2)$ apunta "1 derecha, 2 arriba" |
| **Escalar $k$** | $k$ | El número que **multiplica la potencia/alcance**. No es un vector, es un número real. | $k = 3$ triplica el vector |
| **Vector escalado** | $k \cdot \vec{u}$ | El vector original **estirado** $k$ veces, mismo sentido, más largo. | $3 \cdot (1,2) = (3,6)$ |
| **Vector diferencia** | $\Delta \vec{v} = \vec{T} - \vec{P}$ | La **distancia y dirección** que separa un punto de otro. | De $(2,3)$ a $(5,7)$: $\Delta\vec{v} = (3,4)$ |
| **Módulo / Magnitud** | $\|\vec{v}\|$ | La **longitud de la flecha**: cuánto mide el vector. | $\|(3,4)\| = \sqrt{9+16} = 5$ |
| **Vector de ataque satelital** | $\vec{V}_{\text{ataque}}$ | El vector que apunta el **Cañón Orbital** (superpoder). | $(3,4)$ dirección del rayo |
| **Vector base del radar** | $\vec{U}_{\text{radar}}$ | El **eje de referencia** sobre el que se proyecta el rayo orbital. | $(1,0)$ eje horizontal |
| **Proyección** | $\text{proj}_{\vec{U}}(\vec{V})$ | La **sombra** del vector de ataque sobre el eje del radar. | $\text{proj}_{(1,0)}((3,4)) = (3,0)$ |

**Regla de oro para recordar:** los vectores con la letra **P** ($\vec{P}$) son **puntos** (dónde estás/dónde cae), y los vectores con la letra **V** o **U** ($\vec{V}$, $\vec{u}$) son **flechas de movimiento** (cuánto te mueves y hacia dónde).

---

### 2.1 Pantallas Tácticas y Planos Cartesianos

Para que nadie se pierda con las coordenadas, el juego dibuja **plano cartesiano
en tiempo real**:

* **El Plano Cartesiano dibujado** con ejes $X$ e $Y$ numerados (0 a 9).
* **`●` (Punto):** La posición actual de tu barco que dispara.
* **`+` (Trazos):** El recorrido exacto de tu vector de disparo, casilla por casilla.
* **`◎` (Mira):** La coordenada exacta donde impactará tu proyectil.
* **Mensaje de validez:** Te indica en color verde si el disparo cae **dentro** del área de combate, o en color rojo si cae **fuera** (para que puedas corregirlo antes de gastar el turno).

En la **Batalla vs IA** puedes ajustar el vector con sliders y ver la predicción
antes de disparar. En el **Tutorial Guiado** el plano ya muestra tu barco y el
objetivo marcados, con la historia y la pista matemática a un costado. Esto
convierte al juego en un **tutorial visual de vectores**, porque puedes "probar"
un vector y observar la flecha que dibuja antes de comprometerte.

---

### 3. Tus 5 Habilidades Vectoriales

#### 1. Disparo Vectorial Simple (Suma de Vectores)
* **¿Cómo funciona?:** Tomas la posición de tu barco y le sumas tu vector de disparo.
* **Fórmula:**
  $$\vec{P}_{\text{impacto}} = \vec{P}_{\text{barco}} + \vec{v}_{\text{disparo}} = (x_1 + x_2, y_1 + y_2)$$
* **Ejemplo:** Si tu barco está en $(2, 3)$ y disparas con el vector $(3, 2)$:
  $$(2 + 3, 3 + 2) = (5, 5) \quad \text{¡Impacto en }(5, 5)\text{!}$$

---

#### 2. Artillería con Viento (Suma Múltiple y Compensación)
* **¿Cómo funciona?:** En el mar hay corrientes marinas y viento $\vec{w}_{\text{viento}}$. El viento empujará tu proyectil desviándolo.
* **Fórmula:**
  $$\vec{P}_{\text{impacto}} = \vec{P}_{\text{barco}} + \vec{v}_{\text{disparo}} + \vec{w}_{\text{viento}}$$
* **Truco escolar:** Si el viento sopla $(+1, -1)$ y quieres llegar a un punto fijo, debes **restarle** el viento a tu disparo para compensar el desvío.

---

#### 3. Torpedo Escalar (Multiplicación por un Número Real $k$)
* **¿Cómo funciona?:** En vez de cambiar la dirección, multiplicas la potencia. Un número "escalar" $k$ multiplica a las dos componentes del vector, estirando su alcance en línea recta.
* **Fórmula:**
  $$k \cdot \vec{u} = (k \cdot u_x, k \cdot u_y)$$
* **Ejemplo:** Si apuntas en dirección $\vec{u} = (1, 2)$ con un motor de potencia $k = 3$:
  $$3 \cdot (1, 2) = (3 \cdot 1, 3 \cdot 2) = (3, 6)$$

---

#### 4. Sónar Acústico de Gauss (Módulo y Teorema de Pitágoras)
* **¿Cómo funciona?:** Envía una onda de sonido bajo el agua. El sónar no te dice la posición exacta del enemigo, pero calcula la **distancia euclidiana exacta** al barco enemigo más cercano usando el Teorema de Pitágoras.
* **Fórmula:**
  $$d = \sqrt{(\Delta x)^2 + (\Delta y)^2} = \sqrt{(x_2 - x_1)^2 + (y_2 - y_1)^2}$$
* **Ejemplo:** Si el emisor está en $(0, 0)$ y el enemigo en $(3, 4)$:
  $$d = \sqrt{3^2 + 4^2} = \sqrt{9 + 16} = \sqrt{25} = 5.0 \text{ unidades de distancia.}$$

---

#### 5. SUPERPODER: Cañón de Proyección Orbital
* **¿Cómo funciona?:** Es la habilidad más devastadora del juego. Eliges un vector de ataque satelital $\vec{v}$ y un vector de radar base $\vec{u}$. El satélite proyecta la "sombra ortogonal" de $\vec{v}$ sobre $\vec{u}$.
* **Efecto en el juego:** ¡El rayo orbital barre y daña **todas las casillas a lo largo de la línea proyectada**, pudiendo impactar a múltiples navíos de un solo disparo!

---

### 4. Símbolos en el Tablero de Juego

| Símbolo | Significado |
| :---: | :--- |
| `· ` | Agua inexplorada |
| `◆ ◈ ▲ ▼ ●` | Tus barcos aliados (según su clase) |
| `✖` | **Impacto certero** en un navío |
| `✕` | Disparo al agua (fallo) |
| `◉` | Baliza de sónar activo |
| `▸` | Casilla barrida por el Cañón de Proyección Orbital |

---

### 5. Modos de Juego Incluidos

El menú principal ofrece:

1. **Batalla vs Inteligencia Artificial:** Campaña por turnos donde te enfrentas al *Almirante Vector*.
2. **Tutorial Guiado:** 3 misiones didácticas con historias paso a paso para aprender las fórmulas.
3. **Manual de Fórmulas y Habilidades:** Diccionario de vectores y catálogo de habilidades con su fundamento matemático.
4. **Laboratorio Sandbox & Calculadora Vectorial:** Un espacio libre con depuración visual en tiempo real para experimentar sumas, restas, escalares, módulo, distancia, producto punto y proyecciones, además del Simulador de Disparo (P + V) sobre el plano cartesiano.

---

# PARTE 2: DOCUMENTACIÓN TÉCNICA PARA INGENIEROS Y DOCENTES

Esta sección describe la arquitectura de software, modelado algebraico formal, patrones de diseño y especificaciones de depuración del proyecto.

---

### 1. Arquitectura del Software y Modularidad

El proyecto está diseñado bajo principios de **Separación de Responsabilidades (SoC)** y **Clean Code**, separando la **lógica pura** (comprobable sin ventanas) de la **presentación** (pantallas Tkinter):

```
proyecto_vector/
├── vector2d.py                # Clase algebraica Vector2D (Espacio vectorial R^2, operadores sobrecargados)
├── barco.py                   # Entidad Barco (Geometría discreta paramétrica sobre Z^2)
├── tablero.py                 # Plano Cartesiano 2D, gestión de colisiones e indexación
├── habilidades.py             # Patrón Strategy para las operaciones de combate
├── ia.py                      # Inteligencia Artificial enemiga (Heurística de Caza y Exploración)
├── main.py                    # Entry Point: única forma de lanzar el juego
├── requirements.txt           # Dependencias de Python
├── build_linux.sh             # Genera ejecutable para Linux (PyInstaller)
├── build_windows.bat          # Genera ejecutable para Windows (PyInstaller)
├── BatallaNavalVectorial.spec # Especificación de PyInstaller
├── test_vector2d.py           # Pruebas unitarias de álgebra lineal
├── test_juego.py              # Pruebas unitarias de mecánicas de juego y colisiones
├── test_laboratorio.py        # Pruebas de la matemática del Laboratorio
├── test_sesion.py             # Pruebas de la partida (SesionBatalla) y smoke test de la pantalla
├── test_tutorial.py           # Pruebas del contenido pedagógico del Tutorial
└── juego_naval/
    ├── app.py                 # Registro central de pantallas + main() de la aplicación
    └── juego/
    │   ├── sesion.py          # Sesión de partida: máquina de estados + registro único de habilidades
    │   ├── tutorial.py        # Contenido puro del Tutorial (3 misiones + evaluación)
    │   ├── laboratorio.py     # Matemática pura y dibujo del Laboratorio (funciones puras)
    │   └── guia.py            # Manual: diccionario de vectores y catálogo de habilidades
    └── ui/
        ├── gestor_pantallas.py   # Screen Manager Tkinter (navegación + estado compartido)
        ├── pantalla_base.py      # Clase base de toda pantalla (hooks _construir_ui/_limpiar)
        └── pantallas/
            ├── menu_principal.py # Menú principal
            ├── batalla.py        # Batalla vs IA (Canvas + Matplotlib embebido)
            ├── tutorial.py       # Tutorial guiado
            ├── guia.py           # Manual de fórmulas (tablas con scroll)
            └── laboratorio.py    # Laboratorio y Simulador de Disparo
```

**Principio rector:** ningún archivo de la raíz importa `tkinter` ni
`matplotlib` (salvo a través de las pantallas); toda la matemática vive en
módulos puros testeados por `unittest`.

---

### 2. Formalización Matemática

#### A. Espacio Vectorial Bidimensional $\mathbb{R}^2$
Sea el espacio vectorial $V = (\mathbb{R}^2, +, \cdot)$ sobre el cuerpo $\mathbb{R}$. Todo vector $\vec{v} \in V$ se representa por el par ordenado:
$$\vec{v} = \begin{pmatrix} x \\ y \end{pmatrix} \in \mathbb{R}^2$$

#### B. Parametrización Discreta de Navíos en la Grilla $\mathbb{Z}^2$
Un barco de longitud $L \in \mathbb{N}$ con origen $\vec{P}_0 \in \mathbb{Z}^2$ y vector director unitario $\vec{u} \in \{(1,0), (0,1), (-1,0), (0,-1)\}$ se modela formalmente como el subconjunto discreto:
$$\mathcal{S} = \left\{ \vec{P}_0 + i \cdot \vec{u} \;\middle|\; i \in \{0, 1, \dots, L - 1\} \right\}$$

#### C. Producto Escalar (Dot Product)
Dados $\vec{u}, \vec{v} \in \mathbb{R}^2$, el producto interno canónico se define como:
$$\langle \vec{u}, \vec{v} \rangle = \vec{u} \cdot \vec{v} = u_x v_x + u_y v_y = \|\vec{u}\| \|\vec{v}\| \cos(\theta)$$

#### D. Proyección Vectorial Ortogonal (Cañón Orbital)
La proyección ortogonal del vector $\vec{v}$ sobre el subespacio generado por la base $\vec{u} \neq \vec{0}$ es:
$$\text{proj}_{\vec{u}}(\vec{v}) = \left( \frac{\vec{v} \cdot \vec{u}}{\|\vec{u}\|^2} \right) \vec{u} = \left( \frac{v_x u_x + v_y u_y}{u_x^2 + u_y^2} \right) \begin{pmatrix} u_x \\ u_y \end{pmatrix}$$

El trazado de la trayectoria orbital utiliza una interpolación lineal paramétrica discretizada (rasterización):
$$\vec{r}(t) = \vec{P}_{\text{origen}} + t \cdot \text{proj}_{\vec{u}}(\vec{v}), \quad t \in [0, 1]$$

---

### 3. Sistema de Depuración Matemática en Tiempo Real

El sistema incorpora un motor de depuración que captura el estado algebraico de cada operación antes de modificar el estado del juego:

* **Estructura de retorno:** Todos los métodos de `habilidades.py` y `vector2d.py` devuelven un diccionario `explicacion` con:
  * `operacion`: Nombre formal de la transformación matemática.
  * `formula`: Notación formal en formato algebraico.
  * `pasos`: Lista de cadenas con la sustitución aritmética término a término.
  * `resultado`: Vector o escalar resultante.
* **Visualización:** la pantalla de Batalla muestra un **log pedagógico** con el desglose paso a paso tras cada disparo y cada turno de la IA, con código de colores según el autor (**JUGADOR** o **IA**), permitiendo la verificación pedagógica instantánea en el aula.

---

### 3.1 Sesión de Partida y Máquina de Estados (`juego_naval/juego/sesion.py`)

La lógica de una partida completa vive en un solo lugar, sin duplicados entre
"modo texto" y "modo gráfico" (como ocurría antes de la migración):

* **`EstadoBatalla`:** `TURNO_JUGADOR`, `TURNO_IA`, `VICTORIA`, `DERROTA`.
* **Registro único de habilidades:** `SKILLS` se deriva de las clases de
  `habilidades.py`, y de ahí `COSTOS_HABILIDAD` y `NOMBRES_HABILIDAD`; no hay
  copias de costos ni nombres en ningún otro módulo.
* **`ejecutar_habilidad()`:** función pura que despacha la habilidad contra el
  tablero enemigo (sin tocar estado).
* **`SesionBatalla`:** controlador de la partida. Reglas de turno, energía
  (`min(6, energía+1)`), viento aleatorio cada 3 turnos y victoria/derrota
  viven **solo** aquí. El estado se guarda en `gestor.compartido["sesion"]`
  para sobrevivir a los cambios de pantalla.

### 3.2 Laboratorio de Vectores (`juego_naval/juego/laboratorio.py`)

La representación gráfica usa una arquitectura estándar en apps científicas de
Python: **tkinter es la cáscara** (menú, sliders, pestañas) y **Matplotlib vive
embebido como widget** mediante `FigureCanvasTkAgg`.

El Laboratorio incluye:

1. **Operaciones de vectores:** suma, resta, escalar, módulo, distancia,
   producto punto y proyección, sobre el plano cartesiano con flechas de
   longitud proporcional a la magnitud, regla del paralelogramo (suma/resta),
   sombra perpendicular (proyección) y desglose paso a paso. Los sliders
   modifican los vectores en tiempo real y la toolbar de Matplotlib ofrece
   zoom, desplazamiento y guardado a PNG.

2. **Simulador de Disparo (P + V):** réplica del tablero 10x10 donde se dibuja
   la flecha del vector de disparo desde la posición del barco, se marca el
   punto de impacto y se indica en verde/rojo si cae dentro o fuera del área de
   combate.

El módulo separa **funciones puras** (`calcular_resultado_laboratorio`,
`calcular_preview_disparo`) de las **funciones de dibujo** (`dibujar_flecha`,
`dibujar_laboratorio`, `dibujar_preview_disparo`), por lo que toda la
matemática es comprobable con `unittest` sin abrir una ventana.

### 3.3 Batalla Naval Gráfica (`juego_naval/ui/pantallas/batalla.py`)

La versión **jugable** de la campaña. Reutiliza exactamente la lógica pura:
instancia `SesionBatalla` de `juego_naval/juego/sesion.py`, ejecuta las
habilidades de `habilidades.py` vía `ejecutar_habilidad()` y delega el turno
enemigo a `IAEnemiga.decidir_turno()`.

Vista y controles:

1. **Tableros en Canvas:** a la izquierda tu flota (clic en un barco lo
   selecciona como punto de partida del disparo, con borde dorado); a la
   derecha el radar enemigo con niebla de guerra.
2. **Sliders de vector:** construyen V (y U para el Cañón Orbital) y el escalar
   k del Torpedo. Solo se activan los sliders que la habilidad elegida necesita.
3. **Predicción en vivo:** un mini-plano Matplotlib embebido dibuja la flecha
   P + V y un recuadro verde/rojo sobre la casilla de impacto (verde = dentro,
   rojo = fuera), usando las funciones puras de `juego_naval/juego/laboratorio.py`.
4. **Log pedagógico:** tras cada disparo y cada turno de la IA se muestra el
   desglose matemático paso a paso (mismas cadenas `explicacion`), reforzando
   el aprendizaje de fórmulas.
5. **Energía y viento:** la barra superior muestra la energía táctica (regla de
   recarga `min(6, energía+1)` y viento aleatorio cada 3 turnos).

### 3.4 Gestor de Pantallas (`juego_naval/ui/gestor_pantallas.py`)

Una sola ventana raíz (`tk.Tk`). Cada pantalla es un `Frame` que se muestra y
se destruye bajo demanda, sin abrir ventanas nuevas:

* `gestor.ir(nombre)` — navega guardando la actual en el historial.
* `gestor.reemplazar(nombre)` — navega sin guardar la actual.
* `gestor.volver()` — regresa a la pantalla anterior.
* `gestor.compartido` — dict con el estado que sobrevive a los cambios de
  pantalla (por ejemplo, `"sesion"` durante la batalla).

Cada pantalla hereda de `PantallaBase`, implementa `_construir_ui()` y puede
sobreescribir el hook `_limpiar()` para liberar recursos explícitos (las
pantallas con Matplotlib cierran su figura con `plt.close`).

---

### 4. Algoritmo de la Inteligencia Artificial (`ia.py`)

La IA implementa una máquina de estados finita con lógica vectorial:
1. **Fase de Exploración (Paridad Cartesiana):** Selecciona casillas con paridad $(x + y) \equiv 0 \pmod 2$ para maximizar la cobertura del plano reduciendo en un $50\%$ las búsquedas ciegas.
2. **Cálculo de Desplazamiento Vectorial:** Dado el objetivo elegido $\vec{T}$ y el barco emisor $\vec{P}_{\text{emisor}}$, la IA calcula:
   $$\vec{v}_{\text{tiro}} = \vec{T} - \vec{P}_{\text{emisor}}$$
3. **Fase de Cacería (Gradiente Ortogonal):** Al registrar un impacto exitoso en $\vec{P}_{\text{hit}}$, encola los cuatro vectores adyacentes unitarios:
   $$\mathcal{N} = \{ \vec{P}_{\text{hit}} + (1, 0), \;\vec{P}_{\text{hit}} + (-1, 0), \;\vec{P}_{\text{hit}} + (0, 1), \;\vec{P}_{\text{hit}} + (0, -1) \}$$

---

### 5. Cobertura de Pruebas Unitarias (`unittest`)

Se han desarrollado **65 casos de prueba unitarios** que validan:
* `test_vector2d.py` (9): álgebra lineal (suma, resta, escalar, magnitud,
  distancia, producto punto, proyección, desglose explicativo).
* `test_juego.py` (7): mecánicas de juego (posicionamiento de barcos, disparos,
  agua/impacto/fuera de límite y colisiones, habilidades de combate).
* `test_laboratorio.py` (16): matemática del Laboratorio (7 operaciones +
  opciones registradas + predicción de impacto dentro/fuera).
* `test_sesion.py` (23): costos y nombres de habilidades, ejecución de cada
  disparo sobre el tablero (incluido el rechazo de vectores nulos), máquina de
  estados de `SesionBatalla` (energía, tope, victoria/derrota, turno de la IA)
  y smoke test que abre/cierra la PantallaBatalla.
* `test_tutorial.py` (10): estructura de las 3 misiones y evaluación de
  acierto/error (vectorial y escalar).

Para correr la suite completa:
```bash
python3 -m unittest discover -s . -p "test_*.py"
```

---

### 6. Extensiones Pedagógicas Sugeridas para Docentes
* **Rotaciones con Matrices $2 \times 2$:** Agregar una habilidad "Escudo Giratorio" que aplique la matriz de rotación:
  $$R(\theta) = \begin{pmatrix} \cos\theta & -\sin\theta \\ \sin\theta & \cos\theta \end{pmatrix}$$
* **Ampliación a $\mathbb{R}^3$:** Incorporar eje $Z$ (profundidad submarina y altitud aérea de satélites).
