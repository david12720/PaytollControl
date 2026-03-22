from dataclasses import dataclass


@dataclass
class ExcelAttendanceRecord:
    date: str
    from_time: str
    to_time: str
    sheet: str
