import requests

class BaiDuApi:
    def __init__(self):
        app_id:str
        api_key:str
        secret_key:str

    

class TextSpeech(BaiDuApi):
    
    def __init__(self):
        self.app_id = "38959150"
        self.api_key = "qORBO3CNyKAvsdjrLc3tKgyW"
        self.secret_key = "ZXlf9DxjvzDv6rSFmWYbswaGFB0zmPCV"

    def text2speech(self, text:str) :
        url = "https://aip.baidubce.com/oauth/2.0/token?client_id=qORBO3****3tKgyW&client_secret=ZXlf9D****0zmPCV&grant_type=client_credentials"
    
        payload = json.dumps("")
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        response = requests.request("POST", url, headers=headers, data=payload)
        
        print(response.text)
