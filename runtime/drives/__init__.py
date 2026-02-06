"""
Drive implementations convert text into continuous action vectors.  The
baseline experiment includes three simple drives that extract actions
from text in different ways:

* NumericDrive: extracts floating point numbers from the text to form an action.
* TokenDrive: maps high‑level text features (length, punctuation, uppercase) to an action.
* SemanticDrive: uses a simple text embedding plus a fixed projection to
  generate an action.
* pattern_drive: (added by this patch) extracts motion commands from
  natural language using keyword patterns.  It accepts both English
  and Russian verbs and includes a cooldown to avoid repeated
  triggering of the same command on successive ticks.

New drives can be added here and exported via ``__all__``.  All drives
are callable objects or functions that take a string (agent text) and
return a list of floats representing actions in the [0,1] range.  Some
drives (such as ``pattern_drive``) require additional parameters and
thus take a ``config`` dictionary and random generator explicitly.
"""

from .numeric import NumericDrive
from .token import TokenDrive
from .semantic import SemanticDrive
from .pattern import pattern_drive

__all__ = ["NumericDrive", "TokenDrive", "SemanticDrive", "pattern_drive"]
