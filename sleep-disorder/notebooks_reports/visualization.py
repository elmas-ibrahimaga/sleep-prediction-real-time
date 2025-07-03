import pandas as pd
import matplotlib.pyplot as plt

# Load metrics data
metrics_df = pd.read_csv("notebooks_reports/model_metrics.csv")  # Now load from notebooks_reports

# Plotting the metrics
plt.figure(figsize=(10, 6))
metrics_df.set_index("Model").plot(kind='bar', alpha=0.7)
plt.title("Model Performance Metrics")
plt.ylabel("Scores")
plt.xlabel("Models")
plt.xticks(rotation=45)
plt.legend(loc='upper left')
plt.tight_layout()

# Save figure under notebooks_reports
plt.savefig('notebooks_reports/model_metrics_plot.png')
print("✅ Model performance plot saved at notebooks_reports/model_metrics_plot.png")
