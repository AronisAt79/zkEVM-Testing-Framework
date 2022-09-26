from scripts.w3Utils import setupW3Provider, loadContract, getScName, sendTx
from scripts.debugUtils import getTxTraceByBlock, getTxTraceByHash, getTxTraceFromTxObject, getBlockInfo
from scripts.prover import proof_request, queryProverTasks, flushTasks
from scripts.circuitUtils import opCodes

from pprint import pprint

def test_calibrateOpCode(lcl, circuit, iterations=100, testenv="REPLICA", layer=2):
    '''
    Calculates the maximum number of worst case opcode executions that satisfies BLOCK_GAS_LIMIT
    Requires inputs:
    1. circuit: string > one of [EVM, STATE, etc]
    2. iterations: integer, start form a sufficienctly large value (for example 100000)to exceed gas limit
    Script will then repeat with steps of (minus )-1000 until block gas complies
    3. testenv: string, defaults to 'REPLICA', see environment.json for other options
    4. layer: integer, defaults to 2, for now no need to consider layer 1
    NOTE:Make sure to run this test with coordinator config option "dummy_proof" set to true to avoid spamming prover
    with unessecary proof requests
    example:
    brownie run scripts/globals.py main calibrateOpCode STATE 80000 --network zkevmchain

    >> lcl input referes to the locals() dict that is passed from the main script as *args (see method call: methodInstance(*([locals()]+paramsExpected)))
    '''

    url = lcl['env']["rpcUrls"][f'{testenv}'"_BASE"]+f"l{layer}"
    w3, chainid = setupW3Provider(url,testenv, layer)
    contractName, opCode = getScName(circuit)[0], getScName(circuit)[1]
    jsonmap = lcl['jsonmap']
    sc = loadContract(jsonmap, chainid,contractName)
    txNotSent = True
    iterations = int(iterations)
    while txNotSent:
        print(f"Submitting transaction with {iterations} calls of worst case opcode ({opCode}) for {circuit} circuit")
        tx, txNotSent = sendTx(iterations,sc,lcl['owner'])
        
        if not txNotSent:
            block = tx.block_number
            print(f"Transaction with {iterations} executions of opcode is submitted in block: {block}. Tx cost is {tx.gas_used}")
            # txNotSent = False
        else:
            iterations -= 1000

    return iterations
    
def test_benchProof(lcl,circuit,iterations=100,testenv="REPLICA",retry=False, flush=False, layer=2):
    '''
    Test Sequence: 
    1. Checks if there is ongoing proof task via the info method
    2. Waits until there are no pending/ongoing tasks (of flushes everything if flush=True)
    3. Sends a Tx to invoke the contract in question, according to target circuit
    4. Retrieves the block number where the tx was submitted and audits the block proof state
    until proof is generated or an error occurs

    Inputs:
        -   circuits: EVM, STATE
        -   iterations: the max number of opcode steps that satisfies gasUsed < 300K (exec test_calibrateOpCode
            to get this number)
        -   testenv: see environment.json for possible values. Defaults to 'REPLICA'
        -   retry: (bool) defines whether prover reattempts a failed proof. Must be False for test purpose
        -   flush: (bool) use it to clear tasks cache before starting bench

    Result:
        - proof and proof generation duration
    '''

    url = lcl['env']["rpcUrls"][f'{testenv}'"_BASE"]+f"l{layer}"
    w3, chainid = setupW3Provider(url,testenv, layer)
    contractName, opCode = getScName(circuit)[0], getScName(circuit)[1]
    jsonmap = lcl['jsonmap']
    sc = loadContract(jsonmap, chainid,contractName)
    txNotSent = True
    iterations = int(iterations)
    retry = str(retry).lower()
    proverUrl = lcl['env']["rpcUrls"][f'{testenv}'"_BASE"]+"prover"
    sourceUrl = lcl['SOURCE_URL']

    # put rpc call to info method here

    if flush:
        print("Flushing Tasks")
        flushTasks(proverUrl,True,True,True,1)
        # tasks = queryProverTasks(proverUrl)
        # pprint(tasks.json())
    
    proverIdle = False
    print('Waiting active and queued tasks to finish')
    while not proverIdle:
        tasksInfo = queryProverTasks(proverUrl)
        tasks = tasksInfo.json()['result']['tasks']
        pprint(tasks)
        n = [i['options']['block'] for i in tasks if i['result']==None]
        if len(n) == 0:
            proverIdle = True


    while txNotSent:
        print(f"Submitting transaction with {iterations} calls of worst case opcode ({opCode}) for {circuit} circuit")
        tx, txNotSent = sendTx(iterations,sc,lcl['owner'])
        
   
    block = tx.block_number
    print(f"Transaction with {iterations} executions of opcode is submitted in block: {block}. Tx cost is {tx.gas_used}")

    print(f'Sending proof request for block {block} ')
    error = False
    proof_generated = False
    while not error and not proof_generated:
        r = proof_request(proverUrl,block,sourceUrl,retry)
        print(f'Submitted proof request for block {block}')
        error = 'error' in r.json().keys()
        if error:
            error_message = r.json()['error']
        result = r.json()['result']
        proof_generated = result != None

    print(f'Error: {error_message}')
    print(f"Proof Request for block {block}:\n")
    pprint('result')

    return result, block


def test_calculateBlockCircuitCosts(lcl, blocknumber, testenv='REPLICA', dumpTxTrace=False, layer=2):
    '''
    papaki paei stin potamia
    '''
    url = lcl['env']["rpcUrls"][f'{testenv}'"_BASE"]+f"l{layer}"
    w3, chainid = setupW3Provider(url,testenv, layer)
    jsonmap = lcl['jsonmap']

    bl = getBlockInfo(w3,blocknumber)
    txHases = [i['hash'] for i in bl.transactions]
        


    # pprint(r)
    # pprint(r.json())
    # return r
