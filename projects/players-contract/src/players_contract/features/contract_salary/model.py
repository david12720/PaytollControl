from dataclasses import dataclass


@dataclass
class PlayerContractSalary:
    player_id: str
    team_name: str
    season: str
    person_type: str
    person_role: str | None
    employment_months: int | None
    base_salary_monthly: float | None
    base_salary_yearly: float | None
    housing_allowance_monthly: float | None
    housing_allowance_yearly: float | None
    car_allowance_monthly: float | None
    car_allowance_yearly: float | None
    points_bonus_per_point: float | None
    max_points_for_bonus: float | None
    points_bonus_total: float | None
    goal_assist_penalty_bonus: float | None
    source_file: str = ""
    page_in_document: int = 1
