import pexpect
from py_ecc import bls
from hashlib import sha256
import os

keys = [1111,2222,3333]
pubs = [bls.privtopub(key) for key in keys]

domain = 43

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
            if bls.verify(file_hash, pub, sig, bytes(domain)):
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
        print(child.readline())
        # print(process)
    else:
        print('authority verify faild')

def excute(cmd):
    global child
    child.sendline(cmd)
    child.readline()
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
            sig = bls.sign(file_hash, keys[i], bytes(domain))
            # print(sig)
            sig_file = sig_path+'/sig{}'.format(i)
            with open(sig_file, 'wb') as sigf:
                sigf.write(sig)

# if __name__ == '__main__':
#     pass