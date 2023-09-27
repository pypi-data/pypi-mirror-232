import os
from multiprocessing import resource_tracker


def remove_shm_from_resource_tracker():
    """Monkey-patch multiprocessing.resource_tracker so SharedMemory won't be tracked

    More details at: https://bugs.python.org/issue38119
    """

    def fix_register(name, rtype):
        return
    resource_tracker.register = fix_register

    def fix_unregister(name, rtype):
        return
    resource_tracker.unregister = fix_unregister

    if "shared_memory" in resource_tracker._CLEANUP_FUNCS:
        del resource_tracker._CLEANUP_FUNCS["shared_memory"]


if os.name == 'posix':
    from cffi import FFI
    # atomic semaphore operation
    ffi = FFI()
    ffi.cdef("""    
    unsigned char long_compare_and_swap(long mem_addr, long seek, long oldvalue, long newvalue);
    """)
    cpp = ffi.verify("""    
    unsigned char long_compare_and_swap(long mem_addr, long seek, long oldvalue, long newvalue) {
        long * mem_ptr = (long *) mem_addr;
        mem_ptr += seek;
        return __sync_bool_compare_and_swap(mem_ptr, oldvalue, newvalue);
    };    
    """)

elif os.name == "nt":
    import ctypes
    from pathlib import Path            
    os.add_dll_directory(Path(__file__).parents[3]/'SharedData')
    cpp = ctypes.CDLL('SharedData.dll')
    cpp.long_compare_and_swap.argtypes = [ctypes.c_longlong, ctypes.c_longlong, ctypes.c_longlong, ctypes.c_longlong]
    cpp.long_compare_and_swap.restype = ctypes.c_uint8


