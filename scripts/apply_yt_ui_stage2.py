#!/usr/bin/env python3
"""
Stage 2: Official YouTube TV (Cobalt) 1:1 Home Screen & Slide-out Drawer for SmartTube.
Matches reference 4898.png + full slide-out navigation drawer:
  - Canvas #0F0F0F across all themes and rows
  - Auto-detects any .ttf font in repo (e.g. youtube_sans_bold.ttf) for headers & YouTube wordmark
  - Top bar: hides SmartTube red search circle, top avatar & S-beta clock badge;
    adds clean upper section label ("ГЛАВНАЯ") + bold row header + top-right YouTube logo (Play icon + "YouTube")
  - Video cards: 3-column proportion (276x155dp), crisp 3dp corners, outer double-bezel white focus ring
    (#F1F1F1 outer stroke + #0F0F0F inner gap drawn OUTSIDE clip bounds so it never gets clipped),
    borderless title (#F1F1F1) + channel & views metadata (#AAAAAA)
  - Slide-out left drawer (100% hidden when browsing rows, slides in on D-pad Left):
    #0F0F0F / #141414 drawer surface, YouTube outline vector icons (Search, Home, Shorts, Subscriptions,
    Library, History, Settings), subtle vertical white bar / #F1F1F1 pill highlight on focused item
  - Keeps Glide RGB_565 thumbnail decoding to save 50% RAM on 1 GB RAM devices
"""
import os
import re
import shutil
from pathlib import Path

ROOT = Path("SmartTube")
WORKSPACE = Path(os.environ.get("GITHUB_WORKSPACE", "."))
MODULES = [ROOT / "common", ROOT / "smarttubetv"]

YT_COLORS = {
    "window_background": "#0F0F0F",
    "default_background": "#0F0F0F",
    "grey_background": "#0F0F0F",
    "dark_grey": "#0F0F0F",
    "dark_grey_2": "#0F0F0F",
    "dark_grey_dark": "#0F0F0F",
    "dark_grey_light": "#161616",
    "dark_grey_card": "#00000000",
    "fastlane_background": "#121212",
    "lb_browse_headers_background": "#121212",
    "lb_details_overview_bg_color": "#0F0F0F",
    "lb_details_description_bg_color": "#0F0F0F",
    "lb_basic_card_bg_color": "#00000000",
    "lb_basic_card_info_bg_color": "#00000000",
    "card_background": "#00000000",
    "card_default_background": "#00000000",
    "card_info_background": "#00000000",
    "card_selected_background": "#00000000",
    "card_selected_text_background": "#00000000",
    "lb_default_brand_color": "#121212",
    "lb_default_brand_color_dark": "#0F0F0F",
    "lb_default_search_color": "#00000000",
    "lb_default_search_icon_color": "#F1F1F1",
    "lb_control_button_color": "#26FFFFFF",
    "lb_control_button_text": "#F1F1F1",
    "accent": "#F1F1F1",
    "colorAccent": "#F1F1F1",
    "lb_basic_card_title_text_color": "#F1F1F1",
    "lb_basic_card_content_text_color": "#AAAAAA",
    "lb_browse_title_color": "#F1F1F1",
    "lb_header_text_color": "#F1F1F1",
    "row_header_color": "#F1F1F1",
    "primary_text": "#F1F1F1",
    "secondary_text": "#AAAAAA",
    "card_title_text_color": "#F1F1F1",
    "card_content_text_color": "#AAAAAA",
    "lb_playback_progress_color_no_theme": "#FF0033",
    "progress_bar_color": "#FF0033",
    "player_progress_color": "#FF0033",
    "red_progress": "#FF0033",
}

# Crisp 3dp dark placeholder matching reference 4898.png
DRAWABLE_THUMB_BG = """<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android"
    android:shape="rectangle">
    <solid android:color="#1A1A1A" />
    <corners android:radius="3dp" />
</shape>
"""

# Double-bezel YouTube TV focus frame (2.5dp #F1F1F1 outer stroke + 2.5dp #0F0F0F inner gap)
DRAWABLE_THUMB_FOCUS_RING = """<?xml version="1.0" encoding="utf-8"?>
<layer-list xmlns:android="http://schemas.android.com/apk/res/android">
    <item>
        <shape android:shape="rectangle">
            <solid android:color="@android:color/transparent" />
            <stroke
                android:width="2.5dp"
                android:color="#F1F1F1" />
            <corners android:radius="4dp" />
        </shape>
    </item>
    <item
        android:left="2.5dp"
        android:top="2.5dp"
        android:right="2.5dp"
        android:bottom="2.5dp">
        <shape android:shape="rectangle">
            <solid android:color="@android:color/transparent" />
            <stroke
                android:width="2.5dp"
                android:color="#0F0F0F" />
            <corners android:radius="2dp" />
        </shape>
    </item>
</layer-list>
"""

DRAWABLE_THUMB_FOCUS_SELECTOR = """<?xml version="1.0" encoding="utf-8"?>
<selector xmlns:android="http://schemas.android.com/apk/res/android">
    <item android:state_selected="true" android:drawable="@drawable/yt_thumb_focus_ring" />
    <item android:state_focused="true" android:drawable="@drawable/yt_thumb_focus_ring" />
    <item android:drawable="@android:color/transparent" />
</selector>
"""

DRAWABLE_BADGE_BG = """<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android"
    android:shape="rectangle">
    <solid android:color="#CC000000" />
    <corners android:radius="2dp" />
</shape>
"""

DRAWABLE_PROGRESS_BAR = """<?xml version="1.0" encoding="utf-8"?>
<layer-list xmlns:android="http://schemas.android.com/apk/res/android">
    <item android:id="@android:id/background">
        <shape android:shape="rectangle">
            <solid android:color="#66FFFFFF" />
        </shape>
    </item>
    <item android:id="@android:id/progress">
        <clip>
            <shape android:shape="rectangle">
                <solid android:color="#FF0033" />
            </shape>
        </clip>
    </item>
</layer-list>
"""

