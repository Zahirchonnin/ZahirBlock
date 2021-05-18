import json

def dump(txn):
    for k, v in txn.items():
        if isinstance(v, bytes):
            txn[k] = list(v)
        
    return (json.dumps(txn)).encode()


def load(acc):
    acc = json.loads(acc)
    for k, v in acc.items():
        if isinstance(v, list):
            acc[k] = bytes(v)
            
    return acc