from pulp import LpVariable, LpProblem, LpMinimize, LpStatus, value

import multiprocessing
import threading
import time


def optimize(max_weight):

    weights = [8.08, 5.7, 7.8, 3.2, 2.1, 11, 4.44, 6.4, 16.3, 1.7]
    prices = [24, 28.3, 210, 10.2, 4.4, 40.5, 17, 35.6, 82.7, 14.6]

    max_weight = 50

    n = len(weights)

    x = [LpVariable(f"x{i}", 0, 1, "Integer") for i in range(n)]

    prob = LpProblem("binpacking", LpMinimize)
    prob += sum([x[i] * prices[i]  for i in range(n)]) - (1000 * sum([x[i] for i in range(n)]))

    prob += sum([x[i] * weights[i] for i in range(n)]) <= max_weight


    status = prob.solve()

    print(LpStatus[status])
    
    time.sleep(1)

    
    return [value(v) for v in x]


def run():
    # Number of processes in the pool
    
    args = [1, 2, 3, 4, 5]
    n = 2
    
    
    thread = threading.Thread(target=optimize, args=(10,))
    thread.start()

    thread.join(10)
    if thread.is_alive():
        print("alive")
        
    print("end")
    
    # for n in range(n):
    #     p = multiprocessing.Process(target=optimize, name="Foo", args=(10,))
    #     p.start()

    # # Wait 10 seconds for foo
    # time.sleep(10)

    # # Terminate foo
    # p.terminate()

    # # Cleanup
    # p.join()

if __name__ == "__main__":
    run()