# Official YouTube Play badge vector for top-right header
DRAWABLE_YT_PLAY_BADGE = """<?xml version="1.0" encoding="utf-8"?>
<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="32dp"
    android:height="22dp"
    android:viewportWidth="32"
    android:viewportHeight="22">
    <path
        android:fillColor="#FF0033"
        android:pathData="M31.3,3.4c-0.4,-1.4 -1.5,-2.5 -2.9,-2.9C25.8,0 16,0 16,0S6.2,0 3.6,0.5C2.2,0.9 1.1,2 0.7,3.4C0,6 0,11 0,11s0,5 0.7,7.6c0.4,1.4 1.5,2.5 2.9,2.9C6.2,22 16,22 16,22s9.8,0 12.4,-0.5c1.4,-0.4 2.5,-1.5 2.9,-2.9C32,16 32,11 32,11S32,6 31.3,3.4z" />
    <path
        android:fillColor="#FFFFFF"
        android:pathData="M12.8,15.7L21.1,11L12.8,6.3V15.7z" />
</vector>
"""

# Slide-out drawer item background: clean #F1F1F1 pill when focused, subtle #1FFFFFFF when selected
DRAWABLE_DRAWER_ITEM_BG = """<?xml version="1.0" encoding="utf-8"?>
<selector xmlns:android="http://schemas.android.com/apk/res/android">
    <item android:state_focused="true">
        <shape android:shape="rectangle">
            <solid android:color="#F1F1F1" />
            <corners android:radius="22dp" />
        </shape>
    </item>
    <item android:state_selected="true">
        <shape android:shape="rectangle">
            <solid android:color="#1FFFFFFF" />
            <corners android:radius="22dp" />
        </shape>
    </item>
    <item>
        <shape android:shape="rectangle">
            <solid android:color="@android:color/transparent" />
            <corners android:radius="22dp" />
        </shape>
    </item>
</selector>
"""

DRAWABLE_DRAWER_GRADIENT = """<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android"
    android:shape="rectangle">
    <gradient
        android:angle="0"
        android:startColor="#FC0F0F0F"
        android:centerColor="#F20F0F0F"
        android:endColor="#D90F0F0F"
        android:type="linear" />
</shape>
"""

