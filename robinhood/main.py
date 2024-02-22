import os

import pyotp
import robin_stocks.robinhood as r
from dotenv import load_dotenv
'''
This is an example script that will automatically log you in with two factor authentication.
This script also adds security by using dotenv to store credentials in a safe .env file.
To use this script, create a new file in the same directory with the name ".env" and
put all your credentials in the file. An example is in github named ".test.env".

OR, you can explicitly providing path to ".env"
>>>from pathlib import Path  # Python 3.6+ only
>>>env_path = Path(".") / put the path to the ".env" file here instead of the "."
>>>load_dotenv(dotenv_path=env_path)

Note: must have two factor turned on in robinhood app. README on github has info on
how to do that.
'''
load_dotenv()
print(os.environ['robin_mfa'])
totp = pyotp.TOTP(os.environ['robin_mfa']).now()
login = r.login(os.environ['robin_username'],
                os.environ['robin_password'], store_session=False, mfa_code=totp)

positions_data = r.profiles.load_account_profile()
print(positions_data)
print(r.stocks.get_earnings( "AAPL"))