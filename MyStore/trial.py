import dotenv
import os
import africastalking


test_api="atsk_b2293b2fa35bf9639a5c5054f09b49359bd6c6100c7fe95eb270c32b1cf180397e784eb1"
dotenv.load_dotenv('.env.prod')
def trial():
    username = os.getenv('ATSK_USERNAME')
    # api = os.getenv('ATSK_API')
    api = "atsk_21364cd7cc439449ad674540dbee4914cdb8d76e2a12c9118431e05d93248b2fe333f66e"

    msg = "hey there"
    sms = africastalking.SMSService("sandbox", test_api)
    # sms = africastalking.SMSService("savanna_l", api)
    res = sms.send(msg, ["+254795058569"])

    print(res)

trial()