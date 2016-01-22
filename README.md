# generate_csr
Why was it so hard to generate a CSR with Subject Alternative Names before?

# Why?
Remember those days when you had to copy the openssl.cnf somehwere and add one line for every DNS name you needed a certificate for? What was that command again?
This should be a lot easier!

# How?
```
user@localhost ~ $ git clone https://github.com/rbu/generate_csr ; cd gen_csr
user@localhost ~/generate_csr $ openssl genrsa -out private.key 8192            # because... why not?
Generating RSA private key, 8192 bit long modulus
...
user@localhost ~/generate_csr $ ./generate_csr.py --batch --key private.key rbu.sh www.rbu.sh mail.rbu.sh
-----BEGIN CERTIFICATE REQUEST-----
MIIIoDCCBIgCAQAwHjELMAkGA1UEBhMCWFgxDzANBgNVBAMMBnJidS5zaDCCBCIw
...
AedjkA==
-----END CERTIFICATE REQUEST-----
```

# Setup
- If you need to execute it in an automated environment (ansible etc), use --batch
- For batch mode to fill in some defaults (organisation, email), either set environment variables (REQ_COUNTRY, REQ_PROVINCE, REQ_CITY, REQ_ORG, REQ_OU, REQ_EMAIL) or edit the script
- If you do not run the batch mode, it will ask the field. Confirm the defaults or fill them in.

```
./generate_csr.py --help                            
usage: generate_csr.py [-h] [--batch] [--key PRIVATE_KEY_FILE]
                       DOMAIN [DOMAIN ...]

Generate SSL CSRs with Subject Alternative Names

positional arguments:
  DOMAIN                Domain names to request. First domain is the common
                        name.

optional arguments:
  -h, --help            show this help message and exit
  --batch               Batch mode, supress interaction and go with defaults.
  --key PRIVATE_KEY_FILE
                        Path to a private key file to generate a CSR for. To
                        generate a key, consider calling 'openssl genrsa -out
                        private.key 4096'
```
