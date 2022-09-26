import pandas as pd

def opCodes():
    '''
    Loads a pandas dataframe with implemented opcodes vs gas/circuit cost
    '''
    try:
        op = pd.read_csv('CircuitCosts.csv',sep='|')
        op=op.set_index('opcode')
        print(op.head())
        print("dataframe loaded")
    except:
        print("Error while loading dataframe")
        op = None
    return op
