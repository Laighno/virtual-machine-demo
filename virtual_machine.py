import pexpect
from py_ecc import bls
from hashlib import sha256
import os
import time
from pyevt import abi, ecc, evt_link, libevt
from pyevtsdk import action, api, base, transaction, unit_test

keys = [1111,2222,3333]
pubs = [bls.privtopub(key) for key in keys]

root_key = ecc.PrivateKey.from_string(
            '5KQwrPbwdL6PhXujxW37FSSQZ1JiwsST4cqQzDeyXtP79zkvFD3')
root_pub = ecc.PublicKey.from_string(
            'EVT6MRyAjQq8ud7hVNYcfnVPJqcVpscN5So8BhtHuGYqET5GDW5CV')
# root_key = '5JFZQ7bRRuBJyh42uV5ELwswr2Bt3rfwmyEsyXAoUue18NUreAF'
# root_pub = 'EVT8CAme1QR2664bLQsVfrERBkXL3xEKsALMSfogGavaXFkaVVqR1'
url = 'https://testnet1.everitoken.io'
ecc_domain = 43
domain_name = 'virtual-machine'

api = api.Api(url)
# print(api.get_info())
TG = transaction.TrxGenerator(url=url, payer=root_pub)

# user = base.User.from_string(root_key, root_pub)

EvtAsset = base.EvtAsset
AG = action.ActionGenerator()

# newdomain = AG.new_action(
#         'newdomain', name='virtual-machine', creator=root_pub)

# trx = TG.new_trx()
# # trx.add_action(prodvote)
# trx.add_action(newdomain)
# trx.add_sign(root_key)
# trx.set_payer(root_pub.to_string())
# resp = api.push_transaction(trx.dumps())
# print(resp.content)



def verify(path):
    sigs = []
    sig_path = path+'/signatures'
    for sig_file in os.listdir(sig_path):
        if not os.path.isdir(sig_file):
            f = open(sig_path+"/"+sig_file, 'rb')
            sig = f.read()
            sigs.append(sig)
    with open(path+'/main.py','rb') as f:
        sha256obj = sha256()
        sha256obj.update(f.read())
        file_hash = sha256obj.digest()

    for pub in pubs:
        mark = 0
        for sig in sigs:
            if bls.verify(file_hash, pub, sig, bytes(ecc_domain)):
                mark =1
        if mark == 0:
            return False
    return True

def read():
    global child
    content = b''
    while(True):
        try:
            line = child.readline()
            content += line
        except:
            break
    return bytes.decode(content)

def run(path):
    if(verify(path)):
        global child
        child = pexpect.spawn('python3 -i '+path+'/main.py')
        # print(read())
        # child.readline()
        # print(process)
        global token_name
        token_name = '{}{}'.format(path, int(time.time()))
        issuetoken = AG.new_action('issuetoken', domain=domain_name, names=[
                               token_name], owner=[base.Address().set_public_key(root_pub)])

        trx = TG.new_trx()
        # trx.add_action(prodvote)
        trx.add_action(issuetoken)
        trx.add_sign(root_key)
        trx.set_payer(root_pub.to_string())
        resp = api.push_transaction(trx.dumps())
        # print(resp.content)
        # print(resp)
        if(resp.status_code == 202):
            print('token name on chain is {}'.format(token_name))
        else:
            print('data to chain fialed')
    else:
        print('authority verify faild')

def excute(cmd):
    global child
    child.sendline(cmd)
    child.readline()

    global token_name
    addmeta = AG.new_action(
        'addmeta', meta_key='cmd{}'.format(int(time.time())), meta_value=cmd, creator=base.AuthorizerRef('A', root_pub), domain=domain_name, key=token_name)
    trx = TG.new_trx()
    # trx.add_action(prodvote)
    trx.add_action(addmeta)
    trx.add_sign(root_key)
    trx.set_payer(root_pub.to_string())
    resp = api.push_transaction(trx.dumps())
    # print(resp.content)
    # print(resp)
    if(resp.status_code == 202):
        print('meta on chain in token name:{}'.format(token_name))
    else:
        print('data to chain fialed')
    print(read())

def sign(path):
    with open(path+'/main.py','rb') as f:
        sha256obj = sha256()
        sha256obj.update(f.read())
        file_hash = sha256obj.digest()
        # print(sha256obj)
        # print(file_hash)
        sig_path = path+'/signatures'

        if not os.path.exists(sig_path):
            os.makedirs(sig_path)

        for i in range(len(pubs)):
            sig = bls.sign(file_hash, keys[i], bytes(ecc_domain))
            # print(sig)
            sig_file = sig_path+'/sig{}'.format(i)
            with open(sig_file, 'wb') as sigf:
                sigf.write(sig)

# if __name__ == '__main__':
#     pass