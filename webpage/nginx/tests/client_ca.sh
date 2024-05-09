# Generate the Certificate Authority (CA) Private Key
openssl ecparam -name prime256v1 -genkey -noout -out ca.key
# Generate the Certificate Authority Certificate
openssl req -new -x509 -sha256 -key ca.key -out ca.crt
