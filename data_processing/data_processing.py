import pandas as pd
import matplotlib.pyplot as plt
import os

# Define the path to your CSV file
csv_file = 'sensor_data_up.csv'

# Check if the file exists
if not os.path.exists(csv_file):
    raise FileNotFoundError(f"The file {csv_file} does not exist.")

# Extract the elbow_angle name of the CSV file (without extension) for naming
base_name = os.path.splitext(os.path.basename(csv_file))[0]

# Read the CSV data into a pandas DataFrame
# Specify the delimiter to match the actual file format
df = pd.read_csv(csv_file, delimiter=',')

# Display the first few rows to verify proper reading
print("First few rows of the data:")
print(df.head())

# Check if 'pressing_id' column exists
if 'pressing_id' not in df.columns:
    raise ValueError("The CSV file must contain a 'pressing_id' column.")

# Get unique pressing IDs
pressing_ids = df['pressing_id'].unique()
print(f"Unique pressing_ids found: {pressing_ids}")

# Create a directory to save plots, using the elbow_angle name of the CSV file
plots_dir = f'{base_name}_plots'
os.makedirs(plots_dir, exist_ok=True)

# Iterate over each pressing_id and create plots
for pid in pressing_ids:
    # Filter data for the current pressing_id
    df_pid = df[df['pressing_id'] == pid]

    # Ensure there is data for this pressing_id
    if df_pid.empty:
        print(f"No data found for pressing_id {pid}. Skipping.")
        continue

    # Sort the data by timestamp to ensure the line plot follows the sequence
    df_pid = df_pid.sort_values(by='timestamp')

    # Plot settings
    plt.figure(figsize=(10, 6))

    # Scatter plot: timestamp vs ax (you can choose other axes as needed)
    plt.scatter(df_pid['timestamp'], df_pid['ax'], label='ax', color='white')

    # Line plot: connecting the scatter points
    plt.plot(df_pid['timestamp'], df_pid['ax'], color='white', linestyle='-', alpha=0.7)

    # Optionally, plot other axes (ay, az, gx, gy, gz) similarly
    plt.scatter(df_pid['timestamp'], df_pid['ay'], label='ay', color='green')
    plt.plot(df_pid['timestamp'], df_pid['ay'], color='green', linestyle='-', alpha=0.7)

    plt.scatter(df_pid['timestamp'], df_pid['az'], label='az', color='red')
    plt.plot(df_pid['timestamp'], df_pid['az'], color='red', linestyle='-', alpha=0.7)

    plt.scatter(df_pid['timestamp'], df_pid['gx'], label='gx', color='purple')
    plt.plot(df_pid['timestamp'], df_pid['gx'], color='purple', linestyle='-', alpha=0.7)

    plt.scatter(df_pid['timestamp'], df_pid['gy'], label='gy', color='orange')
    plt.plot(df_pid['timestamp'], df_pid['gy'], color='orange', linestyle='-', alpha=0.7)

    plt.scatter(df_pid['timestamp'], df_pid['gz'], label='gz', color='brown')
    plt.plot(df_pid['timestamp'], df_pid['gz'], color='brown', linestyle='-', alpha=0.7)

    # Customize the plot
    plt.title(f'Sensor Data for Pressing ID {pid}')
    plt.xlabel('Timestamp (ms)')
    plt.ylabel('Sensor Values')
    plt.legend()
    plt.grid(True)

    # Save the plot to the designated directory
    plot_filename = os.path.join(plots_dir, f'{base_name}_pressing_id_{pid}.png')
    plt.savefig(plot_filename)
    plt.close()

    print(f"Plot saved for pressing_id {pid} as {plot_filename}")

print(f"All plots have been saved in the '{plots_dir}' directory.")