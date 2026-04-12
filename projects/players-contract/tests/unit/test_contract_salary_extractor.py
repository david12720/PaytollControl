import json
from pathlib import Path
from unittest.mock import MagicMock

from players_contract.features.contract_salary.extractor import (
    ContractSalaryExtractor,
    DEFAULT_CAR_ALLOWANCE_MONTHLY,
    DEFAULT_HOUSING_ALLOWANCE_MONTHLY,
)


SAMPLE_LLM_RESPONSE = json.dumps({
    "player_id": "325604198",
    "team_name": "מכבי תל אביב",
    "season": "2025/26",
    "person_type": "player",
    "person_role": None,
    "employment_months": 10,
    "base_salary_monthly": 623250,
    "housing_allowance_monthly": 40000,
    "car_allowance_monthly": 2000,
    "points_bonus_per_point": 3640,
    "max_points_for_bonus": 50,
    "goal_assist_penalty_bonus": 1500,
})


def _make_prepared_file(name: str = "test.pdf") -> MagicMock:
    pf = MagicMock()
    pf.source_path = Path(name)
    pf.page_index = 0
    pf.mime_type = "application/pdf"
    pf.data = b"fake-pdf-bytes"
    pf.metadata = {}
    return pf


def test_extract_parses_json_response():
    llm = MagicMock()
    llm.extract_from_pdf.return_value = SAMPLE_LLM_RESPONSE

    extractor = ContractSalaryExtractor(language_model=llm)
    results = extractor.extract([_make_prepared_file()])

    assert len(results) == 1
    record = results[0]
    assert record["player_id"] == "325604198"
    assert record["season"] == "2025/26"
    assert record["person_type"] == "player"
    assert record["person_role"] is None
    assert record["base_salary_monthly"] == 623250
    assert record["base_salary_yearly"] == 623250 * 10
    assert record["housing_allowance_yearly"] == 40000 * 10
    assert record["car_allowance_yearly"] == 2000 * 10
    assert record["car_allowance_monthly"] == 2000
    assert record["points_bonus_per_point"] == 3640
    assert record["max_points_for_bonus"] == 50
    assert record["points_bonus_total"] == 3640 * 50
    assert record["goal_assist_penalty_bonus"] == 1500
    assert record["source_file"] == "test.pdf"
    assert "_llm_raw_text" not in record


def test_extract_parses_fenced_json():
    llm = MagicMock()
    llm.extract_from_pdf.return_value = f"```json\n{SAMPLE_LLM_RESPONSE}\n```"

    extractor = ContractSalaryExtractor(language_model=llm)
    results = extractor.extract([_make_prepared_file()])

    assert len(results) == 1
    assert results[0]["player_id"] == "325604198"


def test_extract_returns_empty_for_no_files():
    llm = MagicMock()
    extractor = ContractSalaryExtractor(language_model=llm)
    assert extractor.extract([]) == []


def test_parse_cached_response():
    llm = MagicMock()
    extractor = ContractSalaryExtractor(language_model=llm)
    results = extractor.parse_cached_response(SAMPLE_LLM_RESPONSE)

    assert len(results) == 1
    assert results[0]["base_salary_monthly"] == 623250


def test_extract_uses_images_for_non_pdf():
    llm = MagicMock()
    llm.extract_from_images.return_value = SAMPLE_LLM_RESPONSE

    pf = _make_prepared_file()
    pf.mime_type = "image/png"

    extractor = ContractSalaryExtractor(language_model=llm)
    results = extractor.extract([pf])

    assert len(results) == 1
    llm.extract_from_images.assert_called_once()


def test_resolve_allowances_replaces_true_with_defaults():
    response = json.dumps({
        "player_id": "123456789",
        "team_name": "הפועל באר שבע",
        "season": "2025/26",
        "person_type": "player",
        "person_role": None,
        "employment_months": 10,
        "base_salary_monthly": 30000,
        "housing_allowance_monthly": True,
        "car_allowance_monthly": True,
        "points_bonus_per_point": None,
        "max_points_for_bonus": None,
        "goal_assist_penalty_bonus": None,
    })
    llm = MagicMock()
    llm.extract_from_pdf.return_value = response

    extractor = ContractSalaryExtractor(language_model=llm)
    results = extractor.extract([_make_prepared_file()])

    record = results[0]
    assert record["car_allowance_monthly"] == DEFAULT_CAR_ALLOWANCE_MONTHLY
    assert record["car_allowance_yearly"] == DEFAULT_CAR_ALLOWANCE_MONTHLY * 10
    assert record["housing_allowance_monthly"] == DEFAULT_HOUSING_ALLOWANCE_MONTHLY
    assert record["housing_allowance_yearly"] == DEFAULT_HOUSING_ALLOWANCE_MONTHLY * 10
    assert record["base_salary_yearly"] == 30000 * 10


def test_resolve_allowances_computes_yearly_from_explicit_monthly():
    response = json.dumps({
        "player_id": "123456789",
        "team_name": "הפועל באר שבע",
        "season": "2025/26",
        "person_type": "player",
        "person_role": None,
        "employment_months": 10,
        "base_salary_monthly": 30000,
        "housing_allowance_monthly": 4000,
        "car_allowance_monthly": None,
        "points_bonus_per_point": None,
        "max_points_for_bonus": None,
        "goal_assist_penalty_bonus": None,
    })
    llm = MagicMock()
    llm.extract_from_pdf.return_value = response

    extractor = ContractSalaryExtractor(language_model=llm)
    results = extractor.extract([_make_prepared_file()])

    record = results[0]
    assert record["housing_allowance_monthly"] == 4000
    assert record["housing_allowance_yearly"] == 4000 * 10
