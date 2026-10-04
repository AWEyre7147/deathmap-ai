"""Launch offline bibliography projection; this wrapper has no retrieval path."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from deathmap_ai.orcs_publication_enrichment import main
if __name__ == '__main__': main()
