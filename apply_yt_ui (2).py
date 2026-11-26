#!/usr/bin/env python3
"""
YouTube TV (2025-2026) 1:1 Home Screen & Collapsible Left Drawer + Ultra-Fast Video Startup
Bulletproof patcher for SmartTube — fixes every discrepancy seen in yt_home_new.png vs official YouTube TV:

  1. KILLS WHITE CARD BOX FOREVER (ComplexImageCardView.java):
     - Overrides setInfoAreaBackgroundColor() & setInfoAreaBackground() to ALWAYS force TRANSPARENT
       (SmartTube's CardPresenter can no longer paint the focused card's bottom area #FFFFFF!).
     - Overrides setMainImageDimensions() to enforce YouTube TV's large 16:9 card geometry
       (352x198dp -> 2 full cards + peek of 3rd, instead of SmartTube's 4 tiny cards).
     - Forces title_text (#F1F1F1 focused / #CCCCCC unfocused) and content_text (#AAAAAA) on #0F0F0F.
     - Clips main_image to 12dp rounded corners and draws a crisp 3.5dp #F1F1F1 focus ring via dispatchDraw().

  2. REPLACES SMARTTUBE TOP BAR 1:1 (NavigateTitleView.java + title_view*.xml):
     - Permanently hides red SearchOrb, clock, date, S-beta badge, and extra orbs.
     - Keeps circular user avatar at top-left (x=22dp, y=34dp, 30dp circle).
     - Transforms SearchOrbView into #272727 Search Pill ("Поиск", 313x36dp, 18dp radius) +
       adds #272727 circular Mic button (36dp) to its left.
     - Pins official YouTube Play badge + "YouTube" wordmark (YouTube Sans Bold) top-right.

  3. COLLAPSIBLE LEFT RAIL <-> EXPANDED DRAWER (BrowseSupportFragment.java + IconHeaderItemPresenter.java):
     - Collapsed: 74dp #0F0F0F icon rail pinned at x=0 (labels hidden, thin YouTube vector icons).
     - Expanded (D-pad Left): 250dp #0F0F0F drawer with 222x39dp solid #F1F1F1 rounded pill (12dp)
       on focused row with #0F0F0F dark icon & bold text.

  4. ULTRA-FAST VIDEO STARTUP:
     - ExoPlayer DefaultLoadControl: bufferForPlaybackMs=400ms, afterRebuffer=800ms (safe master ctor).
     - Background warmup thread in MainApplication.onCreate(): preloads Rust libstjson.so + DNS/TLS.
     - Glide RGB_565 thumbnail decoding (halves bitmap RAM on 1 GB Mi TV Stick).
"""
import os
import re
import shutil
from pathlib import Path

ROOT = Path("SmartTube")
WORKSPACE = Path(os.environ.get("GITHUB_WORKSPACE", "."))
MODULES = [ROOT / "common", ROOT / "smarttubetv"]
LEANBACK_DIR = ROOT / "leanback-1.0.0"

