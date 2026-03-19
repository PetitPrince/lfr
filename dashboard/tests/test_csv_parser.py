import pytest

from dashboard.csv_parser import parse_casting_csv


class TestCSVParserHappyPath:
    def test_valid_student_row(self, run):
        csv = "role,character_name,house,year,path,blood_status\nstudent,Nadia,Libussa,3rd Year,Herbology,Pure-blood"
        rows = parse_casting_csv(csv, run)
        assert len(rows) == 1
        assert rows[0].is_valid
        assert rows[0].data["role"] == "student"
        assert rows[0].data["character_name"] == "Nadia"
        assert rows[0].data["house"] == "Libussa"

    def test_valid_professor_row(self, run):
        csv = "role,character_name,teaching_subject,monitor_of_house\nprofessor,Dr. Blackwood,Potions,Libussa"
        rows = parse_casting_csv(csv, run)
        assert len(rows) == 1
        assert rows[0].is_valid
        assert rows[0].data["teaching_subject"] == "Potions"
        assert rows[0].data["monitor_of_house"] == "Libussa"

    def test_valid_staff_row(self, run):
        csv = "role,character_name,staff_title\nstaff,Agnes,Librarian"
        rows = parse_casting_csv(csv, run)
        assert len(rows) == 1
        assert rows[0].is_valid
        assert rows[0].data["staff_title"] == "Librarian"

    def test_multiple_rows(self, run):
        csv = "role,character_name\nstudent,Alice\nstudent,Bob\nprofessor,Prof X"
        rows = parse_casting_csv(csv, run)
        assert len(rows) == 3
        assert all(r.is_valid for r in rows)

    def test_clubs_semicolon_separated(self, run):
        csv = "role,character_name,clubs\nstudent,Alice,Duelling Club; Quidditch"
        rows = parse_casting_csv(csv, run)
        assert rows[0].is_valid
        assert rows[0].data["clubs"] == ["Duelling Club", "Quidditch"]

    def test_optional_fields_blank(self, run):
        csv = "role,character_name,house,year\nstudent,Alice,,"
        rows = parse_casting_csv(csv, run)
        assert rows[0].is_valid
        assert "house" not in rows[0].data
        assert "year" not in rows[0].data

    def test_row_numbers_start_at_2(self, run):
        csv = "role,character_name\nstudent,Alice\nstudent,Bob"
        rows = parse_casting_csv(csv, run)
        assert rows[0].row_number == 2
        assert rows[1].row_number == 3

    def test_headers_normalized(self, run):
        csv = "Role, Character Name, House\nstudent,Alice,Libussa"
        rows = parse_casting_csv(csv, run)
        assert rows[0].is_valid
        assert rows[0].data["house"] == "Libussa"


class TestCSVParserErrors:
    def test_empty_csv(self, run):
        rows = parse_casting_csv("", run)
        assert len(rows) == 1
        assert not rows[0].is_valid
        assert "Empty CSV" in rows[0].errors[0]

    def test_missing_role_column(self, run):
        csv = "character_name\nAlice"
        rows = parse_casting_csv(csv, run)
        assert not rows[0].is_valid
        assert "Missing required column: role" in rows[0].errors[0]

    def test_missing_character_name_column(self, run):
        csv = "role\nstudent"
        rows = parse_casting_csv(csv, run)
        assert not rows[0].is_valid
        assert "Missing required column: character_name" in rows[0].errors[0]

    def test_invalid_role(self, run):
        csv = "role,character_name\nwizard,Alice"
        rows = parse_casting_csv(csv, run)
        assert not rows[0].is_valid
        assert "Invalid role" in rows[0].errors[0]

    def test_unknown_house(self, run):
        csv = "role,character_name,house\nstudent,Alice,Nonexistent"
        rows = parse_casting_csv(csv, run)
        assert not rows[0].is_valid
        assert "Unknown house" in rows[0].errors[0]

    def test_unknown_year(self, run):
        csv = "role,character_name,year\nstudent,Alice,5th Year"
        rows = parse_casting_csv(csv, run)
        assert not rows[0].is_valid
        assert "Unknown year" in rows[0].errors[0]

    def test_unknown_club(self, run):
        csv = "role,character_name,clubs\nstudent,Alice,Fake Club"
        rows = parse_casting_csv(csv, run)
        assert not rows[0].is_valid
        assert "Unknown club" in rows[0].errors[0]

    def test_unknown_teaching_subject(self, run):
        csv = "role,character_name,teaching_subject\nprofessor,Dr. X,Underwater Basket Weaving"
        rows = parse_casting_csv(csv, run)
        assert not rows[0].is_valid
        assert "Unknown teaching subject" in rows[0].errors[0]

    def test_mixed_valid_and_invalid_rows(self, run):
        csv = "role,character_name,house\nstudent,Alice,Libussa\nstudent,Bob,Nonexistent"
        rows = parse_casting_csv(csv, run)
        assert rows[0].is_valid
        assert not rows[1].is_valid


class TestCSVParserCustomAttributes:
    def test_boolean_custom_attr(self, run):
        from conftest import CustomAttributeDefinitionFactory

        CustomAttributeDefinitionFactory(run=run, name="Prefect", attr_type="boolean", applies_to="student")
        csv = "role,character_name,prefect\nstudent,Alice,yes"
        rows = parse_casting_csv(csv, run)
        assert rows[0].is_valid
        assert rows[0].data["custom_attributes"]["Prefect"] is True

    def test_boolean_custom_attr_false(self, run):
        from conftest import CustomAttributeDefinitionFactory

        CustomAttributeDefinitionFactory(run=run, name="Prefect", attr_type="boolean", applies_to="student")
        csv = "role,character_name,prefect\nstudent,Alice,no"
        rows = parse_casting_csv(csv, run)
        assert rows[0].is_valid
        assert rows[0].data["custom_attributes"]["Prefect"] is False

    def test_choice_custom_attr_valid(self, run):
        from conftest import CustomAttributeDefinitionFactory

        CustomAttributeDefinitionFactory(
            run=run, name="Faction", attr_type="choice", choices=["Red", "Blue"]
        )
        csv = "role,character_name,faction\nstudent,Alice,Red"
        rows = parse_casting_csv(csv, run)
        assert rows[0].is_valid
        assert rows[0].data["custom_attributes"]["Faction"] == "Red"

    def test_choice_custom_attr_invalid(self, run):
        from conftest import CustomAttributeDefinitionFactory

        CustomAttributeDefinitionFactory(
            run=run, name="Faction", attr_type="choice", choices=["Red", "Blue"]
        )
        csv = "role,character_name,faction\nstudent,Alice,Green"
        rows = parse_casting_csv(csv, run)
        assert not rows[0].is_valid
        assert "Invalid value" in rows[0].errors[0]


class TestParsedRow:
    def test_to_dict(self, run):
        csv = "role,character_name\nstudent,Alice"
        rows = parse_casting_csv(csv, run)
        d = rows[0].to_dict()
        assert d["row_number"] == 2
        assert d["is_valid"] is True
        assert d["data"]["character_name"] == "Alice"
        assert d["errors"] == []
