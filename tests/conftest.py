# -*- coding: utf-8 -*-
"""Pytest configuration."""
from __future__ import annotations
import sys
from pathlib import Path

# Добавляем корень проекта в sys.path для импортов
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
