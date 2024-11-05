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

def get_name_data(email, password):
    """
    Extract full name from Garmin Connect with specified fields only.
    """
    try:
        print("Attempting to connect to Garmin...")
        client = Garmin(email, password)
        client.login()
        print("Successfully logged in to Garmin Connect")

        full_name = client.full_name
        print(full_name)
        
        return full_name

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

    name_df = get_name_data(
        email=email,
        password=password,
    )

    #if name_df is not None:
        #output_file = 'garmin_name_data.csv'
        #name_df.to_csv(output_file, index=False)
        #print(f"\nName data saved to {output_file}")