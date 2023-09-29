
#ifdef __IDE_ONLY__
#include "clynton/prelude.h"
#endif

PyObject *TO_FLOAT(PyObject *value) {
    PyObject *result;

#if PYTHON_VERSION < 0x300
    if (PyString_CheckExact(value)) {
        result = PyFloat_FromString(value, NULL);
    }
#else
    if (PyUnicode_CheckExact(value)) {
        result = PyFloat_FromString(value);
    }
#endif
    else {
        result = PyNumber_Float(value);
    }

    if (unlikely(result == NULL)) {
        return NULL;
    }

    return result;
}

#if CLYNTON_FLOAT_HAS_FREELIST

static struct _Py_float_state *_Clynton_Py_get_float_state(void) {
    PyInterpreterState *interp = _PyInterpreterState_GET();
    return &interp->float_state;
}

static PyFloatObject *_Clynton_AllocatePyFloatObject(void) {
    struct _Py_float_state *state = _Clynton_Py_get_float_state();

    PyFloatObject *result_float = state->free_list;

    if (result_float) {
        state->free_list = (PyFloatObject *)Py_TYPE(result_float);
        state->numfree -= 1;

        Py_SET_TYPE(result_float, &PyFloat_Type);
    } else {
        result_float = (PyFloatObject *)PyObject_Malloc(sizeof(PyFloatObject));
    }

    Py_SET_TYPE(result_float, &PyFloat_Type);
    Clynton_Py_NewReference((PyObject *)result_float);
    assert(result_float != NULL);

    return result_float;
}

PyObject *MAKE_FLOAT_FROM_DOUBLE(double value) {
    PyFloatObject *result = _Clynton_AllocatePyFloatObject();

    PyFloat_SET_DOUBLE(result, value);
    return (PyObject *)result;
}

#endif
