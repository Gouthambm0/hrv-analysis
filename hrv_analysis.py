import scipy.stats as st
import sys
import math

def get_hrv_percentile(age: int, gender: str, hrv_metric: str, user_value: float) -> str:
    """
    Calculates the percentile of a user's HRV value based on age and gender
    using normative data from Voss et al. (2015) study with statistical rigor.

    This function provides:
    - Percentile ranking relative to healthy population
    - 95% confidence intervals using t-distribution
    - Sample size and reliability assessment
    - Warnings for small sample sizes

    Args:
        age (int): The user's age in years (must be 25-74).
        gender (str): The user's gender ('male' or 'female').
        hrv_metric (str): The HRV metric to analyze ('sdNN', 'RMSSD', or 'HF'). Case-insensitive.
        user_value (float): The user's measured value for the HRV metric.

    Returns:
        str: Formatted result containing:
            - Percentile ranking with 95% confidence interval
            - Sample size (n) and reliability assessment
            - Warnings for small sample sizes (n < 100)

    Raises:
        ValueError: If age is outside 25-74 range or invalid gender.
        KeyError: If HRV metric is not available for the specified group.

    Example:
        >>> result = get_hrv_percentile(30, 'male', 'sdNN', 50.0)
        >>> print(result)
        For a 30-year-old male, an sdNN value of 50.0 is at the 50.2th percentile
        (95% CI: 45.9-54.5th percentile)
          Sample size: n=330, Reliability: High

    References:
        Voss A, Schroeder R, Heitmann A, Peters A, Perz S (2015) Short-Term Heart
        Rate Variability—Influence of Gender and Age in Healthy Subjects. PLoS ONE
        10(3): e0118308. https://doi.org/10.1371/journal.pone.0118308
    """
    # Normative data from Voss et al. (2015) study
    # 1,906 healthy subjects from KORA S4 study (782 females, 1,124 males)
    # Data includes mean ± SD for each metric and sample size (n) per group
    hrv_norms = {
        'female': {
            '25-34': {
                'sdNN': {'mean': 45.4, 'sd': 18.0},
                'RMSSD': {'mean': 36.1, 'sd': 18.4},
                'HF': {'mean': 161, 'sd': 167},
                'n': 208
            },
            '35-44': {
                'sdNN': {'mean': 42.1, 'sd': 16.8},
                'RMSSD': {'mean': 30.7, 'sd': 15.1},
                'HF': {'mean': 121, 'sd': 145},
                'n': 259
            },
            '45-54': {
                'sdNN': {'mean': 36.6, 'sd': 14.7},
                'RMSSD': {'mean': 24.5, 'sd': 12.3},
                'HF': {'mean': 62, 'sd': 83},
                'n': 158
            },
            '55-64': {
                'sdNN': {'mean': 32.2, 'sd': 13.5},
                'RMSSD': {'mean': 20.3, 'sd': 10.8},
                'HF': {'mean': 35, 'sd': 53},
                'n': 95
            },
            '65-74': {
                'sdNN': {'mean': 31.6, 'sd': 13.6},
                'RMSSD': {'mean': 19.4, 'sd': 10.1},
                'HF': {'mean': 29, 'sd': 38},
                'n': 62
            }
        },
        'male': {
            '25-34': {
                'sdNN': {'mean': 49.9, 'sd': 19.8},
                'RMSSD': {'mean': 36.2, 'sd': 18.1},
                'HF': {'mean': 133, 'sd': 174},
                'n': 330
            },
            '35-44': {
                'sdNN': {'mean': 44.8, 'sd': 18.1},
                'RMSSD': {'mean': 30.6, 'sd': 15.4},
                'HF': {'mean': 89, 'sd': 118},
                'n': 292
            },
            '45-54': {
                'sdNN': {'mean': 41.3, 'sd': 17.6},
                'RMSSD': {'mean': 26.8, 'sd': 13.7},
                'HF': {'mean': 41, 'sd': 49},
                'n': 235
            },
            '55-64': {
                'sdNN': {'mean': 38.3, 'sd': 17.0},
                'RMSSD': {'mean': 23.4, 'sd': 12.0},
                'HF': {'mean': 29, 'sd': 38},
                'n': 183
            },
            '65-74': {
                'sdNN': {'mean': 34.9, 'sd': 15.9},
                'RMSSD': {'mean': 21.1, 'sd': 11.0},
                'HF': {'mean': 22, 'sd': 29},
                'n': 84
            }
        }
    }

    # Determine the correct age group
    if 25 <= age <= 34:
        age_group = '25-34'
    elif 35 <= age <= 44:
        age_group = '35-44'
    elif 45 <= age <= 54:
        age_group = '45-54'
    elif 55 <= age <= 64:
        age_group = '55-64'
    elif 65 <= age <= 74:
        age_group = '65-74'
    else:
        return "Error: Age is outside the study's range (25-74 years)."

    # Validate gender input
    gender = gender.lower()
    if gender not in ['male', 'female']:
        return "Error: Gender must be 'male' or 'female'."

    # Normalize metric name (handle case variations)
    metric_mapping = {
        'sdnn': 'sdNN',
        'rmssd': 'RMSSD', 
        'hf': 'HF'
    }
    normalized_metric = metric_mapping.get(hrv_metric.lower(), hrv_metric)
    
    # Retrieve the data for the specified group and metric
    try:
        group_data = hrv_norms[gender][age_group]
        metric_data = group_data[normalized_metric]
        mean = metric_data['mean']
        sd = metric_data['sd']
        n = group_data['n']
    except KeyError:
        return (f"Error: The metric '{hrv_metric}' is not available for the "
                f"{gender} {age_group} age group in this script. "
                f"Please add it from the source paper.")

    if sd == 0:
        return "Error: Standard deviation is zero, cannot calculate percentile."

    # Calculate the Z-score
    z_score = (user_value - mean) / sd

    # Calculate the percentile from the Z-score using the cumulative distribution function (CDF)
    percentile = st.norm.cdf(z_score) * 100

    # Calculate confidence interval for the percentile estimate
    # Standard error of the mean
    sem = sd / math.sqrt(n)
    
    # For 95% confidence interval, use t-distribution
    df = n - 1
    t_critical = st.t.ppf(0.975, df)  # 97.5th percentile for 95% CI
    
    # Confidence interval for the mean
    ci_lower_mean = mean - t_critical * sem
    ci_upper_mean = mean + t_critical * sem
    
    # Calculate percentiles using confidence interval bounds
    z_lower = (user_value - ci_upper_mean) / sd  # More conservative lower bound
    z_upper = (user_value - ci_lower_mean) / sd  # More conservative upper bound
    
    percentile_lower = st.norm.cdf(z_lower) * 100
    percentile_upper = st.norm.cdf(z_upper) * 100
    
    # Reliability assessment based on sample size
    if n < 50:
        reliability = "Low"
    elif n < 100:
        reliability = "Moderate"
    elif n < 200:
        reliability = "Good"
    else:
        reliability = "High"
    
    # Format the enhanced output
    result = (f"For a {age}-year-old {gender}, an {hrv_metric} value of {user_value} "
              f"is at the {percentile:.1f}th percentile "
              f"(95% CI: {percentile_lower:.1f}-{percentile_upper:.1f}th percentile)\n"
              f"  Sample size: n={n}, Reliability: {reliability}")
    
    # Add warning for small sample sizes
    if n < 100:
        result += f"\n  ⚠️  Warning: Small sample size may affect reliability"
    
    return result


