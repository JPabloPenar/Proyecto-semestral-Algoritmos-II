import tkinter as tk
from dataclasses import dataclass
from vehicles import vehicle, jeep, moto, auto, camion

# ---------- Configuración visual ----------
BG_APP = "#e3f0ff"
PANEL_BG = "#cfeff7"
TERRAIN_BG = "#ffb578"
BAR_BG = "#cfe2ff"
BORDER = "#333333"

W, H = 1000, 620
SIDE_W = 150
BOTTOM_H = 80

TERRAIN_W = W - SIDE_W * 2 - 20
TERRAIN_H = H - BOTTOM_H - 40

VEHICLES = ["jeep", "moto", "camion", "auto"]

@dataclass
class SpawnSpec:
    kind: str
    x: int
    y: int
    side: str   # "left" o "right"

# ---------------- Clase principal ----------------
class GameUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Proyecto final - Interfaz de juego (Tkinter)")
        self.geometry(f"{W}x{H}")
        self.configure(bg=BG_APP)

        self.vehicles = []  # Lista de objetos vehicle

        self._make_layout()
        self._draw_side_palettes()
        self._draw_terrain_static()
        self._bind_drag()
        self._colocar_vehiculos_iniciales()

    # ===== Layout =====
    def _make_layout(self):
        # Panel izquierdo
        self.left = tk.Canvas(self, width=SIDE_W, height=H - BOTTOM_H - 20,
                              bg=PANEL_BG, highlightthickness=2, highlightbackground=BORDER)
        self.left.place(x=10, y=10)

        # Panel derecho
        self.right = tk.Canvas(self, width=SIDE_W, height=H - BOTTOM_H - 20,
                               bg=PANEL_BG, highlightthickness=2, highlightbackground=BORDER)
        self.right.place(x=W - SIDE_W-10, y=10)

        # Terreno central
        self.terrain = tk.Canvas(self, width=TERRAIN_W-20, height=TERRAIN_H,
                                 bg=TERRAIN_BG, highlightthickness=2, highlightbackground=BORDER)
        self.terrain.place(x=SIDE_W + 20, y=10)

        # Barra inferior con botones
        self.bottom = tk.Frame(self, bg=BAR_BG, height=BOTTOM_H, bd=2, relief="ridge")
        self.bottom.pack(side="bottom", fill="x")

        btns = [
            ("Init", self.on_init),
            ("<<", self.on_step_back),
            ("Play", self.on_play),
            (">>", self.on_step_fwd),
            ("Stop", self.on_stop),
        ]
        for text, cmd in btns:
            b = tk.Button(self.bottom, text=text, command=cmd,
                          font=("Segoe UI", 12, "bold"), width=10)
            b.pack(side="left", padx=18, pady=18)

    # ===== Paletas laterales =====
    def _draw_side_palettes(self):
        self.left.create_text(SIDE_W/2, 18, text="Base 1", font=("Segoe UI", 14, "bold"))
        self.right.create_text(SIDE_W/2, 18, text="Base 2", font=("Segoe UI", 14, "bold"))

        y_positions = [70, 160, 250, 340]
        for side_canvas, side_name in [(self.left, "left"), (self.right, "right")]:
            for y, kind in zip(y_positions, VEHICLES):
                self._draw_vehicle_icon(side_canvas, SIDE_W//2, y, kind, palette=True, side=side_name)

    # ===== Colocar vehículos iniciales =====
    def _colocar_vehiculos_iniciales(self):
        posicion = 25
        incremento = 50

#Equipo 1:
        # Jeep
        for i in range(3):
            v = self._draw_vehicle_icon(self.terrain, 50, posicion, "jeep", equipo=1)
            self.vehicles.append(v)
            posicion += incremento

        # Moto
        for i in range(2):
            v = self._draw_vehicle_icon(self.terrain, 50, posicion, "moto", equipo=1)
            self.vehicles.append(v)
            posicion += incremento

        # Camion
        for i in range(2):
            v = self._draw_vehicle_icon(self.terrain, 50, posicion, "camion", equipo=1)
            self.vehicles.append(v)
            posicion += incremento

        # Auto
        for i in range(3):
            v = self._draw_vehicle_icon(self.terrain, 50, posicion, "auto", equipo=1)
            self.vehicles.append(v)
            posicion += incremento
        posicion=25
#Equipo 2:
        # Jeep
        for i in range(3):
            v = self._draw_vehicle_icon(self.terrain, 620, posicion, "jeep", equipo=2)
            self.vehicles.append(v)
            posicion += incremento

        # Moto
        for i in range(2):
            v = self._draw_vehicle_icon(self.terrain, 620, posicion, "moto", equipo=2)
            self.vehicles.append(v)
            posicion += incremento

        # Camion
        for i in range(2):
            v = self._draw_vehicle_icon(self.terrain, 620, posicion, "camion", equipo=2)
            self.vehicles.append(v)
            posicion += incremento

        # Auto
        for i in range(3):
            v = self._draw_vehicle_icon(self.terrain, 620, posicion, "auto", equipo=2)
            self.vehicles.append(v)
            posicion += incremento


    # ===== Dibujo de vehículos =====
    def _draw_vehicle_icon(self, canvas, x, y, kind, palette=False, side="left", equipo=None):
        tag = f"veh_{kind}_{x}_{y}" if not palette else f"icon_{kind}_{side}"
        if equipo==1:
            color="#ff0000"
        elif equipo==2:
            color="#0400ff"
        elif equipo==None:
            color="#000000"

        # Dibujar forma y crear objeto
        if kind == "jeep":
            canvas.create_polygon(
                x, y - 8,
                x - 9, y - 2,
                x - 7, y + 7,
                x + 7, y + 7,
                x + 9, y - 2,
                fill=color, outline="", tags=tag
            )
            obj = jeep(canvas, x, y, tag, equipo)

        elif kind == "moto":
            canvas.create_polygon(
                x, y - 8,
                x - 7, y + 4,
                x + 7, y + 4,
                fill=color, outline="", tags=tag
            )
            obj = moto(canvas, x, y, tag, equipo)

        elif kind == "camion":
            canvas.create_rectangle(
                x - 10, y - 7, x + 10, y + 7,
                fill=color, outline="", tags=tag
            )
            obj = camion(canvas, x, y, tag, equipo)

        elif kind == "auto":
            canvas.create_oval(
                x - 8, y - 5, x + 8, y + 5,
                fill=color, outline="", tags=tag
            )
            obj = auto(canvas, x, y, tag, equipo)

        else:
            obj = None

        # Si es paleta, bind click
        if palette:
            canvas.tag_bind(tag, "<Button-1>",
                            lambda e, k=kind, s=side: self.spawn_from_palette(
                                SpawnSpec(k, 70 if s=="left" else TERRAIN_W-70, 80, s)))
            canvas.create_text(x, y+38, text=kind.capitalize(), font=("Segoe UI", 9), fill="#333")

        return obj

    # ===== Terreno estático y minas =====
    def _draw_terrain_static(self):
        self.terrain.create_text(TERRAIN_W/2, 18, text="Terreno de Acción",
                                 font=("Segoe UI", 16, "bold"))

        def mine_circle(x, y, r, label):
            self.terrain.create_oval(x-r, y-r, x+r, y+r, fill="#6c8a6b", outline=BORDER)
            self.terrain.create_oval(x-r+10, y-r+10, x+r-10, y+r-10, fill="#3f5c3f", outline=BORDER)
            self.terrain.create_text(x, y-28, text=f"Mina {label}", font=("Segoe UI", 12, "bold"))

        def mine_tripwire(x1, y1, x2, y2, label):
            self.terrain.create_line(x1, y1, x2, y2, width=4, fill="#aaa")
            self.terrain.create_text((x1+x2)//2, min(y1, y2)-18, text=f"Mina {label}", font=("Segoe UI", 12, "bold"))

        mine_circle(180, 120, 42, "O1")
        mine_circle(360, 110, 26, "O2")
        mine_tripwire(120, 220, 220, 220, "T1")
        mine_tripwire(320, 200, 320, 300, "T2")

        xg, yg, rg = 120, 320, 42
        self.terrain.create_oval(xg-rg, yg-rg, xg+rg, yg+rg, fill="#b8c1cc", outline=BORDER)
        self.terrain.create_oval(xg-18, yg-18, xg+18, yg+18, fill="#7c8794", outline=BORDER)
        self.terrain.create_line(xg, yg-14, xg, yg+14, width=3)
        self.terrain.create_text(xg, yg-58, text="Mina G1", font=("Segoe UI", 12, "bold"))

    # ===== Spawn desde paleta =====
    def spawn_from_palette(self, spec: SpawnSpec):
        x, y = spec.x, spec.y
        obj = self._draw_vehicle_icon(self.terrain, x, y, spec.kind, palette=False, equipo=1)
        self.vehicles.append(obj)

        last_items = self.terrain.find_all()[-4:]
        drag_tag = f"draggable_{last_items[-1]}"
        for it in last_items:
            self.terrain.addtag_withtag(drag_tag, it)

        self.terrain.move(drag_tag, 0, 30)
        self.terrain.tag_bind(drag_tag, "<Button-1>", self._on_drag_start)
        self.terrain.tag_bind(drag_tag, "<B1-Motion>", self._on_drag_move)

    # ===== Drag genérico =====
    def _bind_drag(self):
        self.drag_data = {"x": 0, "y": 0, "tag": None}

    def _on_drag_start(self, event):
        self.drag_data["x"] = event.x
        self.drag_data["y"] = event.y
        tags = self.terrain.gettags("current")
        dd = [t for t in tags if t.startswith("draggable_")]
        self.drag_data["tag"] = dd[0] if dd else None

    def _on_drag_move(self, event):
        if not self.drag_data["tag"]:
            return
        dx = event.x - self.drag_data["x"]
        dy = event.y - self.drag_data["y"]
        self.terrain.move(self.drag_data["tag"], dx, dy)
        self.drag_data["x"] = event.x
        self.drag_data["y"] = event.y

    # ===== Botones =====
    def on_init(self):
        self.terrain.delete("all")
        self._draw_terrain_static()

    def on_play(self):
        print("[Play] Lógica de simulación aquí")

    def on_stop(self):
        print("[Stop] Detener simulación")

    def on_step_back(self):
        print("[<<] Paso atrás")

    def on_step_fwd(self):
        print("[>>] Paso adelante")

# ---------------- Main ----------------
if __name__ == "__main__":
    GameUI().mainloop()
