import os
import numpy as np
import cv2
import math
import rasterio
from datetime import datetime
from rasterio.warp import reproject, Resampling

BASE_DIR = "dataset_images_MP_2_masks"


# ---------------- DATE ----------------
def extract_year(date_string):
    date_obj = datetime.strptime(date_string, "%d/%m/%Y")
    return date_obj.year


# ---------------- FILE ----------------
def get_watermask_path(location, year):
    folder_path = os.path.join(BASE_DIR, location, f"{location}_{year}")

    for file in os.listdir(folder_path):
        if file.endswith("watermask.tif"):
            return os.path.join(folder_path, file)

    raise FileNotFoundError(f"No watermask found for {location} {year}")


# ---------------- LOAD & ALIGN ----------------
def load_masks(location, from_year, to_year):

    path1 = get_watermask_path(location, from_year)
    path2 = get_watermask_path(location, to_year)

    with rasterio.open(path1) as src1:
        mask1 = src1.read(1)
        transform1 = src1.transform
        crs1 = src1.crs
        height1 = src1.height
        width1 = src1.width

    with rasterio.open(path2) as src2:
        mask2 = src2.read(1)
        transform2 = src2.transform
        crs2 = src2.crs
        bounds = src2.bounds

    mask1 = (mask1 > 0).astype(np.uint8)
    mask2 = (mask2 > 0).astype(np.uint8)

    aligned_mask2 = np.zeros((height1, width1), dtype=np.uint8)

    reproject(
        source=mask2,
        destination=aligned_mask2,
        src_transform=transform2,
        src_crs=crs2,
        dst_transform=transform1,
        dst_crs=crs1,
        resampling=Resampling.nearest
    )

    return mask1, aligned_mask2, bounds


# ---------------- AREA ----------------
def compute_area(mask, pixel_resolution=10):
    pixel_area = pixel_resolution ** 2
    water_pixels = np.sum(mask == 1)
    total_area_m2 = water_pixels * pixel_area
    return total_area_m2 / 1e6


def detect_change(mask1, mask2, pixel_resolution=10):
    area1 = compute_area(mask1, pixel_resolution)
    area2 = compute_area(mask2, pixel_resolution)

    diff = area2 - area1

    if diff > 0:
        change_type = "Dilated"
    elif diff < 0:
        change_type = "Eroded"
    else:
        change_type = "No Significant Change"

    return change_type, area1, area2, diff


# ---------------- CENTROID ----------------
def compute_centroid(mask):
    contours, _ = cv2.findContours(
        mask.astype(np.uint8),
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )

    if len(contours) == 0:
        return None

    largest = max(contours, key=cv2.contourArea)
    M = cv2.moments(largest)

    if M["m00"] == 0:
        return None

    cx = M["m10"] / M["m00"]
    cy = M["m01"] / M["m00"]

    return np.array([cx, cy])


# ---------------- DIRECTION ----------------
def vector_to_direction(dx, dy):
    angle = math.degrees(math.atan2(-dy, dx))

    compass = [
        ("East", -22.5, 22.5),
        ("North-East", 22.5, 67.5),
        ("North", 67.5, 112.5),
        ("North-West", 112.5, 157.5),
        ("West", 157.5, 180),
        ("West", -180, -157.5),
        ("South-West", -157.5, -112.5),
        ("South", -112.5, -67.5),
        ("South-East", -67.5, -22.5)
    ]

    for name, low, high in compass:
        if low <= angle < high:
            return name

    return "Unknown"


# ---------------- MASTER FUNCTION ----------------
def analyze_direction(location, from_date, to_date, pixel_resolution=10):

    from_year = extract_year(from_date)
    to_year = extract_year(to_date)

    mask1, mask2, bounds = load_masks(location, from_year, to_year)

    change_type, area1, area2, area_diff = detect_change(
        mask1, mask2, pixel_resolution
    )

    c1 = compute_centroid(mask1)
    c2 = compute_centroid(mask2)

    if c1 is None or c2 is None:
        return None

    dx = c2[0] - c1[0]
    dy = c2[1] - c1[1]

    pixel_shift = np.sqrt(dx**2 + dy**2)
    meter_shift = pixel_shift * pixel_resolution
    direction = vector_to_direction(dx, dy)

    return {
        "area1": area1,
        "area2": area2,
        "change_type": change_type,
        "area_diff": area_diff,
        "shift_meters": meter_shift,
        "direction": direction,
        "mask2": mask2,
        "bounds": bounds
    }
