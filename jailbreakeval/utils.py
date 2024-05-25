import logging
import re
from typing import Any, Optional

logger = logging.getLogger(__name__)


def expr_to_func(expr):
    def _temp_expr_func_(response: Any) -> Optional[bool]:
        try:
            result = eval(expr, {"re": re}, {"response": response})
            if not isinstance(result, bool):
                logger.warning(f"Failed to extract result from response: {response}. expr: {expr}")
                return None
            return result
        except Exception as e:
            logger.error(f"Failed to extract result from response: {response}. expr: {expr}, exception: {e}")

    return _temp_expr_func_