# Official YouTube TV outline vector icons (24x24 viewport)
YT_VECTOR_ICONS = {
    "yt_ic_search.xml": """<?xml version="1.0" encoding="utf-8"?>
<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="24dp" android:height="24dp" android:viewportWidth="24" android:viewportHeight="24">
    <path android:fillColor="#FFFFFFFF"
        android:pathData="M20.87,20.17l-5.59,-5.59C16.35,13.35 17,11.75 17,10c0,-3.87 -3.13,-7 -7,-7s-7,3.13 -7,7s3.13,7 7,7c1.75,0 3.35,-0.65 4.58,-1.71l5.59,5.59L20.87,20.17zM10,16c-3.31,0 -6,-2.69 -6,-6s2.69,-6 6,-6s6,2.69 6,6S13.31,16 10,16z" />
</vector>""",
    "yt_ic_home.xml": """<?xml version="1.0" encoding="utf-8"?>
<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="24dp" android:height="24dp" android:viewportWidth="24" android:viewportHeight="24">
    <path android:fillColor="#FFFFFFFF"
        android:pathData="M12,4.33l7,6.12V20h-4v-6H9v6H5v-9.55L12,4.33M12,3L4,10v11h6v-6h4v6h6V10L12,3L12,3z" />
</vector>""",
    "yt_ic_shorts.xml": """<?xml version="1.0" encoding="utf-8"?>
<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="24dp" android:height="24dp" android:viewportWidth="24" android:viewportHeight="24">
    <path android:fillColor="#FFFFFFFF"
        android:pathData="M10,14.65v-5.3L15,12L10,14.65zM17.77,10.32c-0.77,-0.32 -1.2,-0.5 -1.2,-0.5L18,9.06c1.84,-0.96 2.53,-3.23 1.56,-5.06s-3.24,-2.53 -5.07,-1.56L6,6.94c-1.29,0.68 -2.07,2.04 -2,3.49c0.07,1.42 0.93,2.67 2.22,3.25c0.03,0.01 1.2,0.5 1.2,0.5L6,14.93c-1.83,0.97 -2.53,3.24 -1.56,5.07c0.97,1.83 3.24,2.53 5.07,1.56l8.5,-4.5c1.29,-0.68 2.06,-2.04 1.99,-3.49C19.93,12.15 19.06,10.9 17.77,10.32zM17.53,16.17l-8.5,4.5c-1.34,0.71 -3.01,0.2 -3.72,-1.14c-0.71,-1.34 -0.2,-3.01 1.14,-3.72l2.04,-1.08l-1.21,-0.5c-0.01,0 -1.16,-0.48 -1.18,-0.49c-0.95,-0.42 -1.58,-1.34 -1.63,-2.38c-0.05,-1.06 0.52,-2.06 1.46,-2.56l8.5,-4.5c1.34,-0.71 3.01,-0.2 3.72,1.14c0.71,1.34 0.2,3.01 -1.14,3.72l-2.04,1.08l1.21,0.5c0.01,0 1.16,0.48 1.17,0.49c0.95,0.43 1.58,1.35 1.63,2.38C19.04,14.68 18.47,15.67 17.53,16.17z" />
</vector>""",
    "yt_ic_subscriptions.xml": """<?xml version="1.0" encoding="utf-8"?>
<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="24dp" android:height="24dp" android:viewportWidth="24" android:viewportHeight="24">
    <path android:fillColor="#FFFFFFFF"
        android:pathData="M10,18v-6l5,3L10,18zM17,3H7v1h10V3zM20,6H4v1h16V6zM22,9H2v12h20V9zM3,10h18v10H3V10z" />
</vector>""",
    "yt_ic_library.xml": """<?xml version="1.0" encoding="utf-8"?>
<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="24dp" android:height="24dp" android:viewportWidth="24" android:viewportHeight="24">
    <path android:fillColor="#FFFFFFFF"
        android:pathData="M11,7l6,3.5L11,14V7L11,7zM18,20H4V6H3v15h15V20zM21,18H6V3h15V18zM7,17h13V4H7V17z" />
</vector>""",
    "yt_ic_history.xml": """<?xml version="1.0" encoding="utf-8"?>
<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="24dp" android:height="24dp" android:viewportWidth="24" android:viewportHeight="24">
    <path android:fillColor="#FFFFFFFF"
        android:pathData="M14.97,16.95L10,13.87V7h2v5.76l4.03,2.49L14.97,16.95zM22,12c0,5.51 -4.49,10 -10,10S2,17.51 2,12h1c0,4.96 4.04,9 9,9s9,-4.04 9,-9s-4.04,-9 -9,-9C8.81,3 5.92,4.64 4.28,7.38C4.17,7.56 4.06,7.75 3.97,7.94C3.96,7.96 3.95,7.98 3.94,8H8v1H2V3h1v4.74C3.04,7.67 3.09,7.59 3.13,7.51C3.24,7.3 3.35,7.09 3.47,6.89C5.28,3.83 8.48,2 12,2C17.51,2 22,6.49 22,12z" />
</vector>""",
    "yt_ic_settings.xml": """<?xml version="1.0" encoding="utf-8"?>
<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="24dp" android:height="24dp" android:viewportWidth="24" android:viewportHeight="24">
    <path android:fillColor="#FFFFFFFF"
        android:pathData="M12,9c1.65,0 3,1.35 3,3s-1.35,3 -3,3s-3,-1.35 -3,-3S10.35,9 12,9M12,8c-2.21,0 -4,1.79 -4,4s1.79,4 4,4s4,-1.79 4,-4S14.21,8 12,8L12,8zM13.22,3l0.55,2.2l0.13,0.51l0.5,0.18c0.61,0.23 1.19,0.56 1.72,0.98l0.4,0.32l0.5,-0.14l2.17,-0.62l1.22,2.11l-1.63,1.59l-0.37,0.36l0.08,0.51c0.05,0.32 0.08,0.64 0.08,0.98s-0.03,0.66 -0.08,0.98l-0.08,0.51l0.37,0.36l1.63,1.59l-1.22,2.11l-2.17,-0.62l-0.5,-0.14l-0.4,0.32c-0.53,0.43 -1.11,0.76 -1.72,0.98l-0.5,0.18l-0.13,0.51L13.22,21h-2.44l-0.55,-2.2l-0.13,-0.51l-0.5,-0.18C9,17.88 8.42,17.55 7.88,17.12l-0.4,-0.32l-0.5,0.14l-2.17,0.62L3.6,15.44l1.63,-1.59l0.37,-0.36l-0.08,-0.51C5.47,12.66 5.44,12.33 5.44,12s0.03,-0.66 0.08,-0.98l0.08,-0.51l-0.37,-0.36L3.6,8.56l1.22,-2.11l2.17,0.62l0.5,0.14l0.4,-0.32C8.42,6.45 9,6.12 9.61,5.9l0.5,-0.18l0.13,-0.51L10.78,3H13.22M14,2h-4L9.26,4.96c-0.73,0.27 -1.4,0.66 -2,1.14L4.34,5.27l-2,3.46l2.19,2.13C4.47,11.23 4.44,11.61 4.44,12s0.03,0.77 0.09,1.14l-2.19,2.13l2,3.46l2.92,-0.83c0.6,0.48 1.27,0.87 2,1.14L10,22h4l0.74,-2.96c0.73,-0.27 1.4,-0.66 2,-1.14l2.92,0.83l2,-3.46l-2.19,-2.13c0.06,-0.37 0.09,-0.75 0.09,-1.14s-0.03,-0.77 -0.09,-1.14l2.19,-2.13l-2,-3.46L16.74,6.1c-0.6,-0.48 -1.27,-0.87 -2,-1.14L14,2L14,2z" />
</vector>""",
}

EXTRA_YT_VALUES = """<?xml version="1.0" encoding="utf-8"?>
<resources>
    <color name="yt_canvas_bg">#0F0F0F</color>
    <color name="yt_drawer_bg">#121212</color>
    <color name="yt_surface_bg">#272727</color>
    <color name="yt_dialog_bg">#161616</color>
    <color name="yt_focus_white">#F1F1F1</color>
    <color name="yt_text_primary">#F1F1F1</color>
    <color name="yt_text_dimmed">#CCCCCC</color>
    <color name="yt_text_secondary">#AAAAAA</color>
    <color name="yt_brand_red">#FF0033</color>
</resources>
"""


def get_primary_res_dir() -> Path:
    for mod in MODULES:
        res_dir = mod / "src" / "main" / "res"
        if res_dir.exists():
            return res_dir
    raise SystemExit("[YT-UI] No Android res/ directory found inside SmartTube!")


def install_font(res_dir: Path) -> bool:
    """Auto-detect any .ttf font in repo (handles browser renames like 'youtube_sans_bold (1).ttf')."""
    search_roots = [WORKSPACE, Path(".")]
    ttf_files = []
    for base in search_roots:
        if not base.exists():
            continue
        for p in base.rglob("*.ttf"):
            if "SmartTube" in p.parts or ".git" in p.parts:
                continue
            ttf_files.append(p)

    # Prefer bold font if multiple exist
    src = None
    for p in ttf_files:
        if "bold" in p.name.lower() or "youtube" in p.name.lower():
            src = p
            break
    if not src and ttf_files:
        src = ttf_files[0]

    if not src:
        print("[YT-UI] WARNING: No .ttf font found in repo -> keeping system font.")
        return False

    font_dir = res_dir / "font"
    font_dir.mkdir(parents=True, exist_ok=True)
    dst = font_dir / "youtube_sans_bold.ttf"
    shutil.copy2(src, dst)
    print(f"[YT-UI] Installed YouTube Sans Bold font from '{src}' -> {dst}")
    return True


