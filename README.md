# BATALLA NAVAL VECTORIAL
### *Aprende Álgebra Lineal, Pitágoras y Proyecciones Jugando*

Un videojuego educativo desarrollado en **Python** que combina una interfaz de
terminal (**CLI/TUI** con la librería **Rich**) y una **interfaz gráfica**
(tkinter + Matplotlib) que dibuja los vectores sobre el eje cartesiano con
fidelidad matemática. Diseñado especialmente para estudiantes de secundaria,
profesores de matemáticas/física e ingenieros.

---

## Inicio Rápido

### 1. Requisitos Previos
* Python 3.8 o superior.
* Librería `rich`:
  ```bash
  pip install rich
  ```

### 2. Ejecutar el Juego
```bash
python3 main.py
```

### 3. Interfaz Gráfica (opcional, recomendada)
El menú principal incluye la opción **"Interfaz Gráfica"**: una ventana con
tkinter + Matplotlib que dibuja los vectores sobre el eje cartesiano con
fidelidad matemática (flechas con punta real, regla del paralelogramo,
proyección con sombra perpendicular, zoom interactivo y sliders en tiempo real).

Requisitos según tu sistema operativo:

* **Windows:** Python ya trae `tkinter`. Solo instala matplotlib:
  ```bash
  pip install matplotlib
  ```
* **Linux (Debian/Ubuntu):** instala `tkinter` del sistema y matplotlib:
  ```bash
  sudo apt install python3-tk
  pip install matplotlib
  ```

> Si tkinter o matplotlib no están instalados, el juego **no se rompe**: el
> menú muestra las instrucciones y el modo texto (Rich) sigue funcionando.

### 4. Ejecutar las Pruebas Unitarias Automatizadas
```bash
python3 -m unittest discover -s . -p "test_*.py"
```

### 5. Empaquetar un Ejecutable (cualquier máquina Linux o Windows)

Para distribuir el juego como un único ejecutable que incluye tkinter,
matplotlib y Rich (sin que los alumnos instalen nada), se usa **PyInstaller**:

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

### 2.1 La Pseudo-Interfaz Gráfica (Pseudo-GUI) en Consola

Para que nadie se pierda con las coordenadas, el juego incluye una **pantalla táctica visual en tiempo real**. Antes de disparar, verás:

* **El Plano Cartesiano dibujado** con ejes $X$ e $Y$ numerados (0 a 9).
* **`●` (Punto verde):** La posición actual de tu barco que dispara.
* **`+` (Trazos amarillos):** El recorrido exacto de tu vector de disparo, casilla por casilla.
* **`◎` (Mira roja):** La coordenada exacta donde impactará tu proyectil.
* **Mensaje de validez:** Te indica en color verde si el disparo cae **dentro** del área de combate, o en color rojo si cae **fuera** (para que puedas corregirlo antes de gastar el turno).

El juego te pedirá confirmación: *"¿Confirmar este vector de disparo? (s/n)"*. Si respondes `n`, puedes corregir tus números y volver a ver la previsualización. Esto convierte al juego en un **tutorial visual de vectores**, porque puedes "probar" un vector y observar la flecha que dibuja antes de comprometerte.

En el **Tutorial Guiado**, además, se muestra un **Dashboard dividido**: a la izquierda la misión, la historia y la pista matemática; a la derecha el plano cartesiano con tu barco y el objetivo ya marcados.

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

El menú principal (opciones 1-7) ofrece:

1. **Batalla vs Inteligencia Artificial** (opción 1): Campaña por turnos donde te enfrentas al *Almirante Vector*.
2. **Tutorial Guiado** (opción 2): 3 misiones didácticas con historias paso a paso para aprender las fórmulas.
3. **Laboratorio Sandbox & Calculadora Vectorial** (opción 3): Un espacio libre con depuración visual en tiempo real para experimentar sumas, restas, ángulos, Pitágoras, producto punto y proyecciones.
4. **Manual de Fórmulas y Habilidades** (opción 4): Diccionario de vectores y catálogo de habilidades con su fundamento matemático.
5. **Interfaz Gráfica** (opción 5): Ventana con el Laboratorio de Vectores y el Simulador de Disparo sobre el plano cartesiano (tkinter + Matplotlib).
6. **Batalla Naval Gráfica** (opción 6): La campaña completa jugable en una ventana tkinter: tableros clicables, sliders para construir el vector, predicción en vivo con Matplotlib y desglose matemático paso a paso (misma lógica que la opción 1).

