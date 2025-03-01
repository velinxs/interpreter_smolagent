#!/usr/bin/env python3
"""
Launcher script for the Evolving Agent System.
"""

import os
import sys
from .agents.evolving_agent import EvolvingAgentSystem, main

if __name__ == "__main__":
    # If no arguments are provided, start in interactive mode
    if len(sys.argv) == 1:
        sys.argv.append("--interactive")
    
    # Run the main function from evolving_agent.py
    main()