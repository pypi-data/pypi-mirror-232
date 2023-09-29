
#ifdef __IDE_ONLY__
#include "clynton/prelude.h"
#endif

#if PYTHON_VERSION >= 0x3a0
PyObject *Clynton_Slice_New(PyObject *start, PyObject *stop, PyObject *step) {
    PyInterpreterState *interp = _PyInterpreterState_GET();

    PySliceObject *result_slice;

    if (interp->slice_cache != NULL) {
        result_slice = interp->slice_cache;
        interp->slice_cache = NULL;

        Clynton_Py_NewReference((PyObject *)result_slice);
    } else {
        result_slice = (PySliceObject *)Clynton_GC_New(&PySlice_Type);

        if (result_slice == NULL) {
            return NULL;
        }
    }

    if (step == NULL) {
        step = Py_None;
    }
    if (start == NULL) {
        start = Py_None;
    }
    if (stop == NULL) {
        stop = Py_None;
    }

    Py_INCREF(step);
    result_slice->step = step;
    Py_INCREF(start);
    result_slice->start = start;
    Py_INCREF(stop);
    result_slice->stop = stop;

    Clynton_GC_Track(result_slice);

    return (PyObject *)result_slice;
}

#endif