# Rainfall Erosivity Monitor (REM)
**Web Application for Monitoring Rainfall Erosivity and Soil Erosion Alerts**

---

## Overview

The **Rainfall Erosivity Monitor (REM)** is a Streamlit-based web application for real-time monitoring of rainfall erosivity and soil erosion risk assessment. It uses precipitation data from GeoSphere Austria weather stations to calculate the EI30 erosivity index and provide field survey recommendations.

### Key Features

- **Real-time Data**: Fetches precipitation data from TAWES weather stations and INCA grid
- **EI30 Calculation**: Computes rainfall erosivity index using USLE/RUSLE2 methodology
- **Storm Detection**: Automatic delineation of erosive storm events
- **Alert System**: Color-coded risk levels (green/yellow/orange/red)
- **Field Survey Recommendations**: Automatic recommendations based on recent erosive events
- **Interactive Map**: Station locations with erosivity indicators
- **Multi-language**: German and English interface

---

## Installation

### Requirements

- Python 3.10+
- See `requirements.txt` for dependencies

### Setup

```bash
# Clone the repository
git clone https://github.com/EdbertoLima/rainfall-erosivity-monitor.git
cd rainfall-erosivity-monitor

# Install dependencies
pip install -r requirements.txt

# Run the application
streamlit run app/weather_app.py
```

---

## Project Structure

```
rainfall-erosivity-monitor/
├── app/
│   └── weather_app.py      # Main Streamlit application
├── assets/
│   └── BAW Research.png    # Logo
├── data/
│   └── messstellen_nlv.csv # Station metadata
├── lambda/
│   └── lambda_function.py  # AWS Lambda alerter (optional)
├── requirements.txt
├── LICENSE
└── README.md
```

---

## Usage

1. **Select Data Source**: Choose between TAWES stations, Klima v2, or INCA grid
2. **Set Location**: Enter coordinates or use default (Kaindorf, Austria)
3. **Select Date Range**: Choose the time period to analyze
4. **Fetch Data**: Click to retrieve precipitation data
5. **Review Results**: Check erosivity values, alerts, and field survey recommendations

---

## Methodology

The application implements the USLE/RUSLE rainfall erosivity methodology:

- **Storm Delineation**: 6-hour gap with < 1.27 mm separates storms (Wischmeier & Smith, 1978)
- **Erosive Threshold**: Storms with ≥ 12.7 mm total or ≥ 6 mm in 15 min
- **Energy Equations**:
  - RUSLE2: e = 0.29[1 - 0.72 exp(-0.082 i)] (McGregor et al., 1995)
  - USLE: e = 0.119 + 0.0873 log₁₀(i), capped at 0.283 (Wischmeier & Smith, 1978)

---

## Related Projects

- [Erosion Survey QField](https://github.com/EdbertoLima/erosion-survey-qfield) - Field guide for soil erosion mapping with QField (DWA-M-921)

---

## References

- Nearing, M.A., Yin, S., Borrelli, P., Polyakov, V.O. (2017). Rainfall erosivity: An historical review. *Catena*, 157, 357–362.
- Wischmeier, W.H., Smith, D.D. (1978). Predicting rainfall erosion losses. *USDA Agriculture Handbook* No. 537.
- McGregor, K.C., Bingner, R.L., Bowie, A.J., Foster, G.R. (1995). Erosivity index values for northern Mississippi. *Trans. ASAE*, 38(4), 1039–1047.

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Contact

**BAW Research**

Pollnbergstraße 1
3252 Petzenkirchen
Austria

Email: [research@baw.at](mailto:research@baw.at)