YT_COLORS = {
    "window_background": "#0F0F0F",
    "default_background": "#0F0F0F",
    "grey_background": "#0F0F0F",
    "dark_grey": "#0F0F0F",
    "dark_grey_2": "#0F0F0F",
    "dark_grey_dark": "#0F0F0F",
    "dark_grey_light": "#161616",
    "dark_grey_card": "#00000000",
    "fastlane_background": "#0F0F0F",
    "lb_browse_headers_background": "#0F0F0F",
    "lb_details_overview_bg_color": "#0F0F0F",
    "lb_details_description_bg_color": "#0F0F0F",
    "lb_basic_card_bg_color": "#00000000",
    "lb_basic_card_info_bg_color": "#00000000",
    "card_background": "#00000000",
    "card_default_background": "#00000000",
    "card_info_background": "#00000000",
    "card_selected_background": "#00000000",
    "card_selected_text_background": "#00000000",
    "lb_default_brand_color": "#0F0F0F",
    "lb_default_brand_color_dark": "#0F0F0F",
    "lb_default_search_color": "#272727",
    "lb_default_search_icon_color": "#F1F1F1",
    "lb_control_button_color": "#272727",
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

DRAWABLE_THUMB_BG = """<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android"
    android:shape="rectangle">
    <solid android:color="#1A1A1A" />
    <corners android:radius="12dp" />
</shape>
"""

DRAWABLE_BADGE_BG = """<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android"
    android:shape="rectangle">
    <solid android:color="#CC000000" />
    <corners android:radius="4dp" />
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

DRAWABLE_SEARCH_PILL_BG = """<?xml version="1.0" encoding="utf-8"?>
<selector xmlns:android="http://schemas.android.com/apk/res/android">
    <item android:state_focused="true">
        <shape android:shape="rectangle">
            <solid android:color="#F1F1F1" />
            <corners android:radius="18dp" />
        </shape>
    </item>
    <item>
        <shape android:shape="rectangle">
            <solid android:color="#272727" />
            <corners android:radius="18dp" />
        </shape>
    </item>
</selector>
"""

DRAWABLE_MIC_CIRCLE_BG = """<?xml version="1.0" encoding="utf-8"?>
<selector xmlns:android="http://schemas.android.com/apk/res/android">
    <item android:state_focused="true">
        <shape android:shape="oval">
            <solid android:color="#F1F1F1" />
        </shape>
    </item>
    <item>
        <shape android:shape="oval">
            <solid android:color="#272727" />
        </shape>
    </item>
</selector>
"""

DRAWABLE_DRAWER_PILL_FOCUSED = """<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android"
    android:shape="rectangle">
    <solid android:color="#F1F1F1" />
    <corners android:radius="12dp" />
</shape>
"""

DRAWABLE_YT_PLAY_BADGE = """<?xml version="1.0" encoding="utf-8"?>
<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="31dp"
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

COLOR_SEARCH_PILL_TEXT = """<?xml version="1.0" encoding="utf-8"?>
<selector xmlns:android="http://schemas.android.com/apk/res/android">
    <item android:state_focused="true" android:color="#0F0F0F" />
    <item android:color="#AAAAAA" />
</selector>
"""

YT_VECTOR_ICONS = {
    "yt_ic_mic.xml": """<?xml version="1.0" encoding="utf-8"?>
<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="20dp" android:height="20dp" android:viewportWidth="24" android:viewportHeight="24">
    <path android:fillColor="#FFFFFFFF"
        android:pathData="M12,3c-1.66,0 -3,1.37 -3,3.07v5.86c0,1.7 1.34,3.07 3,3.07s3,-1.37 3,-3.07V6.07C15,4.37 13.66,3 12,3zM13.5,11.93c0,0.87 -0.67,1.57 -1.5,1.57s-1.5,-0.7 -1.5,-1.57V6.07c0,-0.87 0.67,-1.57 1.5,-1.57s1.5,0.7 1.5,1.57V11.93zM18.5,12h-1.5c0,2.76 -2.24,5 -5,5s-5,-2.24 -5,-5H5.5c0,3.34 2.51,6.09 5.75,6.46V21h1.5v-2.54C15.99,18.09 18.5,15.34 18.5,12z" />
</vector>""",
    "yt_ic_search.xml": """<?xml version="1.0" encoding="utf-8"?>
<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="22dp" android:height="22dp" android:viewportWidth="24" android:viewportHeight="24">
    <path android:fillColor="#FFFFFFFF"
        android:pathData="M20.87,20.17l-5.59,-5.59C16.35,13.35 17,11.75 17,10c0,-3.87 -3.13,-7 -7,-7s-7,3.13 -7,7s3.13,7 7,7c1.75,0 3.35,-0.65 4.58,-1.71l5.59,5.59L20.87,20.17zM10,16c-3.31,0 -6,-2.69 -6,-6s2.69,-6 6,-6s6,2.69 6,6S13.31,16 10,16z" />
</vector>""",
    "yt_ic_home.xml": """<?xml version="1.0" encoding="utf-8"?>
<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="22dp" android:height="22dp" android:viewportWidth="24" android:viewportHeight="24">
    <path android:fillColor="#FFFFFFFF"
        android:pathData="M12,4.33l7,6.12V20h-4v-6H9v6H5v-9.55L12,4.33M12,3L4,10v11h6v-6h4v6h6V10L12,3L12,3z" />
</vector>""",
    "yt_ic_home_filled.xml": """<?xml version="1.0" encoding="utf-8"?>
<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="22dp" android:height="22dp" android:viewportWidth="24" android:viewportHeight="24">
    <path android:fillColor="#FFFFFFFF"
        android:pathData="M4,10v11h6v-6h4v6h6V10l-8,-7L4,10z" />
</vector>""",
    "yt_ic_shorts.xml": """<?xml version="1.0" encoding="utf-8"?>
<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="22dp" android:height="22dp" android:viewportWidth="24" android:viewportHeight="24">
    <path android:fillColor="#FFFFFFFF"
        android:pathData="M10,14.65v-5.3L15,12L10,14.65zM17.77,10.32c-0.77,-0.32 -1.2,-0.5 -1.2,-0.5L18,9.06c1.84,-0.96 2.53,-3.23 1.56,-5.06s-3.24,-2.53 -5.07,-1.56L6,6.94c-1.29,0.68 -2.07,2.04 -2,3.49c0.07,1.42 0.93,2.67 2.22,3.25c0.03,0.01 1.2,0.5 1.2,0.5L6,14.93c-1.83,0.97 -2.53,3.24 -1.56,5.07c0.97,1.83 3.24,2.53 5.07,1.56l8.5,-4.5c1.29,-0.68 2.06,-2.04 1.99,-3.49C19.93,12.15 19.06,10.9 17.77,10.32zM17.53,16.17l-8.5,4.5c-1.34,0.71 -3.01,0.2 -3.72,-1.14c-0.71,-1.34 -0.2,-3.01 1.14,-3.72l2.04,-1.08l-1.21,-0.5c-0.01,0 -1.16,-0.48 -1.18,-0.49c-0.95,-0.42 -1.58,-1.34 -1.63,-2.38c-0.05,-1.06 0.52,-2.06 1.46,-2.56l8.5,-4.5c1.34,-0.71 3.01,-0.2 3.72,1.14c0.71,1.34 0.2,3.01 -1.14,3.72l-2.04,1.08l1.21,0.5c0.01,0 1.16,0.48 1.17,0.49c0.95,0.43 1.58,1.35 1.63,2.38C19.04,14.68 18.47,15.67 17.53,16.17z" />
</vector>""",
    "yt_ic_subscriptions.xml": """<?xml version="1.0" encoding="utf-8"?>
<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="22dp" android:height="22dp" android:viewportWidth="24" android:viewportHeight="24">
    <path android:fillColor="#FFFFFFFF"
        android:pathData="M10,18v-6l5,3L10,18zM17,3H7v1h10V3zM20,6H4v1h16V6zM22,9H2v12h20V9zM3,10h18v10H3V10z" />
</vector>""",
    "yt_ic_library.xml": """<?xml version="1.0" encoding="utf-8"?>
<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="22dp" android:height="22dp" android:viewportWidth="24" android:viewportHeight="24">
    <path android:fillColor="#FFFFFFFF"
        android:pathData="M18,4v15.06l-5.42,-3.87L12,14.77l-0.58,0.42L6,19.06V4H18M19,3H5v18l7,-5l7,5V3L19,3z" />
</vector>""",
    "yt_ic_history.xml": """<?xml version="1.0" encoding="utf-8"?>
<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="22dp" android:height="22dp" android:viewportWidth="24" android:viewportHeight="24">
    <path android:fillColor="#FFFFFFFF"
        android:pathData="M14.97,16.95L10,13.87V7h2v5.76l4.03,2.49L14.97,16.95zM22,12c0,5.51 -4.49,10 -10,10S2,17.51 2,12h1c0,4.96 4.04,9 9,9s9,-4.04 9,-9s-4.04,-9 -9,-9C8.81,3 5.92,4.64 4.28,7.38C4.17,7.56 4.06,7.75 3.97,7.94C3.96,7.96 3.95,7.98 3.94,8H8v1H2V3h1v4.74C3.04,7.67 3.09,7.59 3.13,7.51C3.24,7.3 3.35,7.09 3.47,6.89C5.28,3.83 8.48,2 12,2C17.51,2 22,6.49 22,12z" />
</vector>""",
    "yt_ic_music.xml": """<?xml version="1.0" encoding="utf-8"?>
<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="22dp" android:height="22dp" android:viewportWidth="24" android:viewportHeight="24">
    <path android:fillColor="#FFFFFFFF"
        android:pathData="M12,3c-4.96,0 -9,4.04 -9,9s4.04,9 9,9s9,-4.04 9,-9S16.96,3 12,3zM12,20c-4.41,0 -8,-3.59 -8,-8s3.59,-8 8,-8s8,3.59 8,8S16.41,20 12,20zM12,7c-2.76,0 -5,2.24 -5,5s2.24,5 5,5s5,-2.24 5,-5S14.76,7 12,7zM12,16c-2.21,0 -4,-1.79 -4,-4s1.79,-4 4,-4s4,1.79 4,4S14.21,16 12,16zM10.5,9.5l4.5,2.5l-4.5,2.5V9.5z" />
</vector>""",
    "yt_ic_news.xml": """<?xml version="1.0" encoding="utf-8"?>
<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="22dp" android:height="22dp" android:viewportWidth="24" android:viewportHeight="24">
    <path android:fillColor="#FFFFFFFF"
        android:pathData="M11,11v6H7v-6H11M12,10H6v8h6V10L12,10zM3,3.03V21h14l4,-4V3.03H3zM20,16.59L16.59,20H4V4.03h16V16.59zM18,7H6v1h12V7zM18,10h-5v1h5V10zM18,13h-5v1h5V13zM18,16h-5v1h5V16z" />
</vector>""",
    "yt_ic_gaming.xml": """<?xml version="1.0" encoding="utf-8"?>
<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="22dp" android:height="22dp" android:viewportWidth="24" android:viewportHeight="24">
    <path android:fillColor="#FFFFFFFF"
        android:pathData="M10,12H8v2H6v-2H4v-2h2V8h2v2h2V12zM17,12.5c0,-0.83 -0.67,-1.5 -1.5,-1.5S14,11.67 14,12.5c0,0.83 0.67,1.5 1.5,1.5S17,13.33 17,12.5zM20,9.5C20,8.67 19.33,8 18.5,8S17,8.67 17,9.5c0,0.83 0.67,1.5 1.5,1.5S20,10.33 20,9.5zM16.97,5.15l-4.5,2.53L12,7.95l-0.47,-0.27l-4.5,-2.53L3,7.39v6.43l8.98,5.04L21,13.82V7.39L16.97,5.15M16.97,4l5.03,2.8v7.6L11.98,20L2,14.4V6.8L7.03,4l4.97,2.8L16.97,4L16.97,4z" />
</vector>""",
    "yt_ic_sports.xml": """<?xml version="1.0" encoding="utf-8"?>
<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="22dp" android:height="22dp" android:viewportWidth="24" android:viewportHeight="24">
    <path android:fillColor="#FFFFFFFF"
        android:pathData="M18,5V2H6v3H3v6l3.23,1.61c0.7,2.5 2.97,4.34 5.69,4.38L12,19v3H7v1h10v-1h-5v-3l0.08,-2.01c2.72,-0.04 4.99,-1.88 5.69,-4.38L21,11V5H18zM6,11.38l-2,-1V6h2V11.38zM17,11c0,2.76 -2.24,5 -5,5s-5,-2.24 -5,-5V3h10V11zM20,10.38l-2,1V6h2V10.38z" />
</vector>""",
    "yt_ic_movies.xml": """<?xml version="1.0" encoding="utf-8"?>
<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="22dp" android:height="22dp" android:viewportWidth="24" android:viewportHeight="24">
    <path android:fillColor="#FFFFFFFF"
        android:pathData="M22.01,4L2,4v16h20L22.01,4zM3,5h2.59l1.5,3H4.59L3,5zM7.59,5h2.59l1.5,3H9.09L7.59,5zM12.18,5h2.59l1.5,3h-2.59L12.18,5zM16.77,5h2.59l1.5,3h-2.59L16.77,5zM21,19H3V9h18V19z" />
</vector>""",
    "yt_ic_channels.xml": """<?xml version="1.0" encoding="utf-8"?>
<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="22dp" android:height="22dp" android:viewportWidth="24" android:viewportHeight="24">
    <path android:fillColor="#FFFFFFFF"
        android:pathData="M11,7l6,3.5L11,14V7L11,7zM18,20H4V6H3v15h15V20zM21,18H6V3h15V18zM7,17h13V4H7V17z" />
</vector>""",
    "yt_ic_settings.xml": """<?xml version="1.0" encoding="utf-8"?>
<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="22dp" android:height="22dp" android:viewportWidth="24" android:viewportHeight="24">
    <path android:fillColor="#FFFFFFFF"
        android:pathData="M12,9c1.65,0 3,1.35 3,3s-1.35,3 -3,3s-3,-1.35 -3,-3S10.35,9 12,9M12,8c-2.21,0 -4,1.79 -4,4s1.79,4 4,4s4,-1.79 4,-4S14.21,8 12,8L12,8zM13.22,3l0.55,2.2l0.13,0.51l0.5,0.18c0.61,0.23 1.19,0.56 1.72,0.98l0.4,0.32l0.5,-0.14l2.17,-0.62l1.22,2.11l-1.63,1.59l-0.37,0.36l0.08,0.51c0.05,0.32 0.08,0.64 0.08,0.98s-0.03,0.66 -0.08,0.98l-0.08,0.51l0.37,0.36l1.63,1.59l-1.22,2.11l-2.17,-0.62l-0.5,-0.14l-0.4,0.32c-0.53,0.43 -1.11,0.76 -1.72,0.98l-0.5,0.18l-0.13,0.51L13.22,21h-2.44l-0.55,-2.2l-0.13,-0.51l-0.5,-0.18C9,17.88 8.42,17.55 7.88,17.12l-0.4,-0.32l-0.5,0.14l-2.17,0.62L3.6,15.44l1.63,-1.59l0.37,-0.36l-0.08,-0.51C5.47,12.66 5.44,12.33 5.44,12s0.03,-0.66 0.08,-0.98l0.08,-0.51l-0.37,-0.36L3.6,8.56l1.22,-2.11l2.17,0.62l0.5,0.14l0.4,-0.32C8.42,6.45 9,6.12 9.61,5.9l0.5,-0.18l0.13,-0.51L10.78,3H13.22M14,2h-4L9.26,4.96c-0.73,0.27 -1.4,0.66 -2,1.14L4.34,5.27l-2,3.46l2.19,2.13C4.47,11.23 4.44,11.61 4.44,12s0.03,0.77 0.09,1.14l-2.19,2.13l2,3.46l2.92,-0.83c0.6,0.48 1.27,0.87 2,1.14L10,22h4l0.74,-2.96c0.73,-0.27 1.4,-0.66 2,-1.14l2.92,0.83l2,-3.46l-2.19,-2.13c0.06,-0.37 0.09,-0.75 0.09,-1.14s-0.03,-0.77 -0.09,-1.14l2.19,-2.13l-2,-3.46L16.74,6.1c-0.6,-0.48 -1.27,-0.87 -2,-1.14L14,2L14,2z" />
</vector>""",
}

EXTRA_YT_VALUES = """<?xml version="1.0" encoding="utf-8"?>
<resources>
    <color name="yt_canvas_bg">#0F0F0F</color>
    <color name="yt_drawer_bg">#0F0F0F</color>
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
    search_roots = [WORKSPACE, Path(".")]
    ttf_files = []
    for base in search_roots:
        if not base.exists():
            continue
        for p in base.rglob("*.ttf"):
            if "SmartTube" in p.parts or ".git" in p.parts:
                continue
            ttf_files.append(p)

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
        "yt_badge_bg.xml": DRAWABLE_BADGE_BG,
        "yt_card_progress.xml": DRAWABLE_PROGRESS_BAR,
        "yt_search_pill_bg.xml": DRAWABLE_SEARCH_PILL_BG,
        "yt_mic_circle_bg.xml": DRAWABLE_MIC_CIRCLE_BG,
        "yt_drawer_pill_focused.xml": DRAWABLE_DRAWER_PILL_FOCUSED,
        "yt_play_badge.xml": DRAWABLE_YT_PLAY_BADGE,
    }
    files.update(YT_VECTOR_ICONS)
    for name, content in files.items():
        (drawable_dir / name).write_text(content.strip() + "\n", encoding="utf-8")

    color_dir = res_dir / "color"
    color_dir.mkdir(parents=True, exist_ok=True)
    (color_dir / "yt_search_pill_text.xml").write_text(COLOR_SEARCH_PILL_TEXT.strip() + "\n", encoding="utf-8")

    values_dir = res_dir / "values"
    values_dir.mkdir(parents=True, exist_ok=True)
    (values_dir / "yt_theme_tokens.xml").write_text(EXTRA_YT_VALUES.strip() + "\n", encoding="utf-8")
    print(f"[YT-UI] Wrote YouTube TV drawables, 14 vector icons & color tokens -> {res_dir}")


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
        "lb_browse_rows_margin_top": "90dp",
        "lb_browse_padding_start": "18dp",
        "lb_browse_padding_end": "44dp",
        "lb_browse_item_margin": "15dp",
        "lb_browse_row_title_text_size": "16sp",
        "lb_basic_card_title_text_size": "14sp",
        "lb_basic_card_content_text_size": "12sp",
        "lb_basic_card_info_padding_top": "10dp",
        "lb_basic_card_info_padding_bottom": "4dp",
        "lb_basic_card_info_padding_horizontal": "2dp",
        "lb_browse_headers_width": "250dp",
        "lb_browse_headers_vertical_spacing": "2dp",
        "lb_browse_header_height": "39dp",
        "lb_browse_header_padding_end": "14dp",
        "lb_browse_headers_padding_start": "0dp",
        "card_width": "352dp",
        "card_height": "198dp",
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
        "defaultSearchColor": "@color/yt_surface_bg",
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


# ==============================================================================
# 1. COLLAPSIBLE LEFT NAVIGATION RAIL (74dp <-> 250dp) IN LEANBACK BrowseSupportFragment
# ==============================================================================

def patch_leanback_collapsible_rail():
    candidates = [
        p for p in LEANBACK_DIR.rglob("BrowseSupportFragment.java")
        if "build" not in p.parts
    ] if LEANBACK_DIR.exists() else []

    if not candidates:
        print("[YT-UI] WARNING: leanback-1.0.0 BrowseSupportFragment.java not found!")
        return

    for java_file in candidates:
        text = java_file.read_text(encoding="utf-8")
        if "YT_COLLAPSIBLE_RAIL" in text:
            continue

        original = text
        text = ensure_imports(
            text,
            [
                "android.view.View",
                "android.view.ViewGroup",
                "android.widget.ImageView",
                "android.widget.TextView",
            ],
        )

        margin_pat = re.compile(
            r"(\w+)\s*=\s*\(MarginLayoutParams\)\s*(\w+)\.getLayoutParams\(\);\s*"
            r"\1\.setMarginStart\s*\(\s*(\w+)\s*\?\s*0\s*:\s*-\s*mContainerListMarginStart\s*\)\s*;"
        )
        m1 = margin_pat.search(text)
        if m1:
            lp_var, view_var, flag_var = m1.group(1), m1.group(2), m1.group(3)
            replacement = (
                f"{lp_var} = (MarginLayoutParams) {view_var}.getLayoutParams();\n"
                f"        // YT_COLLAPSIBLE_RAIL: keep 74dp icon rail onscreen when collapsed, 250dp when expanded\n"
                f"        {lp_var}.setMarginStart(0);\n"
                f"        ytApplyRailGeometry({view_var}, {lp_var}, {flag_var});"
            )
            text = text[:m1.start()] + replacement + text[m1.end():]
            print(f"[YT-UI] Patched setHeadersOnScreen rail geometry in {java_file}")

        expand_pat = re.compile(
            r"(\w+)\.setMarginStart\s*\(\s*!\s*(\w+)\s*\?\s*mContainerListMarginStart\s*:\s*0\s*\)\s*;"
        )
        m2 = expand_pat.search(text)
        if m2:
            p_var, exp_var = m2.group(1), m2.group(2)
            replacement = (
                f"// YT_COLLAPSIBLE_RAIL: 56dp (+18dp row padding = 74dp) collapsed, 250dp (+18dp = 268dp) expanded\n"
                f"        int ytCollapsedMargin = (int) (56f * getResources().getDisplayMetrics().density);\n"
                f"        {p_var}.setMarginStart(!{exp_var} ? mContainerListMarginStart : ytCollapsedMargin);"
            )
            text = text[:m2.start()] + replacement + text[m2.end():]
            print(f"[YT-UI] Patched expandMainFragment content offset in {java_file}")

        helper = """
    // YT_COLLAPSIBLE_RAIL: shared state read by NavigateTitleView & IconHeaderItemPresenter
    public static volatile boolean sYtDrawerExpanded = false;
    public static Runnable sYtOnDrawerStateChanged = null;

    private void ytApplyRailGeometry(final View containerList, ViewGroup.MarginLayoutParams lp, boolean onScreen) {
        sYtDrawerExpanded = onScreen;
        float d = containerList.getResources().getDisplayMetrics().density;
        int railPx = (int) (74f * d);
        int expandedPx = mContainerListMarginStart > 0 ? mContainerListMarginStart : (int) (250f * d);
        int targetWidth = onScreen ? expandedPx : railPx;

        lp.width = targetWidth;
        containerList.setBackgroundColor(0xFF0F0F0F);
        containerList.setPadding(0, (int) (78f * d), 0, (int) (16f * d));

        if (containerList.getParent() instanceof View) {
            View dock = (View) containerList.getParent();
            ViewGroup.LayoutParams dlp = dock.getLayoutParams();
            if (dlp != null && dlp.width != targetWidth) {
                dlp.width = targetWidth;
                dock.setLayoutParams(dlp);
            }
            dock.setBackgroundColor(0xFF0F0F0F);
        }

        ytRefreshDrawerItemsTree(containerList, onScreen);
        containerList.post(new Runnable() {
            @Override
            public void run() {
                ytRefreshDrawerItemsTree(containerList, sYtDrawerExpanded);
            }
        });

        Runnable cb = sYtOnDrawerStateChanged;
        if (cb != null) {
            cb.run();
        }
    }

    private void ytRefreshDrawerItemsTree(View view, boolean expanded) {
        if (view == null) return;
        Object tag = view.getTag();
        if ("yt_drawer_row".equals(tag)) {
            ytStyleDrawerRowSnapshot(view, expanded);
            return;
        }
        if (view instanceof ViewGroup) {
            ViewGroup g = (ViewGroup) view;
            for (int i = 0; i < g.getChildCount(); i++) {
                ytRefreshDrawerItemsTree(g.getChildAt(i), expanded);
            }
        }
    }

    public static void ytStyleDrawerRowSnapshot(View rowView, boolean expanded) {
        if (rowView == null) return;
        rowView.setAlpha(1.0f);
        boolean active = rowView.isFocused() || rowView.isSelected();
        if (expanded && rowView.isFocused()) {
            int pillId = rowView.getResources().getIdentifier(
                "yt_drawer_pill_focused", "drawable", rowView.getContext().getPackageName());
            if (pillId != 0) {
                rowView.setBackgroundResource(pillId);
            } else {
                rowView.setBackgroundColor(0xFFF1F1F1);
            }
        } else {
            rowView.setBackgroundColor(0x00000000);
        }

        int iconColor;
        int textColor;
        if (expanded) {
            iconColor = rowView.isFocused() ? 0xFF0F0F0F : 0xFFF1F1F1;
            textColor = rowView.isFocused() ? 0xFF0F0F0F : 0xFFF1F1F1;
        } else {
            iconColor = active ? 0xFFFFFFFF : 0xFF9A9A9A;
            textColor = 0x00000000;
        }

        ytApplyColorsToRowChildren(rowView, expanded, iconColor, textColor);
    }

    private static void ytApplyColorsToRowChildren(View v, boolean expanded, int iconColor, int textColor) {
        if (v instanceof ImageView) {
            ((ImageView) v).setColorFilter(iconColor, android.graphics.PorterDuff.Mode.SRC_IN);
        } else if (v instanceof TextView) {
            TextView tv = (TextView) v;
            tv.setTextColor(textColor);
            tv.setAlpha(expanded ? 1.0f : 0.0f);
            tv.setVisibility(expanded ? View.VISIBLE : View.INVISIBLE);
        } else if (v instanceof ViewGroup) {
            ViewGroup g = (ViewGroup) v;
            for (int i = 0; i < g.getChildCount(); i++) {
                ytApplyColorsToRowChildren(g.getChildAt(i), expanded, iconColor, textColor);
            }
        }
    }
"""
        idx = text.rfind("}")
        if idx != -1 and text != original:
            text = text[:idx] + helper + "\n}\n"
            java_file.write_text(text, encoding="utf-8")
            print(f"[YT-UI] Installed YouTube TV Collapsible Rail engine -> {java_file}")


# ==============================================================================
# 2. LEFT DRAWER ITEMS (IconHeaderItemPresenter.java)
# ==============================================================================

def patch_icon_header_presenter():
    candidates = [
        p for p in ROOT.rglob("IconHeaderItemPresenter.java")
        if "build" not in p.parts
    ]
    if not candidates:
        print("[YT-UI] WARNING: IconHeaderItemPresenter.java not found!")
        return

    for java_file in candidates:
        text = java_file.read_text(encoding="utf-8")
        if "YT_DRAWER_ITEM_1TO1" in text:
            continue

        text = ensure_imports(
            text,
            [
                "android.graphics.PorterDuff",
                "android.graphics.Typeface",
                "android.view.Gravity",
                "android.view.View",
                "android.view.ViewGroup",
                "android.widget.ImageView",
                "android.widget.LinearLayout",
                "android.widget.TextView",
                "androidx.leanback.app.BrowseSupportFragment",
            ],
        )

        bind_re = re.compile(
            r"(public\s+void\s+onBindViewHolder\s*\([^)]*ViewHolder\s+(\w+)\s*,\s*Object\s+(\w+)\s*\)\s*\{)"
        )
        bm = bind_re.search(text)
        if not bm:
            continue

        vh_var = bm.group(2)
        brace_depth = 0
        end_pos = -1
        for i in range(bm.end() - 1, len(text)):
            ch = text[i]
            if ch == "{":
                brace_depth += 1
            elif ch == "}":
                brace_depth -= 1
                if brace_depth == 0:
                    end_pos = i
                    break

        if end_pos == -1:
            continue

        inject_call = f"\n        if ({vh_var} != null) ytBindDrawerItem({vh_var}.view);\n    "
        text = text[:end_pos] + inject_call + text[end_pos:]

        sel_re = re.compile(
            r"((?:protected|public)\s+void\s+onSelectLevelChanged\s*\([^)]*ViewHolder\s+(\w+)\s*\)\s*\{)"
        )
        sm = sel_re.search(text)
        extra_sel_override = ""
        if sm:
            sv = sm.group(2)
            bd = 0
            ep = -1
            for i in range(sm.end() - 1, len(text)):
                if text[i] == "{":
                    bd += 1
                elif text[i] == "}":
                    bd -= 1
                    if bd == 0:
                        ep = i
                        break
            if ep != -1:
                text = text[:ep] + f"\n        if ({sv} != null && {sv}.view != null) {{ {sv}.view.setAlpha(1.0f); BrowseSupportFragment.ytStyleDrawerRowSnapshot({sv}.view, BrowseSupportFragment.sYtDrawerExpanded); }}\n    " + text[ep:]
        else:
            extra_sel_override = """
    @Override
    protected void onSelectLevelChanged(androidx.leanback.widget.RowHeaderPresenter.ViewHolder holder) {
        super.onSelectLevelChanged(holder);
        if (holder != null && holder.view != null) {
            holder.view.setAlpha(1.0f);
            BrowseSupportFragment.ytStyleDrawerRowSnapshot(holder.view, BrowseSupportFragment.sYtDrawerExpanded);
        }
    }
"""

        helper = f"""
    // YT_DRAWER_ITEM_1TO1: Exact YouTube TV drawer row (222x39dp, 12dp #F1F1F1 pill, official icons)
    private void ytBindDrawerItem(final View rowView) {{
        if (rowView == null) return;
        rowView.setTag("yt_drawer_row");
        rowView.setAlpha(1.0f);

        float d = rowView.getResources().getDisplayMetrics().density;
        int rowH = (int) (39f * d);
        int padH = (int) (13f * d);

        ViewGroup.LayoutParams lp = rowView.getLayoutParams();
        if (lp instanceof ViewGroup.MarginLayoutParams) {{
            ViewGroup.MarginLayoutParams mlp = (ViewGroup.MarginLayoutParams) lp;
            mlp.width = ViewGroup.LayoutParams.MATCH_PARENT;
            mlp.height = rowH;
            mlp.setMarginStart((int) (14f * d));
            mlp.setMarginEnd((int) (14f * d));
            mlp.topMargin = (int) (1f * d);
            mlp.bottomMargin = (int) (1f * d);
            rowView.setLayoutParams(mlp);
        }}
        rowView.setPadding(padH, 0, padH, 0);

        ImageView iconView = ytFindFirstImageView(rowView);
        TextView labelView = ytFindFirstTextView(rowView);

        String titleLower = "";
        if (labelView != null) {{
            CharSequence cs = labelView.getText();
            titleLower = cs != null ? cs.toString().toLowerCase() : "";
            labelView.setTextSize(15f);
            labelView.setTypeface(Typeface.create("sans-serif-medium", Typeface.NORMAL));
            labelView.setSingleLine(true);
            if (labelView.getLayoutParams() instanceof ViewGroup.MarginLayoutParams) {{
                ViewGroup.MarginLayoutParams tlp = (ViewGroup.MarginLayoutParams) labelView.getLayoutParams();
                tlp.setMarginStart((int) (18f * d));
                labelView.setLayoutParams(tlp);
            }}
        }}

        if (iconView != null) {{
            int iconPx = (int) (22f * d);
            ViewGroup.LayoutParams ilp = iconView.getLayoutParams();
            if (ilp != null) {{
                ilp.width = iconPx;
                ilp.height = iconPx;
                iconView.setLayoutParams(ilp);
            }}
            iconView.setScaleType(ImageView.ScaleType.FIT_CENTER);

            String ytIconName = ytResolveSectionIcon(titleLower, rowView.isFocused() || rowView.isSelected());
            if (ytIconName != null) {{
                int resId = rowView.getResources().getIdentifier(
                    ytIconName, "drawable", rowView.getContext().getPackageName());
                if (resId != 0) {{
                    iconView.setImageResource(resId);
                }}
            }}
        }}

        int hookTagKey = 0x7f0f7701;
        if (rowView.getTag(hookTagKey) == null) {{
            rowView.setTag(hookTagKey, Boolean.TRUE);
            final View.OnFocusChangeListener prev = rowView.getOnFocusChangeListener();
            rowView.setOnFocusChangeListener(new View.OnFocusChangeListener() {{
                @Override
                public void onFocusChange(View v, boolean hasFocus) {{
                    if (prev != null) {{
                        prev.onFocusChange(v, hasFocus);
                    }}
                    ytRefreshRowIconAndPill(v, hasFocus);
                }}
            }});
        }}

        BrowseSupportFragment.ytStyleDrawerRowSnapshot(rowView, BrowseSupportFragment.sYtDrawerExpanded);
    }}

    private void ytRefreshRowIconAndPill(View rowView, boolean hasFocus) {{
        TextView labelView = ytFindFirstTextView(rowView);
        ImageView iconView = ytFindFirstImageView(rowView);
        if (labelView != null && iconView != null) {{
            CharSequence cs = labelView.getText();
            String tl = cs != null ? cs.toString().toLowerCase() : "";
            String iconName = ytResolveSectionIcon(tl, hasFocus || rowView.isSelected());
            if (iconName != null) {{
                int resId = rowView.getResources().getIdentifier(
                    iconName, "drawable", rowView.getContext().getPackageName());
                if (resId != 0) {{
                    iconView.setImageResource(resId);
                }}
            }}
            labelView.setTypeface(Typeface.create(
                "sans-serif-medium", hasFocus ? Typeface.BOLD : Typeface.NORMAL));
        }}
        BrowseSupportFragment.ytStyleDrawerRowSnapshot(rowView, BrowseSupportFragment.sYtDrawerExpanded);
    }}

    private String ytResolveSectionIcon(String title, boolean active) {{
        if (title == null || title.isEmpty()) return null;
        if (title.contains("поиск") || title.contains("пошук") || title.contains("search")) return "yt_ic_search";
        if (title.contains("главн") || title.contains("головн") || title.contains("home")) {{
            return active ? "yt_ic_home_filled" : "yt_ic_home";
        }}
        if (title.contains("short") || title.contains("шорт")) return "yt_ic_shorts";
        if (title.contains("подпис") || title.contains("підпис") || title.contains("subscrip")) return "yt_ic_subscriptions";
        if (title.contains("библиот") || title.contains("бібліот") || title.contains("librar") || title.contains("плейлист") || title.contains("playlist")) return "yt_ic_library";
        if (title.contains("истор") || title.contains("істор") || title.contains("histor")) return "yt_ic_history";
        if (title.contains("музык") || title.contains("музик") || title.contains("music")) return "yt_ic_music";
        if (title.contains("новост") || title.contains("новин") || title.contains("news")) return "yt_ic_news";
        if (title.contains("игр") || title.contains("ігр") || title.contains("gam")) return "yt_ic_gaming";
        if (title.contains("спорт") || title.contains("sport")) return "yt_ic_sports";
        if (title.contains("фильм") || title.contains("фільм") || title.contains("movie")) return "yt_ic_movies";
        if (title.contains("канал") || title.contains("channel")) return "yt_ic_channels";
        if (title.contains("настрой") || title.contains("налашт") || title.contains("setting")) return "yt_ic_settings";
        return null;
    }}

    private ImageView ytFindFirstImageView(View root) {{
        if (root instanceof ImageView) return (ImageView) root;
        if (root instanceof ViewGroup) {{
            ViewGroup g = (ViewGroup) root;
            for (int i = 0; i < g.getChildCount(); i++) {{
                ImageView iv = ytFindFirstImageView(g.getChildAt(i));
                if (iv != null) return iv;
            }}
        }}
        return null;
    }}

    private TextView ytFindFirstTextView(View root) {{
        if (root instanceof TextView) return (TextView) root;
        if (root instanceof ViewGroup) {{
            ViewGroup g = (ViewGroup) root;
            for (int i = 0; i < g.getChildCount(); i++) {{
                TextView tv = ytFindFirstTextView(g.getChildAt(i));
                if (tv != null) return tv;
            }}
        }}
        return null;
    }}
{extra_sel_override}
"""
        idx = text.rfind("}")
        if idx != -1:
            text = text[:idx] + helper + "\n}\n"
            java_file.write_text(text, encoding="utf-8")
            print(f"[YT-UI] Patched IconHeaderItemPresenter (YouTube TV 1:1 drawer items) -> {java_file}")


# ==============================================================================
# 3. TOP BAR (NavigateTitleView.java) — 1:1 with screenshot_20261126_091356.png
# ==============================================================================

def patch_navigate_title_view():
    candidates = [
        p for p in ROOT.rglob("NavigateTitleView.java")
        if "build" not in p.parts
    ]
    if not candidates:
        print("[YT-UI] WARNING: NavigateTitleView.java not found!")
        return

    for java_file in candidates:
        text = java_file.read_text(encoding="utf-8")
        if "YT_TOP_BAR_1TO1" in text:
            continue

        text = ensure_imports(
            text,
            [
                "android.content.res.ColorStateList",
                "android.graphics.Color",
                "android.graphics.Outline",
                "android.graphics.Typeface",
                "android.os.Build",
                "android.view.Gravity",
                "android.view.View",
                "android.view.ViewGroup",
                "android.view.ViewOutlineProvider",
                "android.widget.FrameLayout",
                "android.widget.ImageView",
                "android.widget.LinearLayout",
                "android.widget.RelativeLayout",
                "android.widget.TextView",
                "androidx.core.content.ContextCompat",
                "androidx.core.content.res.ResourcesCompat",
                "androidx.leanback.app.BrowseSupportFragment",
            ],
        )

        has_attached = re.search(r"void\s+onAttachedToWindow\s*\(\s*\)", text) is not None
        has_detached = re.search(r"void\s+onDetachedFromWindow\s*\(\s*\)", text) is not None
        has_update_vis = re.search(r"void\s+updateComponentsVisibility\s*\([^)]*\)\s*\{", text)

        if has_attached:
            text = re.sub(
                r"(super\.onAttachedToWindow\s*\(\s*\)\s*;)",
                r"\g<1>\n        ytInitTopBarChrome();",
                text,
                count=1,
            )

        if has_detached:
            text = re.sub(
                r"(super\.onDetachedFromWindow\s*\(\s*\)\s*;)",
                r"\g<1>\n        ytCleanupTopBarChrome();",
                text,
                count=1,
            )

        if has_update_vis:
            bd = 0
            ep = -1
            for i in range(has_update_vis.end() - 1, len(text)):
                if text[i] == "{":
                    bd += 1
                elif text[i] == "}":
                    bd -= 1
                    if bd == 0:
                        ep = i
                        break
            if ep != -1:
                text = text[:ep] + "\n        ytHideLegacySmartTubeViews();\n    " + text[ep:]

        overrides = ""
        if not has_attached:
            overrides += """
    @Override
    protected void onAttachedToWindow() {
        super.onAttachedToWindow();
        ytInitTopBarChrome();
    }
"""
        if not has_detached:
            overrides += """
    @Override
    protected void onDetachedFromWindow() {
        ytCleanupTopBarChrome();
        super.onDetachedFromWindow();
    }
"""

        helper = f"""
    // YT_TOP_BAR_1TO1: Pixel-matched YouTube TV top bar (Avatar + Mic + Search Pill + YouTube logo)
    private boolean mYtTopBarReady = false;
    private View mYtSearchOrbRef = null;
    private View mYtMicButtonRef = null;
    private View mYtAccountOrbRef = null;
    private Runnable mYtDrawerSyncRunnable = null;

    private void ytInitTopBarChrome() {{
        post(new Runnable() {{
            @Override
            public void run() {{
                ytBuildOrRefreshTopBar();
            }}
        }});
        if (mYtDrawerSyncRunnable == null) {{
            mYtDrawerSyncRunnable = new Runnable() {{
                @Override
                public void run() {{
                    post(new Runnable() {{
                        @Override
                        public void run() {{
                            ytSyncTopBarToDrawer(BrowseSupportFragment.sYtDrawerExpanded);
                        }}
                    }});
                }}
            }};
        }}
        BrowseSupportFragment.sYtOnDrawerStateChanged = mYtDrawerSyncRunnable;
    }}

    private void ytCleanupTopBarChrome() {{
        if (BrowseSupportFragment.sYtOnDrawerStateChanged == mYtDrawerSyncRunnable) {{
            BrowseSupportFragment.sYtOnDrawerStateChanged = null;
        }}
    }}

    private void ytHideLegacySmartTubeViews() {{
        if (getContext() == null) return;
        String pkg = getContext().getPackageName();
        String[] hideIds = new String[] {{
            "global_time", "clock", "date", "title_badge", "title_text",
            "pip_orb", "exit_pip", "language_orb", "settings_orb", "wifi_orb", "cast_orb",
            "beta_badge", "version_badge", "app_version"
        }};
        for (String name : hideIds) {{
            int id = getResources().getIdentifier(name, "id", pkg);
            if (id != 0) {{
                View v = findViewById(id);
                if (v != null) {{
                    v.setVisibility(View.GONE);
                }}
            }}
        }}
    }}

    private void ytBuildOrRefreshTopBar() {{
        if (getContext() == null) return;
        float d = getResources().getDisplayMetrics().density;
        String pkg = getContext().getPackageName();

        setClipChildren(false);
        setClipToPadding(false);
        setPadding(0, 0, 0, 0);
        setBackgroundColor(Color.TRANSPARENT);

        ytHideLegacySmartTubeViews();

        if (mYtAccountOrbRef == null) {{
            for (String accIdName : new String[] {{"account_orb", "account_view"}}) {{
                int aid = getResources().getIdentifier(accIdName, "id", pkg);
                if (aid != 0) {{
                    View av = findViewById(aid);
                    if (av != null) {{
                        mYtAccountOrbRef = av;
                        break;
                    }}
                }}
            }}
        }}
        if (mYtAccountOrbRef != null) {{
            int avSize = (int) (30f * d);
            ViewGroup.LayoutParams alp = mYtAccountOrbRef.getLayoutParams();
            if (alp instanceof ViewGroup.MarginLayoutParams) {{
                ViewGroup.MarginLayoutParams amlp = (ViewGroup.MarginLayoutParams) alp;
                amlp.width = avSize;
                amlp.height = avSize;
                amlp.setMarginStart((int) (22f * d));
                amlp.topMargin = (int) (34f * d);
                mYtAccountOrbRef.setLayoutParams(amlp);
            }}
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.LOLLIPOP) {{
                mYtAccountOrbRef.setOutlineProvider(new ViewOutlineProvider() {{
                    @Override
                    public void getOutline(View view, Outline outline) {{
                        outline.setOval(0, 0, view.getWidth(), view.getHeight());
                    }}
                }});
                mYtAccountOrbRef.setClipToOutline(true);
            }}
        }}

        if (mYtSearchOrbRef == null) {{
            for (String sIdName : new String[] {{"title_orb", "search_orb"}}) {{
                int sid = getResources().getIdentifier(sIdName, "id", pkg);
                if (sid != 0) {{
                    View sv = findViewById(sid);
                    if (sv != null) {{
                        mYtSearchOrbRef = sv;
                        break;
                    }}
                }}
            }}
        }}

        if (mYtSearchOrbRef instanceof ViewGroup && mYtSearchOrbRef.findViewWithTag("yt_pill_label") == null) {{
            ViewGroup orbGroup = (ViewGroup) mYtSearchOrbRef;
            for (int i = 0; i < orbGroup.getChildCount(); i++) {{
                orbGroup.getChildAt(i).setVisibility(View.GONE);
            }}
            int pillBgId = getResources().getIdentifier("yt_search_pill_bg", "drawable", pkg);
            if (pillBgId != 0) {{
                orbGroup.setBackground(ContextCompat.getDrawable(getContext(), pillBgId));
            }}
            orbGroup.setPadding((int) (18f * d), 0, (int) (18f * d), 0);

            TextView hintTv = new TextView(getContext());
            hintTv.setTag("yt_pill_label");
            hintTv.setText("Поиск");
            hintTv.setTextSize(15f);
            hintTv.setTypeface(Typeface.create("sans-serif-medium", Typeface.NORMAL));
            hintTv.setGravity(Gravity.CENTER_VERTICAL | Gravity.START);
            hintTv.setDuplicateParentStateEnabled(true);
            int txtColorId = getResources().getIdentifier("yt_search_pill_text", "color", pkg);
            if (txtColorId != 0) {{
                ColorStateList csl = ContextCompat.getColorStateList(getContext(), txtColorId);
                if (csl != null) hintTv.setTextColor(csl);
            }} else {{
                hintTv.setTextColor(0xFFAAAAAA);
            }}
            orbGroup.addView(hintTv, new FrameLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT,
                ViewGroup.LayoutParams.MATCH_PARENT
            ));

            ViewGroup.LayoutParams slp = orbGroup.getLayoutParams();
            if (slp instanceof ViewGroup.MarginLayoutParams) {{
                ViewGroup.MarginLayoutParams smlp = (ViewGroup.MarginLayoutParams) slp;
                smlp.width = (int) (313f * d);
                smlp.height = (int) (36f * d);
                smlp.setMarginStart((int) (124f * d));
                smlp.topMargin = (int) (33f * d);
                if (smlp instanceof RelativeLayout.LayoutParams) {{
                    RelativeLayout.LayoutParams rlp = (RelativeLayout.LayoutParams) smlp;
                    rlp.removeRule(RelativeLayout.END_OF);
                    rlp.removeRule(RelativeLayout.RIGHT_OF);
                    rlp.addRule(RelativeLayout.ALIGN_PARENT_START);
                    rlp.addRule(RelativeLayout.ALIGN_PARENT_TOP);
                }}
                orbGroup.setLayoutParams(smlp);
            }}
        }}

        if (findViewWithTag("yt_mic_btn") == null) {{
            FrameLayout micBtn = new FrameLayout(getContext());
            micBtn.setTag("yt_mic_btn");
            micBtn.setFocusable(true);
            micBtn.setClickable(true);
            int micBgId = getResources().getIdentifier("yt_mic_circle_bg", "drawable", pkg);
            if (micBgId != 0) {{
                micBtn.setBackground(ContextCompat.getDrawable(getContext(), micBgId));
            }}
            final ImageView micIcon = new ImageView(getContext());
            int micIcId = getResources().getIdentifier("yt_ic_mic", "drawable", pkg);
            if (micIcId != 0) {{
                micIcon.setImageDrawable(ContextCompat.getDrawable(getContext(), micIcId));
            }}
            micIcon.setColorFilter(0xFFF1F1F1, android.graphics.PorterDuff.Mode.SRC_IN);
            FrameLayout.LayoutParams iconLp = new FrameLayout.LayoutParams(
                (int) (18f * d), (int) (18f * d), Gravity.CENTER);
            micBtn.addView(micIcon, iconLp);

            micBtn.setOnFocusChangeListener(new View.OnFocusChangeListener() {{
                @Override
                public void onFocusChange(View v, boolean hasFocus) {{
                    micIcon.setColorFilter(hasFocus ? 0xFF0F0F0F : 0xFFF1F1F1,
                        android.graphics.PorterDuff.Mode.SRC_IN);
                }}
            }});
            micBtn.setOnClickListener(new View.OnClickListener() {{
                @Override
                public void onClick(View v) {{
                    if (mYtSearchOrbRef != null) {{
                        mYtSearchOrbRef.performClick();
                    }}
                }}
            }});

            ViewGroup.MarginLayoutParams mlp;
            if (this instanceof RelativeLayout) {{
                RelativeLayout.LayoutParams rlp = new RelativeLayout.LayoutParams((int) (36f * d), (int) (36f * d));
                rlp.addRule(RelativeLayout.ALIGN_PARENT_START);
                rlp.addRule(RelativeLayout.ALIGN_PARENT_TOP);
                mlp = rlp;
            }} else {{
                FrameLayout.LayoutParams flp = new FrameLayout.LayoutParams((int) (36f * d), (int) (36f * d), Gravity.TOP | Gravity.START);
                mlp = flp;
            }}
            mlp.setMarginStart((int) (79f * d));
            mlp.topMargin = (int) (33f * d);
            addView(micBtn, mlp);
            mYtMicButtonRef = micBtn;
        }}

        if (findViewWithTag("yt_top_wordmark") == null) {{
            LinearLayout brandBox = new LinearLayout(getContext());
            brandBox.setTag("yt_top_wordmark");
            brandBox.setOrientation(LinearLayout.HORIZONTAL);
            brandBox.setGravity(Gravity.CENTER_VERTICAL);
            brandBox.setFocusable(false);

            ImageView playIcon = new ImageView(getContext());
            int badgeId = getResources().getIdentifier("yt_play_badge", "drawable", pkg);
            if (badgeId != 0) {{
                playIcon.setImageDrawable(ContextCompat.getDrawable(getContext(), badgeId));
            }}
            LinearLayout.LayoutParams iconLp = new LinearLayout.LayoutParams((int) (31f * d), (int) (22f * d));
            iconLp.setMarginEnd((int) (5f * d));
            brandBox.addView(playIcon, iconLp);

            TextView wordmark = new TextView(getContext());
            wordmark.setText("YouTube");
            wordmark.setTextColor(0xFFF1F1F1);
            wordmark.setTextSize(21f);
            wordmark.setLetterSpacing(-0.04f);
            int fontId = getResources().getIdentifier("youtube_sans_bold", "font", pkg);
            if (fontId != 0) {{
                try {{
                    Typeface tf = ResourcesCompat.getFont(getContext(), fontId);
                    if (tf != null) wordmark.setTypeface(tf);
                }} catch (Throwable ignored) {{}}
            }} else {{
                wordmark.setTypeface(Typeface.DEFAULT_BOLD);
            }}
            brandBox.addView(wordmark);

            ViewGroup.MarginLayoutParams blp;
            if (this instanceof RelativeLayout) {{
                RelativeLayout.LayoutParams rlp = new RelativeLayout.LayoutParams(
                    ViewGroup.LayoutParams.WRAP_CONTENT, ViewGroup.LayoutParams.WRAP_CONTENT);
                rlp.addRule(RelativeLayout.ALIGN_PARENT_END);
                rlp.addRule(RelativeLayout.ALIGN_PARENT_TOP);
                blp = rlp;
            }} else {{
                FrameLayout.LayoutParams flp = new FrameLayout.LayoutParams(
                    ViewGroup.LayoutParams.WRAP_CONTENT, ViewGroup.LayoutParams.WRAP_CONTENT,
                    Gravity.TOP | Gravity.END);
                blp = flp;
            }}
            blp.topMargin = (int) (36f * d);
            blp.setMarginEnd((int) (55f * d));
            addView(brandBox, blp);
        }}

        mYtTopBarReady = true;
        ytSyncTopBarToDrawer(BrowseSupportFragment.sYtDrawerExpanded);
    }}

    private void ytSyncTopBarToDrawer(boolean expanded) {{
        if (!mYtTopBarReady || getContext() == null) return;
        float d = getResources().getDisplayMetrics().density;
        float shiftPx = expanded ? (188f * d) : 0f;
        if (mYtMicButtonRef != null) {{
            mYtMicButtonRef.animate().translationX(shiftPx).setDuration(180).start();
        }}
        if (mYtSearchOrbRef != null) {{
            mYtSearchOrbRef.animate().translationX(shiftPx).setDuration(180).start();
        }}
    }}
{overrides}
"""

        idx = text.rfind("}")
        if idx != -1:
            text = text[:idx] + helper + "\n}\n"
            java_file.write_text(text, encoding="utf-8")
            print(f"[YT-UI] Patched NavigateTitleView (YouTube TV 1:1 top bar) -> {java_file}")


# ==============================================================================
# 4. VIDEO CARDS (ComplexImageCardView.java) — KILLS WHITE BOX + ENFORCES 352x198dp
# ==============================================================================

def patch_complex_card_view():
    candidates = [
        p for p in ROOT.rglob("ComplexImageCardView.java")
        if "build" not in p.parts
    ]
    if not candidates:
        print("[YT-UI] WARNING: ComplexImageCardView.java not found!")
        return

    for java_file in candidates:
        text = java_file.read_text(encoding="utf-8")
        if "YT_DISPATCH_DRAW_RING" in text:
            continue

        text = ensure_imports(
            text,
            [
                "android.graphics.Canvas",
                "android.graphics.Color",
                "android.graphics.Outline",
                "android.graphics.Paint",
                "android.graphics.RectF",
                "android.graphics.drawable.Drawable",
                "android.os.Build",
                "android.view.View",
                "android.view.ViewOutlineProvider",
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
                text = super_sel_re.sub(rf"\g<1>\n        applyYouTubeFocusState({param});", text, count=1)
            else:
                text = selected_decl_re.sub(rf"\g<1>\n        applyYouTubeFocusState({param});", text, count=1)

        dispatch_decl_re = re.compile(r"((?:protected|public)\s+void\s+dispatchDraw\s*\(\s*Canvas\s+(\w+)\s*\)\s*\{)")
        dd_match = dispatch_decl_re.search(text)
        has_dispatch = dd_match is not None
        if has_dispatch:
            c_var = dd_match.group(2)
            super_dd_re = re.compile(rf"(super\.dispatchDraw\s*\(\s*{re.escape(c_var)}\s*\)\s*;)")
            if super_dd_re.search(text):
                text = super_dd_re.sub(rf"\g<1>\n        drawYouTubeFocusRing({c_var});", text, count=1)
            else:
                text = dispatch_decl_re.sub(rf"\g<1>\n        drawYouTubeFocusRing({c_var});", text, count=1)

        has_info_bg_color = re.search(r"void\s+setInfoAreaBackgroundColor\s*\(", text) is not None
        has_info_bg = re.search(r"void\s+setInfoAreaBackground\s*\(", text) is not None
        has_main_dims = re.search(r"void\s+setMainImageDimensions\s*\(", text) is not None

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
        applyYouTubeFocusState(selected);
    }
"""
        if not has_dispatch:
            extra_overrides += """
    @Override
    protected void dispatchDraw(Canvas canvas) {
        super.dispatchDraw(canvas);
        drawYouTubeFocusRing(canvas);
    }
"""
        if not has_info_bg_color:
            extra_overrides += """
    @Override
    public void setInfoAreaBackgroundColor(int color) {
        // YT_DISPATCH_DRAW_RING: never allow CardPresenter to paint white/grey box behind title
        super.setInfoAreaBackgroundColor(Color.TRANSPARENT);
    }
"""
        if not has_info_bg:
            extra_overrides += """
    @Override
    public void setInfoAreaBackground(Drawable drawable) {
        super.setInfoAreaBackgroundColor(Color.TRANSPARENT);
    }
"""
        if not has_main_dims:
            extra_overrides += """
    @Override
    public void setMainImageDimensions(int width, int height) {
        // YT_DISPATCH_DRAW_RING: enforce YouTube TV 16:9 large card size (352x198dp) for landscape video cards
        if (width > height && width > 0 && height > 0) {
            float d = getResources().getDisplayMetrics().density;
            super.setMainImageDimensions((int) (352f * d), (int) (198f * d));
        } else {
            super.setMainImageDimensions(width, height);
        }
    }
"""

        helper_code = f"""
    // YT_DISPATCH_DRAW_RING: 12dp rounded thumbnail + crisp 3.5dp solid #F1F1F1 YouTube TV focus frame
    private boolean mYtStyled = false;
    private Paint mYtRingWhitePaint = null;
    private final RectF mYtRingRect = new RectF();

    private View findYtViewByName(String idName) {{
        int id = getResources().getIdentifier(idName, "id", getContext().getPackageName());
        return id != 0 ? findViewById(id) : null;
    }}

    private void initYtPaints() {{
        if (mYtRingWhitePaint != null) return;
        float d = getResources().getDisplayMetrics().density;
        mYtRingWhitePaint = new Paint(Paint.ANTI_ALIAS_FLAG);
        mYtRingWhitePaint.setStyle(Paint.Style.STROKE);
        mYtRingWhitePaint.setColor(0xFFF1F1F1);
        mYtRingWhitePaint.setStrokeWidth(3.5f * d);
    }}

    private void applyYouTubeCardStyle() {{
        if (mYtStyled) return;
        mYtStyled = true;

        initYtPaints();
        setBackgroundColor(Color.TRANSPARENT);

        View infoField = findYtViewByName("info_field");
        if (infoField != null) {{
            infoField.setBackgroundColor(Color.TRANSPARENT);
        }}

        ImageView img = getMainImageView();
        if (img != null && Build.VERSION.SDK_INT >= Build.VERSION_CODES.LOLLIPOP) {{
            final float radiusPx = 12f * getResources().getDisplayMetrics().density;
            img.setOutlineProvider(new ViewOutlineProvider() {{
                @Override
                public void getOutline(View view, Outline outline) {{
                    outline.setRoundRect(0, 0, view.getWidth(), view.getHeight(), radiusPx);
                }}
            }});
            img.setClipToOutline(true);
        }}

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.LOLLIPOP) {{
            final float badgeRadius = 4f * getResources().getDisplayMetrics().density;
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

        applyYouTubeFocusState(isSelected() || isFocused());
    }}

    private void applyYouTubeFocusState(boolean selected) {{
        setBackgroundColor(Color.TRANSPARENT);
        View infoField = findYtViewByName("info_field");
        if (infoField != null) {{
            infoField.setBackgroundColor(Color.TRANSPARENT);
        }}

        View title = findYtViewByName("title_text");
        if (title instanceof TextView) {{
            ((TextView) title).setTextColor(selected ? 0xFFF1F1F1 : 0xFFCCCCCC);
        }}
        View content = findYtViewByName("content_text");
        if (content instanceof TextView) {{
            ((TextView) content).setTextColor(0xFFAAAAAA);
        }}
        invalidate();
    }}

    private void drawYouTubeFocusRing(Canvas canvas) {{
        if (!isSelected() && !isFocused()) {{
            return;
        }}
        ImageView img = getMainImageView();
        if (img == null || img.getWidth() <= 0 || img.getHeight() <= 0) {{
            return;
        }}
        initYtPaints();
        float ox = 0f;
        float oy = 0f;
        View v = img;
        int guard = 0;
        while (v != null && v != this && guard++ < 8) {{
            ox += v.getLeft() + v.getTranslationX();
            oy += v.getTop() + v.getTranslationY();
            v = (v.getParent() instanceof View) ? (View) v.getParent() : null;
        }}
        float d = getResources().getDisplayMetrics().density;
        float w = img.getWidth();
        float h = img.getHeight();

        float inset = 1.75f * d;
        mYtRingRect.set(ox + inset, oy + inset, ox + w - inset, oy + h - inset);
        canvas.drawRoundRect(mYtRingRect, 12f * d, 12f * d, mYtRingWhitePaint);
    }}
{extra_overrides}
"""

        idx = text.rfind("}")
        if idx != -1:
            text = text[:idx] + helper_code + "\n}\n"
            java_file.write_text(text, encoding="utf-8")
            print(f"[YT-UI] Patched ComplexImageCardView (transparent info + 352x198dp + 3.5dp ring) -> {java_file}")


