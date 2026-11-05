# Samavi Solar Annual Calendar

## An Astronomical Research Model Based on Apparent Geocentric Ecliptic Longitude Solar Transits

**Official Project Webpage:** [https://1866universe.github.io/samavi-annual-calendar-solar/](https://1866universe.github.io/samavi-annual-calendar-solar/)

Leveraging an observational ephemeris dataset encompassing **395,461 precision orbital transit points**, this system enables the computation, tracking, and visualization of calendar data across an epoch of **1,100 astronomical years** (equivalent to 1,098 civil calendar years and 10 days). The temporal coverage spans from **1550-03-11 to 2348-03-20 Gregorian**, corresponding to **0928-12-20 to 2026-12-30 Solar Hijri (Jalali)**, and **0001-01-01 to 1100-01-01 Samavi Solar**.

---

### Foundations and Temporal Philosophy

The Samavi Calendar is an investigative computational astronomy model designed to quantify and structure time directly from the physical dynamics of celestial mechanics. In this framework, time is not treated as a rigid conventional unit of uniform intervals (such as administrative divisions, fixed 24-hour mean solar days, or arbitrary month lengths). Instead, time measurement is strictly governed by the instantaneous position of the physical center of the Sun in **Apparent Geocentric Ecliptic Longitude**.

- **Definition of the Samavi Day (1° Arc Steps):** Each Samavi Day represents the exact transit duration required for the Sun to traverse 1 degree of arc along its apparent ecliptic path. The epoch reference point (0°) aligns precisely with the Vernal Equinox. Days are indexed and traversed continuously from 0° to 359°. The 360° boundary resets identically to 0°, marking the onset of the subsequent orbital cycle.
- **Definition of the Samavi Month (30° Arc Steps):** Each Samavi Month corresponds to the Sun traversing a discrete 30-degree segment of the ecliptic.
- **Definition of the Samavi Year (360° Orbital Cycle):** A Samavi Year comprises 12 uniform astronomical months of 30 orbital days each (totaling 360 orbital steps).

This 360-day continuum is not an arbitrary conventional approximation; it represents the 12 spatial 30-degree stations across Earth's complete orbital circuit. Because Earth's orbit around the Sun is elliptical (in accordance with Kepler's Laws of Planetary Motion), the Sun's apparent angular velocity varies continuously throughout the year (accelerating near perihelion in January and decelerating near aphelion in July). Consequently, the actual physical duration of each 1-degree transit fluctuates, producing an authentic, non-linear, quasi-sinusoidal wave pattern across real daily durations over the course of an astronomical year.

---

## Comparative Overview of Conventional Calendar Month Structures

To contextualize the architecture of the Samavi Calendar, consider the structural mechanics of three primary civil calendar frameworks:

### 1. Gregorian Calendar

The Gregorian calendar is a solar calendar with 12 months and approximately 365 days per year:

- **31-Day Months:** January (1), March (3), May (5), July (7), August (8), October (10), December (12)
- **30-Day Months:** April (4), June (6), September (9), November (11)
- **February (2):** 28 days in common years; 29 days in leap years.
- **Annual Length:** 365 days in common years; 366 days in leap years.

### 2. Hijri Shamsi (Jalali) Calendar

The Hijri Shamsi calendar is a solar calendar with 12 months, whose beginning is aligned with the vernal equinox (Nowruz):

- **31-Day Months:** The first half of the year: Farvardin (1) through Shahrivar (6).
- **30-Day Months:** Mehr (7) through Bahman (11).
- **Esfand (12):** 29 days in common years; 30 days in leap years.
- **Annual Length:** 365 days in common years; 366 days in leap years.

### 3. Hijri Qamari Calendar

The Hijri Qamari calendar is an observation-based lunar calendar based on the Moon’s orbital motion, consisting of 12 months and approximately 354 days per year. In computational systems (conventional/tabular), months alternate between 30 and 29 days:

- **30-Day Months:** Muharram (1), Rabi' al-Awwal (3), Jumada al-Awwal (5), Rajab (7), Ramadan (9), Dhu al-Qi'dah (11).
- **29-Day Months:** Safar (2), Rabi' al-Thani (4), Jumada al-Thani (6), Sha'ban (8), Shawwal (10).
- **Dhu al-Hijjah (12):** 29 days in common years; 30 days in tabular leap years.
- **Annual Length:** 354 days in common years; 355 days in leap years.

### Distinctive Computational Paradigm of the Samavi Calendar

> *"In the Samavi Calendar, all metrics are derived solely from physical transit events and precise observational epochs of celestial bodies. Time progression is quantified by real physical transit durations between discrete ecliptic coordinates, rather than invariant 24-hour metric divisions."*

As a direct consequence, two analytical intervals having identical day counts may not contain identical cumulative temporal minutes. This variance stems from celestial dynamics and orbital eccentricity, wherein orbital velocity varies along different segments of the ellipse.

---

### Core Analytical Capabilities

- **Comparative Astronomical Analysis:** Direct analysis of true solar kinematics, enabling simultaneous multi-system synchronization across Solar Hijri, Gregorian, Lunar Hijri, and Samavi Solar calendars.
- **Local Diurnal Solar Ephemeris Engine:** High-precision computation of the 11 diurnal solar transitions (astronomical, nautical, and civil dawn; sunrise; solar noon; sunset; civil, nautical, and astronomical dusk; and apparent solar midnight) computed for user-defined geographic coordinates.
- **Continuous Orbital Duration Tracking & Dynamic Charts:** Real-time visibility into daily solar duration variations, providing an empirical perspective on seasonal progression and temporal stretching via dynamic charts and analytical tables.
- **True Physical Interval Calculator:** High-fidelity calculation of exact physical intervals between historical and future astronomical epochs derived from actual solar transit data.

---

### Epoch Reference Point of the Samavi Solar Calendar

The Samavi Solar Calendar originates from a definitive astronomical reference epoch. This point serves as the invariant zero-epoch ($T_0$) for the day-counting continuum, from which all subsequent and historical dates are computed.

- The fundamental origin is anchored as follows:

| Calendar System | Date & Time Representation |
| :--- | :--- |
| **Samavi Solar Epoch** | `0001-01-01 06:03:58 (Saturday) UTC` |
| **Gregorian Equivalent** | `1550-03-11 06:03:58 UTC` |
| **Solar Hijri Equivalent** | `0928-12-20 06:03:58 UTC` |
| **Lunar Hijri Equivalent** | `0957-02-11 06:03:58 UTC` |

This instant establishes the baseline coordinate. All 395,461 transit records across the 1,100-year epoch maintain strict orbital and mathematical continuity anchored to this common reference.

---

## Computational Engine & Data Integrity

All ephemeris coordinates and transit timestamps are computed using high-precision numerical integration from the **NASA JPL DE440 Development Ephemeris** via the **Skyfield** astrometry runtime library. The underlying Python generator scripts are provided in the [`scripts/`](scripts/) directory for independent verification, peer review, and reproducibility.

---

## Downloads and Release Assets

Official release distributions, Excel application workbooks, and pre-compiled data packages are available under the **Assets** section of GitHub Releases.

**Release Repository:** [Download Samavi Solar Calendar Datasets & Application Packages](https://github.com/1866universe/samavi_annual_calendar_solar/releases)

[نسخه فارسی راهنما (Persian README)](README_FA.md)

---

1866Universe 1405 ©
