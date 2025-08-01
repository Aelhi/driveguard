import psycopg2
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


class SleepDatabase:
    """
    A class that connects to a local PostgreSQL database. Allowing for input of timestamps and generation of trend data visuals
    """

    # Initialize SleepDatabase
    def __init__(self):
        """
        Initializes the SleepDatabase object

        Establishes a connection to the PostgreSQL database and creates a table if not already available

        :return None
        """
        # The following connection variables are dependent on your local machine and can be found in pg Admin for Postgresql - PLEASE CHANGE ACCORDINGLY
        self.connection = psycopg2.connect(
            host="localhost", 
            dbname="DriveGuard", 
            user="postgres", 
            password="Eliahjose30!", 
            port=5432
            )
        
        self.cursor = self.connection.cursor() # Connect to database cursor for executable actions
        self.create_table()


    # Creates a table in the PostgreSQL database if there is none existing
    def create_table(self):
        """
        Executes creation of a "driver_asleep" table in the PostgreSQL database

        Table consists of 1 attribute: Timestamp

        :return None
        """
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS driver (
                    driver_asleep TIMESTAMP PRIMARY KEY
                    );
                    """)


    # Takes a timestamp of when the person fell asleep and uploads it onto the database
    def take_sleep_timestamp(self):
        """
        Takes a timestamp of the person falling asleep and insterts into the PostgreSQL database

        Uses datetime to store the timestamp and pushes the changes

        :return None
        """
        timestamp = datetime.now() # Stores current timestamp

        self.cursor.execute("""INSERT INTO driver (driver_asleep) VALUES
                (%s)
                """, (timestamp,))
        self.connection.commit() # Pushes changes to database


    # Returns the most common hour that a person falls asleep and displays it in a window
    def most_common_sleep_hour(self):
        """
        Parses through the database to calculate the most frequent sleep hour

        Generates a matplot visualization showing both hour and the frequency

        :return None
        """
        self.cursor.execute("""SELECT EXTRACT(HOUR FROM driver_asleep) AS sleep_hour, COUNT(*) AS frequency
                    FROM driver
                    GROUP BY sleep_hour
                    ORDER BY frequency DESC
                    LIMIT 1;
                    """)
        result = self.cursor.fetchone() # Assigns a tuple with the most common sleep hour and the frequency of the hour
        
        if result: # Checks if the query was successful
            # Unpacking the tuple for the hour and the frequency
            sleep_hour = result[0]
            frequency = result[1]
            
            # Create matplotlib window to display the result
            plt.figure(figsize=(8, 6))
            plt.text(0.5, 0.6, f"Most Common Sleep Hour: {int(sleep_hour):02d}:00", 
                    fontsize=24, ha='center', va='center', weight='bold')
            plt.text(0.5, 0.4, f"Frequency: {frequency} occurrences", 
                    fontsize=16, ha='center', va='center')
            plt.xlim(0, 1)
            plt.ylim(0, 1)
            plt.axis('off')
            plt.title("Driver Sleep Analysis", fontsize=18, weight='bold', pad=20)
            plt.show()
        else:
            # Create matplotlib window in case of no data
            plt.figure(figsize=(8, 6))
            plt.text(0.5, 0.5, "No sleep records found", 
                    fontsize=20, ha='center', va='center', color='red')
            plt.xlim(0, 1)
            plt.ylim(0, 1)
            plt.axis('off')
            plt.title("Driver Sleep Analysis", fontsize=18, weight='bold', pad=20)
            plt.show() 


    # Creates a plot of sleep trends
    def plot_sleep_trend(self):
        """
        Creates and displays a bar chart with a trendline to show driver sleep trends throughout a day

        Based on military time

        :return None
        """
        # Fetch all timestamps
        self.cursor.execute("""
            SELECT driver_asleep FROM driver;
        """)
        rows = self.cursor.fetchall()

        # In case of no data to be displayed on a chart
        if not rows:
            print("No sleep data to display.")
            return

        # Prepare DataFrame and extract hour component only (0-23)
        df = pd.DataFrame(rows, columns=['timestamp'])
        df['hour'] = df['timestamp'].dt.hour  # Extract just the hour (0-23)

        # Count frequency per hour
        sleep_counts = df['hour'].value_counts().sort_index()

        # Create complete hour range (0-23) with zeros for missing hours
        full_hours = pd.Series(0, index=range(24))
        full_hours.update(sleep_counts)
        
        # X = hours (0-23), Y = counts
        x_hours = full_hours.index
        y = full_hours.values

        # Plot bar chart
        plt.figure(figsize=(14, 6))
        plt.bar(x_hours, y, width=0.8, color='skyblue', edgecolor='black', label="Sleep Count (per hour)")

        # Plot linear trendline if enough data
        if len(sleep_counts) >= 2:  # Need at least 2 points for linear fit
            z = np.polyfit(x_hours, y, 1)
            p = np.poly1d(z)
            trendline_y = p(x_hours)
            
            # Ensure trendline doesn't go below zero
            trendline_y = np.maximum(trendline_y, 0)
            
            plt.plot(x_hours, trendline_y, "r--", linewidth=2, label="Trendline")

        # Formatting
        plt.title("Driver Sleep Frequency by Hour")
        plt.xlabel("Hour (24-hour format)")
        plt.ylabel("Sleep Occurrences")
        
        # Set x-axis to show all 24 hours
        plt.xlim(-0.5, 23.5)
        plt.xticks(range(0, 24, 2))  # Show every 2 hours: 0, 2, 4, 6, ..., 22
        
        plt.grid(True, alpha=0.3)
        plt.legend()
        plt.tight_layout()
        plt.show()


    # Closes connection to database
    def close_connection(self):
        """
        Closes the connection to the PostgreSQL database

        :return None
        """
        self.cursor.close()
        self.connection.close()
