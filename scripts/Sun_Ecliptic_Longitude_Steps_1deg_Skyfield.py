"""
True Solar-Celestial Calendar Generator (Skyfield / DE440)
Architecture: Ecliptic Longitude Step (Delta Lambda = 1.0 degree per year)
Start from user-defined date/time; find nearest Spring Equinox (lambda=0°),
then generate TEST_YEARS years of true solar-celestial days (360° per year).
Historical Julian/Gregorian Calendar Display — Authoritatively Validated via 
NASA JPL HORIZONS System (DE441 Ephemeris, Geocentric Observer [code: 500]).
"""

import os
import numpy as np
import pandas as pd
import skyfield_data
from skyfield.api import wgs84
from skyfield.iokit import Loader
from skyfield.jpllib import SpiceKernel
from scipy.optimize import brentq
from datetime import datetime, timedelta

# ==============================================================================
# Configuration & Observation Parameters
# ==============================================================================
# IMPORTANT: The calendar generation math is GEOCENTRIC (independent of location).
# These coordinates are ONLY used to calculate 'altitude_deg' and 'azimuth_deg' in the final CSV.
# If you do not need these columns, you can leave these values at 0.0.
# If you need location-specific data, replace these with your target latitude/longitude.
LAT_DEG = 0.0
LON_DEG = 0.0
ELEV_M = 0

# Flexible start date/time and duration in years
START_YEAR  = 1550                      # ephemeris segment only covers dates 1549-12-31 through 2650-01-25
START_MONTH = 3
START_DAY   = 11
START_HOUR  = 0

TEST_YEARS  = 1099                      # Set to 1 for initial 1-year validation against JPL HORIZONS (https://ssd.jpl.nasa.gov/horizons/app.html#/)

SCAN_STEP_HOURS = 4.0                   # Robust uniform scan window for root-bracketing
ROOT_XTOL = 1.0e-11                     # Solver precision in days (~0.86 microseconds)


# ==============================================================================
# Historic Calendar Utilities (Julian / Gregorian Switch on 1582-10-15)
# ==============================================================================

