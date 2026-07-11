from __future__ import annotations

from views.inventory_current import render_current_inventory
from views.inventory_demand import render_inventory_demand_analysis
from views.inventory_history import render_inventory_history


__all__ = [
    "render_current_inventory",
    "render_inventory_demand_analysis",
    "render_inventory_history",
]
