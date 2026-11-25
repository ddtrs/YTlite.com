#!/usr/bin/env python3
"""
Stage 1: Official YouTube TV (Cobalt) 1:1 visual theme for SmartTube.
Features:
  - YouTube TV palette (#0F0F0F canvas, #272727 surfaces, #F1F1F1 focus, #FF0033 progress)
  - Official YouTube Sans Bold font (auto-picked from assets/youtube_sans_bold.ttf)
  - 12dp hardware-accelerated rounded video thumbnails (ViewOutlineProvider, 60 FPS safe)
  - Double-bezel thumbnail-only focus ring (#F1F1F1 + #0F0F0F inner gap) & smooth 1.05x scale
  - Borderless metadata typography directly on #0F0F0F (removes grey Leanback card box)
  - Rounded 4dp badges (preserves LIVE red badge colors) & #FF0033 watch progress bar
  - RGB_565 Glide decoding to halve thumbnail RAM usage on 1 GB RAM devices
"""
import os
import re
import shutil
from pathlib import Path

ROOT = Path("SmartTube")
WORKSPACE = Path(os.environ.get("GITHUB_WORKSPACE", "."))
MODULES = [ROOT / "common", ROOT / "smarttubetv"]

# Official YouTube TV (Cobalt) color tokens
YT_COLORS = {
    # Canvases & backgrounds
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
    # Focus & interactive surfaces
    "lb_default_brand_color": "#0F0F0F",
    "lb_default_brand_color_dark": "#0F0F0F",
    "lb_default_search_color": "#F1F1F1",
    "lb_default_search_icon_color": "#0F0F0F",
    "lb_control_button_color": "#26FFFFFF",
    "lb_control_button_text": "#F1F1F1",
    "accent": "#F1F1F1",
    "colorAccent": "#F1F1F1",
    # Typography
    "lb_basic_card_title_text_color": "#F1F1F1",
    "lb_basic_card_content_text_color": "#AAAAAA",
    "lb_browse_title_color": "#F1F1F1",
    "lb_header_text_color": "#F1F1F1",
    "row_header_color": "#F1F1F1",
    "primary_text": "#F1F1F1",
    "secondary_text": "#AAAAAA",
    "card_title_text_color": "#F1F1F1",
    "card_content_text_color": "#AAAAAA",
    # Progress & brand red
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

# Double-bezel YouTube TV focus ring: crisp 2.5dp #F1F1F1 outer stroke + 1.5dp #0F0F0F inner gap
DRAWABLE_THUMB_FOCUS_RING = """<?xml version="1.0" encoding="utf-8"?>
<layer-list xmlns:android="http://schemas.android.com/apk/res/android">
    <item>
        <shape android:shape="rectangle">
            <solid android:color="@android:color/transparent" />
            <stroke
                android:width="2.5dp"
                android:color="#F1F1F1" />
            <corners android:radius="12dp" />
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
                android:width="1.5dp"
                android:color="#0F0F0F" />
            <corners android:radius="9.5dp" />
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

EXTRA_YT_VALUES = """<?xml version="1.0" encoding="utf-8"?>
<resources>
    <color name="yt_canvas_bg">#0F0F0F</color>
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
    """Place shared drawables/tokens/font in common/res (visible to both common and smarttubetv)."""
    for mod in MODULES:
        res_dir = mod / "src" / "main" / "res"
        if res_dir.exists():
            return res_dir
    raise SystemExit("[YT-UI] No Android res/ directory found inside SmartTube!")


def install_font(res_dir: Path) -> bool:
    candidates = [
        WORKSPACE / "assets" / "youtube_sans_bold.ttf",
        WORKSPACE / "youtube_sans_bold.ttf",
        Path("assets/youtube_sans_bold.ttf"),
        Path("youtube_sans_bold.ttf"),
    ]
    src = next((p for p in candidates if p.is_file()), None)
    if not src:
        print("[YT-UI] WARNING: assets/youtube_sans_bold.ttf not found -> keeping system font.")
        return False

    font_dir = res_dir / "font"
    font_dir.mkdir(parents=True, exist_ok=True)
    dst = font_dir / "youtube_sans_bold.ttf"
    shutil.copy2(src, dst)
    print(f"[YT-UI] Installed YouTube Sans Bold font -> {dst}")
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
    }
    for name, content in files.items():
        (drawable_dir / name).write_text(content.strip() + "\n", encoding="utf-8")

    values_dir = res_dir / "values"
    values_dir.mkdir(parents=True, exist_ok=True)
    (values_dir / "yt_theme_tokens.xml").write_text(EXTRA_YT_VALUES.strip() + "\n", encoding="utf-8")
    print(f"[YT-UI] Wrote YouTube TV drawables and color tokens -> {res_dir}")


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
        "lb_browse_rows_margin_top": "110dp",
        "lb_browse_padding_start": "44dp",
        "lb_browse_padding_end": "44dp",
        "lb_browse_item_margin": "16dp",
        "lb_browse_row_title_text_size": "18sp",
        "lb_basic_card_title_text_size": "14sp",
        "lb_basic_card_content_text_size": "12sp",
        "lb_basic_card_info_padding_top": "10dp",
        "lb_basic_card_info_padding_bottom": "4dp",
        "lb_basic_card_info_padding_horizontal": "2dp",
        "card_width": "240dp",
        "card_height": "135dp",
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
        "defaultBrandColor": "@color/yt_canvas_bg",
        "defaultBrandColorDark": "@color/yt_canvas_bg",
        "defaultSearchColor": "@color/yt_focus_white",
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
    """Safely update or insert attributes on an XML element matching android:id='@+id/<view_id>'."""
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
    candidates = [
        p for p in ROOT.rglob("ComplexImageCardView.java")
        if "build" not in p.parts
    ]
    if not candidates:
        print("[YT-UI] WARNING: ComplexImageCardView.java not found!")
        return

    for java_file in candidates:
        text = java_file.read_text(encoding="utf-8")
        if "YT_STAGE1_APPLIED" in text:
            continue

        text = ensure_imports(
            text,
            [
                "android.graphics.Color",
                "android.graphics.Outline",
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

        # Hook into existing onAttachedToWindow() AFTER super.onAttachedToWindow(), or add one safely
        attached_super_re = re.compile(r"(super\.onAttachedToWindow\s*\(\s*\)\s*;)")
        attached_decl_re = re.compile(r"((?:protected|public)\s+void\s+onAttachedToWindow\s*\(\s*\)\s*\{)")
        has_attached = attached_decl_re.search(text) is not None
        if has_attached:
            if attached_super_re.search(text):
                text = attached_super_re.sub(r"\g<1>\n        applyYouTubeCardStyle();", text, count=1)
            else:
                text = attached_decl_re.sub(r"\g<1>\n        applyYouTubeCardStyle();", text, count=1)

        # Hook into existing setSelected(boolean ...) AFTER super.setSelected(...), or add one safely
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
    // YT_STAGE1_APPLIED: Official YouTube TV 1:1 card visuals (12dp clip, double focus ring, borderless info)
    private boolean mYtStyled = false;

    private View findYtViewByName(String idName) {{
        int id = getResources().getIdentifier(idName, "id", getContext().getPackageName());
        return id != 0 ? findViewById(id) : null;
    }}

    private void applyYouTubeCardStyle() {{
        if (mYtStyled) {{
            return;
        }}
        mYtStyled = true;

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

            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {{
                int ringId = getResources().getIdentifier("yt_thumb_focus_selector", "drawable", getContext().getPackageName());
                if (ringId != 0) {{
                    Drawable ring = ContextCompat.getDrawable(getContext(), ringId);
                    img.setForeground(ring);
                }}
            }}
        }}

        // Clip duration/LIVE badges cleanly to 4dp without overwriting LIVE red backgrounds
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.LOLLIPOP) {{
            final float badgeRadius = 4f * getResources().getDisplayMetrics().density;
            String[] badgeNames = new String[] {{"duration_badge", "badge_text"}};
            for (String bn : badgeNames) {{
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

        // Apply YouTube #FF0033 watch progress bar
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

        ImageView img = getMainImageView();
        if (img != null) {{
            img.setSelected(selected);
            float target = selected ? 1.05f : 1.0f;
            img.animate()
                .scaleX(target)
                .scaleY(target)
                .setDuration(140)
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
            print(f"[YT-UI] Patched ComplexImageCardView -> {java_file}")


def patch_glide_rgb565():
    patched = 0
    for java_file in ROOT.rglob("*Glide*.java"):
        if "build" in java_file.parts:
            continue
        text = java_file.read_text(encoding="utf-8")
        if "DecodeFormat.PREFER_ARGB_8888" in text:
            new_text = text.replace("DecodeFormat.PREFER_ARGB_8888", "DecodeFormat.PREFER_RGB_565")
            if new_text != text:
                java_file.write_text(new_text, encoding="utf-8")
                print(f"[YT-UI] Switched Glide to RGB_565 in {java_file}")
                patched += 1
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
                patched += 1
    if not patched:
        print("[YT-UI] Note: No Glide module needed RGB_565 patching.")


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
    patch_glide_rgb565()
    print("[YT-UI] Stage 1 YouTube TV 1:1 theme applied successfully.")


if __name__ == "__main__":
    main()
