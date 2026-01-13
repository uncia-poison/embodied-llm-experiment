"""
Drive implementations convert text into action vectors. This module contains three placeholder drives:

- NumericDrive: extracts numbers from the text to form an action.
- TokenDrive: maps features of the text (length, punctuation) to an action.
- SemanticDrive: uses a text embedding to generate an action.
"""
from .numeric import NumericDrive
from .token import TokenDrive
from .semantic import SemanticDrive

__all__ = ["NumericDrive", "TokenDrive", "SemanticDrive"]
