import time
from collections import defaultdict

class RateLimiter:
    def __init__(self, max_requests: int, window_seconds: int):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: dict[str, list[float]] = defaultdict(list)

    def allow_request(self, user_id: str) -> tuple[bool, str]:
        now = time.time()
        window_start = now - self.window_seconds

        # Drop timestamps outside the current window
        self.requests[user_id] = [t for t in self.requests[user_id] if t > window_start]

        if len(self.requests[user_id]) >= self.max_requests:
            return False, f"Rate limit exceeded: max {self.max_requests} requests per {self.window_seconds}s."

        self.requests[user_id].append(now)
        return True, ""

limiter = RateLimiter(max_requests=3, window_seconds=10)

for i in range(5):
    ok, msg = limiter.allow_request("user_123")
    print(f"Request {i+1}: {'allowed' if ok else 'blocked'} {msg}")