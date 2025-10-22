import datetime
import hashlib
import json
import os
import time

from cbor2 import dumps
from secp256k1Crypto import PublicKey, PrivateKey
from django.http import HttpResponse
from django.db import IntegrityError, transaction

from apps.device_verify.models import Device
from apps.redeem_codes.models import Address, Campaign


 

enc_key = os.environ['DEVICE_VERIFICATION_SIGN_KEY']

state = {
  "dev_auth_init": 1,
  "dev_auth_device": 2,
  "dev_auth_server": 3
}

keys = {
  "dev_auth_device": 1,
  "device_id": 2,
  "first_auth": 3,
  "auth_time": 4,
  "auth_count": 5,
  "challenge": 6,
  "signature": 7
}

def _verify_signature(uid, challenge, signature, public_key):
  m = hashlib.sha256()
  public_key = PublicKey(bytes(bytearray.fromhex(public_key)), raw=True)

  m.update(bytes(bytearray.fromhex(uid)))
  m.update(bytes(bytearray.fromhex(challenge)))
  h = m.digest()
  _, sig = public_key.ecdsa_signature_normalize(public_key.ecdsa_deserialize_compact(bytes(bytearray.fromhex(signature))))

  return public_key.ecdsa_verify(h, sig, raw=True)

def _success(device, challenge, mess, redeem_code=None):
  m = hashlib.sha256()

  verification_date = time.mktime(datetime.datetime.utcnow().timetuple())
  first_verification = time.mktime(device.verification_start_date.timetuple())

  vd_32 = int(verification_date).to_bytes(4, 'little')
  fv_32 = int(first_verification).to_bytes(4, 'little')
  counter = device.success_counter.to_bytes(4, 'little')

  m.update(bytes(bytearray.fromhex(device.uid)))
  m.update(bytes(bytearray.fromhex(challenge)))
  m.update(fv_32)
  m.update(vd_32)
  m.update(counter)
  m_hash = m.digest()
  

  key = PrivateKey(bytes(bytearray.fromhex(enc_key)), raw=True)
  sig = key.ecdsa_sign(m_hash, raw=True)
  m_signature = key.ecdsa_serialize_compact(sig)

  cbor_data = {
    keys['dev_auth_device']: state['dev_auth_server'],
    keys['first_auth']: int(first_verification),
    keys['auth_time']: int(verification_date),
    keys['auth_count']: device.success_counter,
    keys['signature']: m_signature
  }

  payload = dumps(cbor_data).hex()
  
  resp = {'status': 'success', 'message': mess, 'uid': device.uid, 'first_auth': first_verification, 'last_auth': verification_date, 'counter': device.success_counter, 'signature': m_signature.hex(), 'payload': payload}

  if redeem_code is not None:
    resp['redeem_code'] = redeem_code
    
  return resp

def verify(device_data, redeem_data=None):
  device_id = device_data["device_id"]
  challenge = device_data["challenge"]
  signature = device_data["signature"]
  initial_challenge = device_data["initial_challenge"]
  
  device = None
    
  try:
    device = Device.objects.get(uid=device_id)
  except:
    resp = {'status': 'error', 'message': 'Error: No device ' + device_id + ' found'}

  if device != None:
    if _verify_signature(device_id, initial_challenge, signature, device.public_key):
      mess = 'Success: Your device is genuine. This is not the first time the device was verified.'

      if device.verification_start_date == None:
        device.verification_start_date = datetime.datetime.utcnow()
        mess = 'Success: First verification. Your device is genuine.'
      device.success_counter = device.success_counter + 1
      device.save()
      redeem_code = ''
      
      if redeem_data is not None:
        redeem_code = redeem_data["redeem_code"]
        r_code = Campaign.objects.get(redeem_code=redeem_code)
        if r_code is None:
          resp = {'status': 'error', 'message': 'Error: Invalid redeem code.'}
        elif r_code.redeem_code:  
          resp = {'status': 'error', 'message': 'Error: Code already redeemed.'}
        else:  
          r_code.redemption_state = True
          r_code.redemption_date = datetime.datetime.utcnow()
          ra_obj = Address(campaign_name=redeem_data["campaign_name"], redemption_address=redeem_data["redemption_address"])
        
          try:
            with transaction.atomic():
              ra_obj.save()
              r_code.save()
          except IntegrityError:
              resp = {'status': 'error', 'message': 'Error: Redemption failed.'}
            
          mess = 'Success: Code redeemed successfully.'    
            
      resp = _success(device, challenge, mess, redeem_code)
    else:
      resp = {'status': 'error', 'message': 'Error: Invalid signature.'}

  return resp