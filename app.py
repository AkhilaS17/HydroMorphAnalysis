import streamlit as st
import os
import numpy as np
from datetime import date
import time
import rasterio
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from backend.analysis import analyze_direction
import gdown
import zipfile

DATASET_ZIP = "dataset.zip"
DATASET_FOLDER = "dataset_images_MP_2_masks"

FILE_ID = "1TIGtuseO6Gju4Ltdkk200I7rsV6fdmBl"
URL = f"https://drive.google.com/uc?id={FILE_ID}"

# Download dataset only if not present
if not os.path.exists(DATASET_FOLDER):
    print("Downloading dataset from Google Drive...")
    gdown.download(URL, DATASET_ZIP, quiet=False)

    print("Extracting dataset...")
    with zipfile.ZipFile(DATASET_ZIP, 'r') as zip_ref:
        zip_ref.extractall()

    print("Dataset ready!")
# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Directional Analysis of Water Bodies",
    page_icon="🌊",
    layout="wide"
)

BASE_DIR = "dataset_images_MP_2_masks"

if "result" not in st.session_state:
    st.session_state.result = None

# ---------------- STYLING ----------------
st.markdown("""
<style>
.block-container {
    padding-top: 1.0rem !important;
}

h1 {
    margin-top: 0rem !important;
}
.card {
    padding:20px;
    border-radius:15px;
    background-color:#111f33;
    box-shadow: 0 0 15px rgba(0,212,255,0.15);
    margin-bottom:20px;
}
.section-title {
    font-size:14px;
    color:#9fb3c8;
    letter-spacing:1px;
}
.metric-box {
    background: linear-gradient(145deg, rgba(0,229,255,0.06), rgba(0,229,255,0.02));
    border: 1px solid rgba(0,229,255,0.25);
    padding: 18px;
    border-radius: 14px;
    margin-bottom: 15px;
    backdrop-filter: blur(6px);
    box-shadow: 0 0 18px rgba(0,229,255,0.08);
}

.metric-title {
    font-size: 13px;
    color: #9fb3c8;
    margin-bottom: 6px;
}

.metric-value {
    font-size: 28px;
    color: white;
    font-weight: 600;
}
.direction-text {
    text-align:center;
    font-size:22px;
    color:#00D4FF;
    font-weight:bold;
}
.shift-text {
    text-align:center;
    font-size:14px;
    color:#9fb3c8;
}

 /* Timelapse card container */
.timelapse-container {
    background: linear-gradient(145deg, #111827, #0E1624);
    padding: 16px;
    border-radius: 12px;
    border: 1px solid rgba(0,255,255,0.08);
    margin-bottom: 10px;
}

/* Timelapse title */
.timelapse-title {
    color: #00E5FF;
    margin: 0;
    font-size: 14px;
}

/* Reduce extra vertical spacing */
.timelapse-container h3 {
    margin: 0;
}
</style>
""", unsafe_allow_html=True)


# ---------------- HEADER ----------------
st.markdown("""
<h1 style='text-align:center; color:#00D4FF;'>
 Directional Analysis of Water Bodies
</h1>
""", unsafe_allow_html=True)

st.markdown("---")

