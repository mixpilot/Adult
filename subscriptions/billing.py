"""Shared billing-period helpers for subscriptions and payments."""

BILLING_PERIOD_DAYS = {
    'daily': 1,
    'weekly': 7,
    'monthly': 30,
    'quarterly': 90,
    'yearly': 365,
    'once': 30,
}

TIER_DEFAULT_BILLING = {
    'daily': 'daily',
    'weekly': 'weekly',
    'premium': 'monthly',
    'once': 'once',
}

TIER_PERIOD_LABEL = {
    'daily': '/day',
    'weekly': '/week',
    'premium': '/month',
    'once': 'one-time',
}


def billing_days_for_period(billing_period: str) -> int:
    return BILLING_PERIOD_DAYS.get(billing_period, 30)


def default_billing_for_tier(tier: str) -> str:
    return TIER_DEFAULT_BILLING.get(tier, 'monthly')


def period_label_for_tier(tier: str) -> str:
    return TIER_PERIOD_LABEL.get(tier, '/month')
