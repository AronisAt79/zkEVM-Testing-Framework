from scripts.rpcUtils import rpcCall
from pprint import pprint

def proof_request(proverUrl,block,sourceURL,retry,param="/testnet/"):
    '''
    Sends a proof_request for selected block, Set the retry boolean to false if: you just need the proof status
    or to invoke a new proof generation without the option to retry in case of failure
    '''

    data = f'{{"jsonrpc":"2.0", "method":"proof", "params":[{{"block":{block},"rpc":"{sourceURL}", "retry":{retry}, "param": "{param}"}}], "id":{block}}}'
    # pprint(data)
    url=proverUrl
    response = rpcCall(url,data)
    return response

def queryProverTasks(proverUrl, id=1):
    data=f'{{"jsonrpc":"2.0", "method":"info", "params":[], "id":{id}}}'
    # pprint(data)
    url=proverUrl
    response = rpcCall(url,data)
    return response

def flushTasks(proverUrl,cache,pending,completed, id):
    cache=str(cache).lower()
    pending=str(cache).lower()
    completed=str(cache).lower()
    data = f'{{"jsonrpc":"2.0", "method":"flush", "params":[{{"cache":{cache},"pending":{pending}, "completed":{completed}}}],"id":{id}}}'
    pprint(data)
    url=proverUrl
    response = rpcCall(url,data)
    return response