# ==============================================================================
# 5. ULTRA-FAST VIDEO STARTUP OPTIMIZATIONS
# ==============================================================================

def patch_exoplayer_fast_buffer():
    patched_files = 0
    for java_file in ROOT.rglob("DefaultLoadControl.java"):
        if "build" in java_file.parts:
            continue
        text = java_file.read_text(encoding="utf-8")
        if "YT_FAST_BUFFER" in text:
            continue

        original = text
        changes = []

        new_text, c1 = re.subn(
            r"(public\s+static\s+final\s+int\s+DEFAULT_BUFFER_FOR_PLAYBACK_MS\s*=\s*)\d+(\s*;)",
            r"\g<1>400\g<2> // YT_FAST_BUFFER (was 2500ms)",
            text,
        )
        if c1:
            text = new_text
            changes.append("DEFAULT_BUFFER_FOR_PLAYBACK_MS=400")

        new_text, c2 = re.subn(
            r"(public\s+static\s+final\s+int\s+DEFAULT_BUFFER_FOR_PLAYBACK_AFTER_REBUFFER_MS\s*=\s*)\d+(\s*;)",
            r"\g<1>800\g<2> // YT_FAST_BUFFER (was 5000ms)",
            text,
        )
        if c2:
            text = new_text
            changes.append("DEFAULT_BUFFER_FOR_PLAYBACK_AFTER_REBUFFER_MS=800")

        builder_re = re.compile(
            r"(public\s+Builder\s+setBufferDurationsMs\s*\(\s*"
            r"int\s+(\w+)\s*,\s*int\s+(\w+)\s*,\s*int\s+(\w+)\s*,\s*int\s+(\w+)\s*\)\s*\{)"
        )
        m = builder_re.search(text)
        if m:
            p_play = m.group(4)
            p_rebuf = m.group(5)
            clamp = (
                f"\n      // YT_FAST_BUFFER: cap startup playback wait for instant first frame\n"
                f"      {p_play} = Math.min({p_play}, 400);\n"
                f"      {p_rebuf} = Math.min({p_rebuf}, 800);"
            )
            text = text[:m.end()] + clamp + text[m.end():]
            changes.append("Builder.setBufferDurationsMs clamped(400/800)")

        field_assign_re = re.compile(
            r"(this\.bufferForPlaybackMs\s*=\s*bufferForPlaybackMs\s*;)"
        )
        if field_assign_re.search(text):
            text = field_assign_re.sub(
                "this.bufferForPlaybackMs = Math.min(bufferForPlaybackMs, 400); // YT_FAST_BUFFER",
                text,
                count=1,
            )
            text = re.sub(
                r"(this\.bufferForPlaybackAfterRebufferMs\s*=\s*bufferForPlaybackAfterRebufferMs\s*;)",
                "this.bufferForPlaybackAfterRebufferMs = Math.min(bufferForPlaybackAfterRebufferMs, 800); // YT_FAST_BUFFER",
                text,
                count=1,
            )
            changes.append("master ctor field assignments clamped(400/800)")

        if text != original:
            java_file.write_text(text, encoding="utf-8")
            patched_files += 1
            print(f"[YT-FAST] Patched ExoPlayer LoadControl ({', '.join(changes)}) -> {java_file}")

    if not patched_files:
        print("[YT-FAST] WARNING: DefaultLoadControl.java not found in SmartTube tree!")


