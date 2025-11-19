import bcrypt

# Generate correct hash for admin123
password = 'admin123'
salt = bcrypt.gensalt(rounds=12)
hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
print(f"Password: {password}")
print(f"Bcrypt hash: {hashed.decode('utf-8')}")

# Verify it works
if bcrypt.checkpw(password.encode('utf-8'), hashed):
    print("✓ Hash verification successful!")
else:
    print("✗ Hash verification failed!")