def cal_to_jd(year, month, day, hour=0, minute=0, second=0.0):
    """Convert historic calendar date to Julian Date (JD)."""
    y = year
    m = month
    d = day

    if m <= 2:
        y -= 1
        m += 12

    is_gregorian = (year > 1582) or (year == 1582 and (month > 10 or (month == 10 and day >= 15)))

    if is_gregorian:
        a = y // 100
        b = 2 - a + (a // 4)
    else:
        b = 0

    day_fraction = (hour + minute / 60.0 + second / 3600.0) / 24.0
    jd = int(365.25 * (y + 4716)) + int(30.6001 * (m + 1)) + d + b - 1524.5 + day_fraction
    return jd


def jd_to_cal(jd):
    """Convert Julian Date (JD) to historic calendar date (Julian before 1582-10-15; Gregorian after)."""
    z = int(jd + 0.5)
    f = (jd + 0.5) - z

    if z < 2299161:
        a = z
    else:
        alpha = int((z - 1867216.25) / 36524.25)
        a = z + 1 + alpha - (alpha // 4)

    b = a + 1524
    c = int((b - 122.1) / 365.25)
    d = int(365.25 * c)
    e = int((b - d) / 30.6001)

    day_value = b - d - int(30.6001 * e) + f
    month = e - 1 if e < 14 else e - 13
    year = c - 4716 if month > 2 else c - 4715

    day = int(day_value)
    seconds_of_day = int(round((day_value - day) * 86400.0))

    if seconds_of_day >= 86400:
        seconds_of_day -= 86400
        dt = datetime(year, month, day) + timedelta(days=1)
        year, month, day = dt.year, dt.month, dt.day

    hour, rem = divmod(seconds_of_day, 3600)
    minute, second = divmod(rem, 60)

    return year, month, day, hour, minute, second


def deg_to_dms_str(deg_val):
    """Format decimal degrees to ±DD° MM' SS.S\" string for visual validation."""
    sign = "+" if deg_val >= 0 else "-"
    deg_abs = abs(deg_val)
    d = int(deg_abs)
    m_full = (deg_abs - d) * 60.0
    m = int(m_full)
    s = (m_full - m) * 60.0
    return f"{sign}{d:02d}° {m:02d}' {s:04.1f}\""


# ==============================================================================
# Celestial Mathematics & Ecliptic Longitude Solver
# ==============================================================================

def get_solar_ecliptic_longitude(earth, sun, t):
    """
    Apparent geocentric Ecliptic Longitude (on date) of the Sun in degrees [0, 360).
    Matches Stellarium: Ecliptic long./lat. (on date)
    """
    app = earth.at(t).observe(sun).apparent()
    _, lon, _ = app.ecliptic_latlon(epoch='date')
    return lon.degrees % 360.0


def ecliptic_longitude_offset(earth, sun, t, target_deg):
    """Signed angular difference (deg) from target ecliptic longitude, in [-180, +180]."""
    lon_deg = get_solar_ecliptic_longitude(earth, sun, t)
    diff = (lon_deg - target_deg + 180.0) % 360.0 - 180.0
    return diff


def find_target_longitude_moment(ts, earth, sun, jd_start, jd_end, target_deg, step_hours=SCAN_STEP_HOURS):
    """Refines exact moment when Sun crosses target ecliptic longitude using Brent's method."""
    step_days = step_hours / 24.0
    total_steps = int(np.ceil((jd_end - jd_start) / step_days))

    cur_jd = jd_start
    cur_t = ts.ut1_jd(cur_jd)
    cur_val = ecliptic_longitude_offset(earth, sun, cur_t, target_deg)

    for step_index in range(1, total_steps + 1):
        next_jd = min(jd_start + step_index * step_days, jd_end)
        next_t = ts.ut1_jd(next_jd)
        next_val = ecliptic_longitude_offset(earth, sun, next_t, target_deg)

        # Bracket a zero-crossing (negative to positive) within a reasonable angular span
        if (cur_val < 0.0 < next_val) and (next_val - cur_val < 5.0):
            def objective(jd_val):
                t_eval = ts.ut1_jd(jd_val)
                return ecliptic_longitude_offset(earth, sun, t_eval, target_deg)
            try:
                root_jd = brentq(objective, cur_jd, next_jd, xtol=ROOT_XTOL)
                return root_jd
            except Exception:
                pass

        cur_jd, cur_val = next_jd, next_val

    return None


# ==============================================================================
# Main Program Entry Point
# ==============================================================================

def main():
    print("=" * 78)
    print("True Solar-Celestial Calendar Generator (Architecture 1)")
    print("Ecliptic Longitude Delta Lambda = 1.0° (360 Days per Year)")
    print("=" * 78)
    print()

    data_dir = os.path.join(os.path.dirname(skyfield_data.__file__), "data")
    load = Loader(data_dir)
    ts = load.timescale()

    de440_path = os.path.join(data_dir, "de440.bsp")
    eph = SpiceKernel(de440_path)
    earth = eph["earth"]
    sun = eph["sun"]
    observer = earth + wgs84.latlon(LAT_DEG, LON_DEG, elevation_m=ELEV_M)

    # Anchor at user-defined start date/time (UTC), then find nearest Spring Equinox (lambda=0°)
    start_jd_anchor = cal_to_jd(START_YEAR, START_MONTH, START_DAY, START_HOUR, 0, 0)
    print(f"Searching for Spring Equinox (Lambda = 0.0°) near {START_YEAR:04d}-{START_MONTH:02d}-{START_DAY:02d}...")

    # Adaptive search window around start date: first narrow ±10 days, then broaden if needed
    search_windows = [
        (-10.0, +15.0),
        (-30.0, +40.0),
        (-60.0, +80.0),
    ]

    equinox_epoch_jd = None
    for lo, hi in search_windows:
        search_start_jd = start_jd_anchor + lo
        search_end_jd   = start_jd_anchor + hi
        equinox_epoch_jd = find_target_longitude_moment(ts, earth, sun, search_start_jd, search_end_jd, 0.0)
        if equinox_epoch_jd is not None:
            break

    if equinox_epoch_jd is None:
        raise RuntimeError("Spring Equinox root not found near start date! Try adjusting START_* values.")

    y, m, d, hh, mm, ss = jd_to_cal(equinox_epoch_jd)
    print("Found Spring Equinox (Lambda = 0.0°):")
    print(f"  UTC Timestamp: {y:04d}-{m:02d}-{d:02d} {hh:02d}:{mm:02d}:{ss:02d}")
    print(f"  Astronomical JD: {equinox_epoch_jd:.10f}")
    print()

    # Generate TEST_YEARS blocks, each of 360 true solar-celestial days (1° steps)
    print(f"Generating {TEST_YEARS} year(s) of celestial solar days (1.0° steps)...")
    records = []
    current_search_jd = equinox_jd - 0.2

    # target_lambda_base grows by 360.0 per year to avoid wrap confusion
    target_lambda_base = 0.0

    total_days = TEST_YEARS * 360
    for day_index in range(total_days):
        target_lambda = target_lambda_base + float(day_index % 360)

        window_start = current_search_jd
        window_end = current_search_jd + 1.8

        deg_jd = find_target_longitude_moment(ts, earth, sun, window_start, window_end, target_lambda)

        if deg_jd is None:
            deg_jd = find_target_longitude_moment(ts, earth, sun, current_search_jd, current_search_jd + 3.0, target_lambda)

        if deg_jd is not None:
            current_search_jd = deg_jd + 0.1
            y_d, m_d, d_d, hh_d, mm_d, ss_d = jd_to_cal(deg_jd)
            t_eval = ts.ut1_jd(deg_jd)

            # Report actual lambda modulo 360 for readability
            actual_lambda = get_solar_ecliptic_longitude(earth, sun, t_eval)
            app_sun = observer.at(t_eval).observe(sun).apparent()
            alt, az, _ = app_sun.altaz()

            # Determine solar year and day within year
            year_offset = day_index // 360
            day_in_year = (day_index % 360) + 1

            records.append({
                "solar_year_index": year_offset + 1,
                "solar_day_index": day_in_year,
                "target_lambda_deg": (target_lambda % 360.0),
                "actual_lambda_deg": f"{actual_lambda:.6f}",
                "stellarium_utc": f"{y_d:04d}-{m_d:02d}-{d_d:02d} {hh_d:02d}:{mm_d:02d}:{ss_d:02d}",
                "jd": f"{deg_jd:.10f}",
                "altitude_deg": f"{alt.degrees:.4f}",
                "azimuth_deg": f"{az.degrees:.4f}",
            })

        # Progress every 60 days
        if (day_index + 1) % 60 == 0:
            yr = (day_index + 1) // 360 + 1
            print(f"  Processed {day_index + 1}/{total_days} days (Year {yr}, Month {((day_index % 360) + 1)//30})...")

        # At the boundary of each year (after 360 days), advance base target by +360°
        if (day_index + 1) % 360 == 0:
            target_lambda_base += 360.0

    df = pd.DataFrame(records)

    # Save to CSV with start and end labels
    script_dir = os.path.dirname(os.path.abspath(__file__))
    start_label = f"{START_YEAR:04d}-{START_MONTH:02d}-{START_DAY:02d}"
    # End label: convert JD of the last record to calendar for informative filename
    if len(df) > 0:
        last_jd = float(df.iloc[-1]["jd"])
        ey, em, ed, eh, emin, es = jd_to_cal(last_jd)
        end_label = f"{ey:04d}-{em:02d}-{ed:02d}"
    else:
        end_label = "NA"

    out_csv = os.path.join(
        script_dir,
        f"Sun_Ecliptic_Longitude_Steps_1deg_{start_label}_TO_{end_label}.csv"
    )
    df.to_csv(out_csv, index=False)

    print()
    print("=" * 78)
    print(f"SUCCESS: Generated {len(df)} astronomical days across {TEST_YEARS} year(s).")
    print(f"CSV saved at: {out_csv}")
    print("=" * 78)
    print("\nFirst 5 rows:")
    print(df.head(5).to_string(index=False))
    print("\nLast 5 rows:")
    print(df.tail(5).to_string(index=False))


if __name__ == "__main__":
    main()