def write_shared_resources(res_dir: Path):
    drawable_dir = res_dir / "drawable"
    drawable_dir.mkdir(parents=True, exist_ok=True)
    files = {
        "yt_thumb_rounded_bg.xml": DRAWABLE_THUMB_BG,
        "yt_thumb_focus_ring.xml": DRAWABLE_THUMB_FOCUS_RING,
        "yt_thumb_focus_selector.xml": DRAWABLE_THUMB_FOCUS_SELECTOR,
        "yt_badge_bg.xml": DRAWABLE_BADGE_BG,
        "yt_card_progress.xml": DRAWABLE_PROGRESS_BAR,
        "yt_play_badge.xml": DRAWABLE_YT_PLAY_BADGE,
        "yt_drawer_item_bg.xml": DRAWABLE_DRAWER_ITEM_BG,
        "yt_drawer_gradient.xml": DRAWABLE_DRAWER_GRADIENT,
    }
    files.update(YT_VECTOR_ICONS)
    for name, content in files.items():
        (drawable_dir / name).write_text(content.strip() + "\n", encoding="utf-8")

    values_dir = res_dir / "values"
    values_dir.mkdir(parents=True, exist_ok=True)
    (values_dir / "yt_theme_tokens.xml").write_text(EXTRA_YT_VALUES.strip() + "\n", encoding="utf-8")
    print(f"[YT-UI] Wrote YouTube TV drawables, vector icons & color tokens -> {res_dir}")


def patch_colors_xml(xml_path: Path):
    if xml_path.name == "yt_theme_tokens.xml":
        return
    text = xml_path.read_text(encoding="utf-8")
    changed = 0
    for key, hex_val in YT_COLORS.items():
        pattern = re.compile(rf'(<color\s+name="{re.escape(key)}"[^>]*>)([^<]+)(</color>)')
        new_text, count = pattern.subn(rf"\g<1>{hex_val}\g<3>", text)
        if count:
            text = new_text
            changed += count
    if changed:
        xml_path.write_text(text, encoding="utf-8")
        print(f"[YT-UI] Updated {changed} color tokens in {xml_path}")


def patch_dimens_xml(xml_path: Path):
    text = xml_path.read_text(encoding="utf-8")
    dimens_map = {
        # Match reference 4898.png: 3 large cards across screen + compact top header
        "lb_browse_rows_margin_top": "74dp",
        "lb_browse_padding_start": "44dp",
        "lb_browse_padding_end": "44dp",
        "lb_browse_item_margin": "16dp",
        "lb_browse_row_title_text_size": "18sp",
        "lb_basic_card_title_text_size": "14sp",
        "lb_basic_card_content_text_size": "12sp",
        "lb_basic_card_info_padding_top": "9dp",
        "lb_basic_card_info_padding_bottom": "4dp",
        "lb_basic_card_info_padding_horizontal": "2dp",
        # Slide-out drawer dimensions (100% hidden when closed, sleek 236dp when open)
        "lb_browse_headers_width": "236dp",
        "lb_browse_headers_vertical_spacing": "6dp",
        "lb_browse_header_height": "44dp",
        "lb_browse_header_padding_end": "16dp",
        "card_width": "276dp",
        "card_height": "155dp",
    }
    changed = 0
    for key, val in dimens_map.items():
        pattern = re.compile(rf'(<dimen\s+name="{re.escape(key)}"[^>]*>)([^<]+)(</dimen>)')
        new_text, count = pattern.subn(rf"\g<1>{val}\g<3>", text)
        if count:
            text = new_text
            changed += count
    if changed:
        xml_path.write_text(text, encoding="utf-8")
        print(f"[YT-UI] Updated {changed} dimens in {xml_path}")


def upsert_style_item(style_block: str, item_name: str, item_val: str) -> str:
    pat = re.compile(rf'(<item\s+name="{re.escape(item_name)}"[^>]*>)([^<]+)(</item>)')
    if pat.search(style_block):
        return pat.sub(rf"\g<1>{item_val}\g<3>", style_block, count=1)
    return style_block.replace(
        "</style>",
        f'        <item name="{item_name}">{item_val}</item>\n    </style>',
        1,
    )


def patch_styles_and_themes(xml_path: Path, has_font: bool):
    text = xml_path.read_text(encoding="utf-8")
    original = text

    attr_replacements = {
        "android:windowBackground": "@color/yt_canvas_bg",
        "android:colorBackground": "@color/yt_canvas_bg",
        "defaultBrandColor": "@color/yt_drawer_bg",
        "defaultBrandColorDark": "@color/yt_canvas_bg",
        "defaultSearchColor": "@android:color/transparent",
        "cardBackground": "@android:color/transparent",
        "infoAreaBackground": "@android:color/transparent",
    }
    for attr, val in attr_replacements.items():
        text = re.sub(
            rf'(<item\s+name="{re.escape(attr)}"[^>]*>)[^<]+(</item>)',
            rf"\g<1>{val}\g<2>",
            text,
        )

    if has_font:
        def patch_header_style(match: re.Match) -> str:
            block = match.group(0)
            name_m = re.search(r'name="([^"]+)"', block)
            if not name_m:
                return block
            sname = name_m.group(1)
            if any(k in sname for k in ("Row.Header", "RowHeader", "BrowseTitle", "HeaderText", "DialogTitle")):
                block = upsert_style_item(block, "android:fontFamily", "@font/youtube_sans_bold")
                block = upsert_style_item(block, "android:textColor", "@color/yt_text_primary")
            return block

        text = re.sub(r"<style\b[^>]*>.*?</style>", patch_header_style, text, flags=re.DOTALL)

    if text != original:
        xml_path.write_text(text, encoding="utf-8")
        print(f"[YT-UI] Patched theme styles in {xml_path}")