def patch_application_warmup():
    app_candidates = []
    for mod in MODULES:
        if not mod.exists():
            continue
        for java_file in mod.rglob("*.java"):
            if "build" in java_file.parts:
                continue
            text = java_file.read_text(encoding="utf-8", errors="ignore")
            if re.search(r"class\s+\w+\s+extends\s+(?:MultiDex)?Application\b", text) and "onCreate()" in text:
                app_candidates.append(java_file)

    if not app_candidates:
        return

    for java_file in app_candidates:
        text = java_file.read_text(encoding="utf-8")
        if "YT_FAST_WARMUP" in text:
            continue

        new_text, count = re.subn(
            r"(super\.onCreate\s*\(\s*\)\s*;)",
            r"\g<1>\n        ytFastStartupWarmup();",
            text,
            count=1,
        )
        if not count:
            continue

        warmup_method = """
    // YT_FAST_WARMUP: Preload Rust libstjson.so + pre-resolve YouTube/googlevideo DNS & TLS
    private static volatile boolean sYtWarmupStarted = false;

    private void ytFastStartupWarmup() {
        if (sYtWarmupStarted) {
            return;
        }
        sYtWarmupStarted = true;
        Thread t = new Thread(new Runnable() {
            @Override
            public void run() {
                try {
                    Class.forName("com.liskovsoft.googlecommon.common.converters.jsonpath.nativeimpl.NativeJson");
                } catch (Throwable ignored) {}

                String[] hosts = new String[] {
                    "youtubei.googleapis.com",
                    "redirector.googlevideo.com",
                    "www.youtube.com",
                    "i.ytimg.com"
                };
                for (String host : hosts) {
                    try {
                        java.net.InetAddress.getAllByName(host);
                    } catch (Throwable ignored) {}
                }

                String[] urls = new String[] {
                    "https://youtubei.googleapis.com/generate_204",
                    "https://redirector.googlevideo.com/generate_204"
                };
                for (String u : urls) {
                    java.net.HttpURLConnection conn = null;
                    try {
                        conn = (java.net.HttpURLConnection) new java.net.URL(u).openConnection();
                        conn.setRequestMethod("HEAD");
                        conn.setConnectTimeout(1500);
                        conn.setReadTimeout(1500);
                        conn.setUseCaches(false);
                        conn.getResponseCode();
                    } catch (Throwable ignored) {
                    } finally {
                        if (conn != null) {
                            try { conn.disconnect(); } catch (Throwable ignored) {}
                        }
                    }
                }
            }
        }, "yt-fast-warmup");
        t.setDaemon(true);
        t.setPriority(Thread.NORM_PRIORITY - 1);
        t.start();
    }
"""
        idx = new_text.rfind("}")
        if idx != -1:
            new_text = new_text[:idx] + warmup_method + "\n}\n"
            java_file.write_text(new_text, encoding="utf-8")
            print(f"[YT-FAST] Injected Rust preload + YouTube/googlevideo DNS/TLS warmup -> {java_file}")


