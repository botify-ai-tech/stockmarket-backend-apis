from kiteconnect import KiteConnect

#@timing_decorator
def setup_kite()->KiteConnect:
    kite = KiteConnect(api_key="vo2ciygkrkvlph31")
    return kite


kite_connect = setup_kite()
# https://kite.zerodha.com/connect/login?api_key=vo2ciygkrkvlph31&v=3
data = kite_connect.generate_session("FLwuXSgk7SqYnMwNFpX0S7mOWDGuD19S", api_secret="xcxfii8nxjkuq7hb57ies2k4zwqyx9sv")
print(data['access_token'])
