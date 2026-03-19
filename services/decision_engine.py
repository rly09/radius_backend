"""
Decision Engine - Smart ranking of services using scoring formula.

Score = (0.5 × rating) + (0.3 × proximity) + (0.2 × availability)

Uses Haversine formula for distance calculation.
"""

import math
from datetime import datetime, time
from typing import List, Tuple

from models.service import Service


class DecisionEngine:
    """Ranks and categorizes services using a smart scoring algorithm."""

    # Earth's radius in kilometers
    EARTH_RADIUS_KM = 6371.0

    @staticmethod
    def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Calculate the great-circle distance between two points
        on Earth using the Haversine formula.

        Returns distance in kilometers.
        """
        # Convert to radians
        lat1_r, lon1_r = math.radians(lat1), math.radians(lon1)
        lat2_r, lon2_r = math.radians(lat2), math.radians(lon2)

        dlat = lat2_r - lat1_r
        dlon = lon2_r - lon1_r

        a = (math.sin(dlat / 2) ** 2 +
             math.cos(lat1_r) * math.cos(lat2_r) * math.sin(dlon / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        return DecisionEngine.EARTH_RADIUS_KM * c

    @staticmethod
    def is_service_open(service: Service, check_time: time = None) -> bool:
        """Check if a service is currently open based on time."""
        if check_time is None:
            check_time = datetime.now().time()

        open_t = service.open_time
        close_t = service.close_time

        # Handle overnight hours (e.g., 22:00 - 06:00)
        if close_t < open_t:
            return check_time >= open_t or check_time <= close_t

        return open_t <= check_time <= close_t

    @staticmethod
    def calculate_proximity_score(distance_km: float, max_distance: float = 50.0) -> float:
        """
        Convert distance to a 0-5 proximity score.
        Closer = higher score. Max distance caps at 50km.
        """
        if distance_km >= max_distance:
            return 0.0
        return 5.0 * (1 - distance_km / max_distance)

    def rank_services(
        self,
        services: List[Service],
        user_lat: float,
        user_lon: float,
        filter_open: bool = True
    ) -> List[dict]:
        """
        Rank services by smart score.

        Returns list of dicts with service, distance, score, and open status.
        """
        ranked = []

        for service in services:
            # Calculate distance
            distance = self.haversine(user_lat, user_lon, service.latitude, service.longitude)

            # Check availability
            is_open = self.is_service_open(service)

            # Skip closed services if filtering enabled
            if filter_open and not is_open:
                continue

            # Calculate component scores
            rating_score = float(service.rating) if service.rating else 0.0
            proximity_score = self.calculate_proximity_score(distance)
            availability_score = 5.0 if is_open else 0.0

            # Final smart score
            score = (0.5 * rating_score) + (0.3 * proximity_score) + (0.2 * availability_score)

            ranked.append({
                "service": service,
                "distance_km": round(distance, 2),
                "score": round(score, 2),
                "is_open": is_open,
                "rating_score": rating_score,
                "proximity_score": round(proximity_score, 2),
            })

        # Sort by score descending
        ranked.sort(key=lambda x: x["score"], reverse=True)
        return ranked

    def get_decision_results(
        self,
        services: List[Service],
        user_lat: float,
        user_lon: float
    ) -> Tuple[List[dict], List[dict]]:
        """
        Get decision-categorized results:
        - best_option: highest overall score
        - fastest: nearest (smallest distance)
        - top_rated: highest rating

        Returns (decisions, all_ranked).
        """
        ranked = self.rank_services(services, user_lat, user_lon, filter_open=False)

        if not ranked:
            return [], []

        decisions = []

        # 🥇 Best Option — highest smart score
        best = ranked[0]
        decisions.append({
            "label": "best_option",
            "emoji": "🥇",
            "description": "Best Overall Option",
            "service": best,
        })

        # ⚡ Fastest — nearest by distance
        fastest = min(ranked, key=lambda x: x["distance_km"])
        if fastest["service"].id != best["service"].id:
            decisions.append({
                "label": "fastest",
                "emoji": "⚡",
                "description": "Nearest to You",
                "service": fastest,
            })

        # ⭐ Top Rated — highest rating
        top_rated = max(ranked, key=lambda x: x["rating_score"])
        already_ids = {d["service"]["service"].id for d in decisions}
        if top_rated["service"].id not in already_ids:
            decisions.append({
                "label": "top_rated",
                "emoji": "⭐",
                "description": "Highest Rated",
                "service": top_rated,
            })

        return decisions, ranked