def patch_glide_rgb565():
    for java_file in ROOT.rglob("*Glide*.java"):
        if "build" in java_file.parts:
            continue
        text = java_file.read_text(encoding="utf-8")
        if "DecodeFormat.PREFER_ARGB_8888" in text:
            new_text = text.replace("DecodeFormat.PREFER_ARGB_8888", "DecodeFormat.PREFER_RGB_565")
            if new_text != text:
                java_file.write_text(new_text, encoding="utf-8")
                print(f"[YT-FAST] Switched Glide to RGB_565 in {java_file}")
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
                print(f"[YT-FAST] Injected Glide RGB_565 default in {java_file}")


def main():
    if not ROOT.exists():
        raise SystemExit("[YT-UI] SmartTube directory not found!")

    primary_res = get_primary_res_dir()
    has_font = install_font(primary_res)
    write_shared_resources(primary_res)

    for mod in MODULES + ([LEANBACK_DIR] if LEANBACK_DIR.exists() else []):
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

    patch_leanback_collapsible_rail()
    patch_icon_header_presenter()
    patch_navigate_title_view()
    patch_complex_card_view()
    patch_exoplayer_fast_buffer()
    patch_application_warmup()
    patch_glide_rgb565()
    print("[YT-UI] YouTube TV 1:1 Home Screen + Collapsible Left Drawer + Fast Startup applied successfully.")


if __name__ == "__main__":
    main()
