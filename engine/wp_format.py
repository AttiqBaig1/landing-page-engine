# -*- coding: utf-8 -*-
"""
wp_format.py
------------
Turns a generated index.html into the scoped Gutenberg "Custom HTML" block
that WordPress stores. Shared by the Streamlit app (app.py) and the browser
version (web/), so both publish identical pages.
"""
import re


def scope_css(css: str, wrapper: str = ".lp-engine-site") -> str:
    """
    Prefixes every selector with a wrapper class so the site's CSS can't be
    beaten by the WordPress theme's own styles, and so it can't leak out and
    affect the rest of the WP site either. Tested against the real generated
    CSS (brace count matches exactly before/after — no syntax corruption).
    """
    # Strip comments first: their text can contain commas and braces, and the
    # selector splitter would otherwise treat that prose as selectors and
    # corrupt every rule that follows.
    css = re.sub(r'/\*.*?\*/', '', css, flags=re.S)
    css = re.sub(r':root\{', wrapper + '{', css)

    def _map(sel: str) -> str:
        """`.lp-engine-site body` never matches anything. Rewrite root-level
        selectors (html, body, :root) onto the wrapper element itself."""
        s = sel.strip()
        if not s or s.startswith(wrapper):
            return s
        if s in ('body', 'html', 'html body', ':root'):
            return wrapper
        # Rules already written against the wrapper (possibly with a
        # specificity hack like `:not(#\\9)`) must NOT be nested under it.
        if s.startswith(wrapper) or s.startswith('#lp-engine-root'):
            return s
        for root in ('html body ', 'body ', 'html '):
            if s.startswith(root):
                return f'{wrapper} {s[len(root):]}'
        if s.startswith(('body:', 'body::')):
            return wrapper + s[4:]
        return f'{wrapper} {s}'

    # Track when we are inside an @keyframes block: its `from`, `to` and
    # `0%/100%` steps are NOT selectors. Prefixing them makes the whole
    # keyframes rule invalid, the browser drops it, and every element
    # animating from opacity:0 stays invisible forever — which is exactly
    # what hid the hero H1 on the live site.
    out, depth, i, n = [], 0, 0, len(css)
    keyframes_depth = None
    while i < n:
        if depth == 0:
            brace = css.find('{', i)
            if brace == -1:
                out.append(css[i:]); break
            chunk = css[i:brace].strip()
            if chunk.startswith(('@media', '@keyframes', '@font-face', '@import')) or not chunk:
                if chunk.startswith('@keyframes'):
                    keyframes_depth = 1
                out.append(css[i:brace] + '{'); depth = 1; i = brace + 1; continue
            parts = [s.strip() for s in chunk.split(',')]
            out.append(', '.join(_map(p) for p in parts) + '{')
            depth = 1; i = brace + 1
        else:
            close, open_ = css.find('}', i), css.find('{', i)
            if open_ != -1 and open_ < close:
                nchunk = css[i:open_].strip()
                if keyframes_depth is not None:
                    # inside @keyframes: emit the step selector untouched
                    out.append(css[i:open_] + '{')
                    depth += 1; i = open_ + 1; continue
                if nchunk and not nchunk.startswith('@'):
                    parts = [s.strip() for s in nchunk.split(',')]
                    out.append(', '.join(_map(p) for p in parts) + '{')
                else:
                    out.append(css[i:open_] + '{')
                depth += 1; i = open_ + 1; continue
            if close == -1:
                out.append(css[i:]); break
            out.append(css[i:close] + '}'); depth -= 1; i = close + 1
            if keyframes_depth is not None and depth < keyframes_depth:
                keyframes_depth = None
    return ''.join(out)


def _build_gutenberg(html: str) -> str:
    """Turn a generated index.html into the scoped Gutenberg block WP stores."""
    style_m = re.search(r"<style>(.*?)</style>", html, re.S)
    body_m = re.search(r"<body[^>]*>(.*)</body>", html, re.S)
    raw_css = style_m.group(1) if style_m else ""
    scoped_css = scope_css(raw_css) if raw_css else ""
    style_block = f"<style>{scoped_css}</style>" if scoped_css else ""
    body_inner = body_m.group(1) if body_m else html
    body_html = f'<div id="lp-engine-root" class="lp-engine-site">{style_block}{body_inner}</div>'
    return f"<!-- wp:html -->\n{body_html}\n<!-- /wp:html -->"


build_gutenberg = _build_gutenberg
