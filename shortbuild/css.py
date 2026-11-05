"""Shared short composition CSS and channel themes.

BASE_CSS preserves the production BUD baseline; channel overrides are additive.
"""

BASE_CSS = '\n* { box-sizing: border-box; }\nhtml, body { margin: 0; padding: 0; width: 1080px; height: 1920px; overflow: hidden; background: #070504;\n  font-family: "Be Vietnam Pro", sans-serif; }\n#root { position: relative; width: 1080px; height: 1920px; overflow: hidden; }\n.abs { position: absolute; pointer-events: none; }\n#header { position: absolute; left: 60px; top: 58px; width: 960px; text-align: center; z-index: 20; }\n#chip { display: inline-block; padding: 6px 26px; border-radius: 999px; font-weight: 800; font-size: 32px;\n  letter-spacing: 0.04em; line-height: 1.2; }\n#title { margin-top: 14px; font-weight: 900; font-size: 64px; line-height: 1.16; color: #fff;\n  text-shadow: 0 4px 18px rgba(0,0,0,0.9), 0 0 3px rgba(0,0,0,0.9); }\n.card { position: absolute; left: 60px; width: 960px; text-align: center; z-index: 20; opacity: 0; }\n.big { font-weight: 900; font-size: 92px; line-height: 1.05; letter-spacing: 0.02em;\n  text-shadow: 0 4px 22px rgba(0,0,0,0.95); }\n.sub { margin-top: 14px; font-weight: 700; font-size: 44px; line-height: 1.25; color: #f5f0e6;\n  text-shadow: 0 3px 14px rgba(0,0,0,0.95); }\n.han { margin-top: 12px; font-weight: 700; font-size: 40px; color: #e9d6a6; letter-spacing: 0.08em;\n  font-family: "Noto Serif CJK SC", "Songti SC", "PingFang SC", serif; text-shadow: 0 3px 12px rgba(0,0,0,0.95); }\n#footer { position: absolute; left: 60px; width: 960px; text-align: center; z-index: 20; }\n#src { font-weight: 800; font-size: 32px; color: #f1e5c8; letter-spacing: 0.03em;\n  text-shadow: 0 2px 10px rgba(0,0,0,0.95); }\n'

THEMES = {
    "bud": {"background": "#070504", "accent": "#f1e5c8"},
    "fs": {"background": "#090713", "accent": "#e8bd55"},
}

def theme_css(channel: str) -> str:
    try:
        theme = THEMES[channel.lower()]
    except KeyError as exc:
        raise ValueError(f"Unknown short channel: {channel}") from exc
    return f"\n:root {{ --short-background: {theme['background']}; --short-accent: {theme['accent']}; }}\n"
