# simple_scheduler/scheduler_app.py

import tkinter as tk
from tkinter import ttk, messagebox

from .constants import WORKERS, SHIFTS, DAYS_OF_WEEK
from .schedule_manager import ScheduleManager

class SchedulerApp(tk.Tk):
    """
    The main application window for assigning workers to shifts.
    """

    def __init__(self):
        super().__init__()

        # === 1. Configure overall window properties ===
        self.title("Worker Scheduling Widget")
        self.geometry("700x400")
        self.resizable(width=False, height=False)

        # === 2. Create and customize a ttk.Style instance ===
        #
        # First, instantiate a Style object tied to this root window.
        style = ttk.Style(self)

        # 2.1. Choose a base theme. 
        # Common built‐in choices: 'clam', 'alt', 'default', 'classic'; 
        # platform‐specific ones include 'aqua' (macOS), 'vista' (Windows), etc. 
        style.theme_use('clam')  # For a more neutral, cross‐platform appearance :contentReference[oaicite:0]{index=0}

        # 2.2. Tweak general font/padding for Buttons and Comboboxes
        style.configure(
            'TButton',
            font=('Segoe UI', 10),          # Use a modern sans‐serif
            padding=(8, 4)                  # (x‐pad, y‐pad)
        )
        style.configure(
            'TCombobox',
            font=('Segoe UI', 10),
            padding=(4, 2)
        )

        # 2.3. Customize Treeview appearance: row height, font, headings style
        style.configure(
            'Treeview',
            rowheight=24,                   # Increase row height for readability
            font=('Segoe UI', 10)           # Font for regular cells
        )
        style.configure(
            'Treeview.Heading',
            font=('Segoe UI Semibold', 10)  # Bold font for column headers
        )

        # 2.4. (Optional) Change selected‐row background/foreground
        style.map(
            'Treeview',
            background=[('selected', '#347083')],   # Dark teal when selected
            foreground=[('selected', '#ffffff')]    # White text on selected row
        )  # :contentReference[oaicite:1]{index=1}

        # === 3. Create the in‐memory schedule manager ===
        self.manager = ScheduleManager()

        # === 4. Lay out the window using a two‐column grid ===
        self.columnconfigure(0, weight=0, minsize=250)
        self.columnconfigure(1, weight=1, minsize=450)
        self.rowconfigure(0, weight=1)

        self._create_widgets()


    def _create_widgets(self):
        # === Left Pane: Controls ===
        control_frame = ttk.Frame(self, padding=(10, 10))
        control_frame.grid(row=0, column=0, sticky="nsew")

        # 1. Worker Listbox
        ttk.Label(control_frame, text="Select Worker:").pack(anchor="w", pady=(0, 5))
        self.worker_listbox = tk.Listbox(control_frame, height=6, exportselection=False)
        for w in WORKERS:
            self.worker_listbox.insert(tk.END, w)
        self.worker_listbox.pack(fill="x", pady=(0, 10))

        # 2. Shift Listbox
        ttk.Label(control_frame, text="Select Shift:").pack(anchor="w", pady=(0, 5))
        self.shift_listbox = tk.Listbox(control_frame, height=3, exportselection=False)
        for s in SHIFTS:
            self.shift_listbox.insert(tk.END, s)
        self.shift_listbox.pack(fill="x", pady=(0, 10))

        # 3. Day Combobox
        ttk.Label(control_frame, text="Select Day:").pack(anchor="w", pady=(0, 5))
        self.day_var = tk.StringVar()
        self.day_combobox = ttk.Combobox(
            control_frame,
            textvariable=self.day_var,
            values=DAYS_OF_WEEK,
            state="readonly",
            font=('Segoe UI', 10)        # Ensure Combobox matches button font :contentReference[oaicite:2]{index=2}
        )
        self.day_combobox.pack(fill="x", pady=(0, 20))
        self.day_combobox.set(DAYS_OF_WEEK[0])  # default to Monday

        # 4. Assign Button
        self.assign_button = ttk.Button(
            control_frame,
            text="Assign →",
            command=self._on_assign
        )
        self.assign_button.pack(fill="x")

        # === Right Pane: Schedule Table ===
        table_frame = ttk.Frame(self, padding=(10, 10))
        table_frame.grid(row=0, column=1, sticky="nsew")

        columns = ("day", "shift", "worker")
        self.tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            selectmode="browse"
        )

        # Configure headings
        self.tree.heading("day", text="Day")
        self.tree.heading("shift", text="Shift")
        self.tree.heading("worker", text="Worker")

        # Configure column widths & alignment
        self.tree.column("day",    width=100, anchor="center")
        self.tree.column("shift",  width=180, anchor="center")
        self.tree.column("worker", width=150, anchor="w")

        # Add a vertical scrollbar
        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")

        self.tree.pack(fill="both", expand=True)


    def _on_assign(self):
        """
        Callback whenever the user clicks “Assign →”.
        Gathers selections, validates them, and if valid,
        adds to the ScheduleManager and updates the Treeview.
        """
        # 1. Get selected worker
        try:
            w_idx = self.worker_listbox.curselection()[0]
            selected_worker = WORKERS[w_idx]
        except IndexError:
            messagebox.showwarning("Missing Selection", "Please select a worker.")
            return

        # 2. Get selected shift
        try:
            s_idx = self.shift_listbox.curselection()[0]
            selected_shift = SHIFTS[s_idx]
        except IndexError:
            messagebox.showwarning("Missing Selection", "Please select a shift.")
            return

        # 3. Get selected day
        selected_day = self.day_var.get()
        if selected_day not in DAYS_OF_WEEK:
            messagebox.showwarning("Missing Selection", "Please select a valid day.")
            return

        # 4. Check for exact‐duplicate assignment
        if self.manager.has_duplicate(selected_day, selected_shift, selected_worker):
            messagebox.showinfo(
                "Already Assigned",
                f"{selected_worker} already has {selected_shift} on {selected_day}."
            )
            return

        # 5. Optional: Prevent one worker having two shifts the same day
        # if self.manager.worker_has_shift_on_day(selected_worker, selected_day):
        #     messagebox.showinfo(
        #         "Conflict",
        #         f"{selected_worker} already has a shift on {selected_day}."
        #     )
        #     return

        # 6. Add to manager and update the table
        success = self.manager.add_assignment(selected_day, selected_shift, selected_worker)
        if success:
            self.tree.insert("", tk.END, values=(selected_day, selected_shift, selected_worker))
        else:
            # This should not normally happen (we already checked has_duplicate), but just in case
            messagebox.showerror("Error", "Failed to add assignment (internal error).")