def get_5th_percentile_value(age: int, gender: str, hrv_metric: str) -> float:
    """Calculate the HRV value at the 5th percentile for given age/gender group"""
    hrv_norms = {
        'female': {
            '25-34': {'sdNN': {'mean': 45.4, 'sd': 18.0}, 'RMSSD': {'mean': 36.1, 'sd': 18.4}, 'HF': {'mean': 161, 'sd': 167}},
            '35-44': {'sdNN': {'mean': 42.1, 'sd': 16.8}, 'RMSSD': {'mean': 30.7, 'sd': 15.1}, 'HF': {'mean': 121, 'sd': 145}},
            '45-54': {'sdNN': {'mean': 36.6, 'sd': 14.7}, 'RMSSD': {'mean': 24.5, 'sd': 12.3}, 'HF': {'mean': 62, 'sd': 83}},
            '55-64': {'sdNN': {'mean': 32.2, 'sd': 13.5}, 'RMSSD': {'mean': 20.3, 'sd': 10.8}, 'HF': {'mean': 35, 'sd': 53}},
            '65-74': {'sdNN': {'mean': 31.6, 'sd': 13.6}, 'RMSSD': {'mean': 19.4, 'sd': 10.1}, 'HF': {'mean': 29, 'sd': 38}}
        },
        'male': {
            '25-34': {'sdNN': {'mean': 49.9, 'sd': 19.8}, 'RMSSD': {'mean': 36.2, 'sd': 18.1}, 'HF': {'mean': 133, 'sd': 174}},
            '35-44': {'sdNN': {'mean': 44.8, 'sd': 18.1}, 'RMSSD': {'mean': 30.6, 'sd': 15.4}, 'HF': {'mean': 89, 'sd': 118}},
            '45-54': {'sdNN': {'mean': 41.3, 'sd': 17.6}, 'RMSSD': {'mean': 26.8, 'sd': 13.7}, 'HF': {'mean': 41, 'sd': 49}},
            '55-64': {'sdNN': {'mean': 38.3, 'sd': 17.0}, 'RMSSD': {'mean': 23.4, 'sd': 12.0}, 'HF': {'mean': 29, 'sd': 38}},
            '65-74': {'sdNN': {'mean': 34.9, 'sd': 15.9}, 'RMSSD': {'mean': 21.1, 'sd': 11.0}, 'HF': {'mean': 22, 'sd': 29}}
        }
    }
    
    if 25 <= age <= 34: age_group = '25-34'
    elif 35 <= age <= 44: age_group = '35-44'
    elif 45 <= age <= 54: age_group = '45-54'
    elif 55 <= age <= 64: age_group = '55-64'
    elif 65 <= age <= 74: age_group = '65-74'
    else: return None
    
    gender = gender.lower()
    metric_mapping = {'sdnn': 'sdNN', 'rmssd': 'RMSSD', 'hf': 'HF'}
    normalized_metric = metric_mapping.get(hrv_metric.lower(), hrv_metric)
    
    try:
        data = hrv_norms[gender][age_group][normalized_metric]
        z_score_5th = st.norm.ppf(0.05)
        percentile_5th_value = data['mean'] + (z_score_5th * data['sd'])
        # Ensure the value is not negative for HRV metrics
        return max(0, percentile_5th_value)
    except KeyError:
        return None


