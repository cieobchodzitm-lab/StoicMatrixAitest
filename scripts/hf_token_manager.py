#!/usr/bin/env python3
"""
HuggingFace Token Manager - Secure Token Management

Features:
- Encrypted token storage
- Environment variable validation
- Secure token retrieval
- Token rotation support
- Audit logging
"""

import os
import sys
import json
import hashlib
import secrets
from pathlib import Path
from cryptography.fernet import Fernet
from datetime import datetime
from typing import Optional, Dict
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class HFTokenManager:
    """
    Secure HuggingFace Token Manager
    Encrypts and manages HF tokens with audit logging
    """

    def __init__(self, storage_dir: str = ".hf_secure"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(exist_ok=True, mode=0o700)
        self.key_file = self.storage_dir / ".key"
        self.tokens_file = self.storage_dir / "tokens.enc"
        self.audit_file = self.storage_dir / "audit.log"
        self._init_encryption()

    def _init_encryption(self):
        """Initialize or load encryption key"""
        if self.key_file.exists():
            with open(self.key_file, 'rb') as f:
                self.cipher_key = f.read()
        else:
            self.cipher_key = Fernet.generate_key()
            with open(self.key_file, 'wb') as f:
                f.write(self.cipher_key)
            os.chmod(self.key_file, 0o600)
            logger.info("✓ Encryption key generated")

        self.cipher = Fernet(self.cipher_key)

    def _audit_log(self, action: str, details: str):
        """Log token operations for audit trail"""
        timestamp = datetime.now().isoformat()
        log_entry = f"[{timestamp}] {action}: {details}\n"
        with open(self.audit_file, 'a') as f:
            f.write(log_entry)
        logger.info(f"📋 Audit: {action} - {details}")

    def _load_tokens(self) -> Dict[str, Dict]:
        """Load encrypted tokens"""
        if not self.tokens_file.exists():
            return {}
        try:
            with open(self.tokens_file, 'rb') as f:
                encrypted_data = f.read()
            decrypted = self.cipher.decrypt(encrypted_data)
            return json.loads(decrypted.decode())
        except Exception as e:
            logger.error(f"❌ Failed to load tokens: {e}")
            return {}

    def _save_tokens(self, tokens: Dict):
        """Save encrypted tokens"""
        try:
            json_data = json.dumps(tokens, indent=2)
            encrypted = self.cipher.encrypt(json_data.encode())
            with open(self.tokens_file, 'wb') as f:
                f.write(encrypted)
            os.chmod(self.tokens_file, 0o600)
            logger.info("✓ Tokens saved securely")
        except Exception as e:
            logger.error(f"❌ Failed to save tokens: {e}")
            raise

    def add_token(self, name: str, token: str, description: str = ""):
        """Add new HF token"""
        tokens = self._load_tokens()
        
        if name in tokens:
            logger.warning(f"⚠️  Token '{name}' already exists, overwriting")
        
        tokens[name] = {
            "token": token,
            "description": description,
            "created_at": datetime.now().isoformat(),
            "last_used": None,
            "hash": hashlib.sha256(token.encode()).hexdigest()[:16]
        }
        
        self._save_tokens(tokens)
        self._audit_log("TOKEN_ADDED", f"name={name}, hash={tokens[name]['hash']}")
        logger.info(f"✓ Token '{name}' added successfully")

    def get_token(self, name: str) -> Optional[str]:
        """Retrieve token and update last_used"""
        tokens = self._load_tokens()
        
        if name not in tokens:
            logger.error(f"❌ Token '{name}' not found")
            return None
        
        token_data = tokens[name]
        token_data["last_used"] = datetime.now().isoformat()
        
        self._save_tokens(tokens)
        self._audit_log("TOKEN_RETRIEVED", f"name={name}")
        
        return token_data["token"]

    def list_tokens(self, show_full: bool = False) -> Dict:
        """List all stored tokens (without revealing actual tokens)"""
        tokens = self._load_tokens()
        result = {}
        
        for name, data in tokens.items():
            result[name] = {
                "hash": data.get("hash", "N/A"),
                "description": data.get("description", ""),
                "created_at": data.get("created_at", "N/A"),
                "last_used": data.get("last_used", "Never")
            }
        
        return result

    def delete_token(self, name: str):
        """Delete token"""
        tokens = self._load_tokens()
        
        if name not in tokens:
            logger.error(f"❌ Token '{name}' not found")
            return False
        
        del tokens[name]
        self._save_tokens(tokens)
        self._audit_log("TOKEN_DELETED", f"name={name}")
        logger.info(f"✓ Token '{name}' deleted")
        return True

    def rotate_token(self, name: str, new_token: str):
        """Rotate token (add new, keep old for reference)"""
        tokens = self._load_tokens()
        
        if name not in tokens:
            logger.error(f"❌ Token '{name}' not found")
            return False
        
        old_hash = tokens[name].get("hash", "N/A")
        tokens[name]["token"] = new_token
        tokens[name]["rotated_at"] = datetime.now().isoformat()
        tokens[name]["hash"] = hashlib.sha256(new_token.encode()).hexdigest()[:16]
        tokens[name]["previous_hash"] = old_hash
        
        self._save_tokens(tokens)
        self._audit_log("TOKEN_ROTATED", f"name={name}, old_hash={old_hash}")
        logger.info(f"✓ Token '{name}' rotated successfully")
        return True

    def export_to_env(self, name: str, env_var: str = None):
        """Export token to environment variable"""
        if env_var is None:
            env_var = f"HF_TOKEN_{name.upper()}"
        
        token = self.get_token(name)
        if token:
            os.environ[env_var] = token
            self._audit_log("TOKEN_EXPORTED", f"name={name}, env_var={env_var}")
            logger.info(f"✓ Token '{name}' exported to {env_var}")
            return True
        return False

    def validate_token(self, name: str) -> bool:
        """Validate token format and basic checks"""
        token = self.get_token(name)
        if not token:
            return False
        
        # HF tokens start with 'hf_'
        if not token.startswith('hf_'):
            logger.warning(f"⚠️  Token '{name}' doesn't start with 'hf_'")
            return False
        
        # Minimum length check
        if len(token) < 20:
            logger.warning(f"⚠️  Token '{name}' seems too short")
            return False
        
        self._audit_log("TOKEN_VALIDATED", f"name={name}")
        logger.info(f"✓ Token '{name}' is valid")
        return True


def main():
    """CLI interface for token manager"""
    import argparse
    
    parser = argparse.ArgumentParser(description="HuggingFace Token Manager")
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Add token
    add_parser = subparsers.add_parser("add", help="Add new token")
    add_parser.add_argument("name", help="Token name")
    add_parser.add_argument("token", help="HF token")
    add_parser.add_argument("--description", default="", help="Token description")
    
    # Get token
    get_parser = subparsers.add_parser("get", help="Get token")
    get_parser.add_argument("name", help="Token name")
    
    # List tokens
    list_parser = subparsers.add_parser("list", help="List all tokens")
    
    # Delete token
    del_parser = subparsers.add_parser("delete", help="Delete token")
    del_parser.add_argument("name", help="Token name")
    
    # Rotate token
    rot_parser = subparsers.add_parser("rotate", help="Rotate token")
    rot_parser.add_argument("name", help="Token name")
    rot_parser.add_argument("new_token", help="New HF token")
    
    # Validate token
    val_parser = subparsers.add_parser("validate", help="Validate token")
    val_parser.add_argument("name", help="Token name")
    
    # Export to env
    exp_parser = subparsers.add_parser("export", help="Export to environment")
    exp_parser.add_argument("name", help="Token name")
    exp_parser.add_argument("--var", help="Environment variable name")
    
    args = parser.parse_args()
    manager = HFTokenManager()
    
    if args.command == "add":
        manager.add_token(args.name, args.token, args.description)
    elif args.command == "get":
        token = manager.get_token(args.name)
        if token:
            print(f"Token for '{args.name}': {token[:10]}...")
    elif args.command == "list":
        tokens = manager.list_tokens()
        print("\n📋 Stored Tokens:")
        print(json.dumps(tokens, indent=2))
    elif args.command == "delete":
        manager.delete_token(args.name)
    elif args.command == "rotate":
        manager.rotate_token(args.name, args.new_token)
    elif args.command == "validate":
        valid = manager.validate_token(args.name)
        print(f"Token valid: {valid}")
    elif args.command == "export":
        manager.export_to_env(args.name, args.var)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
