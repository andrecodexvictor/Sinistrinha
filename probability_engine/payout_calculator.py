"""
payout_calculator.py — Determines wins, payouts, free spins, and XP.

Rules
-----
- Matches are evaluated **left‑to‑right adjacently**: the first reel must
  participate.  A "3‑of‑a‑kind" means reels 0‑1‑2 match; a "4‑of‑a‑kind"
  means reels 0‑1‑2‑3 match, and so on.
- Wild symbols substitute for any non‑scatter symbol and grant a +20 % bonus
  when they complete a winning combination.
- Scatters are counted globally (they don't need to be adjacent).
- The best single‑line payout is kept (no multi‑line logic in this version).
"""

from __future__ import annotations

from typing import Dict, List, Optional, Tuple

from .config import (
    MATCH_RATIOS,
    SCATTER_BONUS_MULTIPLIER,
    SCATTER_FREE_SPINS,
    SYMBOLS,
    WILD_BONUS_MULTIPLIER,
    GLOBAL_MULTIPLIER_BOOST,
    XP_JACKPOT_BONUS,
    XP_PER_SPIN,
    XP_WIN_BONUS,
)


class PayoutCalculator:
    """Calculate the payout for a set of 5 reels."""

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def calculate(self, reels: List[str], bet: float) -> Dict:
        """
        Evaluate a spin result.

        Returns
        -------
        dict with keys:
            payout          – monetary payout (0 if loss)
            combination_type – human‑readable description
            multiplier      – effective multiplier applied
            is_jackpot      – True if 5‑of‑a‑kind (non‑wild, non‑scatter)
            free_spins      – number of free spins awarded
            xp_bonus        – experience points earned
            winning_symbol  – name of the symbol that formed the win (or None)
            match_count     – how many reels matched (3, 4, or 5)
            wild_used       – whether a wild completed the combo
        """
        # 1. Scatter evaluation (independent of position)
        scatter_count = sum(
            1 for s in reels if SYMBOLS[s].is_scatter
        )
        free_spins = SCATTER_FREE_SPINS.get(scatter_count, 0)
        scatter_mult = SCATTER_BONUS_MULTIPLIER.get(scatter_count, 1.0)

        # 2. Line evaluation (left‑to‑right adjacent)
        match_count, winning_symbol, wild_used = self._check_winning_line(reels)

        # 3. Calculate monetary payout
        payout = 0.0
        multiplier = 0.0
        combination_type = "loss"
        is_jackpot = False

        if match_count >= 3 and winning_symbol is not None:
            sym = SYMBOLS[winning_symbol]
            base_mult = sym.payout_multiplier * MATCH_RATIOS[match_count]
            if wild_used:
                base_mult *= WILD_BONUS_MULTIPLIER
            if scatter_count >= 3:
                base_mult *= scatter_mult
            
            base_mult *= GLOBAL_MULTIPLIER_BOOST

            multiplier = round(base_mult, 4)
            payout = round(bet * multiplier, 2)
            is_jackpot = match_count == 5 and not sym.is_wild and not sym.is_scatter

            if is_jackpot:
                combination_type = f"JACKPOT 5x {winning_symbol}"
            else:
                wild_tag = " +WILD" if wild_used else ""
                combination_type = f"{match_count}x {winning_symbol}{wild_tag}"

        # 4. XP
        xp = XP_PER_SPIN
        if payout > 0:
            xp += XP_WIN_BONUS
        if is_jackpot:
            xp += XP_JACKPOT_BONUS

        return {
            "payout": payout,
            "combination_type": combination_type,
            "multiplier": multiplier,
            "is_jackpot": is_jackpot,
            "free_spins": free_spins,
            "xp_bonus": xp,
            "winning_symbol": winning_symbol,
            "match_count": match_count,
            "wild_used": wild_used,
        }

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _check_winning_line(
        self, reels: List[str]
    ) -> Tuple[int, str | None, bool]:
        """
        Evaluate the best left‑to‑right adjacent match.

        Returns (match_count, winning_symbol_name, wild_was_used).
        """
        if not reels:
            return 0, None, False

        # Resolve the "anchor" symbol from reel 0.
        # If reel 0 is a scatter we can't form a line win from it.
        first = reels[0]
        first_sym = SYMBOLS[first]

        if first_sym.is_scatter:
            return 0, None, False

        # If reel 0 is a wild, we need to find the first non‑wild symbol
        # to know what we're matching.
        anchor: str | None = None if first_sym.is_wild else first
        wild_used = first_sym.is_wild
        match_count = 1

        for reel_sym_name in reels[1:]:
            sym = SYMBOLS[reel_sym_name]

            if sym.is_scatter:
                break  # scatter doesn't participate in line wins

            if sym.is_wild:
                wild_used = True
                match_count += 1
                continue

            if anchor is None:
                # first concrete symbol found after leading wilds
                anchor = reel_sym_name
                match_count += 1
                continue

            if reel_sym_name == anchor:
                match_count += 1
            else:
                break  # chain broken

        if anchor is None:
            # All matched symbols were wilds — treat as wild jackpot
            # Use the rarest normal symbol as payout reference? No.
            # Wilds alone pay nothing; they only *complete* combos.
            return 0, None, True

        if match_count < 3:
            return match_count, None, wild_used

        return match_count, anchor, wild_used
