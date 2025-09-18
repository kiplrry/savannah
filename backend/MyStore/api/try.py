from africastalking import SMSService

username = "sandbox"  
api_key = "atsk_d3f46aedbb15f5d45ea9f15470ef5bbfa5f5b0082fd28550542e2e11911d1cbbc37cad2e"
api_key = "atsk_48f0ff67325d0927e492db153ce362cee97d4a8c7e166a681d44a991ef44bfc2328e2dfa"

sms = SMSService(username, api_key)

try:
    response = sms.send("Hello from AT API", ["+254795058569"])
    print(response)
except Exception as e:
    print("Error sending SMS:", e)