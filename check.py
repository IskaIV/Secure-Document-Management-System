import hashlib
secret_mod = 18446744073709551615

# Doesn't actually add any cryptographic complexity
def generate_token(role):
    hashed_role = int(hashlib.sha256(role.encode()).hexdigest(), 16) % secret_mod
    return str(hashed_role)

def check_token(token, role):
    hashed_role = int(hashlib.sha256(role.encode()).hexdigest(), 16) % secret_mod
    token = int(token)
    return hashed_role == token
