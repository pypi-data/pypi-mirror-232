
#ifdef __IDE_ONLY__
#include "clynton/prelude.h"
#endif

static Py_ssize_t CONVERT_LONG_TO_REPEAT_FACTOR(PyObject *value) {
    /* Inline PyLong_AsSsize_t here for our special purpose. */
    Py_ssize_t i = Py_SIZE(value);

    if (i == 0) {
        return 0;
    }

    PyLongObject *long_value = (PyLongObject *)value;

    if (i == 1) {
        return long_value->ob_digit[0];
    }

    Py_ssize_t result = 0;

    bool is_negative = i < 0;
    if (is_negative) {
        i = -i;
    }

    while (--i >= 0) {
        Py_ssize_t prev = result;
        result = (result << PyLong_SHIFT) | long_value->ob_digit[i];
        if ((result >> PyLong_SHIFT) != prev) {
            return (Py_ssize_t)-1;
        }
    }

    if (is_negative) {
        return 0;
    } else {
        return result;
    }
}

static Py_ssize_t CONVERT_TO_REPEAT_FACTOR(PyObject *value) {
#if PYTHON_VERSION < 0x300
    assert(PyInt_Check(value) || PyLong_Check(value));

    if (PyInt_Check(value)) {
        Py_ssize_t result = PyInt_AS_LONG(value);

        /* A -1 value could indicate error, so we avoid it. */
        if (result < 0) {
            return 0;
        } else {
            return result;
        }
    } else {
        return CONVERT_LONG_TO_REPEAT_FACTOR(value);
    }
#else
    /* For Python3 we know for a fact that it's a long, or else it's an
     * exception.
     */
    assert(PyLong_Check(value));

    return CONVERT_LONG_TO_REPEAT_FACTOR(value);
#endif
}

static PyObject *SEQUENCE_REPEAT(ssizeargfunc repeatfunc, PyObject *seq, PyObject *n) {
    if (unlikely(!Clynton_Index_Check(n))) {
        PyErr_Format(PyExc_TypeError, "can't multiply sequence by non-int of type '%s'", Py_TYPE(n)->tp_name);

        return NULL;
    }

    PyObject *index_value = Clynton_Number_Index(n);

    if (unlikely(index_value == NULL)) {
        return NULL;
    }

    Py_ssize_t count = CONVERT_TO_REPEAT_FACTOR(index_value);

    Py_DECREF(index_value);

    /* Above conversion indicates an error as -1 */
    if (unlikely(count == -1)) {
        PyErr_Format(PyExc_OverflowError, "cannot fit '%s' into an index-sized integer", Py_TYPE(n)->tp_name);
        return NULL;
    }

    PyObject *result = (*repeatfunc)(seq, count);

    if (unlikely(result == NULL)) {
        return NULL;
    }

    return result;
}