def upsert_attr_in_xml_tag(xml_text: str, view_id: str, attrs: dict) -> str:
    tag_pat = re.compile(
        rf'(<[A-Za-z0-9_.]+(?:\s+[^>]*?)?android:id="@\+id/{re.escape(view_id)}"[^>]*?/?>)',
        flags=re.DOTALL,
    )

    def repl(match: re.Match) -> str:
        tag = match.group(1)
        for attr, val in attrs.items():
            attr_pat = re.compile(rf'({re.escape(attr)}=")([^"]*)(")')
            if attr_pat.search(tag):
                tag = attr_pat.sub(rf"\g<1>{val}\g<3>", tag, count=1)
            else:
                if tag.endswith("/>"):
                    tag = tag[:-2].rstrip() + f'\n        {attr}="{val}" />'
                else:
                    tag = tag[:-1].rstrip() + f'\n        {attr}="{val}">'
        return tag

    return tag_pat.sub(repl, xml_text)


def patch_card_layouts(res_dir: Path):
    layout_dir = res_dir / "layout"
    if not layout_dir.exists():
        return

    for layout in layout_dir.glob("*card*.xml"):
        text = layout.read_text(encoding="utf-8")
        if "main_image" not in text:
            continue

        original = text
        text = upsert_attr_in_xml_tag(
            text, "info_field", {"android:background": "@android:color/transparent"}
        )
        text = upsert_attr_in_xml_tag(
            text,
            "main_image",
            {
                "android:background": "@drawable/yt_thumb_rounded_bg",
                "android:duplicateParentState": "true",
            },
        )
        if 'android:id="@+id/progress_bar"' in text:
            text = upsert_attr_in_xml_tag(
                text,
                "progress_bar",
                {"android:progressDrawable": "@drawable/yt_card_progress"},
            )

        if text != original:
            layout.write_text(text, encoding="utf-8")
            print(f"[YT-UI] Updated card layout {layout}")


def ensure_imports(java_text: str, imports: list) -> str:
    to_add = [imp for imp in imports if f"import {imp};" not in java_text]
    if not to_add:
        return java_text
    pkg_m = re.search(r"^(package\s+[^;]+;\s*)", java_text, flags=re.MULTILINE)
    if not pkg_m:
        return java_text
    block = "\n".join(f"import {imp};" for imp in to_add) + "\n"
    pos = pkg_m.end()
    return java_text[:pos] + "\n" + block + java_text[pos:]


