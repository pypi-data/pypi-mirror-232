from typing import Any, Optional

from .validation_error_detail import ValidationErrorDetail


class StringTooShortError(ValidationErrorDetail):
    error_type = 'string_too_short'

    def __init__(
        self,
        min_length: int,
        loc: tuple[int | str, ...],
        ctx: Optional[dict[str, dict[str, Any]]] = {},
        input: dict[str, Any] = {},
    ):
        ctx = ctx or {'min_length': min_length}
        super().__init__(self.error_type, loc, '', input, ctx)
