# HRV Analysis Tool

A Python tool for analyzing Heart Rate Variability (HRV) metrics against normative population data.

## Overview

This tool calculates percentile rankings for HRV metrics (sdNN, RMSSD, HF) based on age and gender, using normative data from the large-scale Voss et al. (2015) study with 1,906 healthy subjects.

## Features

- **Percentile calculation** with 95% confidence intervals
- **Multiple HRV metrics**: sdNN, RMSSD, HF (High Frequency power)
- **Age/gender normative data** (ages 25-74)
- **Statistical rigor** using t-distribution for confidence intervals
- **Sample size reliability assessment**
- **Command-line and interactive modes**

## Installation

```bash
pip install scipy
```

## Usage

### Command Line
```bash
# Single metric
python hrv_analysis.py 30 male 45.0 30.0

# With HF power
python hrv_analysis.py 30 male 45.0 30.0 120.0
```

### Interactive Mode
```bash
python hrv_analysis.py
```

### Python Import
```python
from hrv_analysis import get_hrv_percentile, get_5th_percentile_value

result = get_hrv_percentile(30, 'male', 'sdNN', 45.0)
print(result)
```

## Output Example

```
For a 30-year-old male, an sdNN value of 45.0 is at the 35.2th percentile
(95% CI: 29.8-40.7th percentile)
  Sample size: n=330, Reliability: High
```

## HRV Metrics

- **sdNN**: Standard deviation of NN intervals (overall HRV)
- **RMSSD**: Root mean square of successive RR interval differences (parasympathetic activity)
- **HF**: High frequency power (0.15-0.4 Hz, vagal tone)

## Scientific Background

Based on normative data from:

> Voss A, Schroeder R, Heitmann A, Peters A, Perz S (2015) Short-Term Heart Rate Variability—Influence of Gender and Age in Healthy Subjects. PLoS ONE 10(3): e0118308. https://doi.org/10.1371/journal.pone.0118308

## Age Groups and Sample Sizes

| Age Group | Males | Females |
|-----------|-------|---------|
| 25-34     | 330   | 208     |
| 35-44     | 292   | 259     |
| 45-54     | 235   | 158     |
| 55-64     | 183   | 95      |
| 65-74     | 84    | 62      |

## License

MIT License - Feel free to use in research and clinical applications.

## Contributing

Pull requests welcome! Please include proper citations for any additional normative datasets.

## Medical Disclaimer

This tool is for research and educational purposes. Always consult healthcare professionals for medical interpretation of HRV data.