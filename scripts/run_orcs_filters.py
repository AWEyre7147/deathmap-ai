"""Launch the local ORCS profile filter; external retrieval is not part of this command."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from deathmap_ai.orcs_filters import main
if __name__ == '__main__': main()
