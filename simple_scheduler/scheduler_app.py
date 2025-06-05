"""
simple_scheduler/scheduler_app.py

Tkinter GUI for the simple worker scheduler.
"""

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

from .constants import WORKERS, SHIFTS, DAYS_OF_WEEK
from .schedule_manager import ScheduleManager

class SchedulerApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Worker Scheduling Widget")
        self.geometry("700x400")
        self.resizable(width=False, height=False)

        # Create a ScheduleManager instance to hold current assignments
        self.manager = ScheduleManager()

        # Configure two‐column grid (left controls, right table)
        self.columnconfigure(0, weight=0, minsize=250)
        self.columnconfigure(1, weight=1, minsize=450)
        self.rowconfigure(0, weight=1)

        # Build the two panes
        self._create_widgets()

    def _create_widgets(self):
        # === Left Pane ===
        control_frame = ttk.Frame(self, padding=(10, 10))
        control_frame.grid(row=0, column=0, sticky="nsew")

        # Worker Listbox
        ttk.Label(control_frame, text="Select Worker:").pack(anchor="w", pady=(0, 5))
        self.worker_listbox = tk.Listbox(control_frame, height=6, exportselection=False)
        for w in WORKERS:
            self.worker_listbox.insert(tk.END, w)
        self.worker_listbox.pack(fill="x", pady=(0, 10))

        # Shift Listbox
        ttk.Label(control_frame, text="Select Shift:").pack(anchor="w", pady=(0, 5))
        self.shift_listbox = tk.Listbox(control_frame, height=3, exportselection=False)
        for s in SHIFTS:
            self.shift_listbox.insert(tk.END, s)
        self.shift_listbox.pack(fill="x", pady=(0, 10))

        # Day Combobox
        ttk.Label(control_frame, text="Select Day:").pack(anchor="w", pady=(0, 5))
        self.day_var = tk.StringVar()
        self.day_combobox = ttk.Combobox(
            control_frame,
            textvariable=self.day_var,
            values=DAYS_OF_WEEK,
            state="readonly"
        )
        self.day_combobox.pack(fill="x", pady=(0, 20))
        self.day_combobox.set(DAYS_OF_WEEK[0])  # default to Monday

        # Assign button
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

        # Configure column widths & anchors
        self.tree.column("day", width=100, anchor="center")
        self.tree.column("shift", width=180, anchor="center")
        self.tree.column("worker", width=150, anchor="w")

        # Vertical scrollbar
        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")

        self.tree.pack(fill="both", expand=True)

    def _on_assign(self):
        """
        Callback for the “Assign →” button.
        Gathers the user’s selections, checks via ScheduleManager,
        and then updates the Treeview if valid.
        """
        # 1. Get selected worker
        try:
            worker_idx = self.worker_listbox.curselection()[0]
            selected_worker = WORKERS[worker_idx]
        except IndexError:
            messagebox.showwarning("Missing Selection", "Please select a worker.")
            return

        # 2. Get selected shift
        try:
            shift_idx = self.shift_listbox.curselection()[0]
            selected_shift = SHIFTS[shift_idx]
        except IndexError:
            messagebox.showwarning("Missing Selection", "Please select a shift.")
            return

        # 3. Get selected day
        selected_day = self.day_var.get()
        if selected_day not in DAYS_OF_WEEK:
            messagebox.showwarning("Missing Selection", "Please select a valid day.")
            return

        # 4. Check duplicates via ScheduleManager
        if self.manager.has_duplicate(selected_day, selected_shift, selected_worker):
            messagebox.showinfo(
                "Already Assigned",
                f"{selected_worker} already has {selected_shift} on {selected_day}."
            )
            return

        # Optional: Enforce “one shift per worker per day” 
        # (uncomment if desired)
        # if self.manager.worker_has_shift_on_day(selected_worker, selected_day):
        #     messagebox.showinfo(
        #         "Conflict",
        #         f"{selected_worker} already has a shift on {selected_day}."
        #     )
        #     return

        # 5. Add to manager & Treeview
        success = self.manager.add_assignment(selected_day, selected_shift, selected_worker)
        if success:
            self.tree.insert("", tk.END, values=(selected_day, selected_shift, selected_worker))
        else:
            # (Should not happen, since we already checked has_duplicate,
            # but good to be safe.)
            messagebox.showerror(
                "Error",
                "Failed to add assignment (internal error)."
            )
