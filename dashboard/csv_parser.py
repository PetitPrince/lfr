import csv
import io
from dataclasses import dataclass, field


@dataclass
class ParsedRow:
    row_number: int
    data: dict = field(default_factory=dict)
    errors: list = field(default_factory=list)

    @property
    def is_valid(self):
        return len(self.errors) == 0

    def to_dict(self):
        return {
            "row_number": self.row_number,
            "data": self.data,
            "errors": self.errors,
            "is_valid": self.is_valid,
        }


# Expected CSV columns (all optional except role and character_name)
EXPECTED_COLUMNS = {
    "role", "character_name", "house", "year", "path", "clubs",
    "blood_status", "teaching_subject", "monitor_of_house",
    "monitor_of_club", "staff_title",
}

VALID_ROLES = {"student", "professor", "staff", "headmaster"}


def parse_casting_csv(csv_text, run):
    """Parse CSV text into a list of ParsedRow objects.

    Args:
        csv_text: Raw CSV string
        run: Run instance (used for vocabulary validation)

    Returns:
        List of ParsedRow objects
    """
    reader = csv.DictReader(io.StringIO(csv_text))

    if not reader.fieldnames:
        return [ParsedRow(row_number=0, errors=["Empty CSV or no header row."])]

    # Normalize headers
    clean_fieldnames = [f.strip().lower().replace(" ", "_") for f in reader.fieldnames]

    # Check for required columns
    if "role" not in clean_fieldnames:
        return [ParsedRow(row_number=0, errors=["Missing required column: role"])]
    if "character_name" not in clean_fieldnames:
        return [ParsedRow(row_number=0, errors=["Missing required column: character_name"])]

    # Build lookup sets for validation
    house_names = set(run.houses.values_list("name", flat=True))
    year_names = set(run.years.values_list("name", flat=True))
    path_names = set(run.paths.values_list("name", flat=True))
    club_names = set(run.clubs.values_list("name", flat=True))
    blood_status_names = set(run.blood_statuses.values_list("name", flat=True))
    subject_names = set(run.teaching_subjects.values_list("name", flat=True))

    # Detect custom attribute columns
    custom_attr_defs = {a.name.lower().replace(" ", "_"): a for a in run.custom_attributes.all()}

    rows = []
    for i, raw_row in enumerate(reader, start=2):  # row 2 = first data row
        # Remap to clean field names
        row = {}
        for orig_key, clean_key in zip(reader.fieldnames, clean_fieldnames):
            row[clean_key] = (raw_row.get(orig_key) or "").strip()

        parsed = ParsedRow(row_number=i)
        data = {}

        # Role
        role = row.get("role", "").lower()
        if role not in VALID_ROLES:
            parsed.errors.append(f"Invalid role: '{row.get('role', '')}'. Must be one of: {', '.join(VALID_ROLES)}")
        data["role"] = role

        # Character name
        data["character_name"] = row.get("character_name", "")

        # House
        house = row.get("house", "")
        if house:
            if house not in house_names:
                parsed.errors.append(f"Unknown house: '{house}'")
            data["house"] = house

        # Year
        year = row.get("year", "")
        if year:
            if year not in year_names:
                parsed.errors.append(f"Unknown year: '{year}'")
            data["year"] = year

        # Path
        path = row.get("path", "")
        if path:
            if path not in path_names:
                parsed.errors.append(f"Unknown path: '{path}'")
            data["path"] = path

        # Blood status
        blood_status = row.get("blood_status", "")
        if blood_status:
            if blood_status not in blood_status_names:
                parsed.errors.append(f"Unknown blood status: '{blood_status}'")
            data["blood_status"] = blood_status

        # Clubs (semicolon-separated within the cell)
        clubs_str = row.get("clubs", "")
        if clubs_str:
            club_list = [c.strip() for c in clubs_str.split(";") if c.strip()]
            for c in club_list:
                if c not in club_names:
                    parsed.errors.append(f"Unknown club: '{c}'")
            data["clubs"] = club_list

        # Teaching subject (single value)
        subject = row.get("teaching_subject", "")
        if subject:
            if subject not in subject_names:
                parsed.errors.append(f"Unknown teaching subject: '{subject}'")
            data["teaching_subject"] = subject

        # Monitor of house
        monitor_house = row.get("monitor_of_house", "")
        if monitor_house:
            if monitor_house not in house_names:
                parsed.errors.append(f"Unknown monitor_of_house: '{monitor_house}'")
            data["monitor_of_house"] = monitor_house

        # Monitor of club
        monitor_club = row.get("monitor_of_club", "")
        if monitor_club:
            if monitor_club not in club_names:
                parsed.errors.append(f"Unknown monitor_of_club: '{monitor_club}'")
            data["monitor_of_club"] = monitor_club

        # Staff title
        data["staff_title"] = row.get("staff_title", "")

        # Custom attributes
        custom_attrs = {}
        for col_key, attr_def in custom_attr_defs.items():
            val = row.get(col_key, "")
            if val:
                if attr_def.attr_type == "boolean":
                    custom_attrs[attr_def.name] = val.lower() in ("true", "yes", "1", "y")
                elif attr_def.attr_type == "choice":
                    if attr_def.choices and val not in attr_def.choices:
                        parsed.errors.append(
                            f"Invalid value '{val}' for {attr_def.name}. "
                            f"Must be one of: {', '.join(attr_def.choices)}"
                        )
                    custom_attrs[attr_def.name] = val
                else:
                    custom_attrs[attr_def.name] = val
        if custom_attrs:
            data["custom_attributes"] = custom_attrs

        parsed.data = data
        rows.append(parsed)

    return rows
