"""Markup helpers shared by channel short builders."""

from html import escape


def footer(source_line: str) -> str:
    """Return the on-screen footer containing only the source line (no credits)."""
    source_line = source_line.strip()
    if not source_line:
        raise ValueError("source line cannot be empty")
    return f'<div id="footer"><div id="src">{escape(source_line)}</div></div>'
