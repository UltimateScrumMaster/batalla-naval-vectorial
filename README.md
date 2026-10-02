# BATALLA NAVAL VECTORIAL
### *Aprende Álgebra Lineal, Pitágoras y Proyecciones Jugando*

Un videojuego educativo desarrollado en **Python** con dos modalidades de visualización:
1. **Cliente Moderno en Godot 4 .NET (C#)** conectado vía WebSockets con gráficos vectoriales dinámicos, animaciones tácticas y consola pedagógica.
2. **Interfaz Clásica de Escritorio** (tkinter + Matplotlib) para ejecución inmediata sin dependencias complejas.

Toda la lógica del juego (álgebra vectorial, batalla por turnos, tutorial, laboratorio, IA y servidor) vive en módulos **puros** dentro del paquete `juego_naval/` (separados en `dominio/`, `logica/`, `servidor/` y `ui/`) y es 100% comprobable mediante pruebas unitarias automatizadas (`unittest`).

---

## Inicio Rápido

### 1. Requisitos Previos
* Python 3.8 o superior.
* Dependencias del sistema:
  ```bash
  pip install -r requirements.txt
  ```

> [!NOTE]
> Se recomienda usar un entorno virtual (`.venv`). El juego incluye en `main.py` y `main_server.py` mecanismos de autodetección del entorno virtual para evitar conflictos con librerías del sistema operativo.

---

### 2. Modos de Ejecución

#### Opción A: Modo Videojuego Moderno (Godot 4 .NET + Servidor Python WebSockets)

> [!TIP]
> **Modo recomendado para estudiantes y ferias:** Ofrece animaciones de vuelo balístico, ondas expansivas de radar, consolas de análisis algebraico en tiempo real y temas visuales personalizables (*Cyber-Navy*, *Fósforo Verde*, *Ámbar*).

1. **Iniciar el Servidor de Cálculo Táctico (Python):**
   ```bash
   ./.venv/bin/python main_server.py
   ```
2. **Abrir el Cliente Gráfico:**
   * Abrir **Godot 4 .NET** e importar la carpeta `cliente_godot/`.
   * Presionar **Play (F5)** para acceder al Menú Principal y comenzar la partida.

#### Opción B: Modo Clásico de Escritorio (Tkinter + Matplotlib)
```bash
./.venv/bin/python main.py
```
*(o simplemente `python3 main.py`: se relanzará con el `.venv` si es necesario).*

---

### 3. Pruebas Unitarias Automatizadas (85 Tests)

El proyecto cuenta con una suite completa de 85 pruebas unitarias que validan el álgebra, la máquina de estados y el servidor de red:

```bash
./.venv/bin/python -m unittest discover -s tests -p "test_*.py"
```

---

### 4. Empaquetado de Ejecutables Autónomos (Standalone)

Para distribuir el juego clásico como un único ejecutable sin requerir instalación de Python en las máquinas de los estudiantes, se utiliza **PyInstaller**:

* **Linux** (genera `dist/BatallaNavalVectorial`):
  ```bash
  bash scripts/build_linux.sh
  ```
* **Windows** (genera `dist\BatallaNavalVectorial.exe`):
  ```bat
  scripts\build_windows.bat
  ```

---

# PARTE 1: GUÍA DIDÁCTICA PARA ESTUDIANTES

Bienvenido al mando de tu flota. Para ganar esta batalla no necesitas disparar a ciegas: vas a utilizar el poder del **álgebra lineal y los vectores** para calcular tus impactos con exactitud matemática.

---

### 1. El Plano Cartesiano: Tu Mapa de Batalla
El mar es un plano de coordenadas $10 \times 10$:
* **Eje X (Horizontal):** Va de izquierda a derecha ($0$ al $9$).
* **Eje Y (Vertical):** Va de abajo hacia arriba ($0$ al $9$).
* **Origen $(0, 0)$:** Es la esquina inferior izquierda.

Un punto o posición se escribe como $(x, y)$. Por ejemplo, si tu fragata está en $(2, 3)$, significa que avanzó $2$ casillas a la derecha y $3$ casillas hacia arriba desde el origen.

---

### 2. ¿Qué es un Vector y Cómo Funciona?
Un vector es un segmento orientado que indica **magnitud, dirección y sentido**:
* $\vec{v} = (3, 2)$ significa: "avanza $3$ casillas a la derecha en $X$, y sube $2$ casillas en $Y$".

---

### 2.1 Diccionario de Vectores

| Concepto | Símbolo | Significado Táctico | Ejemplo Numérico |
| :--- | :---: | :--- | :--- |
| **Posición del barco** | $\vec{P}_{\text{barco}}$ | Punto de partida del disparo en la grilla. | Fragata en $(2, 3)$ |
| **Vector de tiro** | $\vec{V}_{\text{tiro}}$ | Desplazamiento que viaja el proyectil. | $(3, 2)$ = 3 derecha, 2 arriba |
| **Punto de impacto** | $\vec{P}_{\text{impacto}}$ | Casilla de llegada: $\vec{P}_{\text{barco}} + \vec{V}_{\text{tiro}}$. | $(2,3) + (3,2) = (5,5)$ |
| **Vector de viento** | $\vec{V}_{\text{viento}}$ | Desvío por corrientes marinas. | $(1,-1)$ sopla derecha y abajo |
| **Dirección base** | $\vec{u}_{\text{dir}}$ | Orientación unitaria o direccional del torpedo. | $(1,2)$ apunta hacia el cuadrante I |
| **Escalar $k$** | $k$ | Factor multiplicador de potencia (número real). | $k = 3$ triplica el alcance |
| **Vector escalado** | $k \cdot \vec{u}$ | Vector resultante con mayor módulo y mismo sentido. | $3 \cdot (1,2) = (3,6)$ |
| **Vector diferencia** | $\Delta \vec{v} = \vec{T} - \vec{P}$ | Distancia y dirección entre emisor y objetivo. | De $(2,3)$ a $(5,7)$: $\Delta\vec{v} = (3,4)$ |
| **Módulo / Magnitud** | $\|\vec{v}\|$ | Longitud euclidiana del vector. | $\|(3,4)\| = \sqrt{3^2+4^2} = 5$ |
| **Vector de ataque** | $\vec{V}_{\text{ataque}}$ | Vector direccional del Cañón Orbital. | $(3,4)$ dirección del ataque |
| **Vector base radar** | $\vec{U}_{\text{radar}}$ | Eje sobre el cual se proyecta la sombra ortogonal. | $(1,0)$ eje horizontal |
| **Proyección** | $\text{proj}_{\vec{U}}(\vec{V})$ | Sombra perpendicular proyectada sobre el eje. | $\text{proj}_{(1,0)}((3,4)) = (3,0)$ |

> [!NOTE]
> **Regla nemotécnica:** Los símbolos con $\vec{P}$ representan **posiciones fijas** en el tablero, mientras que las letras $\vec{V}$ y $\vec{u}$ representan **vectores de desplazamiento**.

---

### 3. Las 5 Habilidades Vectoriales

#### 1. Disparo Vectorial Simple (Suma de Vectores en $\mathbb{R}^2$)
* **Concepto:** Suma componente a componente entre el vector de posición del barco y el vector de disparo.
* **Fórmula:**

$$
\vec{P}_{\text{impacto}} = \vec{P}_{\text{barco}} + \vec{v}_{\text{disparo}} = (x_1 + x_2, \; y_1 + y_2)
$$

---

#### 2. Artillería con Viento (Suma Múltiple y Compensación Vectorial)
* **Concepto:** El proyectil es afectado por la corriente marina $\vec{w}_{\text{viento}}$. Para impactar un objetivo $\vec{T}$, se debe compensar el viento restándolo: $\vec{v} = \vec{T} - \vec{P} - \vec{w}$.
* **Fórmula:**

$$
\vec{P}_{\text{impacto}} = \vec{P}_{\text{barco}} + \vec{v}_{\text{disparo}} + \vec{w}_{\text{viento}}
$$

---

#### 3. Torpedo Escalar (Multiplicación por un Escalar $k \in \mathbb{R}$)
* **Concepto:** Se fija una dirección base $\vec{u}$ y se multiplica por un escalar de potencia $k$, expandiendo su alcance en línea recta.
* **Fórmula:**

$$
k \cdot \vec{u} = (k \cdot u_x, \; k \cdot u_y)
$$

$$
\vec{P}_{\text{impacto}} = \vec{P}_{\text{barco}} + (k \cdot \vec{u})
$$

---

#### 4. Sónar Acústico de Gauss (Módulo Euclidiano y Teorema de Pitágoras)
* **Concepto:** Emite una onda acústica bajo el agua y calcula la distancia euclidiana exacta al navío enemigo más cercano.
* **Fórmula:**

$$
d = \|\Delta \vec{v}\| = \sqrt{(\Delta x)^2 + (\Delta y)^2} = \sqrt{(x_2 - x_1)^2 + (y_2 - y_1)^2}
$$

---

#### 5. Cañón de Proyección Orbital (Proyección Ortogonal)
* **Concepto:** El satélite calcula la proyección ortogonal de $\vec{v}$ sobre $\vec{u}$ y emite un haz de energía que barre todas las celdas a lo largo de la sombra proyectada.
* **Fórmula:**

$$
\text{proj}_{\vec{u}}(\vec{v}) = \left( \frac{\vec{v} \cdot \vec{u}}{\|\vec{u}\|^2} \right) \vec{u}
$$

---

### 4. Símbolos en los Tableros de Combate

| Símbolo | Significado Táctico |
| :---: | :--- |
| `[·]` | Agua inexplorada (Niebla de guerra) |
| `[B]` / Casilla Verde | Buque aliado a flote |
| `[X]` / Casilla Roja | Impacto certero en un navío |
| `[-]` / Cruz Azul | Disparo al agua (Fallo) |
| `[O]` / Anillo Pulsante | Onda de sónar acústico activo |
| `[>]` / Trazo Naranja | Casilla barrida por el Cañón Orbital |

---

# PARTE 2: DOCUMENTACIÓN TÉCNICA PARA DOCENTES/INGENIEROS/DEVS etc.

---

### 1. Arquitectura del Software y Modularidad

El sistema implementa una arquitectura en capas desacopladas (**Separation of Concerns - SoC**), donde la lógica matemática no depende de frameworks gráficos y puede operar como microservicio WebSocket independiente:

```
proyecto_vector/
├── main.py                    # Entry point interfaz clasica Tkinter + Matplotlib
├── main_server.py             # Entry point del servidor WebSocket asincrono
├── requirements.txt           # Dependencias de runtime (matplotlib, pillow, websockets)
├── README.md
├── juego_naval/               # Paquete principal
│   ├── app.py                 # Composicion y registro central de pantallas
│   ├── diag.py                # Diagnostico en consola ([diag], silenciable)
│   ├── servidor/              # Servidor WebSocket (asyncio + websockets + JSON-RPC)
│   │   ├── __init__.py
│   │   └── ws_server.py       #   Gestion de sesiones remotas y serializacion JSON
│   ├── dominio/               # ESTRUCTURA DEL JUEGO: Entidades y geometria pura
│   │   ├── vector2d.py        #   Clase algebraica Vector2D (Espacio R^2)
│   │   ├── barco.py           #   Entidad Barco (Geometria parametrica discreta Z^2)
│   │   └── tablero.py         #   Plano Cartesiano 2D, colisiones e indexacion
│   ├── logica/                # REGLAS Y LOGICA: Modulos puros sin dependencias UI
│   │   ├── habilidades.py     #   Patron Strategy para operaciones de combate
│   │   ├── ia.py              #   Inteligencia Artificial (Paridad + Caza Ortogonal)
│   │   ├── sesion.py          #   Sesion de partida (Maquina de estados finita)
│   │   ├── tutorial.py        #   Contenido y evaluacion de misiones guiadas
│   │   ├── laboratorio.py     #   Calculadora y funciones puras de laboratorio
│   │   └── guia.py            #   Manual y catalogo algebraico
│   └── ui/                    # Capa clasica Tkinter + Matplotlib
│       ├── gestor_pantallas.py
│       ├── pantalla_base.py
│       └── pantallas/
├── cliente_godot/             # CLIENTE GODOT 4 .NET (C#)
│   ├── project.godot          #   Configuracion Godot 4
│   ├── BatallaNavalVectorial.csproj # Proyecto .NET 8
│   ├── Scenes/                #   Escenas (MainMenu.tscn, Battle.tscn)
│   └── Scripts/               #   Scripts C# (Network, UI, Protocol DTOs, Settings)
├── tests/                     # Suite de pruebas automatizadas (85 tests)
└── scripts/                   # Scripts de build y empaquetado standalone
```

---

### 2. Formalización Matemática

#### A. Espacio Vectorial Bidimensional $\mathbb{R}^2$
Sea el espacio vectorial $V = (\mathbb{R}^2, +, \cdot)$ sobre el cuerpo $\mathbb{R}$. Todo vector $\vec{v} \in V$ se representa formalmente por el par ordenado:

$$
\vec{v} = \begin{pmatrix} x \\ y \end{pmatrix} \in \mathbb{R}^2
$$

#### B. Parametrización Discreta de Navíos en la Grilla $\mathbb{Z}^2$
Un navío de longitud $L \in \mathbb{N}$ con origen $\vec{P}_0 \in \mathbb{Z}^2$ y vector director unitario $\vec{u} \in \{(1,0), (0,1), (-1,0), (0,-1)\}$ se define formalmente como el conjunto discreto:

$$
\mathcal{S} = \{ \vec{P}_0 + i \cdot \vec{u} \mid i \in \{0, 1, \dots, L - 1\} \}
$$

#### C. Producto Escalar Canónico (Dot Product)
Dados $\vec{u}, \vec{v} \in \mathbb{R}^2$, el producto interno canónico se define como:

$$
\langle \vec{u}, \vec{v} \rangle = \vec{u} \cdot \vec{v} = u_x v_x + u_y v_y = \|\vec{u}\| \|\vec{v}\| \cos(\theta)
$$

#### D. Proyección Vectorial Ortogonal
La proyección ortogonal del vector $\vec{v}$ sobre el subespacio generado por la base $\vec{u} \neq \vec{0}$ es:

$$
\text{proj}_{\vec{u}}(\vec{v}) = \left( \frac{\vec{v} \cdot \vec{u}}{\|\vec{u}\|^2} \right) \vec{u} = \left( \frac{v_x u_x + v_y u_y}{u_x^2 + u_y^2} \right) \begin{pmatrix} u_x \\ u_y \end{pmatrix}
$$

La rasterización de la trayectoria proyectada en el plano utiliza una interpolación lineal paramétrica:

$$
\vec{r}(t) = \vec{P}_{\text{origen}} + t \cdot \text{proj}_{\vec{u}}(\vec{v}), \quad t \in [0, 1]
$$

---

### 3. Inteligencia Artificial Enemiga (`juego_naval/logica/ia.py`)

La IA implementa una máquina de estados finita con lógica vectorial:

1. **Fase de Exploración (Paridad Cartesiana):** Selecciona casillas con paridad $(x + y) \equiv 0 \pmod 2$ para maximizar la cobertura del plano reduciendo en un $50\%$ las búsquedas ciegas.
2. **Cálculo de Desplazamiento Vectorial:** Dado el objetivo elegido $\vec{T}$ y el barco emisor $\vec{P}_{\text{emisor}}$, la IA calcula:

$$
\vec{v}_{\text{tiro}} = \vec{T} - \vec{P}_{\text{emisor}}
$$

3. **Fase de Cacería (Gradiente Ortogonal):** Al registrar un impacto exitoso en $\vec{P}_{\text{hit}}$, encola los cuatro vectores adyacentes unitarios:

$$
\mathcal{N} = \{ \vec{P}_{\text{hit}} + (1, 0), \; \vec{P}_{\text{hit}} + (-1, 0), \; \vec{P}_{\text{hit}} + (0, 1), \; \vec{P}_{\text{hit}} + (0, -1) \}
$$

---

### 4. Cobertura de Pruebas Unitarias (85 Tests)

La suite de pruebas automatizadas valida:
* `tests/test_vector2d.py` (9): Álgebra lineal (suma, resta, escalar, módulo, distancia, producto punto, proyecciones, explicaciones didácticas).
* `tests/test_juego.py` (7): Geometría de barcos, colisiones, límites de mapa y habilidades.
* `tests/test_laboratorio.py` (16): Cálculo puro y funciones del laboratorio interactivo.
* `tests/test_sesion.py` (23): Máquina de estados de batalla, energía, viento, victoria y turnos de IA.
* `tests/test_tutorial.py` (10): Validación y evaluación de las 3 misiones guiadas.
* `tests/test_servidor.py` (20): Servidor WebSocket asíncrono, eventos JSON, previsualizaciones en tiempo real y resolución de turnos.

Comando para ejecutar la suite completa:
```bash
./.venv/bin/python -m unittest discover -s tests -p "test_*.py"
```

---

### 5. Extensiones Pedagógicas Sugeridas para Docentes

> [!TIP]
> **Rotaciones con Matrices $2 \times 2$:**
> Se puede incorporar una habilidad "Escudo Giratorio" o "Desvío Angular" aplicando la matriz canónica de rotación:
> 
> $$
> R(\theta) = \begin{pmatrix} \cos\theta & -\sin\theta \\ \sin\theta & \cos\theta \end{pmatrix}
> $$

> [!NOTE]
> **Ampliación al Espacio Tridimensional $\mathbb{R}^3$:**
> Incorporar una tercera coordenada $Z$ para modelar profundidad submarina (torpedos y sónar 3D) y altitud aérea (ataques con satélites y aviones de reconocimiento).
