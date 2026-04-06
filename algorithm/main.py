import tkinter as tk
from tkinter import font as tkfont
from building import NODES, EDGES, EXITS, BUILDING_NAME
from algorithms import build_graph, bfs, dfs

CANVAS_W = 760
CANVAS_H = 580
R        = 26   # node half-height (pill shape)
RX       = 48   # node half-width  (pill shape)

GRAPH = build_graph(EDGES)

# ── Palette — matches the screenshot ─────────────────────────────
COL_BG          = "#f7f7f5"      # off-white canvas
COL_PANEL_BG    = "#ffffff"
COL_EDGE        = "#cccccc"      # default grey edge
COL_EDGE_PATH   = "#e07820"      # orange active path
COL_EDGE_BLOCK  = "#e03030"      # red dashed blocked

COL_NODE_FILL   = "#ffffff"      # normal room fill
COL_NODE_BD     = "#cccccc"      # normal room border
COL_NODE_TEXT   = "#222222"

COL_PATH_FILL   = "#ffffff"
COL_PATH_BD     = "#e07820"      # orange border on path nodes

COL_EXIT_FILL   = "#4a9e5c"      # green pill
COL_EXIT_TEXT   = "#ffffff"

COL_PIN_RED     = "#d93025"      # "You" teardrop
COL_PIN_GLOW    = "#f8c8c8"      # soft red glow circle

COL_INCIDENT_FILL = "#f0e0e0"    # pale red for blocked node
COL_INCIDENT_BD   = "#cccccc"
COL_INCIDENT_BADGE= "#d93025"    # red badge circle

COL_WARN_BG     = "#fdf3e3"      # amber warning bar
COL_WARN_BORDER = "#e8a020"
COL_WARN_TEXT   = "#a06010"

COL_PANEL_DIV   = "#eeeeee"
COL_ROUTE_HDR   = "#999999"
COL_ROUTE_TEXT  = "#111111"
COL_STEP_NUM_BG = "#e0e0e0"
COL_STEP_NUM_FG = "#666666"
COL_EXIT_GREEN  = "#4a9e5c"
COL_SWIPE_TEXT  = "#aaaaaa"
COL_MUTED       = "#999999"

# Sidebar
COL_SIDE_BG     = "#ffffff"
COL_SIDE_BD     = "#e8e8e8"
COL_BTN_BFS_BG  = "#e07820"
COL_BTN_BFS_FG  = "#ffffff"
COL_BTN_INC_BG  = "#d93025"
COL_BTN_INC_FG  = "#ffffff"
COL_BTN_RST_BG  = "#eeeeee"
COL_BTN_RST_FG  = "#555555"


