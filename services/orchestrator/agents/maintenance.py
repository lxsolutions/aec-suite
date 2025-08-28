




import numpy as np
from datetime import datetime, timedelta

def analyze_sensor_data(sensor_readings: dict):
    """Analyze sensor data for maintenance predictions."""

    # Example structure:
    # readings = {
    #     "temperature": [20.5, 21.3, 19.8],  # recent values
    #     "humidity": [45, 50, 47],
    #     "structural_integrity": [96.2, 95.8, 96.0]
    # }

    alerts = []
    maintenance_needs = []

    current_time = datetime.now()

    for sensor_type, values in sensor_readings.items():
        mean_value = np.mean(values)
        std_dev = np.std(values)

        if sensor_type == "temperature":
            if mean_value > 25 or std_dev > 3:
                alerts.append(f"Temperature anomalies detected (avg: {mean_value:.1f}°C)")
                maintenance_needs.append({
                    "sensor": sensor_type,
                    "issue": "Potential HVAC malfunction",
                    "recommended_action": "Inspect cooling systems"
                })

        elif sensor_type == "humidity":
            if mean_value > 60 or std_dev > 5:
                alerts.append(f"Humidity levels are high (avg: {mean_value:.1f}%)")
                maintenance_needs.append({
                    "sensor": sensor_type,
                    "issue": "Moisture buildup risk",
                    "recommended_action": "Check ventilation systems"
                })

        elif sensor_type == "structural_integrity":
            if mean_value < 95:
                alerts.append(f"Structural integrity below threshold (avg: {mean_value:.1f}%)")
                maintenance_needs.append({
                    "sensor": sensor_type,
                    "issue": "Potential structural weakness",
                    "recommended_action": "Schedule immediate inspection"
                })

    # Predict next maintenance window
    last_maintenance = datetime.now() - timedelta(days=90)  # Assume last was 3 months ago
    days_since_last = (current_time - last_maintenance).days

    if days_since_last > 120:
        maintenance_needs.append({
            "sensor": "general",
            "issue": "Routine maintenance overdue",
            "recommended_action": "Schedule comprehensive inspection"
        })

    return {
        "analysis_date": current_time.strftime("%Y-%m-%d %H:%M"),
        "alerts": alerts,
        "maintenance_needs": maintenance_needs,
        "sensor_statistics": {k: {"mean": np.mean(v), "std_dev": np.std(v)} for k, v in sensor_readings.items()}
    }

if __name__ == "__main__":
    # Example usage with mock data
    sample_data = {
        "temperature": [20.5, 21.3, 19.8],
        "humidity": [45, 50, 47],
        "structural_integrity": [96.2, 95.8, 96.0]
    }

    result = analyze_sensor_data(sample_data)
    print(f"Maintenance analysis: {result}")



