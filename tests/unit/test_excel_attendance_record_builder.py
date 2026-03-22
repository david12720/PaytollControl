from datetime import datetime, time

from payroll_control.abstractions.schema_detector import ColumnMapping
from payroll_control.features.excel_attendance.record_builder import build_records


MAPPING = ColumnMapping(
    date_column="A",
    from_time_column="B",
    to_time_column="C",
    header_row=1,
    data_start_row=2,
)


class TestBuildRecords:
    def test_basic_string_values(self):
        rows = [
            ["01/02/2025", "06:00", "18:00"],
            ["02/02/2025", "07:00", "17:00"],
        ]
        result = build_records(rows, MAPPING, "02.25")
        assert len(result) == 2
        assert result[0] == {
            "date": "01/02/2025",
            "from_time": "06:00",
            "to_time": "18:00",
            "sheet": "02.25",
        }
        assert result[1]["date"] == "02/02/2025"

    def test_datetime_objects_formatted(self):
        rows = [
            [datetime(2025, 2, 1), time(6, 0), time(18, 0)],
        ]
        result = build_records(rows, MAPPING, "sheet1")
        assert result[0]["date"] == "01/02/2025"
        assert result[0]["from_time"] == "06:00"
        assert result[0]["to_time"] == "18:00"

    def test_skips_rows_with_missing_date(self):
        rows = [
            [None, "06:00", "18:00"],
            ["01/02/2025", "07:00", "17:00"],
        ]
        result = build_records(rows, MAPPING, "s1")
        assert len(result) == 1
        assert result[0]["date"] == "01/02/2025"

    def test_skips_rows_with_missing_times(self):
        rows = [
            ["01/02/2025", None, "18:00"],
            ["02/02/2025", "07:00", None],
            ["03/02/2025", "08:00", "16:00"],
        ]
        result = build_records(rows, MAPPING, "s1")
        assert len(result) == 1
        assert result[0]["date"] == "03/02/2025"

    def test_skips_rows_with_empty_strings(self):
        rows = [
            ["01/02/2025", "", "18:00"],
            ["02/02/2025", "07:00", "17:00"],
        ]
        result = build_records(rows, MAPPING, "s1")
        assert len(result) == 1

    def test_skips_short_rows(self):
        rows = [
            ["01/02/2025", "06:00"],
        ]
        result = build_records(rows, MAPPING, "s1")
        assert len(result) == 0

    def test_non_a_columns(self):
        mapping = ColumnMapping(
            date_column="D",
            from_time_column="E",
            to_time_column="F",
            header_row=2,
            data_start_row=3,
        )
        rows = [
            [None, None, None, "01/02/2025", "06:00", "18:00"],
        ]
        result = build_records(rows, mapping, "sheet1")
        assert len(result) == 1
        assert result[0]["date"] == "01/02/2025"

    def test_empty_rows_returns_empty(self):
        result = build_records([], MAPPING, "s1")
        assert result == []

    def test_sheet_name_preserved(self):
        rows = [["01/02/2025", "06:00", "18:00"]]
        result = build_records(rows, MAPPING, "פברואר")
        assert result[0]["sheet"] == "פברואר"
