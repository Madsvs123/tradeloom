from dataclasses import dataclass


@dataclass(frozen=False)
class PlatformRoute:
    key: str
    api_prefix: str
    urls_module: str


PLATFORM_ROUTES = [
    PlatformRoute("accounts", "accounts/", "apps.accounts.urls"),
    PlatformRoute("marketplace", "marketplace/", "apps.marketplace.urls"),
    PlatformRoute("rfq", "rfq/", "apps.rfq.urls"),
    PlatformRoute("orders", "order/", "apps.orders.urls"),
    PlatformRoute("procurement", "procurement/", "apps.procurement.urls"),
    PlatformRoute("finance", "finance/", "apps.finance.urls"),
    PlatformRoute("logistics", "logistics/", "apps.logistics.urls"),
    PlatformRoute("compliance", "compliance/", "apps.compliance.urls"),
    PlatformRoute("communications", "comms/", "apps.communications.urls"),
    PlatformRoute("vendor_ops", "vendor/", "apps.vendor_ops.urls"),
    PlatformRoute("platform_admin", "platform/", "apps.platform_admin.urls"),
    PlatformRoute("analytics", "analytics/", "apps.analytics.urls"),
    PlatformRoute("integrations", "integrations/", "apps.integrations.urls"),
    PlatformRoute("contracts", "contracts/", "apps.contracts.urls"),
    PlatformRoute("workflows", "workflows/", "apps.workflows.urls"),
    PlatformRoute("sourcing", "sourcing/", "apps.sourcing.urls"),
    PlatformRoute("quality", "quality/", "apps.quality.urls"),
    PlatformRoute("sustainability", "sustainability/", "apps.sustainability.urls"),
    PlatformRoute("trade_finance", "trade-finance/", "apps.trade_finance.urls"),
    PlatformRoute("projects", "projects/", "apps.projects.urls"),
]
