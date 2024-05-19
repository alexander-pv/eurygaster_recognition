# Generate the Client Certificate Private Key
openssl ecparam -name prime256v1 -genkey -noout -out webpage.key
# Create the Client Certificate Signing Request
openssl req -new -sha256 -key webpage.key -out webpage.csr
# Generate the Client Certificate
openssl x509 -req -in webpage.csr -CA ca.crt -CAkey ca.key -CAcreateserial -out webpage.crt -days 1000 -sha256
