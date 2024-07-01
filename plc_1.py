import random
from sqlalchemy import create_engine, Table, MetaData, Column, Float, DateTime
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from sklearn.linear_model import LinearRegression
import numpy as np

# Define the connection string
server = "AKSHAT_PATIL"
database = "PLC"
connection_string = f"mssql+pyodbc://{server}/{database}?driver=ODBC+Driver+17+for+SQL+Server"

# Create the engine
engine = create_engine(connection_string, echo=True)

# Create a connection
with engine.connect() as connection:
    # Define metadata
    metadata = MetaData()

    # Define the table structure
    tbl = Table(
        'TBL',
        metadata,
        Column('Value', Float),
        Column('Time_1', DateTime)
    )

    # Create the table
    metadata.create_all(connection)

    # Initialize lists to store values and corresponding times for plotting
    values = []
    times = []
    predicted_values_list = []  # New list to store predicted values

    # Create a figure and axis for the plot
    fig, ax = plt.subplots()

    # Function to predict the next value based on historical values
    def predict_next_value(values):
        X = np.arange(1, len(values)).reshape(-1, 1)
        y = np.array(values[:-1])

        model = LinearRegression().fit(X, y)

        next_X = np.array([[len(values)]])
        predicted_value = model.predict(next_X)

        # Ensure the predicted value is within the range [0, 50]
        return min(max(predicted_value[0], 0), 50)

    # Function to insert random values with corresponding time every 2 seconds
    def insert_random_values(i):
        global values, times, predicted_values_list

        value = random.uniform(0, 50)  # Generate a random float between 0 and 50
        current_time = datetime.now()

        # Insert values into the database
        with engine.connect() as new_connection:
            new_connection.execute(tbl.insert().values(Value=value, Time_1=current_time))
            new_connection.commit()  # Commit the changes to the database
            print(f"Inserted value: {value} at time: {current_time}")

        # Update the lists
        values.append(value)
        times.append(current_time)

        # Keep the last 10 values for the plot
        values = values[-10:]
        times = times[-10:]

        # Plot the updated values
        ax.clear()
        ax.plot(times, values, marker='o', linestyle='-', color='b', label='Actual Values')

        # Plot the predicted values
        if len(values) > 1:
            predicted_value = predict_next_value(values)
            predicted_values_list.append(predicted_value)
            ax.plot(times[-1], predicted_value, marker='x', linestyle='-', color='r', label='Predicted Values')

            # Display the predicted value near the graph
            ax.text(times[-1], predicted_value, f'Predicted Value: {predicted_value:.2f}', fontsize=8, color='r')

            # Display the actual value near the graph
            ax.text(times[-1], values[-1], f'Actual Value: {values[-1]:.2f}', fontsize=8, color='b')

        # Plot the line for predicted values
        if len(predicted_values_list) > 1:
            ax.plot(times[-2:], predicted_values_list[-2:], linestyle='-', color='r', alpha=0.5)

        # Plot the dotted line for the average of actual values
        if len(values) > 1:
            average_value = np.mean(values)
            ax.axhline(y=average_value, linestyle='--', color='g', label='Average Value')

        ax.set_xlabel('Time')
        ax.set_ylabel('Value')
        ax.set_title('Real-time Plot of Values with Predictions')
        ax.legend()
        plt.pause(0.1)  # Pause to allow the plot to update

    # Use FuncAnimation to continuously update the plot
    animation = FuncAnimation(fig, insert_random_values, interval=2000, save_count=10)

    plt.show()  # Display the plot

    # To stop the animation when you manually stop the execution
    try:
        while True:
            pass
    except KeyboardInterrupt:
        pass
    finally:
        animation.event_source.stop()
        plt.close()
