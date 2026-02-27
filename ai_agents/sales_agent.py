"""Sales agent focused on conversion-safe recommendations."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .prompt_utils import build_agent_context


@dataclass
class SalesAgent:
    name: str = "sales_agent"
    input_schema: dict[str, Any] = None

    def __post_init__(self) -> None:
        self.input_schema = {
            "type": "object",
            "required": [
                "product_name",
                "stock_days_cover",
                "current_margin_pct",
                "requested_discount_pct",
            ],
            "properties": {
                "product_name": {"type": "string"},
                "stock_days_cover": {"type": "number"},
                "current_margin_pct": {"type": "number"},
                "requested_discount_pct": {"type": "number"},
                "campaign_goal": {"type": "string"},
            },
            "additionalProperties": False,
        }

    def build_prompt(self, payload: dict[str, Any]) -> str:
        return build_agent_context(self.name, payload)

    def evaluate(self, payload: dict[str, Any]) -> dict[str, Any]:
        current_margin = float(payload.get("current_margin_pct", 0))
        requested_discount = float(payload.get("requested_discount_pct", 0))
        stock_days_cover = float(payload.get("stock_days_cover", 30))
        product_name = payload.get("product_name", "product")
        margin_after_discount = current_margin - requested_discount

        if margin_after_discount < 20:
            action = "upsell_instead_of_discount"
            text = (
                f"Avoid discounting {product_name}; margin falls to "
                f"{margin_after_discount:.1f}%. Recommend value-add upsell."
            )
        elif stock_days_cover <= 3:
            action = "push_sales_with_urgency"
            text = (
                f"Run urgency messaging for {product_name} and approve a "
                f"{requested_discount:.1f}% promo."
            )
        else:
            action = "standard_sales_push"
            text = f"Promote {product_name} with benefit-led messaging; no aggressive urgency needed."
        return {"action": action, "text": text, "metadata": {"margin_after_discount": margin_after_discount}}
