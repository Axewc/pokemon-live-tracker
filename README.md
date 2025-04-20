# Pokémon Omega Ruby Live Tracker via Citra GDB Stub + Python  

## 1. Motivación  

Crear una herramienta que permita extraer y visualizar en tiempo real datos de tu partida de **Pokémon Omega Ruby** corriendo en el emulador **Citra**. Con ello podrás:  

- Mostrar tu equipo Pokémon actual con imágenes y sobrenombres.  
- Recibir notificaciones instantáneas al capturar un nuevo Pokémon.  
- Extender la plataforma para monitorizar incubación de huevos, estadísticas de batalla, conteo de ítems, etc.

## 2. Objetivos  

1. **Conectar** al proceso de Citra mediante su GDB Stub.  
2. **Leer** bloques de memoria donde el juego guarda tu equipo.  
3. **Parsear** estructuras de Pokémon (especie, nivel, apodo, etc.).  
4. **Mostrar** en una GUI básica (usando PyQt5/Tkinter) la imagen y apodo de cada miembro del equipo.  
5. Proporcionar un esqueleto fácil de personalizar para añadir nuevos watchpoints y eventos.

---

## 3. Fundamentos teóricos  

### 3.1. Emulación y memoria  

- Citra emula la arquitectura ARM11/ARM9 de la 3DS.  
- Cada juego mapea datos (partida guardada, estado de RAM) en regiones de memoria del proceso emulado.  
- Conocer direcciones y estructuras (offsets) es clave: la documentación de **3DBrew** detalla cómo se organizan las estructuras de Pokémon en memoria.

### 3.2. GDB Remote Serial Protocol (RSP)  

- GDB Stub expone un servidor TCP que habla el RSP.  
- Permite comandos como `m` (read memory), `Z/watchpoint` (poner watchpoints), `qSupported` (negociación inicial).  
- Lee/escribe memoria sin parchear el binario original.

### 3.3. Python + pwntools (o pygdb)  

- **pwntools** facilita conectar a un stub GDB:  

  ```python
  from pwn import gdb
  conn = gdb.debug(None, gdb_args=['--remote','localhost:1234'])
  data = conn.read(0xOFFSET, tamaño)
  ```  

- También puedes usar un cliente RSP puro o incluso `socket` + implementación manual.

### 3.4. Decodificación de estructuras  

- En Python se pueden definir clases con `ctypes.Structure` para mapear bytes a campos:  

  ```python
  class Pokemon(ctypes.Structure):
      _fields_ = [
        ('species_id', ctypes.c_uint16),
        ('level',     ctypes.c_uint8),
        ('nickname',  ctypes.c_char * 10),
        # …
      ]
  ```  

---

## 4. Prerrequisitos  

- **Citra** (versión con GDB Stub habilitado)  
- **Python 3.8+**  
- Librerías Python:  

  ```bash
  pip install pwntools PyQt5 pillow
  ```  

- Conocimientos básicos de Python, GDB y GUI en Python.

---

## 5. Configuración de Citra  

1. Abre Citra y ve a **Emulación → Configuración → Debug**.  
2. Marca **Enable GDB Stub** y anota el puerto (p.ej. `1234`).  
3. Inicia tu ROM de Pokémon Omega Ruby.

---

## 6. Localización de offsets (placeholders)  

> ⚠️ **Importante**: los valores varían según región/version.  
> Usa GDB o Cheat Engine para encontrar:  
>
> - **TEAM_BASE_OFFSET**: dirección donde empieza el array de 6 miembros del equipo.  
> - **POKEMON_STRUCT_SIZE**: tamaño en bytes de cada Pokémon.  
> - **IMAGE_ID_OFFSET**: dentro de la estructura, offset al ID de sprite.  

```text
# Ejemplo de placeholders
TEAM_BASE_OFFSET      = 0x02345678  
POKEMON_STRUCT_SIZE   = 0xA0  
OFFSET_SPECIES_ID     = 0x00  
OFFSET_LEVEL          = 0x02  
OFFSET_NICKNAME       = 0x20
OFFSET_IMAGE_INDEX    = 0x40
```

