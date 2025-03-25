import time

def measure_execution_time(func, *args, **kwargs):
    """
    Measures the execution time of a function.
    
    Parameters:
    - func: The function to be timed.
    - *args: Positional arguments for the function.
    - **kwargs: Keyword arguments for the function.
    
    Returns:
    - result: The result of the function call.
    - elapsed_time: Time in seconds that the function took to execute.
    """
    start_time = time.time()
    result = func(*args, **kwargs)
    end_time = time.time()
    
    elapsed_time = end_time - start_time
    return result, elapsed_time
