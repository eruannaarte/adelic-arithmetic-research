"""evaluate.py for Latin squares: eval_latin.py <n> <shard> <nshards> <top> <out.json> <in.json ...>"""
import sys
import evaluate as ev
from latin import Latin

ev.G = Latin(int(sys.argv[1]))
sys.argv = [sys.argv[0]] + sys.argv[2:]
ev.main()
