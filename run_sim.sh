#!/bin/bash
cd "$(dirname "$0")"
pip install -r requirements.txt
streamlit run simulator.py