def get_normative_range(age: int, gender: str, hrv_metric: str) -> str:
    """Calculate the normative range using 5th-95th percentiles for given age/gender group"""
    hrv_norms = {
        'female': {
            '25-34': {'sdNN': {'mean': 45.4, 'sd': 18.0}, 'RMSSD': {'mean': 36.1, 'sd': 18.4}, 'HF': {'mean': 161, 'sd': 167}},
            '35-44': {'sdNN': {'mean': 42.1, 'sd': 16.8}, 'RMSSD': {'mean': 30.7, 'sd': 15.1}, 'HF': {'mean': 121, 'sd': 145}},
            '45-54': {'sdNN': {'mean': 36.6, 'sd': 14.7}, 'RMSSD': {'mean': 24.5, 'sd': 12.3}, 'HF': {'mean': 62, 'sd': 83}},
            '55-64': {'sdNN': {'mean': 32.2, 'sd': 13.5}, 'RMSSD': {'mean': 20.3, 'sd': 10.8}, 'HF': {'mean': 35, 'sd': 53}},
            '65-74': {'sdNN': {'mean': 31.6, 'sd': 13.6}, 'RMSSD': {'mean': 19.4, 'sd': 10.1}, 'HF': {'mean': 29, 'sd': 38}}
        },
        'male': {
            '25-34': {'sdNN': {'mean': 49.9, 'sd': 19.8}, 'RMSSD': {'mean': 36.2, 'sd': 18.1}, 'HF': {'mean': 133, 'sd': 174}},
            '35-44': {'sdNN': {'mean': 44.8, 'sd': 18.1}, 'RMSSD': {'mean': 30.6, 'sd': 15.4}, 'HF': {'mean': 89, 'sd': 118}},
            '45-54': {'sdNN': {'mean': 41.3, 'sd': 17.6}, 'RMSSD': {'mean': 26.8, 'sd': 13.7}, 'HF': {'mean': 41, 'sd': 49}},
            '55-64': {'sdNN': {'mean': 38.3, 'sd': 17.0}, 'RMSSD': {'mean': 23.4, 'sd': 12.0}, 'HF': {'mean': 29, 'sd': 38}},
            '65-74': {'sdNN': {'mean': 34.9, 'sd': 15.9}, 'RMSSD': {'mean': 21.1, 'sd': 11.0}, 'HF': {'mean': 22, 'sd': 29}}
        }
    }
    
    if 25 <= age <= 34: age_group = '25-34'
    elif 35 <= age <= 44: age_group = '35-44'
    elif 45 <= age <= 54: age_group = '45-54'
    elif 55 <= age <= 64: age_group = '55-64'
    elif 65 <= age <= 74: age_group = '65-74'
    else: return None
    
    gender = gender.lower()
    metric_mapping = {'sdnn': 'sdNN', 'rmssd': 'RMSSD', 'hf': 'HF'}
    normalized_metric = metric_mapping.get(hrv_metric.lower(), hrv_metric)
    
    try:
        data = hrv_norms[gender][age_group][normalized_metric]
        mean = data['mean']
        sd = data['sd']
        
        # Calculate 5th and 95th percentiles using normal distribution
        z_5th = st.norm.ppf(0.05)   # -1.645
        z_95th = st.norm.ppf(0.95)  # 1.645
        
        percentile_5th = mean + (z_5th * sd)
        percentile_95th = mean + (z_95th * sd)
        
        # For physiologically meaningful metrics, ensure lower bound is reasonable
        # RMSSD and HF should not start at zero in healthy populations
        if normalized_metric in ['RMSSD', 'HF']:
            # Use a minimum threshold based on measurement precision
            min_threshold = 1.0 if normalized_metric == 'RMSSD' else 5.0
            percentile_5th = max(min_threshold, percentile_5th)
        else:
            # For sdNN, zero is theoretically possible but practically very rare
            percentile_5th = max(0.1, percentile_5th)
        
        return f"{hrv_metric} normative range (5th-95th percentile): {percentile_5th:.1f} - {percentile_95th:.1f}"
    except KeyError:
        return None


