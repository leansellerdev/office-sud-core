from office_sud_core.models.base import FillInfoPageParams


class StatementFillInfoParams(FillInfoPageParams):
    cat_group: str
    cat: str
    statement_character: str
