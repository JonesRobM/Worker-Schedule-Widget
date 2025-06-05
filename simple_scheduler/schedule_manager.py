"""
simple_scheduler/schedule_manager.py

Core logic for storing and validating schedule assignments.
"""

from collections import namedtuple

# We define a simple namedtuple to hold an assignment
Assignment = namedtuple("Assignment", ["day", "shift", "worker"])

class ScheduleManager:
    """
    In‐memory manager for schedule assignments.
    """
    def __init__(self):
        # Start with an empty list of assignments
        self._assignments = []

    def all_assignments(self):
        """
        Return a shallow list of all current assignments.
        Each item is a namedtuple: (day, shift, worker).
        """
        return list(self._assignments)

    def add_assignment(self, day: str, shift: str, worker: str) -> bool:
        """
        Attempt to add a new assignment. 
        Returns True if added successfully; False if it already exists.
        """
        new = Assignment(day=day, shift=shift, worker=worker)
        if new in self._assignments:
            return False
        self._assignments.append(new)
        return True

    def has_duplicate(self, day: str, shift: str, worker: str) -> bool:
        """
        Check if (day, shift, worker) is already present.
        """
        return Assignment(day=day, shift=shift, worker=worker) in self._assignments

    # If you later want to enforce “one shift per worker per day,” 
    # you could add methods like:
    def worker_has_shift_on_day(self, worker: str, day: str) -> bool:
        """
        Returns True if the given worker already has any shift on that day.
        """
        for assn in self._assignments:
            if assn.worker == worker and assn.day == day:
                return True
        return False

    # And similar: e.g., max N workers per shift, etc.