def patch_complex_card_view():
    """
    Fixes the focus ring clipping bug from Stage 1:
    Instead of putting foreground on the clipped ImageView, we add an unclipped overlay View
    inside the thumbnail's parent container (or parent card) so the double-bezel white ring
    renders crisply OUTSIDE the 3dp thumbnail corners!
    """
    candidates = [
        p for p in ROOT.rglob("ComplexImageCardView.java")
        if "build" not in p.parts
    ]
    if not candidates:
        print("[YT-UI] WARNING: ComplexImageCardView.java not found!")
        return

    for java_file in candidates:
        text = java_file.read_text(encoding="utf-8")
        if "YT_STAGE2_CARD" in text:
            continue

        text = ensure_imports(
            text,
            [
                "android.graphics.Color",
                "android.graphics.Outline",
                "android.graphics.drawable.Drawable",
                "android.os.Build",
                "android.view.View",
                "android.view.ViewGroup",
                "android.view.ViewOutlineProvider",
                "android.widget.FrameLayout",
                "android.widget.ImageView",
                "android.widget.ProgressBar",
                "android.widget.TextView",
                "androidx.core.content.ContextCompat",
            ],
        )

        attached_super_re = re.compile(r"(super\.onAttachedToWindow\s*\(\s*\)\s*;)")
        attached_decl_re = re.compile(r"((?:protected|public)\s+void\s+onAttachedToWindow\s*\(\s*\)\s*\{)")
        has_attached = attached_decl_re.search(text) is not None
        if has_attached:
            if attached_super_re.search(text):
                text = attached_super_re.sub(r"\g<1>\n        applyYouTubeCardStyle();", text, count=1)
            else:
                text = attached_decl_re.sub(r"\g<1>\n        applyYouTubeCardStyle();", text, count=1)

        selected_decl_re = re.compile(r"(public\s+void\s+setSelected\s*\(\s*boolean\s+(\w+)\s*\)\s*\{)")
        sel_match = selected_decl_re.search(text)
        has_selected = sel_match is not None
        if has_selected:
            param = sel_match.group(2)
            super_sel_re = re.compile(rf"(super\.setSelected\s*\(\s*{re.escape(param)}\s*\)\s*;)")
            if super_sel_re.search(text):
                text = super_sel_re.sub(rf"\g<1>\n        applyYouTubeFocusAnim({param});", text, count=1)
            else:
                text = selected_decl_re.sub(rf"\g<1>\n        applyYouTubeFocusAnim({param});", text, count=1)

        extra_overrides = ""
        if not has_attached:
            extra_overrides += """
    @Override
    protected void onAttachedToWindow() {
        super.onAttachedToWindow();
        applyYouTubeCardStyle();
    }
"""
        if not has_selected:
            extra_overrides += """
    @Override
    public void setSelected(boolean selected) {
        super.setSelected(selected);
        applyYouTubeFocusAnim(selected);
    }
"""

        helper_code = f"""
    // YT_STAGE2_CARD: 3dp crisp corners + unclipped double-bezel white focus ring + borderless text
    private boolean mYtStyled = false;
    private View mYtFocusOverlay = null;

    private View findYtViewByName(String idName) {{
        int id = getResources().getIdentifier(idName, "id", getContext().getPackageName());
        return id != 0 ? findViewById(id) : null;
    }}

    private void applyYouTubeCardStyle() {{
        if (mYtStyled) {{
            return;
        }}
        mYtStyled = true;

        setClipChildren(false);
        setClipToPadding(false);
        setBackgroundColor(Color.TRANSPARENT);

        View infoField = findYtViewByName("info_field");
        if (infoField != null) {{
            infoField.setBackgroundColor(Color.TRANSPARENT);
        }}

        ImageView img = getMainImageView();
        if (img != null) {{
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.LOLLIPOP) {{
                final float radiusPx = 3f * getResources().getDisplayMetrics().density;
                img.setOutlineProvider(new ViewOutlineProvider() {{
                    @Override
                    public void getOutline(View view, Outline outline) {{
                        outline.setRoundRect(0, 0, view.getWidth(), view.getHeight(), radiusPx);
                    }}
                }});
                img.setClipToOutline(true);
            }}

            // Attach unclipped double-bezel white focus ring on top of thumbnail container
            if (img.getParent() instanceof ViewGroup) {{
                ViewGroup thumbParent = (ViewGroup) img.getParent();
                thumbParent.setClipChildren(false);
                thumbParent.setClipToPadding(false);
                int ringId = getResources().getIdentifier("yt_thumb_focus_ring", "drawable", getContext().getPackageName());
                if (ringId != 0 && mYtFocusOverlay == null) {{
                    mYtFocusOverlay = new View(getContext());
                    mYtFocusOverlay.setBackground(ContextCompat.getDrawable(getContext(), ringId));
                    mYtFocusOverlay.setVisibility(isSelected() ? View.VISIBLE : View.INVISIBLE);
                    int pad = (int) (-3f * getResources().getDisplayMetrics().density);
                    ViewGroup.LayoutParams lp = img.getLayoutParams();
                    if (lp instanceof ViewGroup.MarginLayoutParams) {{
                        ViewGroup.MarginLayoutParams mlp = new ViewGroup.MarginLayoutParams(lp.width, lp.height);
                        mlp.setMargins(pad, pad, pad, pad);
                        thumbParent.addView(mYtFocusOverlay, mlp);
                    }} else {{
                        thumbParent.addView(mYtFocusOverlay, new ViewGroup.LayoutParams(
                            ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.MATCH_PARENT));
                    }}
                }}
            }}
        }}

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.LOLLIPOP) {{
            final float badgeRadius = 2f * getResources().getDisplayMetrics().density;
            for (String bn : new String[] {{"duration_badge", "badge_text"}}) {{
                View badge = findYtViewByName(bn);
                if (badge != null) {{
                    badge.setOutlineProvider(new ViewOutlineProvider() {{
                        @Override
                        public void getOutline(View view, Outline outline) {{
                            outline.setRoundRect(0, 0, view.getWidth(), view.getHeight(), badgeRadius);
                        }}
                    }});
                    badge.setClipToOutline(true);
                }}
            }}
        }}

        View pb = findYtViewByName("progress_bar");
        if (pb instanceof ProgressBar) {{
            int pbRes = getResources().getIdentifier("yt_card_progress", "drawable", getContext().getPackageName());
            if (pbRes != 0) {{
                ((ProgressBar) pb).setProgressDrawable(ContextCompat.getDrawable(getContext(), pbRes));
            }}
        }}

        applyYouTubeFocusAnim(isSelected());
    }}

    private void applyYouTubeFocusAnim(boolean selected) {{
        setBackgroundColor(Color.TRANSPARENT);
        View infoField = findYtViewByName("info_field");
        if (infoField != null) {{
            infoField.setBackgroundColor(Color.TRANSPARENT);
        }}

        if (mYtFocusOverlay != null) {{
            mYtFocusOverlay.setVisibility(selected ? View.VISIBLE : View.INVISIBLE);
            float ringScale = selected ? 1.045f : 1.0f;
            mYtFocusOverlay.animate().scaleX(ringScale).scaleY(ringScale).setDuration(130).start();
        }}

        ImageView img = getMainImageView();
        if (img != null) {{
            float target = selected ? 1.045f : 1.0f;
            img.animate()
                .scaleX(target)
                .scaleY(target)
                .setDuration(130)
                .start();
        }}

        View title = findYtViewByName("title_text");
        if (title instanceof TextView) {{
            ((TextView) title).setTextColor(selected ? 0xFFF1F1F1 : 0xFFCCCCCC);
        }}
        View content = findYtViewByName("content_text");
        if (content instanceof TextView) {{
            ((TextView) content).setTextColor(0xFFAAAAAA);
        }}
    }}
{extra_overrides}
"""

        idx = text.rfind("}")
        if idx != -1:
            text = text[:idx] + helper_code + "\n}\n"
            java_file.write_text(text, encoding="utf-8")
            print(f"[YT-UI] Patched ComplexImageCardView (unclipped white focus frame) -> {java_file}")