if __name__ == '__main__':
    # Check if command line arguments are provided
    if len(sys.argv) >= 5:
        try:
            age = int(sys.argv[1])
            gender = sys.argv[2]
            sdnn_value = float(sys.argv[3])
            rmssd_value = float(sys.argv[4])
            
            print("HRV Percentile Calculator")
            print("=" * 25)
            
            # Calculate for sdNN
            result1 = get_hrv_percentile(age, gender, 'sdNN', sdnn_value)
            print(result1)
            
            # Calculate for RMSSD
            result2 = get_hrv_percentile(age, gender, 'RMSSD', rmssd_value)
            print(result2)
            
            # Calculate for HF if provided
            if len(sys.argv) >= 6:
                hf_value = float(sys.argv[5])
                result3 = get_hrv_percentile(age, gender, 'HF', hf_value)
                print(result3)
            
            print("\n5th Percentile Values:")
            print("-" * 25)
            sdnn_5th = get_5th_percentile_value(age, gender, 'sdNN')
            rmssd_5th = get_5th_percentile_value(age, gender, 'RMSSD')
            hf_5th = get_5th_percentile_value(age, gender, 'HF')
            
            if sdnn_5th: print(f"sdNN 5th percentile: {sdnn_5th:.1f}")
            if rmssd_5th: print(f"RMSSD 5th percentile: {rmssd_5th:.1f}")
            if hf_5th: print(f"HF 5th percentile: {hf_5th:.1f}")
            
            
        except ValueError:
            print("Error: Please provide valid numeric values")
            print("Usage: python3 hrv_analysis.py <age> <gender> <sdNN> <RMSSD> [HF]")
        except Exception as e:
            print(f"An error occurred: {e}")
    else:
        # Interactive mode
        print("HRV Percentile Calculator")
        print("=" * 25)
        print("Usage: python3 hrv_analysis.py <age> <gender> <sdNN> <RMSSD> [HF]")
        print("Or run without arguments for interactive mode\n")
        
        try:
            # Get user input
            age = int(input("Enter your age (25-74): "))
            gender = input("Enter your gender (male/female): ").strip()
            
            print("\nAvailable HRV metrics: sdNN, RMSSD, HF")
            print("You can enter multiple metrics (press Enter after each one, type 'done' when finished)")
            
            metrics_to_calculate = []
            
            while True:
                metric = input("Enter HRV metric name (or 'done' to finish): ").strip()
                if metric.lower() == 'done':
                    break
                
                if metric:
                    try:
                        value = float(input(f"Enter your {metric} value: "))
                        metrics_to_calculate.append((metric, value))
                    except ValueError:
                        print("Invalid value. Please enter a number.")
                        continue
            
            if not metrics_to_calculate:
                print("No metrics entered. Exiting.")
                exit()
            
            print("\nResults:")
            print("-" * 50)
            
            # Calculate percentiles for all entered metrics
            for metric, value in metrics_to_calculate:
                result = get_hrv_percentile(age, gender, metric, value)
                print(result)
            
            print("\n5th Percentile Values:")
            print("-" * 25)
            sdnn_5th = get_5th_percentile_value(age, gender, 'sdNN')
            rmssd_5th = get_5th_percentile_value(age, gender, 'RMSSD')
            hf_5th = get_5th_percentile_value(age, gender, 'HF')
            
            if sdnn_5th: print(f"sdNN 5th percentile: {sdnn_5th:.1f}")
            if rmssd_5th: print(f"RMSSD 5th percentile: {rmssd_5th:.1f}")
            if hf_5th: print(f"HF 5th percentile: {hf_5th:.1f}")
            
                
        except ValueError:
            print("Invalid input. Please enter valid numbers for age and HRV values.")
        except KeyboardInterrupt:
            print("\nExiting...")
        except Exception as e:
            print(f"An error occurred: {e}")
