"""
main.py — FastAPI microservice for Sinistrinha probability engine.

Endpoints
---------
POST /probability/spin            – execute a spin
GET  /probability/user-report/{id} – behavioural report
GET  /probability/recent-wins      – FOMO win feed
POST /probability/update-weights   – global stat ingestion
GET  /probability/stats            – global RTP / house metrics
GET  /health                       – liveness probe
"""

from __future__ import annotations

import logging
import time
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from .config import SYMBOLS, DEFAULT_TARGET_RTP
from .house_edge import HouseEdgeController
from .learning_agent import AdaptiveLearningAgent
from .payout_calculator import PayoutCalculator
from .simulator import RecentWinsSimulator
from .weight_engine import WeightEngine

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger("sinistrinha.probability")

# ---------------------------------------------------------------------------
# Singletons (in‑process state; a production system would use Redis / DB)
# ---------------------------------------------------------------------------

app = FastAPI(
    title="Sinistrinha Probability Engine",
    version="1.0.0",
    description="Core slot machine probability, payout, and behavioural analysis API.",
)

weight_engine = WeightEngine()
payout_calc = PayoutCalculator()
house_edge = HouseEdgeController(target_rtp=DEFAULT_TARGET_RTP)
learning_agent = AdaptiveLearningAgent()
wins_simulator = RecentWinsSimulator()


# ---------------------------------------------------------------------------
# Request / Response schemas
# ---------------------------------------------------------------------------

class SpinRequest(BaseModel):
    user_id: str
    bet_amount: float = Field(gt=0, description="Bet amount in BRL")
    user_level: int = Field(default=1, ge=1, le=10)
    display_name: str = Field(default="Anonymous")
    initial_budget: float = Field(default=0.0, ge=0)

class SpinResponse(BaseModel):
    reels: List[str]
    reel_icons: List[str]
    payout: float
    combination_type: str
    multiplier: float
    is_jackpot: bool
    free_spins: int
    xp_bonus: int
    winning_symbol: Optional[str]
    match_count: int
    wild_used: bool
    modifier_used: float
    near_miss_forced: bool
    session_rtp: float
    reasoning: Dict[str, str]
    active_triggers: List[str]

class UpdateWeightsRequest(BaseModel):
    total_wagered: float = 0.0
    total_paid: float = 0.0

class GlobalStatsResponse(BaseModel):
    global_rtp: float
    house_edge: float
    total_wagered: float
    total_paid: float
    total_spins: int
    target_rtp: float


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/health")
def health():
    return {"status": "ok", "service": "probability_engine"}


@app.post("/probability/spin", response_model=SpinResponse)
def spin(req: SpinRequest):
    """Execute a single spin for a player."""

    ts = time.time()

    # 1. Determine modifier from house edge controller
    modifier, reasons = house_edge.get_spin_modifier(
        user_id=req.user_id,
        user_level=req.user_level,
    )

    # 2. Apply learning agent recommendation on top
    recommendation = learning_agent.recommend_modifier(req.user_id)
    modifier += recommendation["weight_modifier"]
    modifier = max(0.5, min(1.5, modifier))
    reasons["learning_agent"] = recommendation["reasoning"]

    # 3. Generate reels
    reels = weight_engine.spin_all(modifier=modifier)

    # 4. Near‑miss check
    near_miss_forced, reels = house_edge.should_force_near_miss(reels)
    if near_miss_forced:
        reasons["near_miss"] = "forced on center reel"

    # 5. Calculate payout
    result = payout_calc.calculate(reels, req.bet_amount)

    # 6. Update session stats in house edge controller
    house_edge.update_session_stats(req.user_id, req.bet_amount, result["payout"])

    # 7. Update learning agent
    learning_agent.update_user_profile(req.user_id, {
        "bet": req.bet_amount,
        "payout": result["payout"],
        "is_jackpot": result["is_jackpot"],
        "timestamp": ts,
    })

    # 8. Register real win in the feed simulator
    if result["payout"] > 0 and result["winning_symbol"]:
        wins_simulator.register_real_win(
            user_id=req.user_id,
            display_name=req.display_name,
            symbol=result["winning_symbol"],
            payout=result["payout"],
            bet=req.bet_amount,
        )

    # 9. Session RTP for response
    session_rtp = house_edge.get_session_rtp(req.user_id)

    # 10. Active psychological triggers
    profile = learning_agent.user_profiles.get(req.user_id)
    active_triggers = profile.active_triggers if profile else []

    # 11. Observability log
    logger.info(
        "SPIN | user=%s bet=%.2f payout=%.2f mod=%.4f near_miss=%s "
        "combo=%s session_rtp=%.4f triggers=%s reasons=%s",
        req.user_id,
        req.bet_amount,
        result["payout"],
        modifier,
        near_miss_forced,
        result["combination_type"],
        session_rtp,
        active_triggers,
        reasons,
    )

    # 12. Build response
    reel_icons = [SYMBOLS[s].icon for s in reels]

    return SpinResponse(
        reels=reels,
        reel_icons=reel_icons,
        payout=result["payout"],
        combination_type=result["combination_type"],
        multiplier=result["multiplier"],
        is_jackpot=result["is_jackpot"],
        free_spins=result["free_spins"],
        xp_bonus=result["xp_bonus"],
        winning_symbol=result["winning_symbol"],
        match_count=result["match_count"],
        wild_used=result["wild_used"],
        modifier_used=round(modifier, 4),
        near_miss_forced=near_miss_forced,
        session_rtp=round(session_rtp, 4),
        reasoning=reasons,
        active_triggers=active_triggers,
    )


@app.get("/probability/user-report/{user_id}")
def user_report(user_id: str):
    """Export behavioural analysis report for a player."""
    report = learning_agent.export_behavioral_report(user_id)
    session = house_edge.sessions.get(user_id)
    if session:
        report["session"] = {
            "spins": session.spins,
            "wagered": round(session.total_wagered, 2),
            "won": round(session.total_won, 2),
            "session_rtp": round(session.session_rtp, 4),
            "volatility_mode": session.volatility_mode,
            "consecutive_wins": session.consecutive_wins,
            "consecutive_losses": session.consecutive_losses,
        }
    return report


@app.get("/probability/recent-wins")
def recent_wins(limit: int = 20, real_ratio: float = 0.6):
    """Return the recent wins feed (real + simulated)."""
    return wins_simulator.generate_feed(limit=limit, real_ratio=real_ratio)


@app.post("/probability/update-weights")
def update_weights(req: UpdateWeightsRequest):
    """Ingest global statistics (called periodically by Celery task)."""
    learning_agent.global_stats["total_wagered"] = req.total_wagered
    learning_agent.global_stats["total_paid"] = req.total_paid
    return {"status": "updated", "global_stats": learning_agent.global_stats}


@app.get("/probability/stats", response_model=GlobalStatsResponse)
def global_stats():
    """Return global RTP and house edge metrics."""
    gs = learning_agent.global_stats
    total_w = gs["total_wagered"]
    total_p = gs["total_paid"]
    rtp = total_p / total_w if total_w > 0 else 0.0
    return GlobalStatsResponse(
        global_rtp=round(rtp, 4),
        house_edge=round(1 - rtp, 4),
        total_wagered=round(total_w, 2),
        total_paid=round(total_p, 2),
        total_spins=gs["total_spins"],
        target_rtp=DEFAULT_TARGET_RTP,
    )
