import requests
import json
from datetime import datetime, timedelta
import pandas as pd
import os
import sys
from garminconnect import (
    Garmin,
    GarminConnectConnectionError,
    GarminConnectTooManyRequestsError,
    GarminConnectAuthenticationError
)


def get_sleep_data(email, password, start_date=None, end_date=None):
    """
    Extract sleep data from Garmin Connect with corrected data structure parsing.
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
                        'deep_sleep': daily_sleep_dto.get('deepSleepSeconds', 0) / 3600,
                        'light_sleep': daily_sleep_dto.get('lightSleepSeconds', 0) / 3600,
                        'rem_sleep': daily_sleep_dto.get('remSleepSeconds', 0) / 3600,
                        'awake_time': daily_sleep_dto.get('awakeSleepSeconds', 0) / 3600,
                        'sleep_score': daily_sleep_dto.get('sleepScores', {}).get('overall', {}).get('value'),
                        'start_time': start_time.strftime('%Y-%m-%d %H:%M:%S') if start_time else None,
                        'end_time': end_time.strftime('%Y-%m-%d %H:%M:%S') if end_time else None,
                        'resting_heart_rate': sleep_data.get('restingHeartRate'),
                        'avg_stress': daily_sleep_dto.get('avgSleepStress'),
                        'body_battery_change': sleep_data.get('bodyBatteryChange'),
                        'avg_hrv': sleep_data.get('avgOvernightHrv'),
                        'awake_count': daily_sleep_dto.get('awakeCount'),
                        'sleep_quality': daily_sleep_dto.get('sleepScores', {}).get('overall', {}).get('qualifierKey'),
                        'average_respiration': daily_sleep_dto.get('averageRespirationValue'),
                        'lowest_respiration': daily_sleep_dto.get('lowestRespirationValue'),
                        'highest_respiration': daily_sleep_dto.get('highestRespirationValue'),
                        'restless_moments': sleep_data.get('restlessMomentsCount')
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
            # Add calculated columns
            df['sleep_efficiency'] = (df['deep_sleep'] + df['light_sleep'] + df['rem_sleep']) / df['total_sleep'] * 100
            df['deep_sleep_percentage'] = df['deep_sleep'] / df['total_sleep'] * 100
            df['rem_sleep_percentage'] = df['rem_sleep'] / df['total_sleep'] * 100

            # Replace NaN values with 0 for numeric columns
            numeric_columns = ['sleep_efficiency', 'deep_sleep_percentage', 'rem_sleep_percentage']
            df[numeric_columns] = df[numeric_columns].fillna(0)

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
    email = os.environ.get('GARMIN_EMAIL')
    password = os.environ.get('GARMIN_PASSWORD')

    sleep_df = get_sleep_data(
        email=email,
        password=password,
        start_date=(datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    )

    if sleep_df is not None:
        output_file = 'garmin_sleep_data.csv'
        sleep_df.to_csv(output_file, index=False)
        print(f"\nSleep data saved to {output_file}")
