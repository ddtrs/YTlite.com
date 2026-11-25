#!/usr/bin/env python3
"""
YouTube TV 1:1 UI + Ultra-Fast Video Startup Patcher for SmartTube.
Includes:
  [FAST VIDEO STARTUP]
  - ExoPlayer DefaultLoadControl instant start:
      bufferForPlaybackMs: 2500ms -> 400ms
      bufferForPlaybackAfterRebufferMs: 5000ms -> 800ms
      (patched in both defaults and Builder.setBufferDurationsMs / constructor)
  - Background startup warmup thread in Application.onCreate():
      * Eagerly preloads Rust libstjson.so (NativeJson) off main thread
      * Pre-resolves DNS & warms TLS connections to youtubei.googleapis.com,
        redirector.googlevideo.com, www.youtube.com, i.ytimg.com
  - Glide RGB_565 thumbnail decoding (halves RAM usage on 1 GB Mi TV Stick)

  [YOUTUBE TV UI]
  - Official YouTube TV palette (#0F0F0F canvas, #272727 surfaces, #F1F1F1 focus, #FF0033 progress)
  - Auto-detects any .ttf font in repo (YouTube Sans Bold)
  - 10dp rounded video thumbnails + guaranteed-visible double-bezel white focus ring
    drawn via zero-allocation dispatchDraw(Canvas) (never clipped by clipToOutline or RecyclerView)
  - Borderless metadata typography directly on #0F0F0F
  - Safe top spacing (108dp) so cards never collide with top bar until Stage 3 full top-bar rewrite
  - Prints exact paths of SmartTube Browse/Title/Header/ExoPlayer classes for ADB 1:1 polish
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
    "lb_default_search_color": "#272727",
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

DRAWABLE_THUMB_BG = """<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android"
    android:shape="rectangle">
    <solid android:color="#1A1A1A" />
    <corners android:radius="10dp" />
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
        "yt_play_badge.xml": DRAWABLE_YT_PLAY_BADGE,
        "yt_drawer_item_bg.xml": DRAWABLE_DRAWER_ITEM_BG,
    }
    for name, content in files.items():
        (drawable_dir / name).write_text(content.strip() + "\n", encoding="utf-8")

    values_dir = res_dir / "values"
    values_dir.mkdir(parents=True, exist_ok=True)
    (values_dir / "yt_theme_tokens.xml").write_text(EXTRA_YT_VALUES.strip() + "\n", encoding="utf-8")
    print(f"[YT-UI] Wrote YouTube TV drawables & color tokens -> {res_dir}")


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
        # Keep safe 108dp top margin so first row never collides with top bar
        "lb_browse_rows_margin_top": "108dp",
        "lb_browse_padding_start": "44dp",
        "lb_browse_padding_end": "44dp",
        "lb_browse_item_margin": "16dp",
        "lb_browse_row_title_text_size": "18sp",
        "lb_basic_card_title_text_size": "14sp",
        "lb_basic_card_content_text_size": "12sp",
        "lb_basic_card_info_padding_top": "9dp",
        "lb_basic_card_info_padding_bottom": "4dp",
        "lb_basic_card_info_padding_horizontal": "2dp",
        "card_width": "256dp",
        "card_height": "144dp",
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
    Bulletproof YouTube TV 1:1 Video Card:
      - 10dp hardware-clipped rounded thumbnail (matches 4900.jpg / 4901.jpg)
      - Crisp double-bezel white focus ring (#F1F1F1 outer 2.5dp + #0F0F0F inner 2dp gap)
        drawn in dispatchDraw(Canvas) directly over main_image bounds:
        * Never clipped by ViewOutlineProvider
        * Never clipped by RecyclerView/HorizontalGridView
        * Zero allocations per frame (pre-allocated Paint & RectF)
      - Transparent info_field directly on #0F0F0F
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
                "android.os.Build",
                "android.view.View",
                "android.view.ViewOutlineProvider",
                "android.widget.ImageView",
                "android.widget.ProgressBar",
                "android.widget.TextView",
                "androidx.core.content.ContextCompat",
            ],
        )

        # Hook onAttachedToWindow
        attached_super_re = re.compile(r"(super\.onAttachedToWindow\s*\(\s*\)\s*;)")
        attached_decl_re = re.compile(r"((?:protected|public)\s+void\s+onAttachedToWindow\s*\(\s*\)\s*\{)")
        has_attached = attached_decl_re.search(text) is not None
        if has_attached:
            if attached_super_re.search(text):
                text = attached_super_re.sub(r"\g<1>\n        applyYouTubeCardStyle();", text, count=1)
            else:
                text = attached_decl_re.sub(r"\g<1>\n        applyYouTubeCardStyle();", text, count=1)

        # Hook setSelected(boolean)
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

        # Hook dispatchDraw(Canvas) if already present, else override cleanly
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

        helper_code = f"""
    // YT_DISPATCH_DRAW_RING: 10dp rounded clip + unclipped double-bezel white focus ring
    private boolean mYtStyled = false;
    private Paint mYtRingWhitePaint = null;
    private Paint mYtRingGapPaint = null;
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
        mYtRingWhitePaint.setStrokeWidth(2.6f * d);

        mYtRingGapPaint = new Paint(Paint.ANTI_ALIAS_FLAG);
        mYtRingGapPaint.setStyle(Paint.Style.STROKE);
        mYtRingGapPaint.setColor(0xFF0F0F0F);
        mYtRingGapPaint.setStrokeWidth(2.2f * d);
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
            final float radiusPx = 10f * getResources().getDisplayMetrics().density;
            img.setOutlineProvider(new ViewOutlineProvid
