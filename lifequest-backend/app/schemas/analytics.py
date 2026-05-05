from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import date


class DailyXPPoint(BaseModel):
    date: date
    xp: int
    tasks_completed: int


class CategoryDistribution(BaseModel):
    category: str
    count: int
    percentage: float
    total_xp: int


class HeatmapCell(BaseModel):
    date: date
    value: int  # 0-4 for intensity


class StatsOverview(BaseModel):
    total_xp: int
    total_tasks_completed: int
    current_streak: int
    max_streak: int
    level: int
    gold: int
    crystals: int
    avg_effort_score: Optional[float]


class AnalyticsDashboardResponse(BaseModel):
    overview: StatsOverview
    xp_chart: List[DailyXPPoint]          # For line/bar chart
    category_distribution: List[CategoryDistribution]  # For pie chart
    heatmap: List[HeatmapCell]             # GitHub-style heatmap
    effort_score_avg_by_category: Dict[str, float]