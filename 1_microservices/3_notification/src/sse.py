
from __future__ import annotations

def format_sse(*, event: str, data: str) -> str:
    """Format a single SSE event frame.

    Per spec, each field is on its own line; frames end with a blank line.
    """
    # (No id/retry fields for now.)
    return f"event: {event}
" f"data: {data}

"
