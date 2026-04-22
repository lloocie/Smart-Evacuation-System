import tkinter as tk
from tkinter import font as tkfont
from building import NODES, EDGES, EDGES_WEIGHTED, EXITS, BUILDING_NAME
from algorithms import build_weighted_graph, dijkstra_shortest_path

# ==================== LARGER CANVAS ====================
CANVAS_W = 1000
CANVAS_H = 800
RX = 50
RY = 28

# SIMPLIFIED HIGH-CONTRAST COLORS
COLORS = {
    'bg':            '#2c3e50',
    'canvas_bg':     '#f0f0f0',
    'sidebar_bg':    '#ffffff',
    'sidebar_border': '#b0b0b0',
    'edge':          '#888888',
    'edge_path':     '#ff8c00',
    'edge_blocked':  '#ff0000',
    'node_fill':     '#ffffff',
    'node_border':   '#333333',
    'node_text':     '#000000',
    'path_border':   '#ff8c00',
    'exit_fill':     '#2ecc71',
    'exit_text':     '#ffffff',
    'pin_red':       '#e74c3c',
    'pin_glow':      '#ffcccc',
    'incident_fill': '#ffdddd',
    'incident_badge':'#ff0000',
    'incident_text': '#ff0000',
    'warn_bg':       '#fff3cd',
    'warn_border':   '#ffc107',
    'warn_text':     '#856404',
    'btn_primary':   '#ff8c00',
    'btn_primary_hover': '#e07c00',
    'btn_primary_text':  '#ffffff',
    'btn_danger':    '#ff0000',
    'btn_danger_hover': '#cc0000',
    'btn_danger_text':  '#ffffff',
    'btn_secondary': '#6c757d',
    'btn_secondary_hover': '#5a6268',
    'btn_secondary_text': '#ffffff',
    'log_success':   '#ff8c00',
    'log_warn':      '#ff0000',
    'log_info':      '#6c757d',
    'route_header':  '#6c757d',
    'route_text':    '#000000',
    'step_num_bg':   '#dddddd',
    'step_num_fg':   '#000000',
    'exit_green':    '#2ecc71',
}

# Build weighted graph from explicit distances
GRAPH_ADJ, EDGE_WEIGHTS = build_weighted_graph(EDGES_WEIGHTED)


