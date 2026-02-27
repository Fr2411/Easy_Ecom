"""Orchestrates specialized retail agents and optional OpenAI function-calling."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

from services.client_service import get_client_profile

from .discount_supervisor import DiscountSupervisor
from .sales_agent import SalesAgent
from .stock_agent import StockAgent

try:
    from openai import OpenAI
except Exception:
    OpenAI = None


@dataclass
class AgentOrchestrator:
    model: str = "gpt-4o-mini"
    openai_client: Any = None

    def __post_init__(self) -> None:
        self.sales_agent = SalesAgent()
        self.stock_agent = StockAgent()
        self.discount_supervisor = DiscountSupervisor()

        if self.openai_client is None and OpenAI is not None:
            self.openai_client = OpenAI()

        self.function_schemas = [
            {
                "type": "function",
                "function": {
                    "name": "sales_agent_decision",
                    "description": "Generate a sales-oriented recommendation with margin awareness.",
                    "parameters": self.sales_agent.input_schema,
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "stock_agent_decision",
                    "description": "Assess stock urgency and provide replenishment action.",
                    "parameters": self.stock_agent.input_schema,
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "discount_supervisor_decision",
                    "description": "Apply discount approval policy and return approval action.",
                    "parameters": self.discount_supervisor.input_schema,
                },
            },
        ]

    def _payload_with_context(self, payload: dict[str, Any]) -> dict[str, Any]:
        enriched = dict(payload)
        client_id = payload.get("client_id")
        if client_id:
            enriched["client_context"] = get_client_profile(str(client_id))
        else:
            enriched["client_context"] = payload.get("client_context", {})
        return enriched

    def route(self, payload: dict[str, Any]) -> dict[str, Any]:
        enriched = self._payload_with_context(payload)
        sales_out = self.sales_agent.evaluate(enriched)
        stock_out = self.stock_agent.evaluate(enriched)
        discount_out = self.discount_supervisor.evaluate(enriched)
        return {
            "action": "orchestrated_plan",
            "text": "Combined guidance from sales, stock, and discount supervisors.",
            "metadata": {
                "sales_agent": sales_out,
                "stock_agent": stock_out,
                "discount_supervisor": discount_out,
                "client_context": enriched.get("client_context", {}),
            },
        }

    def call_openai_with_functions(self, payload: dict[str, Any]) -> dict[str, Any]:
        enriched = self._payload_with_context(payload)
        if self.openai_client is None:
            return {
                "action": "local_fallback",
                "text": "OpenAI client unavailable; returning local orchestration.",
                "metadata": self.route(enriched),
            }

        user_prompt = (
            "Decide which function to call for this retail request and return compliant args:\n"
            + json.dumps(enriched)
        )
        response = self.openai_client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a retail AI orchestrator. Use function tools for decisions and "
                        "respect sales push, margin safety, stock urgency, discount approvals, and client policies."
                    ),
                },
                {"role": "user", "content": user_prompt},
            ],
            tools=self.function_schemas,
            tool_choice="auto",
        )

        msg = response.choices[0].message
        if not msg.tool_calls:
            return {
                "action": "no_tool_call",
                "text": msg.content or "Model responded without tool usage.",
            }

        tool_call = msg.tool_calls[0]
        return {
            "action": "tool_call_selected",
            "text": f"Model selected {tool_call.function.name}",
            "metadata": {
                "function": tool_call.function.name,
                "arguments": json.loads(tool_call.function.arguments or "{}"),
                "client_context": enriched.get("client_context", {}),
            },
        }