---

# PARTE 2: DOCUMENTACIÓN TÉCNICA PARA INGENIEROS Y DOCENTES

Esta sección describe la arquitectura de software, modelado algebraico formal, patrones de diseño y especificaciones de depuración del proyecto.

---

### 1. Arquitectura del Software y Modularidad

El proyecto está diseñado bajo principios de **Separación de Responsabilidades (SoC)** y **Clean Code**, sin ofuscación y con alta cohesión:

```
proyecto_vector/
├── vector2d.py        # Clase algebraica Vector2D (Espacio vectorial R^2, operadores sobrecargados)
├── barco.py           # Entidad Barco (Geometría discreta paramétrica sobre Z^2)
├── tablero.py         # Plano Cartesiano 2D, gestión de colisiones e indexación
├── habilidades.py     # Patrón Strategy para las operaciones de combate
├── ia.py              # Inteligencia Artificial enemiga (Heurística de Caza y Exploración)
├── interfaz.py        # Renderizado TUI con Rich (Layouts, Grillas Cartesianas y Tablas)
├── interfaz_grafica.py# Ventana tkinter + Matplotlib (Laboratorio de Vectores y Simulador de Disparo)
├── juego_grafico.py  # Batalla Naval jugable en ventana gráfica (tkinter Canvas + Matplotlib)
├── juego.py           # Bucle de juego (Game Loop), Modo Sandbox y Tutoriales
├── main.py            # CLI Entry Point (menú principal con fallback a Rich)
├── test_vector2d.py   # Pruebas unitarias de álgebra lineal
├── test_juego.py      # Pruebas unitarias de mecánicas de juego y colisiones
├── test_interfaz_grafica.py  # Pruebas de la lógica matemática de la GUI
├── test_juego_grafico.py     # Pruebas de la batalla gráfica (disparos, costos y smoke test)
├── requirements.txt   # Dependencias de Python
├── build_linux.sh     # Genera ejecutable para Linux (PyInstaller)
└── build_windows.bat  # Genera ejecutable para Windows (PyInstaller)
```

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
* **Visualización:** El componente `renderizar_panel_depuracion()` en `interfaz.py` dibuja un panel de doble borde con código de colores según el autor (**JUGADOR** en cian o **IA** en magenta), permitiendo la verificación pedagógica instantánea en el aula.

---

### 3.1 Sistema de Pseudo-GUI y Rasterización de Vectores (`interfaz.py`)

El renderizado visual se apoya en dos componentes clave:

1. **`trazar_vector_en_tablero(tablero, origen, destino)`:** Implementa **rasterización discreta** de la trayectoria vectorial mediante interpolación lineal paramétrica sobre $\mathbb{Z}^2$:
   $$t_k = \frac{k}{N}, \quad N = \lceil 2 \cdot \|\vec{d}\| \rceil, \quad \vec{p}_k = \vec{P}_{origen} + t_k \cdot \vec{d}$$
   Escribe marcadores temporales (`●`, `+`, `◎`) en `Tablero.marcas_temporales`, que se renderizan con prioridad sobre la niebla de guerra.

2. **`mostrar_pantalla_mision_guiada(..., tablero)`:** Utiliza `rich.layout.Layout` para construir un **Dashboard de dos columnas** (información de la misión / plano cartesiano), ofreciendo una experiencia tipo GUI embebida en la terminal.

El flujo de interacción `pedir_vector_con_previsualizacion()` en `juego.py` implementa el patrón **previsualizar → confirmar → ejecutar**: dibuja la predicción del impacto en el radar enemigo y solicita confirmación (`s/n`) antes de gastar energía táctica, evitando disparos nulos o fuera de rango.

---

### 3.2 Interfaz Gráfica de Vectores (`interfaz_grafica.py`)

La representación gráfica usa una arquitectura híbrida estándar en apps
científicas de Python: **tkinter es la cáscara** (menú, sliders, pestañas) y
**Matplotlib vive embebido como widget** mediante `FigureCanvasTkAgg`.

Incluye dos pestañas:

1. **Laboratorio de Vectores:** operaciones (suma, resta, escalar, módulo,
   distancia, producto punto, proyección) sobre el plano cartesiano con
   flechas de longitud proporcional a la magnitud, regla del paralelogramo
   (suma/resta), sombra perpendicular (proyección) y desglose paso a paso.
   Los sliders modifican los vectores en tiempo real y la toolbar de
   Matplotlib ofrece zoom, desplazamiento y guardado a PNG.

