#!/usr/bin/env python3
"""
YouTube TV (2025-2026) 1:1 Home Screen & Collapsible Left Drawer + Ultra-Fast Video Startup
Pixel-calibrated directly from Mi TV Stick 1920x1080 ADB screenshots (xhdpi, 960x540dp):
  [HOME SCREEN - 1:1 with screenshot_20261126_091356.png]
  - Pure #0F0F0F canvas & drawer background
  - Top bar (y=33dp): circular user avatar at x=25dp, #272727 Mic circle (36dp) at x=79dp,
    #272727 Search pill ("Поиск", 313x36dp, 18dp radius) at x=124dp, official YouTube Play
    badge + "YouTube" wordmark (YouTube Sans Bold) pinned top-right (marginEnd=55dp).
    SmartTube red search orb, clock, date, S-beta badge & extra orbs hidden cleanly.
  - Video cards: 360x202dp (16:9, 2 full cards + peek of 3rd), 12dp rounded corners,
    crisp 3.5dp solid #F1F1F1 focus ring drawn unclipped via dispatchDraw(Canvas),
    borderless title (#F1F1F1) + channel/views (#AAAAAA) directly on #0F0F0F, #FF0033 progress bar.

  [LEFT NAVIGATION RAIL <-> EXPANDED DRAWER - 1:1 with screenshot_20261126_091356.png & yt_menu.png]
  - Collapsed (browsing videos): slim 74dp #0F0F0F left icon rail with YouTube thin-stroke
    vector icons (active icon bright #FFFFFF / filled Home, inactive #9A9A9A), labels hidden,
    cards start at x=74dp, Mic + Search pill sit at x=79dp.
  - Expanded (D-pad Left): smoothly expands to 250dp #0F0F0F drawer, cards glide to x=268dp,
    Mic + Search pill glide to x=267dp, focused row renders as 222x39dp solid #F1F1F1 rounded
    rectangle (12dp radius) with #0F0F0F dark icon & bold text; unfocused rows stay crisp #F1F1F1.
  - Official YouTube TV vector icon set auto-mapped to RU / UK / EN section titles.

  [ULTRA-FAST VIDEO STARTUP]
  - ExoPlayer DefaultLoadControl: bufferForPlaybackMs=400ms, afterRebuffer=800ms (safe master ctor patch)
  - Background warmup daemon in Application.onCreate(): preloads Rust libstjson.so + DNS/TLS warmup
  - Glide RGB_565 thumbnail decoding (halves bitmap RAM on 1 GB Mi TV Stick)
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

# Top bar Search Pill (#272727 normal -> #F1F1F1 focused, 18dp pill radius)
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

# Top bar Mic Circle (36dp oval, #272727 normal -> #F1F1F1 focused)
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

# Expanded left drawer focused item pill: exact 12dp rounded rectangle (#F1F1F1) from yt_menu.png
DRAWABLE_DRAWER_PILL_FOCUSED = """<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android"
    android:shape="rectangle">
    <solid android:color="#F1F1F1" />
    <corners android:radius="12dp" />
</shape>
"""

# Official YouTube Play badge (31x21.5dp) for top-right header
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

# ColorStateList for Search Pill text (no focus listener conflict!)
COLOR_SEARCH_PILL_TEXT = """<?xml version="1.0" encoding="utf-8"?>
<selector xmlns:android="http://schemas.android.com/apk/res/android">
    <item android:state_focused="true" android:color="#0F0F0F" />
    <item android:color="#AAAAAA" />
</selector>
"""

# Official YouTube TV thin-stroke vector icon set (matching screenshot_20261126_091356.png & yt_menu.png)
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
        new_text, count = pa
