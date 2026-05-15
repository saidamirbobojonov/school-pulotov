from __future__ import annotations

import hashlib
import re
import time
from dataclasses import dataclass

from django.conf import settings
from django.core.cache import cache
from django.http import HttpResponse


@dataclass(frozen=True)
class _RateLimitRule:
    name: str
    path_re: re.Pattern[str]
    methods: set[str]
    limit: int
    window: int
    query_param: str | None = None


def _client_ip(request) -> str:
    if getattr(settings, "RATELIMIT_TRUST_PROXY", False):
        forwarded = (request.META.get("HTTP_X_FORWARDED_FOR") or "").split(",")[0].strip()
        if forwarded:
            return forwarded
    return request.META.get("REMOTE_ADDR") or "unknown"


def _load_rules() -> list[_RateLimitRule]:
    raw = getattr(settings, "RATELIMIT_RULES", None)
    if not raw:
        return []

    rules: list[_RateLimitRule] = []
    for item in raw:
        try:
            rules.append(
                _RateLimitRule(
                    name=str(item["name"]),
                    path_re=re.compile(str(item["path_regex"])),
                    methods={m.upper() for m in item.get("methods", ["GET"])},
                    limit=int(item.get("limit", 60)),
                    window=int(item.get("window", 60)),
                    query_param=item.get("query_param"),
                )
            )
        except Exception:
            continue
    return rules


class SimpleRateLimitMiddleware:
    """
    Simple per-IP + per-path throttling using Django cache.

    This is not a full DDoS solution (that belongs at the CDN/WAF/load-balancer),
    but it reduces brute-force and abusive high-frequency requests.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.rules = _load_rules()

    def __call__(self, request):
        if getattr(settings, "RATELIMIT_ENABLED", False) and self.rules:
            ip = _client_ip(request)
            path = request.path
            method = request.method.upper()

            for rule in self.rules:
                if method not in rule.methods:
                    continue
                if not rule.path_re.search(path):
                    continue
                if rule.query_param and not (request.GET.get(rule.query_param) or "").strip():
                    continue

                key_raw = f"rl:{rule.name}:{ip}:{path}"
                key = "rl:" + hashlib.sha256(key_raw.encode("utf-8")).hexdigest()
                now = int(time.time())
                bucket = now // max(rule.window, 1)

                cache_key = f"{key}:{bucket}"
                count = cache.get(cache_key, 0)
                if count >= rule.limit:
                    return HttpResponse(
                        "Too Many Requests",
                        status=429,
                        headers={"Retry-After": str(rule.window)},
                    )
                cache.set(cache_key, count + 1, timeout=rule.window + 5)

        return self.get_response(request)