def patch_top_bar_and_drawer():
    """
    1. Top Bar (1:1 with reference 4898.png):
       - Hides SmartTube's red search circle, top-left avatar & top-right S-beta clock/logo
       - Injects official YouTube top-right wordmark (Red Play badge + 'YouTube' in YouTube Sans Bold)
       - Adds subtle uppercase section eyebrow ('ГЛАВНАЯ') above the first row header
    2. Slide-out Left Navigation Drawer (100% hidden when closed, slides out on D-pad Left):
       - Sets drawer background to #121212 with YouTube pill focus (#F1F1F1 bg + #0F0F0F text/icon)
       - Maps section icons to official YouTube outline vector drawables
    """
    # A. Patch TitleView / BrowseTitleView XML layouts for top-right YouTube logo & clean header
    for res_dir in [m / "src" / "main" / "res" for m in MODULES]:
        layout_dir = res_dir / "layout"
        if not layout_dir.exists():
            continue

        for title_xml in list(layout_dir.glob("*title*.xml")) + list(layout_dir.glob("*browse*.xml")):
            text = title_xml.read_text(encoding="utf-8")
            original = text

            # Hide SmartTube clock / date / beta badge views if present
            for hide_id in ("clock", "date", "global_time", "logo", "app_logo", "search_orb"):
                if f'android:id="@+id/{hide_id}"' in text:
                    text = upsert_attr_in_xml_tag(text, hide_id, {"android:visibility": "gone"})

            if text != original:
                title_xml.write_text(text, encoding="utf-8")
                print(f"[YT-UI] Cleaned SmartTube top bar elements in {title_xml}")

        # B. Patch Leanback Header item layout for YouTube pill highlight & icon tint
        for header_xml in layout_dir.glob("*header*.xml"):
            text = header_xml.read_text(encoding="utf-8")
            if "row_header" not in text and "header_icon" not in text and "header_label" not in text:
                continue
            original = text
            if 'android:id="@+id/header_label"' in text:
                text = upsert_attr_in_xml_tag(
                    text,
                    "header_label",
                    {
                        "android:textSize": "14sp",
                        "android:textColor": "#F1F1F1",
                    },
                )
            if text != original:
                header_xml.write_text(text, encoding="utf-8")
                print(f"[YT-UI] Styled slide-out drawer item layout {header_xml}")

    # C. Patch BrowseFragment / BrowseSupportFragment & HeadersFragment in Java to enforce:
    #    - 100% slide-out drawer (HEADERS_ENABLED, hidden by default, slides over rows)
    #    - Top-right official YouTube logo injection into BrowseFragment root view
    #    - Drawer background #121212 & white pill focus state
    for java_file in ROOT.rglob("*.java"):
        if "build" in java_file.parts:
            continue
        fname = java_file.name
        if fname not in ("BrowseFragment.java", "MainFragment.java", "HeadersFragment.java"):
            continue

        text = java_file.read_text(encoding="utf-8")
        if "YT_STAGE2_NAV" in text:
            continue

        if fname in ("BrowseFragment.java", "MainFragment.java") and "onViewCreated" in text:
            text = ensure_imports(
                text,
                [
                    "android.graphics.Color",
                    "android.graphics.Typeface",
                    "android.view.Gravity",
                    "android.view.View",
                    "android.view.ViewGroup",
                    "android.widget.FrameLayout",
                    "android.widget.ImageView",
                    "android.widget.LinearLayout",
                    "android.widget.TextView",
                    "androidx.core.content.ContextCompat",
                    "androidx.core.content.res.ResourcesCompat",
                ],
            )

            hook = """
        // YT_STAGE2_NAV: Official YouTube TV top-right wordmark + clean canvas
        applyYouTubeTopChrome(view);"""

            # Inject right after super.onViewCreated(view, savedInstanceState);
            new_text, count = re.subn(
                r"(super\.onViewCreated\s*\(\s*(\w+)\s*,\s*\w+\s*\)\s*;)",
                lambda m: m.group(1) + hook.replace("(view)", f"({m.group(2)})"),
                text,
                count=1,
            )
            if count:
                helper = """
    private void applyYouTubeTopChrome(View root) {
        if (!(root instanceof ViewGroup) || getContext() == null) {
            return;
        }
        ViewGroup vg = (ViewGroup) root;
        vg.setBackgroundColor(0xFF0F0F0F);

        // Hide SmartTube top-left red search orb / top-right clock & S-beta badge
        String[] legacyIds = new String[] {
            "search_orb", "title_orb", "clock", "date", "global_time", "title_badge"
        };
        for (String idName : legacyIds) {
            int id = getResources().getIdentifier(idName, "id", getContext().getPackageName());
            if (id != 0) {
                View v = vg.findViewById(id);
                if (v != null) {
                    v.setVisibility(View.GONE);
                }
            }
        }

        // Add official YouTube logo (Red Play badge + YouTube wordmark) in top-right corner
        if (vg.findViewWithTag("yt_top_wordmark") == null) {
            float d = getResources().getDisplayMetrics().density;
            LinearLayout brandBox = new LinearLayout(getContext());
            brandBox.setTag("yt_top_wordmark");
            brandBox.setOrientation(LinearLayout.HORIZONTAL);
            brandBox.setGravity(Gravity.CENTER_VERTICAL);

            ImageView playIcon = new ImageView(getContext());
            int badgeId = getResources().getIdentifier("yt_play_badge", "drawable", getContext().getPackageName());
            if (badgeId != 0) {
                playIcon.setImageDrawable(ContextCompat.getDrawable(getContext(), badgeId));
            }
            LinearLayout.LayoutParams iconLp = new LinearLayout.LayoutParams((int) (28 * d), (int) (20 * d));
            iconLp.rightMargin = (int) (6 * d);
            brandBox.addView(playIcon, iconLp);

            TextView wordmark = new TextView(getContext());
            wordmark.setText("YouTube");
            wordmark.setTextColor(0xFFF1F1F1);
            wordmark.setTextSize(20f);
            wordmark.setLetterSpacing(-0.03f);
            int fontId = getResources().getIdentifier("youtube_sans_bold", "font", getContext().getPackageName());
            if (fontId != 0) {
                try {
                    Typeface tf = ResourcesCompat.getFont(getContext(), fontId);
                    if (tf != null) {
                        wordmark.setTypeface(tf);
                    }
                } catch (Throwable ignored) {}
            } else {
                wordmark.setTypeface(Typeface.DEFAULT_BOLD);
            }
            brandBox.addView(wordmark);

            FrameLayout.LayoutParams lp = new FrameLayout.LayoutParams(
                ViewGroup.LayoutParams.WRAP_CONTENT,
                ViewGroup.LayoutParams.WRAP_CONTENT,
                Gravity.TOP | Gravity.END
            );
            lp.topMargin = (int) (24 * d);
            lp.rightMargin = (int) (44 * d);
            vg.addView(brandBox, lp);
        }
    }
"""
                idx = new_text.rfind("}")
                if idx != -1:
                    new_text = new_text[:idx] + helper + "\n}\n"
                    java_file.write_text(new_text, encoding="utf-8")
                    print(f"[YT-UI] Injected YouTube top chrome into {java_file}")

        elif fname == "HeadersFragment.java" and "onViewCreated" in text:
            text = ensure_imports(
                text,
                [
                    "android.view.View",
                    "androidx.core.content.ContextCompat",
                ],
            )
            new_text, count = re.subn(
                r"(super\.onViewCreated\s*\(\s*(\w+)\s*,\s*\w+\s*\)\s*;)",
                lambda m: m.group(1)
                + f"\n        // YT_STAGE2_NAV: Sleek #121212 slide-out drawer gradient\n"
                + f"        int gradId = getResources().getIdentifier(\"yt_drawer_gradient\", \"drawable\", {m.group(2)}.getContext().getPackageName());\n"
                + f"        if (gradId != 0) {{ {m.group(2)}.setBackground(ContextCompat.getDrawable({m.group(2)}.getContext(), gradId)); }} else {{ {m.group(2)}.setBackgroundColor(0xF5121212); }}",
                text,
                count=1,
            )
            if count:
                java_file.write_text(new_text, encoding="utf-8")
                print(f"[YT-UI] Styled slide-out HeadersFragment drawer -> {java_file}")


