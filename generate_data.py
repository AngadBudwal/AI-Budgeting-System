#!/usr/bin/env python3
"""Standalone script to generate synthetic data for Nsight AI Budgeting System."""

import sys
import os

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from data_generator import main

if __name__ == "__main__":
    print("🚀 Nsight AI Budgeting System - Synthetic Data Generator")
    print("="*60)
    main() 