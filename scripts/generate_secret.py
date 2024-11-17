import secrets
import os
from pathlib import Path

def generate_secret_key():
    """Generate a secure secret key"""
    return secrets.token_hex(32)

def save_secret_key(secret_key):
    """Save secret key to .env file"""
    # Get project root directory
    root_dir = Path(__file__).parent.parent
    
    # Create or update .env file
    env_path = root_dir / '.env'
    
    if env_path.exists():
        # Read existing environment variables
        with open(env_path, 'r') as f:
            lines = f.readlines()
        
        # Update or append SECRET_KEY
        secret_found = False
        for i, line in enumerate(lines):
            if line.startswith('SECRET_KEY='):
                lines[i] = f'SECRET_KEY={secret_key}\n'
                secret_found = True
                break
        
        if not secret_found:
            lines.append(f'SECRET_KEY={secret_key}\n')
        
        # Write back to file
        with open(env_path, 'w') as f:
            f.writelines(lines)
    else:
        # Create new .env file
        with open(env_path, 'w') as f:
            f.write(f'SECRET_KEY={secret_key}\n')
    
    return env_path

if __name__ == "__main__":
    print("Generating new secret key...")
    secret_key = generate_secret_key()
    env_path = save_secret_key(secret_key)
    print(f"Secret key generated and saved to {env_path}")
    print("\nSecret key:", secret_key)
    print("\nMake sure to:")
    print("1. Never commit the .env file to version control")
    print("2. Keep this secret key safe")
    print("3. Use different secret keys for development and production")