"""Stock health and replenishment agent."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .prompt_utils import build_agent_context


@dataclass
class StockAgent:
    name: str = "stock_agent"
    input_schema: dict[str, Any] = None

    def __post_init__(self) -> None:
        self.input_schema = {
            "type": "object",
            "required": ["product_name", "stock_days_cover", "reorder_lead_days", "daily_sales_velocity"],
            "properties": {
                "product_name": {"type": "string"},
                "stock_days_cover": {"type": "number"},
                "reorder_lead_days": {"type": "number"},
                "daily_sales_velocity": {"type": "number"},
            },
            "additionalProperties": False,
        }

    def build_prompt(self, payload: dict[str, Any]) -> str:
        return build_agent_context(self.name, payload)

    def evaluate(self, payload: dict[str, Any]) -> dict[str, Any]:
        stock_cover = float(payload.get("stock_days_cover", 30))
        lead = float(payload.get("reorder_lead_days", 7))
        product_name = payload.get("product_name", "product")
        if stock_cover <= 3:
            action = "expedite_reorder"
            text = f"Critical low stock for {product_name}; expedite reorder immediately."
            urgency = "HIGH"
        elif stock_cover <= 7 or stock_cover <= lead:
            action = "schedule_reorder"
            text = f"Reorder {product_name} this cycle to prevent stockout risk."
            urgency = "MEDIUM"
        else:
            action = "monitor_stock"
            text = f"Stock for {product_name} is stable; continue routine monitoring."
            urgency = "LOW"
        return {"action": action, "text": text, "metadata": {"urgency": urgency, "stock_days_cover": stock_cover}}
