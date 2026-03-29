from dataclasses import dataclass


@dataclass
class PlayerContractSalary:
    player_name: str
    player_id: str
    team_name: str
    season: str
    base_salary_monthly: float | None
    bonuses_monthly: float | None
    global_bonus: float | None
    credit_points: float | None
    housing_allowance_yearly: float | None
    housing_allowance_monthly: float | None
    car_allowance_monthly: float | None
    points_bonus_per_point: float | None
    max_points_for_bonus: float | None
    points_bonus_total: float | None
    goal_assist_penalty_bonus: float | None
    source_file: str = ""
    page_in_document: int = 1
