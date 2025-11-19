import bcrypt

password = 'admin123'
stored_hash = '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYBq.lkvy.'

print('Testing current hash from init.sql:')
print(f'Password: {password}')
print(f'Hash: {stored_hash}')
print(f'Hash length: {len(stored_hash)}')
print(f'Expected length: 60')

try:
    result = bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8'))
    print(f'✓ Verification successful: {result}')
except Exception as e:
    print(f'✗ Verification failed: {e}')

print('\nGenerating NEW correct hash:')
new_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(rounds=12))
new_hash_str = new_hash.decode('utf-8')
print(f'New hash: {new_hash_str}')
print(f'New hash length: {len(new_hash_str)}')
print(f'Verification: {bcrypt.checkpw(password.encode("utf-8"), new_hash)}')

