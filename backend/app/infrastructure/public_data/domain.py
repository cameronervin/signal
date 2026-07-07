import asyncio

import dns.resolver

from app.infrastructure.public_data.types import DomainSnapshot


class DomainMxClient:
    async def domain_snapshot(self, *, email: str) -> DomainSnapshot:
        domain = email.split("@")[-1].lower()
        has_mx = await asyncio.to_thread(_has_mx_record, domain)
        return DomainSnapshot(has_mx=has_mx)


def _has_mx_record(domain: str) -> bool:
    try:
        answers = dns.resolver.resolve(domain, "MX")
    except dns.exception.DNSException:
        return False
    return any(answers)
