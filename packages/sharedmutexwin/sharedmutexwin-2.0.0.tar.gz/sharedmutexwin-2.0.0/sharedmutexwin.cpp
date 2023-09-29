#include <Python.h>
#include <Windows.h>

__declspec(dllexport) char long_compare_and_swap(long long mem_addr, long long seek, long long oldvalue, long long newvalue)
{
    long long* mem_ptr = (long long*)mem_addr;
    mem_ptr += seek;
    long long result = InterlockedCompareExchange64(mem_ptr, newvalue, oldvalue);
    return (result == oldvalue);
}

static PyObject* py_long_compare_and_swap(PyObject* self, PyObject* args)
{
    long long mem_addr, seek, oldvalue, newvalue;
    if (!PyArg_ParseTuple(args, "LLLL", &mem_addr, &seek, &oldvalue, &newvalue))
        return NULL;

    char result = long_compare_and_swap(mem_addr, seek, oldvalue, newvalue);
    return Py_BuildValue("b", result);
}

static PyMethodDef sharedmutexwin_methods[] = {
    {"long_compare_and_swap", py_long_compare_and_swap, METH_VARARGS, "Long Compare and Swap"},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef sharedmutexwin_module = {
    PyModuleDef_HEAD_INIT,
    "sharedmutexwin",
    "Python module for custom C++ functions",
    -1,
    sharedmutexwin_methods
};

PyMODINIT_FUNC PyInit_sharedmutexwin(void)
{
    return PyModule_Create(&sharedmutexwin_module);
}
