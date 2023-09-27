import requests, hashlib

api_url = "https://payok.io/api/"

class AuthPayOk():
    def __init__(self, api_key, api_id):
        self.api_key = api_key
        self.api_id = api_id

    def Balance(self):

        data = {
            "API_KEY": self.api_key,
            "API_ID": self.api_id
        }

        response = requests.post(api_url + "balance", data=data).json()
        return response
    
    def Transaction(
            self, 
            shop: int, 
            paymant: int = None, 
            offset: int = None
        ):

        data = {
            "API_KEY": self.api_key,
            "API_ID": self.api_id,
            "shop": shop,
            "payment": paymant,
            "offset": offset
        }

        response = requests.post(api_url + "transaction", data=data).json()
        return response
    
    def PayOut(
            self, 
            payout_id: int = None, 
            offset: int = None
        ):

        data = {
            "API_KEY": self.api_key,
            "API_ID": self.api_id,
            "payout_id": payout_id,
            "offset": offset
        }

        response = requests.post(api_url + "payout", data=data).json()
        return response
            
    
    def Pay(
            self, 
            amount: float, 
            payment: str, 
            shop: int, 
            desc: str, 
            secret: str, 
            currency: str = "RUB", 
            email: str = None, 
            succes_url: str = None,
            method: str = None,
            lang: str = None,
            custom = None
        ):

        array = [str(amount), payment, str(shop), currency, desc, secret]
        sign = hashlib.md5('|'.join(array).encode('utf-8')).hexdigest()
        url = f'https://payok.io/pay?amount={amount}&payment={payment}&desc={desc}&shop={shop}&sign={sign}&email={email}&method={method}&succes_url={succes_url}&customparam={custom}'
        return url

    def POC(
            self, 
            amount: float, 
            method: str, 
            reciever: str, 
            comission_type: str, 
            sbp_bank: str, 
            webhook_url: str
        ):

        data = {
            "API_KEY": self.api_key,
            "API_ID": self.api_id,
            "amount": amount,
            "method": method,
            "reciever": reciever,
            "comission_type": comission_type,
            "sbp_bank": sbp_bank,
            "webhook_url": webhook_url
        }

        response = requests.post(api_url + "payout_create", data=data)
        return response

    