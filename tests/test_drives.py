from embodied_llm.drives.semantic import HashNgramEmbedder
from embodied_llm.drives.simple import PatternDrive


def test_pattern_silence_does_not_move():
    drive = PatternDrive(8, inertia=0.0)
    assert drive("I observe quietly.") == [0.0] * 8


def test_pattern_stop_is_zero():
    drive = PatternDrive(8, inertia=0.0)
    assert drive("stop and remain still") == [0.0] * 8


def test_hash_embedding_preserves_phrase_similarity():
    embedder = HashNgramEmbedder(256)
    a = embedder.embed("raise the arm slowly")
    b = embedder.embed("raise the arm")
    c = embedder.embed("the moon is made of glass")
    assert float(a @ b) > float(a @ c)
