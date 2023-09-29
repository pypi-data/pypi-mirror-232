import os
from typing import Dict
import json
from google.cloud import storage
from google.oauth2 import service_account
import requests 

import crcmod
import six
from .api_client import APIClient


from google.cloud import kms

# READ SDK CONFIG FILE
dir_path = os.path.dirname(os.path.realpath(__file__))
with open(os.path.join(dir_path, "config.json"), "r") as f:
    config = json.load(f)

def seed_comparison(best_seed_info:Dict,new_seed_info:Dict):
    return new_seed_info if new_seed_info['metric'] > best_seed_info['metric'] else best_seed_info


def crc32c(data):
    """
    Calculates the CRC32C checksum of the provided data.

    Args:
        data: the bytes over which the checksum should be calculated.

    Returns:
        An int representing the CRC32C checksum of the provided bytes.
    """
    crc32c_fun = crcmod.predefined.mkPredefinedCrcFun('crc-32c')
    return crc32c_fun(six.ensure_binary(data))


def decrypt_symmetric(project_id, location_id, key_ring_id, key_id, ciphertext,kms_cred_info):
    """
    Decrypt the ciphertext using the symmetric key

    Args:
        project_id (string): Google Cloud project ID (e.g. 'my-project').
        location_id (string): Cloud KMS location (e.g. 'us-east1').
        key_ring_id (string): ID of the Cloud KMS key ring (e.g. 'my-key-ring').
        key_id (string): ID of the key to use (e.g. 'my-key').
        ciphertext (bytes): Encrypted bytes to decrypt.
        kms_cred_info (dict) : Decryption keys 

    Returns:
        DecryptResponse: Response including plaintext.

    """
    

    # Import the client library.

    # with open("kms-test.json") as info:
    #     info = json.load(info)
   
    kms_cred_info = json.loads(kms_cred_info)
    
    kms__local_credentials = service_account.Credentials.from_service_account_info(kms_cred_info)
    

    # Create the client.
    client = kms.KeyManagementServiceClient(credentials=kms__local_credentials)
    # Build the key name.
    key_name = client.crypto_key_path(project_id, location_id, key_ring_id, key_id)

    # Optional, but recommended: compute ciphertext's CRC32C.
    # See crc32c() function defined below.
    ciphertext_crc32c = crc32c(ciphertext)

    # Call the API.
    decrypt_response = client.decrypt(
        request={'name': key_name, 'ciphertext': ciphertext, 'ciphertext_crc32c': ciphertext_crc32c})

    # Optional, but recommended: perform integrity verification on decrypt_response.
    # For more details on ensuring E2E in-transit integrity to and from Cloud KMS visit:
    # https://cloud.google.com/kms/docs/data-integrity-guidelines
    if not decrypt_response.plaintext_crc32c == crc32c(decrypt_response.plaintext):
        raise Exception('The response received from the server was corrupted in-transit.')
    # End integrity verification

    return decrypt_response.plaintext






 
def get_kms_credentials(exp_token):
    url = f"{config['backend_ip']}/api/v2/get_decryption_keys/experiment_token/{exp_token}"
    response_credentials = getRequest(url)
    if response_credentials:
        return response_credentials
    
    return None
    
def get_storage_credentials(exp_token):
   
    url = f"{config['backend_ip']}/api/v2/get_credentials/experiment_token/{exp_token}"
    response = getRequest(url)
    
    if response:

        #response = response.json()
        data = bytes(response['data'],encoding='latin-1')
        kms_creds = get_kms_credentials(exp_token=exp_token)
       


        decrypted_storage_cred=decrypt_symmetric("dev-backend-369517","global","usercred-ring","symmetric-key",data,kms_creds['data'])
       
        return str(decrypted_storage_cred,'UTF-8')
    return None

def getRequest(url):
    response = requests.get(url, headers={"X-Alectio-Flavor": "PRO"})
    if response.status_code  in [200, 201, 202, 203, 204, 2005, 206]:
        return response.json()        
    return None