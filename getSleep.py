import os
import requests
import json
from datetime import datetime, timedelta
import pandas as pd
import sys
from dotenv import load_dotenv
from garminconnect import (
    Garmin,
    GarminConnectConnectionError,
    GarminConnectTooManyRequestsError,
    GarminConnectAuthenticationError
)

load_dotenv()

def get_sleep_data(email, password, start_date=None, end_date=None):
    """
    Extract sleep data from Garmin Connect with specified fields only.
    """
    try:
        print("Attempting to connect to Garmin...")
        client = Garmin(email, password)
        client.login()
        print("Successfully logged in to Garmin Connect")

        if not end_date:
            end_date = datetime.now().date()
        else:
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()

        if not start_date:
            start_date = end_date - timedelta(days=7)
        else:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()

        print(f"Fetching sleep data from {start_date} to {end_date}")

        all_sleep_data = []
        current_date = start_date

        while current_date <= end_date:
            try:
                print(f"\nFetching data for {current_date}...")
                sleep_data = client.get_sleep_data(current_date.strftime('%Y-%m-%d'))

                if sleep_data and 'dailySleepDTO' in sleep_data:
                    daily_sleep_dto = sleep_data['dailySleepDTO']

                    # Convert timestamps to datetime
                    start_time = datetime.fromtimestamp(
                        daily_sleep_dto['sleepStartTimestampLocal'] / 1000
                    ) if daily_sleep_dto.get('sleepStartTimestampLocal') else None

                    end_time = datetime.fromtimestamp(
                        daily_sleep_dto['sleepEndTimestampLocal'] / 1000
                    ) if daily_sleep_dto.get('sleepEndTimestampLocal') else None

                    daily_sleep = {
                        'date': current_date.strftime('%Y-%m-%d'),
                        'total_sleep': daily_sleep_dto.get('sleepTimeSeconds', 0) / 3600,
                        'sleep_score': daily_sleep_dto.get('sleepScores', {}).get('overall', {}).get('value'),
                        'start_time': start_time.strftime('%Y-%m-%d %H:%M:%S') if start_time else None,
                        'end_time': end_time.strftime('%Y-%m-%d %H:%M:%S') if end_time else None,
                        'resting_heart_rate': sleep_data.get('restingHeartRate'),
                        'avg_hrv': sleep_data.get('avgOvernightHrv'),
                        'sleep_quality': daily_sleep_dto.get('sleepScores', {}).get('overall', {}).get('qualifierKey')
                    }

                    print(f"Processed sleep data: {daily_sleep}")
                    all_sleep_data.append(daily_sleep)
                else:
                    print(f"No valid sleep data for {current_date}")

            except Exception as e:
                print(f"Error getting data for {current_date}: {str(e)}")
                import traceback
                print(traceback.format_exc())

            current_date += timedelta(days=1)

        print("\nCreating DataFrame...")
        df = pd.DataFrame(all_sleep_data)

        if not df.empty:
            print("\nFinal DataFrame head:")
            print(df.head())
        else:
            print("\nWarning: DataFrame is empty - no sleep data was processed")

        return df

    except GarminConnectAuthenticationError:
        print("Authentication failed - check your email and password")
    except GarminConnectTooManyRequestsError:
        print("Too many requests - please wait a while before trying again")
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        print(traceback.format_exc())

    return None

if __name__ == "__main__":
    # Get email and password from environment variables
    email = os.getenv('GARMIN_EMAIL')
    password = os.getenv('GARMIN_PASSWORD')

    if not email or not password:
        print("Error: GARMIN_EMAIL and GARMIN_PASSWORD environment variables must be set.")
        sys.exit(1)

    sleep_df = get_sleep_data(
        email=email,
        password=password,
        start_date=(datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
    )

    if sleep_df is not None:
        output_file = 'garmin_sleep_data.csv'
        sleep_df.to_csv(output_file, index=False)
        print(f"\nSleep data saved to {output_file}")