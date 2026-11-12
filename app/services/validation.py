from datetime import date


class ValidationError(ValueError):
    pass


def required_text(value: str | None, field: str, limit: int) -> str:
    value = (value or "").strip()
    if not value:
        raise ValidationError(f"{field} es obligatorio.")
    if len(value) > limit:
        raise ValidationError(f"{field} supera el máximo de {limit} caracteres.")
    return value


def optional_date(value: str | None, field: str) -> date | None:
    if not value:
        return None
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise ValidationError(f"{field} no tiene una fecha válida.") from exc