# ---------------- GLOBAL COMPASS FUNCTION ----------------
def draw_compass(deg):

    fig = go.Figure()

    angle = np.deg2rad(deg)

    # ---- Outer Ring ----
    fig.add_shape(
        type="circle",
        x0=-1, y0=-1,
        x1=1, y1=1,
        line=dict(color="#00E5FF", width=4),
    )

    # ---- Inner Fill ----
    fig.add_shape(
        type="circle",
        x0=-0.95, y0=-0.95,
        x1=0.95, y1=0.95,
        line=dict(color="rgba(0,0,0,0)"),
        fillcolor="#0E2233"
    )

    # ---- Needle Tip ----
    tip_x = 0.8 * np.sin(angle)
    tip_y = 0.8 * np.cos(angle)

    # ---- Needle Base Width ----
    base_left_x = 0.08 * np.sin(angle + np.pi/2)
    base_left_y = 0.08 * np.cos(angle + np.pi/2)

    base_right_x = 0.08 * np.sin(angle - np.pi/2)
    base_right_y = 0.08 * np.cos(angle - np.pi/2)

    # ---- Sharp Triangle Needle ----
    fig.add_shape(
        type="path",
        path=f"""
        M {base_left_x},{base_left_y}
        L {tip_x},{tip_y}
        L {base_right_x},{base_right_y}
        Z
        """,
        fillcolor="#00E5FF",
        line=dict(color="#00E5FF")
    )

    # ---- Back Needle (Grey) ----
    fig.add_shape(
        type="path",
        path=f"""
        M {-base_left_x},{-base_left_y}
        L {-0.6*tip_x},{-0.6*tip_y}
        L {-base_right_x},{-base_right_y}
        Z
        """,
        fillcolor="rgba(255,255,255,0.2)",
        line=dict(color="rgba(255,255,255,0.2)")
    )

    # ---- Center Hub ----
    fig.add_trace(go.Scatter(
        x=[0],
        y=[0],
        mode="markers",
        marker=dict(size=12, color="#00E5FF"),
        showlegend=False,
        hoverinfo="skip"
    ))

    # ---- Direction Labels ----
    directions = {
        "N": (0, 0.85),
        "NE": (0.6, 0.6),
        "E": (0.85, 0),
        "SE": (0.6, -0.6),
        "S": (0, -0.85),
        "SW": (-0.6, -0.6),
        "W": (-0.85, 0),
        "NW": (-0.6, 0.6),
    }

    for label, (x, y) in directions.items():
        fig.add_annotation(
            x=x, y=y,
            text=f"<b>{label}</b>",
            showarrow=False,
            font=dict(color="white", size=14)
        )

    fig.update_layout(
        width=350,
        height=350,
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor="#0E1624",
        plot_bgcolor="#0E1624",
        xaxis=dict(visible=False, range=[-1, 1]),
        yaxis=dict(visible=False, range=[-1, 1], scaleanchor="x"),
        showlegend=False   # 🔥 removes trace0, trace1, trace2
    )

    return fig

# ---------------- MAIN LAYOUT ----------------
left, right = st.columns([1.2, 2])

# ==========================================================
# ================= LEFT PANEL =============================
# ==========================================================
with left:

    # ================= INPUT SECTION =================
    st.markdown("### Input Parameters")

    locations_list = [
        folder for folder in os.listdir(BASE_DIR)
        if os.path.isdir(os.path.join(BASE_DIR, folder))
    ]

    location = st.selectbox("Location", locations_list)

    from_date = st.date_input(
        "From Date",
        min_value=date(2019, 1, 1),
        max_value=date(2025, 12, 31)
    )

    to_date = st.date_input(
        "To Date",
        min_value=date(2019, 1, 1),
        max_value=date(2025, 12, 31)
    )

    if st.button("Run Analysis", use_container_width=True):
        with st.spinner("Analyzing..."):
            result = analyze_direction(
                location,
                from_date.strftime("%d/%m/%Y"),
                to_date.strftime("%d/%m/%Y")
            )
            st.session_state.result = result

    # ==========================================================
    # ================= RESULTS SECTION =========================
    # ==========================================================
    if st.session_state.result:

        result = st.session_state.result

        # ---------------- AREA REPORT (Below Inputs) ----------------
        st.markdown("###  Area Report")

        st.markdown(f"""
        <div class="metric-box">
            <div class="metric-title">Initial Area (sq.km)</div>
            <div class="metric-value">{result['area1']:.3f}</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="metric-box">
            <div class="metric-title">Final Area (sq.km)</div>
            <div class="metric-value">{result['area2']:.3f}</div>
        </div>
        """, unsafe_allow_html=True)

        # ---------------- ANALYSIS ROW ----------------
        analysis_col, direction_col = st.columns([1, 1.2])

        # ================= LEFT SIDE (Change + Diff) =================
        with analysis_col:

            st.markdown("###  Change Type")

            st.success(result["change_type"])

            st.markdown("###  Area Difference")
            st.markdown(f"""
            <div class="metric-box">
                <div class="metric-title">Difference (sq.km)</div>
                <div class="metric-value">{result['area_diff']:.3f}</div>
            </div>
            """, unsafe_allow_html=True)

        # ================= RIGHT SIDE (Direction) =================
        with direction_col:

            st.markdown("### 🧭 Direction")

            direction_map = {
                "North": 0,
                "North-East": 45,
                "East": 90,
                "South-East": 135,
                "South": 180,
                "South-West": 225,
                "West": 270,
                "North-West": 315
            }

            degree = direction_map.get(result["direction"], 0)

            st.plotly_chart(draw_compass(degree), use_container_width=True)

            st.markdown(
                f"""
                <div style='text-align:center; font-size:18px; color:#00D4FF; font-weight:600;'>
                {result['direction']}
                </div>
                <div style='text-align:center; font-size:13px; color:#9fb3c8;'>
                Shift: {result['shift_meters']:.2f} meters
                </div>
                """,
                unsafe_allow_html=True
            )

