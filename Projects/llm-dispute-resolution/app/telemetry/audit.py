import time
from typing import Callable, Any, Coroutine

_AUDIT_BUFFER: dict[str, list[dict]] = {}


def audit_step(step_name: str):
    def decorator(fn: Callable[..., Coroutine[Any, Any, dict]]):
        async def wrapper(*args, **kwargs):
            dispute_id = None
            # Attempt to extract dispute id if present among args
            for a in args:
                if isinstance(a, str) and a.startswith("dsp_"):
                    dispute_id = a
            start = time.perf_counter()
            success = True
            try:
                result = await fn(*args, **kwargs)
                return result
            except Exception as e:  # pylint: disable=broad-except
                success = False
                result = {"error": str(e)}
                raise
            finally:
                latency = int((time.perf_counter() - start) * 1000)
                if dispute_id:
                    _AUDIT_BUFFER.setdefault(dispute_id, []).append({
                        "step": step_name,
                        "timestamp": time.time(),
                        "latency_ms": latency,
                        "success": success
                    })
        return wrapper
    return decorator



def get_audit_events(dispute_id: str):
    return _AUDIT_BUFFER.get(dispute_id, [])

def flush_audit_events(dispute_id: str):
    events = _AUDIT_BUFFER.pop(dispute_id, [])
    return events