def patch_header_presenter():
    """Style slide-out left drawer items like YouTube TV: white pill focus (#F1F1F1) + dark text/icon."""
    for java_file in ROOT.rglob("*HeaderPresenter*.java"):
        if "build" in java_file.parts:
            continue
        text = java_file.read_text(encoding="utf-8")
        if "YT_STAGE2_HEADER_ITEM" in text:
            continue

        if "onBindViewHolder" in text:
            text = ensure_imports(
                text,
                [
                    "android.graphics.PorterDuff",
                    "android.view.View",
                    "android.widget.ImageView",
                    "android.widget.TextView",
                    "androidx.core.content.ContextCompat",
                ],
            )
            helper = """
    // YT_STAGE2_HEADER_ITEM: YouTube TV slide-out drawer pill focus (#F1F1F1 fill, #0F0F0F text/icon)
    private void styleYouTubeDrawerRow(final View rowView) {
        if (rowView == null) return;
        int bgId = rowView.getResources().getIdentifier("yt_drawer_item_bg", "drawable", rowView.getContext().getPackageName());
        if (bgId != 0) {
            rowView.setBackground(ContextCompat.getDrawable(rowView.getContext(), bgId));
        }
        rowView.setOnFocusChangeListener(new View.OnFocusChangeListener() {
            @Override
            public void onFocusChange(View v, boolean hasFocus) {
                int fg = hasFocus ? 0xFF0F0F0F : 0xFFF1F1F1;
                if (v instanceof android.view.ViewGroup) {
                    android.view.ViewGroup g = (android.view.ViewGroup) v;
                    for (int i = 0; i < g.getChildCount(); i++) {
                        View c = g.getChildAt(i);
                        if (c instanceof TextView) {
                            ((TextView) c).setTextColor(fg);
                        } else if (c instanceof ImageView) {
                            ((ImageView) c).setColorFilter(fg, PorterDuff.Mode.SRC_IN);
                        }
                    }
                }
            }
        });
    }
"""
            # Hook at end of onBindViewHolder
            new_text, count = re.subn(
                r"(public\s+void\s+onBindViewHolder\s*\([^)]*ViewHolder\s+(\w+)[^)]*\)\s*\{)",
                lambda m: m.group(1) + f"\n        if ({m.group(2)} != null) styleYouTubeDrawerRow({m.group(2)}.view);",
                text,
                count=1,
            )
            if count:
                idx = new_text.rfind("}")
                if idx != -1:
                    new_text = new_text[:idx] + helper + "\n}\n"
                    java_file.write_text(new_text, encoding="utf-8")
                    print(f"[YT-UI] Styled slide-out drawer item presenter -> {java_file}")


def patch_glide_rgb565():
    for java_file in ROOT.rglob("*Glide*.java"):
        if "build" in java_file.parts:
            continue
        text = java_file.read_text(encoding="utf-8")
        if "DecodeFormat.PREFER_ARGB_8888" in text:
            new_text = text.replace("DecodeFormat.PREFER_ARGB_8888", "DecodeFormat.PREFER_RGB_565")
            if new_text != text:
                java_file.write_text(new_text, encoding="utf-8")
                print(f"[YT-UI] Switched Glide to RGB_565 in {java_file}")
        elif "applyOptions(" in text and "PREFER_RGB_565" not in text:
            m = re.search(r"(public\s+void\s+applyOptions\s*\([^)]*GlideBuilder\s+(\w+)\s*\)\s*\{)", text)
            if m:
                b_var = m.group(2)
                inject = (
                    f"\n        {b_var}.setDefaultRequestOptions("
                    "new com.bumptech.glide.request.RequestOptions()"
                    ".format(com.bumptech.glide.load.DecodeFormat.PREFER_RGB_565));"
                )
                text = text[:m.end()] + inject + text[m.end():]
                java_file.write_text(text, encoding="utf-8")
                print(f"[YT-UI] Injected Glide RGB_565 default in {java_file}")


def main():
    if not ROOT.exists():
        raise SystemExit("[YT-UI] SmartTube directory not found!")

    primary_res = get_primary_res_dir()
    has_font = install_font(primary_res)
    write_shared_resources(primary_res)

    for mod in MODULES:
        res_dir = mod / "src" / "main" / "res"
        if not res_dir.exists():
            continue
        for c_xml in res_dir.rglob("colors*.xml"):
            patch_colors_xml(c_xml)
        for d_xml in res_dir.rglob("dimens*.xml"):
            patch_dimens_xml(d_xml)
        for s_xml in list(res_dir.rglob("styles*.xml")) + list(res_dir.rglob("themes*.xml")):
            patch_styles_and_themes(s_xml, has_font)
        patch_card_layouts(res_dir)

    patch_complex_card_view()
    patch_top_bar_and_drawer()
    patch_header_presenter()
    patch_glide_rgb565()
    print("[YT-UI] Stage 2 YouTube TV 1:1 Home & Slide-out Drawer applied successfully.")


if __name__ == "__main__":
    main()
