#import Cython/lightingControl_C.c
import sys
# insert at 1, 0 is the script path (or '' in REPL)
sys.path.insert(1, 'Optimized/pyd')
import lightingControl

if __name__ == "__main__":
    lightingControl()