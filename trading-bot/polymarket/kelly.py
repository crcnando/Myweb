"""
Kelly Criterion Position Sizer
Calculates optimal bet size given a known edge in a binary outcome market.
"""

from dataclasses import dataclass


@dataclass
class KellyResult:
    edge: float           # Probability edge (your_prob - market_prob)
    fair_prob: float      # Your estimated true probability
    market_prob: float    # Current market-implied probability
    kelly_full: float     # Full Kelly fraction of bankroll
    kelly_scaled: float   # Scaled Kelly (safer)
    position_usdc: float  # Recommended position in USDC
    side: str             # "YES" or "NO"
    expected_value: float # Expected value per dollar wagered


def calculate_kelly(
    fair_prob: float,
    market_prob: float,
    bankroll: float,
    kelly_fraction: float = 0.25,
    max_position: float = 500.0,
    min_position: float = 10.0,
) -> KellyResult | None:
    """
    Binary Kelly for prediction market contracts.

    A contract pays $1.00 if YES, $0.00 if NO.
    Buying YES at price p costs p USDC, wins (1-p) USDC if correct.
    Buying NO at price (1-p) costs (1-p) USDC, wins p USDC if correct.

    Kelly formula for binary bets:
        f* = (b*p - q) / b
    where:
        b = net odds (payout per unit risked)
        p = your probability
        q = 1 - p (probability of losing)
    """
    edge = fair_prob - market_prob

    if abs(edge) < 0.01:
        return None  # No meaningful edge

    if edge > 0:
        # Buy YES: paying market_prob, winning (1 - market_prob)
        side = "YES"
        prob_win = fair_prob
        prob_lose = 1.0 - fair_prob
        net_odds = (1.0 - market_prob) / market_prob  # payout ratio
    else:
        # Buy NO: paying (1 - market_prob), winning market_prob
        side = "NO"
        prob_win = 1.0 - fair_prob
        prob_lose = fair_prob
        net_odds = market_prob / (1.0 - market_prob)

    # Full Kelly fraction
    kelly_full = (net_odds * prob_win - prob_lose) / net_odds
    kelly_full = max(0.0, kelly_full)  # Never negative (don't bet)

    # Scale Kelly for safety (quarter-Kelly is standard)
    kelly_scaled = kelly_full * kelly_fraction

    # Convert to USDC amount
    position_usdc = bankroll * kelly_scaled
    position_usdc = max(min_position, min(max_position, position_usdc))

    # Expected value per dollar
    ev = (net_odds * prob_win) - prob_lose

    return KellyResult(
        edge=edge,
        fair_prob=fair_prob,
        market_prob=market_prob,
        kelly_full=kelly_full,
        kelly_scaled=kelly_scaled,
        position_usdc=position_usdc,
        side=side,
        expected_value=ev,
    )


def estimate_fair_probability(
    current_price: float,
    reference_price: float,
    time_remaining_secs: int,
    contract_duration_secs: int = 900,  # 15-minute contract
    volatility_annual: float = 0.80,    # BTC annual vol ~80%
) -> float:
    """
    Estimate fair probability that price will be HIGHER at expiry
    using a simplified Brownian motion model.

    Returns P(price_at_expiry > reference_price).
    """
    import math

    if time_remaining_secs <= 0:
        return 1.0 if current_price > reference_price else 0.0

    # Annualized vol to per-second vol
    seconds_per_year = 365.25 * 24 * 3600
    vol_per_second = volatility_annual / math.sqrt(seconds_per_year)

    # Total expected vol over remaining time
    total_vol = vol_per_second * math.sqrt(time_remaining_secs)

    if total_vol == 0:
        return 1.0 if current_price > reference_price else 0.0

    # Log-normal drift: ln(S_t / S_0) / sigma
    log_return = math.log(current_price / reference_price)
    z_score = log_return / total_vol

    # P(X > 0) = N(z_score) using complementary error function
    prob_higher = 0.5 * (1 + math.erf(z_score / math.sqrt(2)))

    return prob_higher
