"""
Pricing Strategy for Agent monetization.

This module defines the PricingStrategy value object that describes
how an Agent is priced in the Ainalyn Marketplace.

IMPORTANT: Pricing in the SDK is purely DESCRIPTIVE. According to
the v0.2 specification (Gate 4 - Billing Compliance):
- Pricing strategy is a HINT only, not a decision
- SDK cannot calculate, compute, or return fees
- Actual billing is handled exclusively by Platform Core

According to 06_execution_billing_pricing_revenue_boundary.md,
only three pricing models are supported:
1. FIXED: Fixed price per successful execution
2. USAGE_BASED: Price based on verified usage units
3. COMPOSITE: Fixed base fee + usage-based overage
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class PricingType(Enum):
    """
    Enumeration of supported pricing models.

    Attributes:
        FIXED: Fixed price per successful execution.
            Example: $0.10 per document processed.
        USAGE_BASED: Price based on Platform Core verified usage units.
            Example: $0.001 per token, $0.05 per minute of audio.
        COMPOSITE: Combination of fixed base + usage overage.
            Example: $0.05 base + $0.001 per token over 1000.
    """

    FIXED = "FIXED"
    USAGE_BASED = "USAGE_BASED"
    COMPOSITE = "COMPOSITE"


@dataclass(frozen=True, slots=True)
class PricingComponent:
    """
    A component in a composite pricing strategy.

    Used for COMPOSITE pricing to define individual pricing elements.

    Attributes:
        name: Component name (e.g., "base_fee", "token_usage").
        type: The pricing type for this component.
        amount_cents: Amount in cents (for FIXED components).
        rate_per_unit: Rate per unit (for USAGE_BASED components).
        unit: Usage unit name (e.g., "token", "minute", "request").
        included_units: Units included in base fee before overage charges.
    """

    name: str
    type: PricingType
    amount_cents: int | None = None
    rate_per_unit: float | None = None
    unit: str | None = None
    included_units: int | None = None


@dataclass(frozen=True, slots=True)
class PricingStrategy:
    """
    Describes the pricing model for an Agent.

    PricingStrategy is a DESCRIPTION for marketplace display and
    Platform Core reference. The SDK does NOT calculate fees.

    IMPORTANT - Gate 4 Compliance:
    - This is a hint only, not a billing decision
    - Actual pricing is determined by Platform Core
    - SDK cannot return, compute, or influence actual charges

    Attributes:
        type: The primary pricing model (FIXED, USAGE_BASED, or COMPOSITE).
        fixed_price_cents: Price in cents for FIXED pricing.
            Example: 10 = $0.10 per execution.
        usage_rate_per_unit: Rate per unit for USAGE_BASED pricing.
            Example: 0.001 = $0.001 per unit.
        usage_unit: Name of the usage unit.
            Examples: "token", "minute", "page", "request", "character".
        components: Tuple of pricing components for COMPOSITE pricing.
        currency: Currency code (default: "USD").

    Example - Fixed Pricing:
        >>> strategy = PricingStrategy(
        ...     type=PricingType.FIXED,
        ...     fixed_price_cents=10,  # $0.10 per execution
        ... )

    Example - Usage Based:
        >>> strategy = PricingStrategy(
        ...     type=PricingType.USAGE_BASED,
        ...     usage_rate_per_unit=0.001,  # $0.001 per token
        ...     usage_unit="token",
        ... )

    Example - Composite:
        >>> strategy = PricingStrategy(
        ...     type=PricingType.COMPOSITE,
        ...     components=(
        ...         PricingComponent(
        ...             name="base_fee",
        ...             type=PricingType.FIXED,
        ...             amount_cents=5,
        ...         ),
        ...         PricingComponent(
        ...             name="token_overage",
        ...             type=PricingType.USAGE_BASED,
        ...             rate_per_unit=0.001,
        ...             unit="token",
        ...             included_units=1000,
        ...         ),
        ...     ),
        ... )
    """

    type: PricingType
    fixed_price_cents: int | None = None
    usage_rate_per_unit: float | None = None
    usage_unit: str | None = None
    components: tuple[PricingComponent, ...] = field(default_factory=tuple)
    currency: str = "USD"