# ==========================================================
# ================= RIGHT PANEL ============================
# ==========================================================
with right:

    if "result" in st.session_state and st.session_state.result:

        # ---------- TITLE ----------
        st.markdown("""
        <div class="timelapse-container">
            <h3 class="timelapse-title"> Water Body Timelapse</h3>
        </div>
        """, unsafe_allow_html=True)

        # ---------- LEGEND ----------
        st.markdown("""
        <div style="margin-bottom:15px; font-size:14px;">
        🔴 <b style="color:red;">Red</b> → Erosion &nbsp;&nbsp;&nbsp;
        🔵 <b style="color:blue;">Blue</b> → Dilation &nbsp;&nbsp;&nbsp;
        🔷 <b style="color:#00AAFF;">Light Blue</b> → Stable Water &nbsp;&nbsp;&nbsp;
        🟢 <b style="color:#BAC88C;">Green</b> → Land Area
        </div>
        """, unsafe_allow_html=True)

        # ---------- COLLECT IMAGES ----------
        all_images = []

        for year in range(from_date.year, to_date.year + 1):

            year_folder = os.path.join(
                BASE_DIR,
                location,
                f"{location}_{year}"
            )

            if not os.path.exists(year_folder):
                continue

            for file in os.listdir(year_folder):

                if file.endswith("watermask.tif"):

                    parts = file.split("_")

                    if len(parts) >= 3:
                        try:
                            file_year = int(parts[1])
                            file_month = int(parts[2])
                        except:
                            continue

                        file_date = date(file_year, file_month, 1)

                        if from_date <= file_date <= to_date:
                            full_path = os.path.join(year_folder, file)
                            all_images.append((file_date, full_path))

        all_images.sort(key=lambda x: x[0])

        if len(all_images) < 2:
            st.warning("Not enough images for selected period.")
            st.stop()

        # ---------- PLACEHOLDER ----------
        frame_placeholder = st.empty()

        import matplotlib.pyplot as plt

        # ---------- LOAD FIRST IMAGE ----------
        with rasterio.open(all_images[0][1]) as src:
            prev_mask = (src.read(1) > 0).astype(np.uint8)

        # ---------- TIMELAPSE LOOP ----------
        for file_date, path in all_images[1:]:

            with rasterio.open(path) as src:
                new_mask = (src.read(1) > 0).astype(np.uint8)

            # --- Fix Shape Mismatch ---
            if new_mask.shape != prev_mask.shape:
                min_h = min(prev_mask.shape[0], new_mask.shape[0])
                min_w = min(prev_mask.shape[1], new_mask.shape[1])
                prev_mask = prev_mask[:min_h, :min_w]
                new_mask = new_mask[:min_h, :min_w]

            h, w = prev_mask.shape
            land_color = [186, 200, 140]
            img = np.full((h, w, 3), land_color, dtype=np.uint8)

            stable = (prev_mask == 1) & (new_mask == 1)
            erosion = (prev_mask == 1) & (new_mask == 0)
            dilation = (prev_mask == 0) & (new_mask == 1)

            img[stable] = [0, 170, 255]
            img[erosion] = [255, 0, 0]
            img[dilation] = [0, 0, 255]

            fig, ax = plt.subplots(figsize=(8, 6))

            ax.imshow(img, interpolation="bilinear")
            ax.set_aspect("equal")
            ax.axis("off")

            ax.set_title(
                f"{location} - {file_date.strftime('%B %Y')}",
                fontsize=13,
                color="white",
                pad=10
            )

            fig.patch.set_facecolor("#0E1117")
            ax.set_facecolor("#0E1117")

            frame_placeholder.pyplot(fig, clear_figure=True)

            prev_mask = new_mask
            time.sleep(0.6)
        
    