2. **Simulador de Disparo (P + V):** réplica del tablero 10x10 donde se dibuja
   la flecha del vector de disparo desde la posición del barco, se marca el
   punto de impacto y se indica en verde/rojo si cae dentro o fuera del área
   de combate.

El módulo separa **funciones puras** (`calcular_resultado_laboratorio`,
`calcular_preview_disparo`) de las **funciones de dibujo** (`dibujar_flecha`,
`dibujar_laboratorio`), por lo que toda la matemática es comprobable con
`unittest` sin abrir una ventana. `hay_interfaz_grafica()` detecta si la
máquina tiene tkinter, matplotlib y pantalla; si no, `main.py` muestra las
instrucciones de instalación y el juego continúa en modo texto.

---

### 3.3 Batalla Naval Gráfica (`juego_grafico.py`)

La versión **jugable** de la campaña en una sola ventana tkinter. Reutiliza
EXACTAMENTE la lógica de terminal: instancia `PartidaBatallaNaval` de `juego.py`,
ejecuta las mismas habilidades de `habilidades.py` vía la función pura
`ejecutar_ataque_jugador()` y delega el turno enemigo a
`IAEnemiga.decidir_turno()`.

Vista y controles:

1. **Tableros en Canvas:** a la izquierda tu flota (clic en un barco lo
   selecciona como punto de partida del disparo, con borde dorado); a la
   derecha el radar enemigo con niebla de guerra.
2. **Sliders de vector:** construyen V (y U para el Cañón Orbital) y el escalar
   k del Torpedo. Solo se activan los sliders que la habilidad elegida necesita.
3. **Predicción en vivo:** un mini-plano Matplotlib embebido dibuja la flecha
   P + V y un recuadro verde/rojo sobre la casilla de impacto (verde = dentro,
   rojo = fuera), usando las funciones puras de `interfaz_grafica.py`.
4. **Log pedagógico:** tras cada disparo y cada turno de la IA se muestra el
   desglose matemático paso a paso (mismas cadenas `explicacion` que en
   terminal), reforzando el aprendizaje de fórmulas.
5. **Energía y viento:** la barra superior muestra la energía táctica (misma
   regla de recarga `min(6, energía+1)` y viento aleatorio cada 3 turnos).

Toda la matemática es testeable sin ventana (`ejecutar_ataque_jugador`,
`COSTOS_HABILIDAD`), y el smoke test abre/cierra la ventana automáticamente.

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

Se han desarrollado **43 casos de prueba unitarios** que validan:
* `test_suma_vectores`, `test_resta_vectores`, `test_multiplicacion_escalar`
* `test_magnitud_pitagoras`, `test_distancia_euclidiana`
* `test_producto_punto`, `test_proyeccion_ortogonal`
* `test_desglose_explicativo` (Generación correcta del log de depuración)
* `test_posicionamiento_barco` (Ecuación paramétrica de celdas)
* `test_tablero_disparos` (Detección de agua, impacto, fuera de límite y colisiones)
* `test_habilidad_suma`, `test_habilidad_viento`, `test_habilidad_sonar`, `test_habilidad_proyeccion_orbital`
* `test_interfaz_grafica.py`: 16 pruebas de la lógica matemática de la interfaz
  gráfica (operaciones del laboratorio y predicción de impacto dentro/fuera).
* `test_juego_grafico.py`: 10 pruebas de la batalla gráfica (costos de
  habilidades, ejecución de cada disparo sobre el tablero, rechazo de vectores
  nulos y smoke test que abre/cierra la ventana).

Para correr la suite completa:
```bash
python3 -m unittest discover -s . -p "test_*.py"
```

---

### 6. Extensiones Pedagógicas Sugeridas para Docentes
* **Rotaciones con Matrices $2 \times 2$:** Agregar una habilidad "Escudo Giratorio" que aplique la matriz de rotación:
  $$R(\theta) = \begin{pmatrix} \cos\theta & -\sin\theta \\ \sin\theta & \cos\theta \end{pmatrix}$$
* **Ampliación a $\mathbb{R}^3$:** Incorporar eje $Z$ (profundidad submarina y altitud aérea de satélites).