---

## 7. Implementación en Python  

### 7.1. Conexión al stub GDB  

```python
from pwn import remote
import ctypes

HOST = '127.0.0.1'
PORT = 1234

# Cliente RSP simple
sock = remote(HOST, PORT)

def read_mem(addr: int, length: int) -> bytes:
    # Comando 'm addr,length'
    cmd = f'm{addr:x},{length:x}'.encode() + b'\n'
    sock.send(cmd)
    # Leer respuesta (hex)
    resp = sock.recvuntil(b'\n').strip()
    return bytes.fromhex(resp.decode())
```

### 7.2. Definición de la estructura Pokémon  

```python
class Pokemon(ctypes.Structure):
    _fields_ = [
        ('species_id', ctypes.c_uint16),
        ('level', ctypes.c_uint8),
        ('_pad', ctypes.c_uint8),
        ('nickname', ctypes.c_char * 10),
        ('_unk', ctypes.c_byte * (OFFSET_IMAGE_INDEX - 12)),
        ('image_index', ctypes.c_uint16),
        # …
    ]

def parse_pokemon(raw: bytes) -> Pokemon:
    return Pokemon.from_buffer_copy(raw)
```

### 7.3. Lectura del equipo completo  

```python
def get_team():
    team = []
    for i in range(6):
        addr = TEAM_BASE_OFFSET + i * POKEMON_STRUCT_SIZE
        raw = read_mem(addr, POKEMON_STRUCT_SIZE)
        pkm = parse_pokemon(raw)
        if pkm.species_id == 0:
            continue  # hueco vacío
        team.append(pkm)
    return team
```

---

## 8. GUI básica con PyQt5  

```python
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QHBoxLayout
from PyQt5.QtGui import QPixmap
from PIL import Image

class TeamWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Pokémon Live Tracker")
        self.layout = QHBoxLayout()
        self.setLayout(self.layout)
        self.slots = []
        for _ in range(6):
            v = QVBoxLayout()
            img_lbl = QLabel()
            nick_lbl = QLabel("—")
            v.addWidget(img_lbl)
            v.addWidget(nick_lbl)
            self.layout.addLayout(v)
            self.slots.append((img_lbl, nick_lbl))

    def update_team(self, team):
        for idx, (img_lbl, nick_lbl) in enumerate(self.slots):
            if idx < len(team):
                p = team[idx]
                # Carga sprite local según p.image_index
                pix = QPixmap(f"sprites/{p.image_index}.png")
                img_lbl.setPixmap(pix)
                nick_lbl.setText(p.nickname.decode('utf-8').strip('\x00'))
            else:
                img_lbl.clear()
                nick_lbl.setText("—")
```

Y el bucle principal:

```python
import time

app = QApplication(sys.argv)
win = TeamWindow()
win.show()

def refresh():
    team = get_team()
    win.update_team(team)

# Temporizador simple
from threading import Thread
def ticker():
    while True:
        refresh()
        time.sleep(1.0)

Thread(target=ticker, daemon=True).start()
sys.exit(app.exec_())
```

---

## 9. Ejecución  

1. Descarga/coloca los **sprites** en `./sprites/` nombrados según el índice en memoria.  
2. Ajusta los **offsets** en el script Python.  
3. Ejecuta tu ROM en Citra con GDB Stub activo.  
4. Lanza `python tracker.py` y observa cómo aparece tu equipo en la ventana.

---

## 10. Extensiones futuras  

- **Watchpoints** para notificar capturas/evoluciones (usar `Z/watch` en RSP).  
- Mostrar cajas de PC, estadísticas de IVs/EVs.  
- Integrar con un servidor web (Dash, Flask) para acceso remoto.  
- Guardar historial de capturas en una base de datos SQLite.