class App:
    def __init__(self, root):
        self.root       = root
        self.pin        = None
        self.incidents  = set()   # blocked node ids
        self.bfs_path   = []

        root.title(BUILDING_NAME)
        root.configure(bg=COL_BG)
        root.resizable(False, False)

        self._setup_fonts()
        self._build_ui()
        self._draw()

    # ── Fonts ─────────────────────────────────────────────────────
    def _setup_fonts(self):
        fam = next((f for f in ("SF Pro Display", "Helvetica Neue", "Helvetica")
                    if f in tkfont.families()), "Helvetica")
        self.f_node    = tkfont.Font(family=fam, size=10)
        self.f_exit    = tkfont.Font(family=fam, size=10, weight="bold")
        self.f_pin_lbl = tkfont.Font(family=fam, size=8,  weight="bold")
        self.f_badge   = tkfont.Font(family=fam, size=9,  weight="bold")
        self.f_blocked = tkfont.Font(family=fam, size=8)
        self.f_warn    = tkfont.Font(family=fam, size=10, weight="bold")
        self.f_hdr     = tkfont.Font(family=fam, size=8,  weight="bold")
        self.f_route   = tkfont.Font(family=fam, size=11, weight="bold")
        self.f_step    = tkfont.Font(family=fam, size=10)
        self.f_finish  = tkfont.Font(family=fam, size=10, weight="bold")
        self.f_num     = tkfont.Font(family=fam, size=8,  weight="bold")
        self.f_swipe   = tkfont.Font(family=fam, size=9)
        self.f_side_hd = tkfont.Font(family=fam, size=10, weight="bold")
        self.f_side    = tkfont.Font(family=fam, size=9)
        self.f_btn     = tkfont.Font(family=fam, size=9,  weight="bold")

    # ── UI ────────────────────────────────────────────────────────
    def _build_ui(self):
        # ── Warning bar ───────────────────────────────────────────
        self.warn_outer = tk.Frame(self.root, bg=COL_WARN_BG,
                                   highlightbackground=COL_WARN_BORDER,
                                   highlightthickness=1)
        self.warn_outer.pack(fill="x")
        self.warn_label = tk.Label(
            self.warn_outer,
            text="Click a room to drop your pin, then press  Run BFS",
            bg=COL_WARN_BG, fg=COL_WARN_TEXT,
            font=self.f_warn, anchor="w", padx=16, pady=8
        )
        self.warn_label.pack(fill="x")

        # ── Main row: canvas + sidebar ────────────────────────────
        main_row = tk.Frame(self.root, bg=COL_BG)
        main_row.pack(fill="both", expand=True)

        # Canvas
        self.canvas = tk.Canvas(
            main_row, width=CANVAS_W, height=CANVAS_H,
            bg=COL_BG, highlightthickness=0
        )
        self.canvas.pack(side="left")
        self.canvas.bind("<Button-1>", self._on_click)

        # Sidebar
        sidebar = tk.Frame(main_row, bg=COL_SIDE_BG, width=200,
                           highlightbackground=COL_SIDE_BD,
                           highlightthickness=1)
        sidebar.pack(side="right", fill="y")
        sidebar.pack_propagate(False)

        tk.Label(sidebar, text=BUILDING_NAME,
                 bg=COL_SIDE_BG, fg="#333333",
                 font=self.f_side_hd, wraplength=180,
                 justify="left", anchor="w").pack(anchor="w", padx=16, pady=(18, 4))

        tk.Label(sidebar,
                 text="① Click a room\n② Run BFS for shortest path\n③ Add Incident to block a room",
                 bg=COL_SIDE_BG, fg=COL_MUTED,
                 font=self.f_side, justify="left", anchor="w").pack(anchor="w", padx=16, pady=(0, 14))

        tk.Frame(sidebar, bg=COL_SIDE_BD, height=1).pack(fill="x", padx=16, pady=(0, 12))

        def pill_btn(text, cmd, bg, fg):
            tk.Button(sidebar, text=text, command=cmd,
                      bg=bg, fg=fg, activebackground=bg, activeforeground=fg,
                      font=self.f_btn, relief="flat", bd=0,
                      cursor="hand2", padx=0, pady=8,
                      width=18).pack(padx=16, pady=3, fill="x")

        pill_btn("▶  Run BFS",        self._run_bfs,      COL_BTN_BFS_BG, COL_BTN_BFS_FG)
        pill_btn("⚠  Add Incident",   self._add_incident, COL_BTN_INC_BG, COL_BTN_INC_FG)
        pill_btn("↺  Reset",          self._reset,        COL_BTN_RST_BG, COL_BTN_RST_FG)

        tk.Frame(sidebar, bg=COL_SIDE_BD, height=1).pack(fill="x", padx=16, pady=(12, 8))

        self.log = tk.Text(sidebar, bg="#fafafa", fg="#555555",
                           font=self.f_side, relief="flat", bd=0,
                           wrap="word", state="disabled", cursor="arrow",
                           highlightthickness=0)
        self.log.pack(fill="both", expand=True, padx=16, pady=(0, 16))
        self.log.tag_config("path",  foreground=COL_BTN_BFS_BG)
        self.log.tag_config("warn",  foreground=COL_BTN_INC_BG)
        self.log.tag_config("muted", foreground=COL_MUTED)

        self._log([("Click any room to place your pin.\n", "muted")])

        # ── Bottom panel ──────────────────────────────────────────
        self.panel = tk.Frame(self.root, bg=COL_PANEL_BG,
                              highlightbackground=COL_PANEL_DIV,
                              highlightthickness=1)
        self.panel.pack(fill="x")

        # handle
        tk.Frame(self.panel, bg="#dddddd", height=4, width=36).pack(pady=(8, 0))

        # EVACUATION ROUTE header
        hdr_row = tk.Frame(self.panel, bg=COL_PANEL_BG)
        hdr_row.pack(fill="x", padx=20, pady=(6, 2))
        tk.Label(hdr_row, text="EVACUATION ROUTE",
                 bg=COL_PANEL_BG, fg=COL_ROUTE_HDR,
                 font=self.f_hdr).pack(side="left")

        # Breadcrumb
        self.route_lbl = tk.Label(
            self.panel, text="—",
            bg=COL_PANEL_BG, fg=COL_ROUTE_TEXT,
            font=self.f_route, wraplength=700,
            justify="left", anchor="w", padx=20
        )
        self.route_lbl.pack(fill="x")

        tk.Frame(self.panel, bg=COL_PANEL_DIV, height=1).pack(fill="x", padx=20, pady=5)

        self.steps_frame = tk.Frame(self.panel, bg=COL_PANEL_BG)
        self.steps_frame.pack(fill="x", padx=20)

        # bottom warning + Finish row
        bot_row = tk.Frame(self.panel, bg=COL_PANEL_BG)
        bot_row.pack(fill="x", padx=20, pady=(4, 2))
        self.bot_warn_lbl = tk.Label(bot_row, text="",
                                     bg=COL_PANEL_BG, fg=COL_BTN_INC_BG,
                                     font=self.f_step, anchor="w")
        self.bot_warn_lbl.pack(side="left")
        tk.Label(bot_row, text="Finish", bg=COL_PANEL_BG,
                 fg=COL_EXIT_GREEN, font=self.f_finish).pack(side="right")

        tk.Label(self.panel, text="Swipe up for directions  ∧",
                 bg=COL_PANEL_BG, fg=COL_SWIPE_TEXT,
                 font=self.f_swipe).pack(pady=(2, 10))

    # ── Drawing ───────────────────────────────────────────────────
    def _draw(self):
        self.canvas.delete("all")

        path_edge_set = set()
        for i in range(len(self.bfs_path) - 1):
            a, b = self.bfs_path[i], self.bfs_path[i+1]
            path_edge_set.add((min(a, b), max(a, b)))

        # ── Edges ─────────────────────────────────────────────────
        for a, b in EDGES:
            x1, y1 = NODES[a][1], NODES[a][2]
            x2, y2 = NODES[b][1], NODES[b][2]
            key = (min(a, b), max(a, b))
            a_inc = a in self.incidents
            b_inc = b in self.incidents

            if key in path_edge_set and not a_inc and not b_inc:
                self.canvas.create_line(x1, y1, x2, y2,
                                        fill=COL_EDGE_PATH, width=3)
            elif a_inc or b_inc:
                self.canvas.create_line(x1, y1, x2, y2,
                                        fill=COL_EDGE_BLOCK, width=2,
                                        dash=(6, 4))
            else:
                self.canvas.create_line(x1, y1, x2, y2,
                                        fill=COL_EDGE, width=2)

        # ── Nodes ─────────────────────────────────────────────────
        for nid, (label, x, y) in NODES.items():
            is_exit    = nid in EXITS
            is_pin     = nid == self.pin
            is_inc     = nid in self.incidents
            on_path    = nid in self.bfs_path

            rx = RX + 6 if is_exit else RX
            ry = R  + 4 if is_exit else R

            # Choose colours
            if is_exit:
                fill, bd, tc = COL_EXIT_FILL, COL_EXIT_FILL, COL_EXIT_TEXT
            elif is_inc:
                fill, bd, tc = COL_INCIDENT_FILL, COL_INCIDENT_BD, "#aa3333"
            elif on_path:
                fill, bd, tc = COL_PATH_FILL, COL_PATH_BD, COL_NODE_TEXT
            elif is_pin:
                fill, bd, tc = COL_NODE_FILL, "#e07820", COL_NODE_TEXT
            else:
                fill, bd, tc = COL_NODE_FILL, COL_NODE_BD, COL_NODE_TEXT

            # Pill shape via rounded rectangle (simulate with oval + rect)
            self._pill(x, y, rx, ry, fill=fill, outline=bd, width=2)

            # Label
            font = self.f_exit if is_exit else self.f_node
            self.canvas.create_text(x, y, text=label, fill=tc, font=font)

            # Incident badge — red circle with ✕ top-right
            if is_inc:
                bx, by = x + rx - 4, y - ry + 4
                self.canvas.create_oval(bx-13, by-13, bx+13, by+13,
                                        fill=COL_INCIDENT_BADGE,
                                        outline="white", width=2)
                self.canvas.create_text(bx, by, text="✕",
                                        fill="white", font=self.f_badge)
                # "Blocked" label below node
                self.canvas.create_text(x, y + ry + 14,
                                        text="⚠ Blocked",
                                        fill=COL_INCIDENT_BADGE,
                                        font=self.f_blocked)
                # Incident glow behind node
                self.canvas.tag_lower(
                    self.canvas.create_oval(
                        x - rx - 14, y - ry - 14,
                        x + rx + 14, y + ry + 14,
                        fill="#fce8e8", outline=""
                    )
                )

            # "You" pin marker
            if is_pin:
                # Glow
                self.canvas.create_oval(x-22, y-ry-40, x+22, y-ry+6,
                                        fill=COL_PIN_GLOW, outline="")
                # Teardrop body
                self.canvas.create_oval(x-14, y-ry-42, x+14, y-ry-16,
                                        fill=COL_PIN_RED, outline="white", width=2)
                # Pointer triangle
                self.canvas.create_polygon(
                    x, y-ry-4, x-7, y-ry-18, x+7, y-ry-18,
                    fill=COL_PIN_RED, outline=""
                )
                # "You" text
                self.canvas.create_text(x, y-ry-29,
                                        text="You", fill="white",
                                        font=self.f_pin_lbl)

    def _pill(self, cx, cy, rx, ry, **kw):
        """Draw a rounded-rectangle (pill) on the canvas."""
        r = min(rx, ry)
        x0, y0, x1, y1 = cx-rx, cy-ry, cx+rx, cy+ry
        pts = [
            x0+r, y0,  x1-r, y0,
            x1,   y0,  x1,   y0+r,
            x1,   y1-r,x1,   y1,
            x1-r, y1,  x0+r, y1,
            x0,   y1,  x0,   y1-r,
            x0,   y0+r,x0,   y0,
            x0+r, y0,
        ]
        self.canvas.create_polygon(pts, smooth=True, **kw)

    # ── Interaction ───────────────────────────────────────────────
    def _on_click(self, event):
        for nid, (_, x, y) in NODES.items():
            if abs(event.x - x) <= RX + 8 and abs(event.y - y) <= R + 8:
                if nid != self.pin:
                    self.pin      = nid
                    self.bfs_path = []
                    self._draw()
                    self._refresh_panel()
                    name = NODES[nid][0]
                    self._log([("Pin → ", "muted"), (f"{name}\n", "path"),
                               ("Press Run BFS.\n", "muted")])
                return

    def _run_bfs(self):
        if self.pin is None:
            self._log([("Drop your pin first.\n", "warn")]); return

        safe_edges = [(a, b) for a, b in EDGES
                      if a not in self.incidents and b not in self.incidents]
        from algorithms import build_graph as bg
        g = bg(safe_edges)
        path = bfs(self.pin, g, EXITS)
        self.bfs_path = path or []
        self._draw()
        self._refresh_panel(path)

        if path:
            names = [NODES[n][0] for n in path]
            self._log([("BFS shortest path\n", "path")] +
                      [(f"  {n}\n", None) for n in names] +
                      [(f"\n{len(path)-1} step(s) to safety.\n", "path")])
        else:
            self._log([("No exit reachable!\n", "warn")])

    def _add_incident(self):
        if self.pin is None:
            self._log([("Select a room first.\n", "warn")]); return
        if self.pin in EXITS:
            self._log([("Cannot block an EXIT.\n", "warn")]); return
        if self.pin in self.incidents:
            self.incidents.discard(self.pin)
            name = NODES[self.pin][0]
            self._log([("Incident cleared: ", "muted"), (f"{name}\n", "path")])
        else:
            self.incidents.add(self.pin)
            name = NODES[self.pin][0]
            self._log([("Incident added: ", "muted"), (f"{name}\n", "warn"),
                       ("Run BFS to reroute.\n", "muted")])
        self.bfs_path = []
        self._draw()
        self._refresh_panel()

    def _reset(self):
        self.pin       = None
        self.incidents = set()
        self.bfs_path  = []
        self._draw()
        self._refresh_panel()
        self._log([("Reset. Click a room to begin.\n", "muted")])

    # ── Bottom panel ──────────────────────────────────────────────
    def _refresh_panel(self, path=None):
        for w in self.steps_frame.winfo_children():
            w.destroy()

        # Warning bar
        if self.incidents:
            inames = ", ".join(NODES[n][0] for n in self.incidents)
            self.warn_label.config(
                text=f"⚠  {inames} blocked — Find alternate route"
            )
        elif self.pin is None:
            self.warn_label.config(
                text="Click a room to drop your pin, then press  Run BFS"
            )
        else:
            self.warn_label.config(
                text=f"📍  {NODES[self.pin][0]} selected — press Run BFS to find exit"
            )

        if not self.bfs_path:
            self.route_lbl.config(text="—")
            self.bot_warn_lbl.config(text="")
            return

        names = [NODES[n][0] for n in self.bfs_path]
        self.route_lbl.config(text="  →  ".join(names))

        # Step instructions
        steps = names[1:]
        step_texts = []
        for i, s in enumerate(steps):
            if i == 0:
                step_texts.append(f"Go to {s}")
            elif i == len(steps) - 1:
                step_texts.append(None)  # handled separately as "Exit through"
            elif "Stairs" in s:
                step_texts.append(f"Take the stairs")
            elif "Hallway" in s or "Hall" in s:
                step_texts.append(f"Continue straight")
            else:
                step_texts.append(f"Proceed to {s}")

        for i, (txt, node_name) in enumerate(zip(step_texts, steps)):
            row = tk.Frame(self.steps_frame, bg=COL_PANEL_BG, pady=2)
            row.pack(fill="x")

            nc = tk.Canvas(row, width=22, height=22,
                           bg=COL_PANEL_BG, highlightthickness=0)
            nc.pack(side="left", padx=(0, 10))
            nc.create_oval(1, 1, 21, 21, fill=COL_STEP_NUM_BG, outline="")
            nc.create_text(11, 11, text=str(i+1),
                           fill=COL_STEP_NUM_FG, font=self.f_num)

            if i == len(steps) - 1:
                f = tk.Frame(row, bg=COL_PANEL_BG)
                f.pack(side="left")
                tk.Label(f, text="Exit through ",
                         bg=COL_PANEL_BG, fg=COL_NODE_TEXT,
                         font=self.f_step).pack(side="left")
                tk.Label(f, text=node_name,
                         bg=COL_PANEL_BG, fg=COL_EXIT_GREEN,
                         font=self.f_finish).pack(side="left")
            else:
                tk.Label(row, text=txt or f"Proceed to {node_name}",
                         bg=COL_PANEL_BG, fg=COL_NODE_TEXT,
                         font=self.f_step).pack(side="left")

        if self.incidents:
            inames = ", ".join(NODES[n][0] for n in self.incidents)
            self.bot_warn_lbl.config(text=f"⚠  {inames} is blocked")
        else:
            self.bot_warn_lbl.config(text="")

    # ── Log ───────────────────────────────────────────────────────
    def _log(self, segments):
        self.log.config(state="normal")
        self.log.delete("1.0", "end")
        for text, tag in segments:
            if tag:
                self.log.insert("end", text, tag)
            else:
                self.log.insert("end", text)
        self.log.config(state="disabled")


if __name__ == "__main__":
    root = tk.Tk()
    App(root)
    root.mainloop()