class EvacuationApp:
    def __init__(self, root):
        self.root = root
        self.pin = None
        self.incidents = set()
        self.current_path = None
        self.current_distance = None

        self._setup_window()
        self._setup_fonts()
        self._build_ui()
        self._draw()
        self._update_all()

    def _setup_window(self):
        self.root.title(f"{BUILDING_NAME} – Evacuation Planner (weighted Dijkstra)")
        self.root.configure(bg=COLORS['bg'])
        self.root.geometry("1260x950")
        self.root.resizable(False, False)

    def _setup_fonts(self):
        fam = next((f for f in ("Segoe UI", "Helvetica Neue", "Helvetica")
                    if f in tkfont.families()), "Helvetica")
        self.fonts = {
            'node':      tkfont.Font(family=fam, size=10),
            'exit':      tkfont.Font(family=fam, size=10, weight="bold"),
            'pin_label': tkfont.Font(family=fam, size=8, weight="bold"),
            'badge':     tkfont.Font(family=fam, size=9, weight="bold"),
            'blocked':   tkfont.Font(family=fam, size=8),
            'warning':   tkfont.Font(family=fam, size=10, weight="bold"),
            'header':    tkfont.Font(family=fam, size=9, weight="bold"),
            'route':     tkfont.Font(family=fam, size=11, weight="bold"),
            'step':      tkfont.Font(family=fam, size=10),
            'finish':    tkfont.Font(family=fam, size=10, weight="bold"),
            'number':    tkfont.Font(family=fam, size=8, weight="bold"),
            'title':     tkfont.Font(family=fam, size=12, weight="bold"),
            'sidebar':   tkfont.Font(family=fam, size=9),
            'button':    tkfont.Font(family=fam, size=9, weight="bold"),
            'distance':  tkfont.Font(family=fam, size=9, weight="bold"),
        }

    # ---------- UI Construction ----------
    def _build_ui(self):
        self.warn_frame = tk.Frame(self.root, bg=COLORS['warn_bg'],
                                   highlightbackground=COLORS['warn_border'],
                                   highlightthickness=1)
        self.warn_frame.pack(fill="x")
        self.warn_label = tk.Label(self.warn_frame, text="",
                                   bg=COLORS['warn_bg'], fg=COLORS['warn_text'],
                                   font=self.fonts['warning'], anchor="w",
                                   padx=16, pady=8)
        self.warn_label.pack(fill="x")

        main_row = tk.Frame(self.root, bg=COLORS['bg'])
        main_row.pack(fill="both", expand=True)

        self.canvas = tk.Canvas(main_row, width=CANVAS_W, height=CANVAS_H,
                                bg=COLORS['canvas_bg'], highlightthickness=0)
        self.canvas.pack(side="left", padx=10, pady=10)
        self.canvas.bind("<Button-1>", self._on_canvas_click)

        self._build_sidebar(main_row)
        self._build_bottom_panel()

    def _build_sidebar(self, parent):
        sidebar = tk.Frame(parent, bg=COLORS['sidebar_bg'], width=260,
                           highlightbackground=COLORS['sidebar_border'],
                           highlightthickness=1)
        sidebar.pack(side="right", fill="y")
        sidebar.pack_propagate(False)

        tk.Label(sidebar, text=BUILDING_NAME,
                 bg=COLORS['sidebar_bg'], fg='#000000',
                 font=self.fonts['title'], anchor="w").pack(anchor="w", padx=16, pady=(20, 8))

        tk.Label(sidebar,
                 text="1. Click a room\n2. Block room (if needed)\n3. Shortest PHYSICAL path",
                 bg=COLORS['sidebar_bg'], fg='#333333',
                 font=self.fonts['sidebar'], justify="left", anchor="w").pack(anchor="w", padx=16, pady=(0, 20))

        tk.Frame(sidebar, bg=COLORS['sidebar_border'], height=1).pack(fill="x", padx=16, pady=(0, 16))

        self._add_button(sidebar, "▶  FIND ROUTE", self._manual_recalc,
                         COLORS['btn_primary'], COLORS['btn_primary_hover'], COLORS['btn_primary_text'])
        self._add_button(sidebar, "⚠  BLOCK ROOM", self._toggle_incident,
                         COLORS['btn_danger'], COLORS['btn_danger_hover'], COLORS['btn_danger_text'])
        self._add_button(sidebar, "↺  RESET", self._reset,
                         COLORS['btn_secondary'], COLORS['btn_secondary_hover'], COLORS['btn_secondary_text'])

        tk.Frame(sidebar, bg=COLORS['sidebar_border'], height=1).pack(fill="x", padx=16, pady=(16, 12))

        log_frame = tk.Frame(sidebar, bg=COLORS['sidebar_bg'])
        log_frame.pack(fill="both", expand=True, padx=16, pady=(0, 16))
        tk.Label(log_frame, text="ACTIVITY LOG", bg=COLORS['sidebar_bg'],
                 fg='#333333', font=self.fonts['header'], anchor="w").pack(fill="x")

        self.log = tk.Text(log_frame, bg='#f8f8f8', fg='#000000',
                           font=self.fonts['sidebar'], relief="flat", bd=0,
                           wrap="word", state="disabled", cursor="arrow",
                           highlightthickness=1, highlightbackground=COLORS['sidebar_border'],
                           height=10)
        self.log.pack(fill="both", expand=True, pady=(4, 0))
        self.log.tag_config("success", foreground=COLORS['log_success'])
        self.log.tag_config("warn", foreground=COLORS['log_warn'])
        self.log.tag_config("info", foreground=COLORS['log_info'])

        self._log("Ready. Click a room.", "info")

    def _add_button(self, parent, text, command, bg, hover_bg, fg):
        btn = tk.Button(parent, text=text, command=command,
                        bg=bg, fg=fg, activebackground=hover_bg,
                        activeforeground=fg, font=self.fonts['button'],
                        relief="raised", bd=1, cursor="hand2",
                        padx=0, pady=10, width=24)
        btn.pack(padx=16, pady=6, fill="x")
        btn.bind("<Enter>", lambda e: btn.config(bg=hover_bg, relief="sunken"))
        btn.bind("<Leave>", lambda e: btn.config(bg=bg, relief="raised"))
        return btn

    def _build_bottom_panel(self):
        self.panel = tk.Frame(self.root, bg=COLORS['sidebar_bg'],
                              highlightbackground=COLORS['sidebar_border'],
                              highlightthickness=1)
        self.panel.pack(fill="x")

        tk.Frame(self.panel, bg='#cccccc', height=3, width=50).pack(pady=(6, 0))

        hdr = tk.Frame(self.panel, bg=COLORS['sidebar_bg'])
        hdr.pack(fill="x", padx=20, pady=(8, 4))
        tk.Label(hdr, text="EVACUATION ROUTE (shortest physical distance)",
                 bg=COLORS['sidebar_bg'], fg=COLORS['route_header'],
                 font=self.fonts['header']).pack(side="left")
        self.distance_label = tk.Label(hdr, text="", bg=COLORS['sidebar_bg'],
                                       fg=COLORS['btn_primary'], font=self.fonts['distance'])
        self.distance_label.pack(side="right")

        self.route_lbl = tk.Label(self.panel, text="—", bg=COLORS['sidebar_bg'],
                                  fg=COLORS['route_text'], font=self.fonts['route'],
                                  anchor="w", padx=20)
        self.route_lbl.pack(fill="x")

        tk.Frame(self.panel, bg=COLORS['sidebar_border'], height=1).pack(fill="x", padx=20, pady=6)

        self.steps_frame = tk.Frame(self.panel, bg=COLORS['sidebar_bg'])
        self.steps_frame.pack(fill="x", padx=20)

        bot = tk.Frame(self.panel, bg=COLORS['sidebar_bg'])
        bot.pack(fill="x", padx=20, pady=(8, 10))
        self.block_warn = tk.Label(bot, text="", bg=COLORS['sidebar_bg'],
                                   fg=COLORS['btn_danger'], font=self.fonts['step'])
        self.block_warn.pack(side="left")
        tk.Label(bot, text="EXIT", bg=COLORS['sidebar_bg'],
                 fg=COLORS['exit_green'], font=self.fonts['finish']).pack(side="right")

    # ---------- Drawing ----------
    def _draw(self):
        self.canvas.delete("all")

        path_edges = set()
        if self.current_path:
            for i in range(len(self.current_path) - 1):
                a, b = self.current_path[i], self.current_path[i+1]
                path_edges.add((min(a, b), max(a, b)))

        for a, b in EDGES:   # EDGES is unweighted list for drawing
            x1, y1 = NODES[a][1], NODES[a][2]
            x2, y2 = NODES[b][1], NODES[b][2]
            key = (min(a, b), max(a, b))
            a_block = a in self.incidents
            b_block = b in self.incidents

            if key in path_edges and not a_block and not b_block:
                self.canvas.create_line(x1, y1, x2, y2, fill=COLORS['edge_path'], width=4)
            elif a_block or b_block:
                self.canvas.create_line(x1, y1, x2, y2, fill=COLORS['edge_blocked'], width=2, dash=(6, 4))
            else:
                self.canvas.create_line(x1, y1, x2, y2, fill=COLORS['edge'], width=2)

        for nid, (label, x, y) in NODES.items():
            is_exit = nid in EXITS
            is_pin = nid == self.pin
            is_inc = nid in self.incidents
            on_path = self.current_path and nid in self.current_path

            if is_exit:
                fill, outline, tc = COLORS['exit_fill'], COLORS['exit_fill'], COLORS['exit_text']
            elif is_inc:
                fill, outline, tc = COLORS['incident_fill'], COLORS['incident_badge'], COLORS['incident_text']
            elif on_path:
                fill, outline, tc = COLORS['node_fill'], COLORS['path_border'], COLORS['node_text']
            else:
                fill, outline, tc = COLORS['node_fill'], COLORS['node_border'], COLORS['node_text']

            self._draw_pill(x, y, RX, RY, fill=fill, outline=outline, width=2)

            font = self.fonts['exit'] if is_exit else self.fonts['node']
            self.canvas.create_text(x, y, text=label, fill=tc, font=font)

            if is_inc:
                bx, by = x + RX - 4, y - RY + 4
                self.canvas.create_oval(bx-13, by-13, bx+13, by+13,
                                        fill=COLORS['incident_badge'], outline='white', width=2)
                self.canvas.create_text(bx, by, text="✕", fill='white', font=self.fonts['badge'])
                self.canvas.create_text(x, y + RY + 16, text="BLOCKED",
                                        fill=COLORS['incident_text'], font=self.fonts['blocked'])

            if is_pin:
                self.canvas.create_oval(x-24, y-RY-44, x+24, y-RY+8,
                                        fill=COLORS['pin_glow'], outline="")
                self.canvas.create_oval(x-16, y-RY-46, x+16, y-RY-18,
                                        fill=COLORS['pin_red'], outline='white', width=2)
                self.canvas.create_polygon(x, y-RY-4, x-8, y-RY-20, x+8, y-RY-20,
                                           fill=COLORS['pin_red'], outline="")
                self.canvas.create_text(x, y-RY-31, text="YOU", fill='white',
                                        font=self.fonts['pin_label'])

    def _draw_pill(self, cx, cy, rx, ry, **kwargs):
        r = min(rx, ry)
        x0, y0, x1, y1 = cx - rx, cy - ry, cx + rx, cy + ry
        pts = [x0 + r, y0, x1 - r, y0, x1, y0, x1, y0 + r,
               x1, y1 - r, x1, y1, x1 - r, y1, x0 + r, y1,
               x0, y1, x0, y1 - r, x0, y0 + r, x0, y0, x0 + r, y0]
        self.canvas.create_polygon(pts, smooth=True, **kwargs)

    # ---------- Core Logic ----------
    def _on_canvas_click(self, event):
        for nid, (_, x, y) in NODES.items():
            if abs(event.x - x) <= RX + 10 and abs(event.y - y) <= RY + 10:
                if nid != self.pin:
                    self.pin = nid
                    self._calculate_path()
                    self._draw()
                    self._update_all()
                    self._log(f"📍 Location: {NODES[nid][0]}", "success")
                return

    def _calculate_path(self):
        if self.pin is None:
            self.current_path = None
            self.current_distance = None
        else:
            self.current_path = dijkstra_shortest_path(
                self.pin, GRAPH_ADJ, EDGE_WEIGHTS, EXITS, self.incidents
            )
            if self.current_path:
                total = 0.0
                for i in range(len(self.current_path) - 1):
                    a, b = self.current_path[i], self.current_path[i+1]
                    key = (min(a, b), max(a, b))
                    total += EDGE_WEIGHTS.get(key, 0.0)
                self.current_distance = total
            else:
                self.current_distance = None
        self._update_all()

    def _toggle_incident(self):
        if self.pin is None:
            self._log("Select a room first.", "warn")
            return
        if self.pin in EXITS:
            self._log("Cannot block an exit.", "warn")
            return
        if self.pin in self.incidents:
            self.incidents.discard(self.pin)
            self._log(f"✓ Cleared: {NODES[self.pin][0]}", "success")
        else:
            self.incidents.add(self.pin)
            self._log(f"⚠ Blocked: {NODES[self.pin][0]}", "warn")
        self._calculate_path()
        self._draw()
        self._update_all()

    def _manual_recalc(self):
        if self.pin is None:
            self._log("No location selected.", "warn")
            return
        self._calculate_path()
        self._draw()
        self._update_all()
        self._log("Route recalculated (weighted Dijkstra).", "success")

    def _reset(self):
        self.pin = None
        self.incidents.clear()
        self.current_path = None
        self.current_distance = None
        self._draw()
        self._update_all()
        self._log("Reset. Click a room.", "info")

    # ---------- UI Updates ----------
    def _update_all(self):
        self._update_warning_bar()
        self._update_bottom_panel()

    def _update_warning_bar(self):
        if self.incidents:
            blocked = ", ".join(NODES[n][0] for n in self.incidents)
            self.warn_label.config(text=f"⚠ BLOCKED: {blocked}")
        elif self.pin is None:
            self.warn_label.config(text="📍 Click any room")
        else:
            self.warn_label.config(text=f"📍 {NODES[self.pin][0]} – route ready")

    def _update_bottom_panel(self):
        for w in self.steps_frame.winfo_children():
            w.destroy()

        if not self.current_path:
            self.route_lbl.config(text="—")
            self.distance_label.config(text="")
            self.block_warn.config(text="")
            return

        names = [NODES[n][0] for n in self.current_path]
        self.route_lbl.config(text="  →  ".join(names))

        if self.current_distance is not None:
            self.distance_label.config(text=f"{self.current_distance:.1f} m")
        else:
            self.distance_label.config(text="")

        steps = names[1:]
        for i, step in enumerate(steps):
            row = tk.Frame(self.steps_frame, bg=COLORS['sidebar_bg'], pady=2)
            row.pack(fill="x")

            num = tk.Canvas(row, width=22, height=22, bg=COLORS['sidebar_bg'], highlightthickness=0)
            num.pack(side="left", padx=(0, 10))
            num.create_oval(1, 1, 21, 21, fill=COLORS['step_num_bg'], outline="")
            num.create_text(11, 11, text=str(i+1), fill=COLORS['step_num_fg'], font=self.fonts['number'])

            if i == len(steps) - 1:
                frame = tk.Frame(row, bg=COLORS['sidebar_bg'])
                frame.pack(side="left")
                tk.Label(frame, text="Exit through ", bg=COLORS['sidebar_bg'],
                         fg=COLORS['node_text'], font=self.fonts['step']).pack(side="left")
                tk.Label(frame, text=step, bg=COLORS['sidebar_bg'],
                         fg=COLORS['exit_green'], font=self.fonts['finish']).pack(side="left")
            else:
                if "Stairs" in step:
                    text = "Take stairs"
                elif "Hallway" in step or "Corridor" in step or "Spine" in step:
                    text = "Continue straight"
                else:
                    text = f"Go to {step}"
                tk.Label(row, text=text, bg=COLORS['sidebar_bg'],
                         fg=COLORS['node_text'], font=self.fonts['step']).pack(side="left")

        if self.incidents:
            blocked = ", ".join(NODES[n][0] for n in self.incidents)
            self.block_warn.config(text=f"⚠ Blocked: {blocked}")
        else:
            self.block_warn.config(text="")

    def _log(self, msg, tag):
        self.log.config(state="normal")
        self.log.insert("end", msg + "\n", tag)
        self.log.see("end")
        self.log.config(state="disabled")


if __name__ == "__main__":
    root = tk.Tk()
    app = EvacuationApp(root)
    root.mainloop()