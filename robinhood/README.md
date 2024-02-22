To setup robinhood API:

Start by going to Robinhood App and change from SMS 2FA to Authenticator
Create a .env file that looks like this:
robin_username = <your_email>
robin_password=<your_password>
robin_mfa=<The code that robinhood gives when enabling 2FA>

Click continue in robinhood APP

Then run the code
```
python3 robinhood/main.py
```