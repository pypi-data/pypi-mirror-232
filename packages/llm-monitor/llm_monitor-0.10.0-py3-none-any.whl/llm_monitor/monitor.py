import time
from datetime import datetime
from typing import Any, Dict, Optional
from uuid import uuid4

import pytz

from llm_monitor.schema.transaction import TransactionRecord
from llm_monitor.utils.aggregator import add_record_to_batch, initialize_api_client


class LLMMonitor:
    timers: Dict[str, Dict[str, float]] = {}
    records: Dict[str, TransactionRecord] = {}

    def __init__(self, project_name: str, *args: Any, **kwargs: Any) -> None:
        initialize_api_client(project_name=project_name)

    def log_prompt(
        self, prompt: str, model: str, parent_trace_id: Optional[str]
    ) -> str:
        trace_id = str(uuid4())

        self.timers[trace_id] = {}
        self.timers[trace_id]["start"] = time.perf_counter()

        self.records[trace_id] = TransactionRecord(
            input_text=prompt,
            model=model,
            trace_id=trace_id,
            parent_trace_id=parent_trace_id,
            created_at=datetime.now(tz=pytz.utc).isoformat(),
        )
        return trace_id

    def log_completion(
        self,
        trace_id: str,
        output_text: str,
        num_input_tokens: int,
        num_output_tokens: int,
        num_total_tokens: int,
        finish_reason: Optional[str],
        status_code: Optional[int],
    ) -> None:
        self.timers[trace_id]["stop"] = time.perf_counter()
        latency_ms = round(
            (self.timers[trace_id]["stop"] - self.timers[trace_id]["start"]) * 1000
        )
        del self.timers[trace_id]

        model_dict = self.records[trace_id].model_dump()
        model_dict.update(
            output_text=output_text,
            num_input_tokens=num_input_tokens,
            num_output_tokens=num_output_tokens,
            num_total_tokens=num_total_tokens,
            finish_reason=finish_reason,
            latency_ms=latency_ms,
            status_code=status_code or 200,
        )

        add_record_to_batch(TransactionRecord(**model_dict))
        del self.records[trace_id]

    def log_error(
        self, trace_id: str, error_message: str, status_code: Optional[int]
    ) -> None:
        self.timers[trace_id]["stop"] = time.perf_counter()
        latency_ms = round(
            (self.timers[trace_id]["stop"] - self.timers[trace_id]["start"]) * 1000
        )
        del self.timers[trace_id]

        model_dict = self.records[trace_id].model_dump()
        model_dict.update(
            output_text=f"ERROR: {error_message}",
            num_input_tokens=0,
            num_output_tokens=0,
            num_total_tokens=0,
            latency_ms=latency_ms,
            status_code=status_code or 500,
        )

        add_record_to_batch(TransactionRecord(**model_dict))
        del self.records[trace_id]
