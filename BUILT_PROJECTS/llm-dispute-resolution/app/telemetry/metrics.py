from fastapi import APIRouter
from ..domain.schemas import MetricsOut
import statistics


class Metrics:
    def __init__(self):
        self._classification_latencies: list[int] = []
        self._recommendation_latencies: list[int] = []
        self._cases_by_label: dict[str, int] = {}
        self._total_cases = 0

    def record_classification_latency(self, ms: int):
        if ms:
            self._classification_latencies.append(ms)

    def record_recommendation_latency(self, ms: int):
        if ms:
            self._recommendation_latencies.append(ms)

    def increment_case(self, label: str):
        self._total_cases += 1
        self._cases_by_label[label] = self._cases_by_label.get(label, 0) + 1

    def p95(self, data: list[int]) -> float:
        if not data:
            return 0.0
        data_sorted = sorted(data)
        k = int(len(data_sorted) * 0.95) - 1
        k = max(0, min(k, len(data_sorted) - 1))
        return float(data_sorted[k])

    def snapshot(self) -> MetricsOut:
        return MetricsOut(
            total_cases=self._total_cases,
            classification_latency_ms_p95=self.p95(self._classification_latencies),
            recommendation_latency_ms_p95=self.p95(self._recommendation_latencies),
            cases_by_label=self._cases_by_label,
            avg_cost_per_case_usd=0.0  # Placeholder until cost accounting added
        )


metrics = Metrics()
metrics_router = APIRouter(tags=["metrics"])


@metrics_router.get("/metrics", response_model=MetricsOut)
async def get_metrics():
    return metrics.snapshot()
