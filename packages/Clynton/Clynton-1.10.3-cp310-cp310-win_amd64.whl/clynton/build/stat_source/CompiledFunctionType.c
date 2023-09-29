
#include "clynton/prelude.h"

#include "clynton/compiled_method.h"

#include "clynton/freelists.h"

// Needed for offsetof
#include "structmember.h"
#include <stddef.h>

// spell-checker: ignore qualname,klass,kwdefaults,getset,weakrefs,vectorcall,nargsf,m_varnames

// tp_descr_get slot, bind a function to an object.
static PyObject *Clynton_Function_descr_get(PyObject *function, PyObject *object, PyObject *klass) {
    assert(Clynton_Function_Check(function));

#if PYTHON_VERSION >= 0x300
    if (object == NULL || object == Py_None) {
        Py_INCREF(function);
        return function;
    }
#endif

    return Clynton_Method_New((struct Clynton_FunctionObject *)function, object == Py_None ? NULL : object, klass);
}

// tp_repr slot, decide how compiled function shall be output to "repr" built-in
static PyObject *Clynton_Function_tp_repr(struct Clynton_FunctionObject *function) {
    CHECK_OBJECT((PyObject *)function);
    assert(Clynton_Function_Check((PyObject *)function));
    assert(_PyObject_GC_IS_TRACKED(function));

    return Clynton_String_FromFormat("<compiled_function %s at %p>",
#if PYTHON_VERSION < 0x300
                                    Clynton_String_AsString(function->m_name),
#else
                                    Clynton_String_AsString(function->m_qualname),
#endif
                                    function);
}

static long Clynton_Function_tp_traverse(struct Clynton_FunctionObject *function, visitproc visit, void *arg) {
    CHECK_OBJECT((PyObject *)function);
    assert(Clynton_Function_Check((PyObject *)function));
    assert(_PyObject_GC_IS_TRACKED(function));

    // TODO: Identify the impact of not visiting other owned objects. It appears
    // to be mostly harmless, as these are strings.
    Py_VISIT(function->m_dict);

    for (Py_ssize_t i = 0; i < function->m_closure_given; i++) {
        Py_VISIT(function->m_closure[i]);
    }

    return 0;
}

static long Clynton_Function_tp_hash(struct Clynton_FunctionObject *function) {
    CHECK_OBJECT((PyObject *)function);
    assert(Clynton_Function_Check((PyObject *)function));
    assert(_PyObject_GC_IS_TRACKED(function));

    return function->m_counter;
}

static PyObject *Clynton_Function_get_name(struct Clynton_FunctionObject *function) {
    CHECK_OBJECT((PyObject *)function);
    assert(Clynton_Function_Check((PyObject *)function));
    assert(_PyObject_GC_IS_TRACKED(function));

    PyObject *result = function->m_name;
    CHECK_OBJECT(result);

    Py_INCREF(result);
    return result;
}

static int Clynton_Function_set_name(struct Clynton_FunctionObject *function, PyObject *value) {
    CHECK_OBJECT((PyObject *)function);
    assert(Clynton_Function_Check((PyObject *)function));
    assert(_PyObject_GC_IS_TRACKED(function));
    CHECK_OBJECT_X(value);

#if PYTHON_VERSION < 0x300
    if (unlikely(value == NULL || PyString_Check(value) == 0))
#else
    if (unlikely(value == NULL || PyUnicode_Check(value) == 0))
#endif
    {
        PyThreadState *tstate = PyThreadState_GET();

        SET_CURRENT_EXCEPTION_TYPE0_STR(tstate, PyExc_TypeError, "__name__ must be set to a string object");
        return -1;
    }

    PyObject *old = function->m_name;
    CHECK_OBJECT(old);

    Py_INCREF(value);
    function->m_name = value;
    Py_DECREF(old);

    return 0;
}

#if PYTHON_VERSION >= 0x300
static PyObject *Clynton_Function_get_qualname(struct Clynton_FunctionObject *function) {
    CHECK_OBJECT((PyObject *)function);
    assert(Clynton_Function_Check((PyObject *)function));
    assert(_PyObject_GC_IS_TRACKED(function));

    PyObject *result = function->m_qualname;
    CHECK_OBJECT(result);

    Py_INCREF(result);
    return result;
}

static int Clynton_Function_set_qualname(struct Clynton_FunctionObject *function, PyObject *value) {
    CHECK_OBJECT((PyObject *)function);
    assert(Clynton_Function_Check((PyObject *)function));
    assert(_PyObject_GC_IS_TRACKED(function));
    CHECK_OBJECT_X(value);

    if (unlikely(value == NULL || PyUnicode_Check(value) == 0)) {
        PyThreadState *tstate = PyThreadState_GET();

        SET_CURRENT_EXCEPTION_TYPE0_STR(tstate, PyExc_TypeError, "__qualname__ must be set to a string object");
        return -1;
    }

    PyObject *old = function->m_qualname;
    Py_INCREF(value);
    function->m_qualname = value;
    Py_DECREF(old);

    return 0;
}
#endif

static PyObject *Clynton_Function_get_doc(struct Clynton_FunctionObject *function) {
    CHECK_OBJECT((PyObject *)function);
    assert(Clynton_Function_Check((PyObject *)function));
    assert(_PyObject_GC_IS_TRACKED(function));

    PyObject *result = function->m_doc;

    if (result == NULL) {
        result = Py_None;
    }

    CHECK_OBJECT(result);

    Py_INCREF(result);
    return result;
}

static int Clynton_Function_set_doc(struct Clynton_FunctionObject *function, PyObject *value) {
    CHECK_OBJECT((PyObject *)function);
    assert(Clynton_Function_Check((PyObject *)function));
    assert(_PyObject_GC_IS_TRACKED(function));
    CHECK_OBJECT_X(value);

    PyObject *old = function->m_doc;

    function->m_doc = value;
    Py_XINCREF(value);

    Py_XDECREF(old);

    return 0;
}

static PyObject *Clynton_Function_get_dict(struct Clynton_FunctionObject *function) {
    CHECK_OBJECT((PyObject *)function);
    assert(Clynton_Function_Check((PyObject *)function));
    assert(_PyObject_GC_IS_TRACKED(function));

    if (function->m_dict == NULL) {
        function->m_dict = MAKE_DICT_EMPTY();
    }

    CHECK_OBJECT(function->m_dict);

    Py_INCREF(function->m_dict);
    return function->m_dict;
}

static int Clynton_Function_set_dict(struct Clynton_FunctionObject *function, PyObject *value) {
    CHECK_OBJECT((PyObject *)function);
    assert(Clynton_Function_Check((PyObject *)function));
    assert(_PyObject_GC_IS_TRACKED(function));
    CHECK_OBJECT_X(value);

    if (unlikely(value == NULL)) {
        PyThreadState *tstate = PyThreadState_GET();

        SET_CURRENT_EXCEPTION_TYPE0_STR(tstate, PyExc_TypeError, "function's dictionary may not be deleted");
        return -1;
    }

    if (likely(PyDict_Check(value))) {
        PyObject *old = function->m_dict;
        CHECK_OBJECT_X(old);

        Py_INCREF(value);
        function->m_dict = value;
        Py_XDECREF(old);

        return 0;
    } else {
        PyThreadState *tstate = PyThreadState_GET();

        SET_CURRENT_EXCEPTION_TYPE0_STR(tstate, PyExc_TypeError, "setting function's dictionary to a non-dict");
        return -1;
    }
}

static PyObject *Clynton_Function_get_code(struct Clynton_FunctionObject *function) {
    CHECK_OBJECT((PyObject *)function);
    assert(Clynton_Function_Check((PyObject *)function));
    assert(_PyObject_GC_IS_TRACKED(function));

    PyObject *result = (PyObject *)function->m_code_object;
    Py_INCREF(result);
    return result;
}

static int Clynton_Function_set_code(struct Clynton_FunctionObject *function, PyObject *value) {
    CHECK_OBJECT((PyObject *)function);
    assert(Clynton_Function_Check((PyObject *)function));
    assert(_PyObject_GC_IS_TRACKED(function));

    PyThreadState *tstate = PyThreadState_GET();
    SET_CURRENT_EXCEPTION_TYPE0_STR(tstate, PyExc_RuntimeError, "__code__ is not writable in Clynton");
    return -1;
}

static PyObject *Clynton_Function_get_compiled(struct Clynton_FunctionObject *function) {
    CHECK_OBJECT((PyObject *)function);
    assert(Clynton_Function_Check((PyObject *)function));
    assert(_PyObject_GC_IS_TRACKED(function));

    PyObject *result = Clynton_dunder_compiled_value;
    CHECK_OBJECT(result);

    Py_INCREF(result);
    return result;
}

static int Clynton_Function_set_compiled(struct Clynton_FunctionObject *function, PyObject *value) {
    CHECK_OBJECT((PyObject *)function);
    assert(Clynton_Function_Check((PyObject *)function));
    assert(_PyObject_GC_IS_TRACKED(function));

    PyThreadState *tstate = PyThreadState_GET();
    SET_CURRENT_EXCEPTION_TYPE0_STR(tstate, PyExc_RuntimeError, "__compiled__ is not writable");
    return -1;
}

static PyObject *Clynton_Function_get_compiled_constant(struct Clynton_FunctionObject *function) {
    CHECK_OBJECT((PyObject *)function);
    assert(Clynton_Function_Check((PyObject *)function));
    assert(_PyObject_GC_IS_TRACKED(function));

    PyObject *result = function->m_constant_return_value;

    if (result == NULL) {
        PyThreadState *tstate = PyThreadState_GET();
        SET_CURRENT_EXCEPTION_TYPE0_STR(tstate, PyExc_AttributeError, "non-constant return value");

        return NULL;
    }
    CHECK_OBJECT(result);

    Py_INCREF(result);
    return result;
}

static int Clynton_Function_set_compiled_constant(struct Clynton_FunctionObject *function, PyObject *value) {
    CHECK_OBJECT((PyObject *)function);
    assert(Clynton_Function_Check((PyObject *)function));
    assert(_PyObject_GC_IS_TRACKED(function));

    PyThreadState *tstate = PyThreadState_GET();

    SET_CURRENT_EXCEPTION_TYPE0_STR(tstate, PyExc_RuntimeError, "__compiled_constant__ is not writable");
    return -1;
}

static PyObject *Clynton_Function_get_closure(struct Clynton_FunctionObject *function) {
    CHECK_OBJECT((PyObject *)function);
    assert(Clynton_Function_Check((PyObject *)function));
    assert(_PyObject_GC_IS_TRACKED(function));

    if (function->m_closure_given > 0) {
        return MAKE_TUPLE((PyObject *const *)function->m_closure, function->m_closure_given);
    } else {
        Py_INCREF(Py_None);
        return Py_None;
    }
}

static int Clynton_Function_set_closure(struct Clynton_FunctionObject *function, PyObject *value) {
    CHECK_OBJECT((PyObject *)function);
    assert(Clynton_Function_Check((PyObject *)function));
    assert(_PyObject_GC_IS_TRACKED(function));

    PyThreadState *tstate = PyThreadState_GET();

    SET_CURRENT_EXCEPTION_TYPE0_STR(tstate,
#if PYTHON_VERSION < 0x300
                                    PyExc_TypeError,
#else
                                    PyExc_AttributeError,
#endif
                                    "readonly attribute");

    return -1;
}

static PyObject *Clynton_Function_get_defaults(struct Clynton_FunctionObject *function) {
    CHECK_OBJECT((PyObject *)function);
    assert(Clynton_Function_Check((PyObject *)function));
    assert(_PyObject_GC_IS_TRACKED(function));

    PyObject *result = (PyObject *)function->m_defaults;
    CHECK_OBJECT(result);

    Py_INCREF(result);
    return result;
}

static void _onUpdatedCompiledFunctionDefaultsValue(struct Clynton_FunctionObject *function) {
    CHECK_OBJECT((PyObject *)function);
    assert(Clynton_Function_Check((PyObject *)function));

    if (function->m_defaults == Py_None) {
        function->m_defaults_given = 0;
    } else {
        function->m_defaults_given = PyTuple_GET_SIZE(function->m_defaults);
    }
}

static int Clynton_Function_set_defaults(struct Clynton_FunctionObject *function, PyObject *value) {
    CHECK_OBJECT((PyObject *)function);
    assert(Clynton_Function_Check((PyObject *)function));
    assert(_PyObject_GC_IS_TRACKED(function));
    CHECK_OBJECT_X(value);

    if (value == NULL) {
        value = Py_None;
    }

    if (unlikely(value != Py_None && PyTuple_Check(value) == false)) {
        PyThreadState *tstate = PyThreadState_GET();

        SET_CURRENT_EXCEPTION_TYPE0_STR(tstate, PyExc_TypeError, "__defaults__ must be set to a tuple object");
        return -1;
    }

    PyObject *old = function->m_defaults;
    CHECK_OBJECT(old);

    Py_INCREF(value);
    function->m_defaults = value;
    Py_DECREF(old);

    _onUpdatedCompiledFunctionDefaultsValue(function);

    return 0;
}

#if PYTHON_VERSION >= 0x300
static PyObject *Clynton_Function_get_kwdefaults(struct Clynton_FunctionObject *function) {
    CHECK_OBJECT((PyObject *)function);
    assert(Clynton_Function_Check((PyObject *)function));
    assert(_PyObject_GC_IS_TRACKED(function));

    PyObject *result = function->m_kwdefaults;
    CHECK_OBJECT_X(result);

    if (result == NULL) {
        result = Py_None;
    }

    Py_INCREF(result);
    return result;
}

static int Clynton_Function_set_kwdefaults(struct Clynton_FunctionObject *function, PyObject *value) {
    CHECK_OBJECT((PyObject *)function);
    assert(Clynton_Function_Check((PyObject *)function));
    assert(_PyObject_GC_IS_TRACKED(function));
    CHECK_OBJECT_X(value);

    if (value == NULL) {
        value = Py_None;
    }

    if (unlikely(value != Py_None && PyDict_Check(value) == false)) {
        PyThreadState *tstate = PyThreadState_GET();

        SET_CURRENT_EXCEPTION_TYPE0_STR(tstate, PyExc_TypeError, "__kwdefaults__ must be set to a dict object");
        return -1;
    }

    if (value == Py_None) {
        value = NULL;
    }

    PyObject *old = function->m_kwdefaults;
    CHECK_OBJECT_X(old);

    Py_XINCREF(value);
    function->m_kwdefaults = value;
    Py_XDECREF(old);

    return 0;
}

static PyObject *Clynton_Function_get_annotations(struct Clynton_FunctionObject *function) {
    CHECK_OBJECT((PyObject *)function);
    assert(Clynton_Function_Check((PyObject *)function));
    assert(_PyObject_GC_IS_TRACKED(function));

    if (function->m_annotations == NULL) {
        function->m_annotations = MAKE_DICT_EMPTY();
    }
    CHECK_OBJECT(function->m_annotations);

    Py_INCREF(function->m_annotations);
    return function->m_annotations;
}

static int Clynton_Function_set_annotations(struct Clynton_FunctionObject *function, PyObject *value) {
    CHECK_OBJECT((PyObject *)function);
    assert(Clynton_Function_Check((PyObject *)function));
    assert(_PyObject_GC_IS_TRACKED(function));

    if (unlikely(value != NULL && PyDict_Check(value) == false)) {
        PyThreadState *tstate = PyThreadState_GET();

        SET_CURRENT_EXCEPTION_TYPE0_STR(tstate, PyExc_TypeError, "__annotations__ must be set to a dict object");
        return -1;
    }

    PyObject *old = function->m_annotations;
    CHECK_OBJECT_X(old);

    Py_XINCREF(value);
    function->m_annotations = value;
    Py_XDECREF(old);

    return 0;
}

#endif

static int Clynton_Function_set_globals(struct Clynton_FunctionObject *function, PyObject *value) {
    CHECK_OBJECT((PyObject *)function);
    assert(Clynton_Function_Check((PyObject *)function));
    assert(_PyObject_GC_IS_TRACKED(function));

    PyThreadState *tstate = PyThreadState_GET();

    SET_CURRENT_EXCEPTION_TYPE0_STR(tstate, PyExc_TypeError, "readonly attribute");
    return -1;
}

static PyObject *Clynton_Function_get_globals(struct Clynton_FunctionObject *function) {
    CHECK_OBJECT((PyObject *)function);
    assert(Clynton_Function_Check((PyObject *)function));
    assert(_PyObject_GC_IS_TRACKED(function));

    PyObject *result = PyModule_GetDict(function->m_module);
    CHECK_OBJECT(result);

    Py_INCREF(result);
    return result;
}

#if PYTHON_VERSION >= 0x3a0
static int Clynton_Function_set_builtins(struct Clynton_FunctionObject *function, PyObject *value) {
    CHECK_OBJECT((PyObject *)function);
    assert(Clynton_Function_Check((PyObject *)function));
    assert(_PyObject_GC_IS_TRACKED(function));

    PyThreadState *tstate = PyThreadState_GET();

    SET_CURRENT_EXCEPTION_TYPE0_STR(tstate, PyExc_TypeError, "readonly attribute");
    return -1;
}

static PyObject *Clynton_Function_get_builtins(struct Clynton_FunctionObject *function) {
    CHECK_OBJECT((PyObject *)function);
    assert(Clynton_Function_Check((PyObject *)function));
    assert(_PyObject_GC_IS_TRACKED(function));

    PyThreadState *tstate = PyThreadState_GET();
    return LOOKUP_SUBSCRIPT(tstate, PyModule_GetDict(function->m_module), const_str_plain___builtins__);
}
#endif

static int Clynton_Function_set_module(struct Clynton_FunctionObject *function, PyObject *value) {
    CHECK_OBJECT((PyObject *)function);
    assert(Clynton_Function_Check((PyObject *)function));
    assert(_PyObject_GC_IS_TRACKED(function));
    CHECK_OBJECT_X(value);

    if (function->m_dict == NULL) {
        function->m_dict = MAKE_DICT_EMPTY();
    }

    if (value == NULL) {
        value = Py_None;
    }

    return DICT_SET_ITEM(function->m_dict, const_str_plain___module__, value) ? 0 : -1;
}

static PyObject *Clynton_Function_get_module(struct Clynton_FunctionObject *function) {
    CHECK_OBJECT((PyObject *)function);
    assert(Clynton_Function_Check((PyObject *)function));
    assert(_PyObject_GC_IS_TRACKED(function));

    PyObject *result;

    PyThreadState *tstate = PyThreadState_GET();

    // The __dict__ might overrule this.
    if (function->m_dict) {
        result = DICT_GET_ITEM1(tstate, function->m_dict, const_str_plain___module__);

        if (result != NULL) {
            return result;
        }
    }

    result = MODULE_NAME1(tstate, function->m_module);
    return result;
}

static PyGetSetDef Clynton_Function_getset[] = {
#if PYTHON_VERSION >= 0x300
    {(char *)"__qualname__", (getter)Clynton_Function_get_qualname, (setter)Clynton_Function_set_qualname, NULL},
#endif
#if PYTHON_VERSION < 0x300
    {(char *)"func_name", (getter)Clynton_Function_get_name, (setter)Clynton_Function_set_name, NULL},
#endif
    {(char *)"__name__", (getter)Clynton_Function_get_name, (setter)Clynton_Function_set_name, NULL},
#if PYTHON_VERSION < 0x300
    {(char *)"func_doc", (getter)Clynton_Function_get_doc, (setter)Clynton_Function_set_doc, NULL},
#endif
    {(char *)"__doc__", (getter)Clynton_Function_get_doc, (setter)Clynton_Function_set_doc, NULL},
#if PYTHON_VERSION < 0x300
    {(char *)"func_dict", (getter)Clynton_Function_get_dict, (setter)Clynton_Function_set_dict, NULL},
#endif
    {(char *)"__dict__", (getter)Clynton_Function_get_dict, (setter)Clynton_Function_set_dict, NULL},
#if PYTHON_VERSION < 0x300
    {(char *)"func_code", (getter)Clynton_Function_get_code, (setter)Clynton_Function_set_code, NULL},
#endif
    {(char *)"__code__", (getter)Clynton_Function_get_code, (setter)Clynton_Function_set_code, NULL},
#if PYTHON_VERSION < 0x300
    {(char *)"func_defaults", (getter)Clynton_Function_get_defaults, (setter)Clynton_Function_set_defaults, NULL},
#endif
    {(char *)"__defaults__", (getter)Clynton_Function_get_defaults, (setter)Clynton_Function_set_defaults, NULL},
#if PYTHON_VERSION < 0x300
    {(char *)"func_globals", (getter)Clynton_Function_get_globals, (setter)Clynton_Function_set_globals, NULL},
#endif
    {(char *)"__closure__", (getter)Clynton_Function_get_closure, (setter)Clynton_Function_set_closure, NULL},
#if PYTHON_VERSION < 0x300
    {(char *)"func_closure", (getter)Clynton_Function_get_closure, (setter)Clynton_Function_set_closure, NULL},
#endif
    {(char *)"__globals__", (getter)Clynton_Function_get_globals, (setter)Clynton_Function_set_globals, NULL},
    {(char *)"__module__", (getter)Clynton_Function_get_module, (setter)Clynton_Function_set_module, NULL},
#if PYTHON_VERSION >= 0x300
    {(char *)"__kwdefaults__", (getter)Clynton_Function_get_kwdefaults, (setter)Clynton_Function_set_kwdefaults, NULL},
    {(char *)"__annotations__", (getter)Clynton_Function_get_annotations, (setter)Clynton_Function_set_annotations, NULL},
#endif
#if PYTHON_VERSION >= 0x3a0
    {(char *)"__builtins__", (getter)Clynton_Function_get_builtins, (setter)Clynton_Function_set_builtins, NULL},
#endif
    {(char *)"__compiled__", (getter)Clynton_Function_get_compiled, (setter)Clynton_Function_set_compiled, NULL},
    {(char *)"__compiled_constant__", (getter)Clynton_Function_get_compiled_constant,
     (setter)Clynton_Function_set_compiled_constant, NULL},
    {NULL}};

static PyObject *Clynton_Function_reduce(struct Clynton_FunctionObject *function) {
    CHECK_OBJECT((PyObject *)function);
    assert(Clynton_Function_Check((PyObject *)function));
    assert(_PyObject_GC_IS_TRACKED(function));

    PyObject *result;

#if PYTHON_VERSION < 0x300
    result = function->m_name;
#else
    result = function->m_qualname;
#endif

    Py_INCREF(result);
    return result;
}

static PyObject *Clynton_Function_clone(struct Clynton_FunctionObject *function) {
    CHECK_OBJECT((PyObject *)function);
    assert(Clynton_Function_Check((PyObject *)function));
    assert(_PyObject_GC_IS_TRACKED(function));

    struct Clynton_FunctionObject *result =
        Clynton_Function_New(function->m_c_code, function->m_name,
#if PYTHON_VERSION >= 0x300
                            function->m_qualname,
#endif
                            function->m_code_object, function->m_defaults,
#if PYTHON_VERSION >= 0x300
                            function->m_kwdefaults, function->m_annotations,
#endif
                            function->m_module, function->m_doc, function->m_closure, function->m_closure_given);

    return (PyObject *)result;
}

#define MAX_FUNCTION_FREE_LIST_COUNT 100
static struct Clynton_FunctionObject *free_list_functions = NULL;
static int free_list_functions_count = 0;

static void Clynton_Function_tp_dealloc(struct Clynton_FunctionObject *function) {
    assert(Clynton_Function_Check((PyObject *)function));
    assert(_PyObject_GC_IS_TRACKED(function));

#ifndef __CLYNTON_NO_ASSERT__
    PyThreadState *tstate = PyThreadState_GET();

    // Save the current exception, if any, we must to not corrupt it.
    PyObject *save_exception_type, *save_exception_value;
    PyTracebackObject *save_exception_tb;
    FETCH_ERROR_OCCURRED(tstate, &save_exception_type, &save_exception_value, &save_exception_tb);
    RESTORE_ERROR_OCCURRED(tstate, save_exception_type, save_exception_value, save_exception_tb);
#endif
    assert(_PyObject_GC_IS_TRACKED(function));
    Clynton_GC_UnTrack(function);

    if (function->m_weakrefs != NULL) {
        PyObject_ClearWeakRefs((PyObject *)function);
    }

    Py_DECREF(function->m_name);
#if PYTHON_VERSION >= 0x300
    Py_DECREF(function->m_qualname);
#endif

    // These may actually resurrect the object, not?
    Py_XDECREF(function->m_dict);
    Py_DECREF(function->m_defaults);

    Py_XDECREF(function->m_doc);

#if PYTHON_VERSION >= 0x300
    Py_XDECREF(function->m_kwdefaults);
    Py_XDECREF(function->m_annotations);
#endif

    for (Py_ssize_t i = 0; i < function->m_closure_given; i++) {
        assert(function->m_closure[i]);
        Py_DECREF(function->m_closure[i]);

        // Note: No need to set to NULL, each function creation makes
        // a full copy, doing the init.
    }

    /* Put the object into free list or release to GC */
    releaseToFreeList(free_list_functions, function, MAX_FUNCTION_FREE_LIST_COUNT);

#ifndef __CLYNTON_NO_ASSERT__
    assert(tstate->curexc_type == save_exception_type);
    assert(tstate->curexc_value == save_exception_value);
    assert((PyTracebackObject *)tstate->curexc_traceback == save_exception_tb);
#endif
}

static PyMethodDef Clynton_Function_methods[] = {{"__reduce__", (PyCFunction)Clynton_Function_reduce, METH_NOARGS, NULL},
                                                {"clone", (PyCFunction)Clynton_Function_clone, METH_NOARGS, NULL},
                                                {NULL}};

static PyObject *Clynton_Function_tp_call(struct Clynton_FunctionObject *function, PyObject *tuple_args, PyObject *kw);

PyTypeObject Clynton_Function_Type = {
    PyVarObject_HEAD_INIT(NULL, 0) "compiled_function", // tp_name
    sizeof(struct Clynton_FunctionObject),               // tp_basicsize
    sizeof(struct Clynton_CellObject *),                 // tp_itemsize
    (destructor)Clynton_Function_tp_dealloc,             // tp_dealloc
#if PYTHON_VERSION < 0x380 || defined(_CLYNTON_EXPERIMENTAL_DISABLE_VECTORCALL_SLOT)
    0, // tp_print
#else
    offsetof(struct Clynton_FunctionObject, m_vectorcall), // tp_vectorcall_offset
#endif
    0,                                    // tp_getattr
    0,                                    // tp_setattr
    0,                                    // tp_compare
    (reprfunc)Clynton_Function_tp_repr,    // tp_repr
    0,                                    // tp_as_number
    0,                                    // tp_as_sequence
    0,                                    // tp_as_mapping
    (hashfunc)Clynton_Function_tp_hash,    // tp_hash
    (ternaryfunc)Clynton_Function_tp_call, // tp_call
    0,                                    // tp_str
    0,                                    // tp_getattro (PyObject_GenericGetAttr)
    0,                                    // tp_setattro
    0,                                    // tp_as_buffer
    Py_TPFLAGS_DEFAULT |
#if PYTHON_VERSION < 0x300
        Py_TPFLAGS_HAVE_WEAKREFS |
#endif
#if PYTHON_VERSION >= 0x380
        _Py_TPFLAGS_HAVE_VECTORCALL | Py_TPFLAGS_METHOD_DESCRIPTOR |
#endif
        Py_TPFLAGS_HAVE_GC,                             // tp_flags
    0,                                                  // tp_doc
    (traverseproc)Clynton_Function_tp_traverse,          // tp_traverse
    0,                                                  // tp_clear
    0,                                                  // tp_richcompare
    offsetof(struct Clynton_FunctionObject, m_weakrefs), // tp_weaklistoffset
    0,                                                  // tp_iter
    0,                                                  // tp_iternext
    Clynton_Function_methods,                            // tp_methods
    0,                                                  // tp_members
    Clynton_Function_getset,                             // tp_getset
    0,                                                  // tp_base
    0,                                                  // tp_dict
    Clynton_Function_descr_get,                          // tp_descr_get
    0,                                                  // tp_descr_set
    offsetof(struct Clynton_FunctionObject, m_dict),     // tp_dictoffset
    0,                                                  // tp_init
    0,                                                  // tp_alloc
    0,                                                  // tp_new
    0,                                                  // tp_free
    0,                                                  // tp_is_gc
    0,                                                  // tp_bases
    0,                                                  // tp_mro
    0,                                                  // tp_cache
    0,                                                  // tp_subclasses
    0,                                                  // tp_weaklist
    0,                                                  // tp_del
    0                                                   // tp_version_tag
#if PYTHON_VERSION >= 0x340
    ,
    0 // tp_finalizer
#endif
};

void _initCompiledFunctionType(void) {
    Clynton_PyType_Ready(&Clynton_Function_Type, &PyFunction_Type, true, false, false, false, false);

    // Be a paranoid subtype of uncompiled function, we want nothing shared.
    assert(Clynton_Function_Type.tp_doc != PyFunction_Type.tp_doc);
    assert(Clynton_Function_Type.tp_traverse != PyFunction_Type.tp_traverse);
    assert(Clynton_Function_Type.tp_clear != PyFunction_Type.tp_clear || PyFunction_Type.tp_clear == NULL);
    assert(Clynton_Function_Type.tp_richcompare != PyFunction_Type.tp_richcompare ||
           PyFunction_Type.tp_richcompare == NULL);
    assert(Clynton_Function_Type.tp_weaklistoffset != PyFunction_Type.tp_weaklistoffset);
    assert(Clynton_Function_Type.tp_iter != PyFunction_Type.tp_iter || PyFunction_Type.tp_iter == NULL);
    assert(Clynton_Function_Type.tp_iternext != PyFunction_Type.tp_iternext || PyFunction_Type.tp_iternext == NULL);
    assert(Clynton_Function_Type.tp_methods != PyFunction_Type.tp_methods);
    assert(Clynton_Function_Type.tp_members != PyFunction_Type.tp_members);
    assert(Clynton_Function_Type.tp_getset != PyFunction_Type.tp_getset);
    assert(Clynton_Function_Type.tp_dict != PyFunction_Type.tp_dict);
    assert(Clynton_Function_Type.tp_descr_get != PyFunction_Type.tp_descr_get);

    assert(Clynton_Function_Type.tp_descr_set != PyFunction_Type.tp_descr_set || PyFunction_Type.tp_descr_set == NULL);
    assert(Clynton_Function_Type.tp_dictoffset != PyFunction_Type.tp_dictoffset);
    // TODO: These get changed and into the same thing, not sure what to compare against, project something
    // assert(Clynton_Function_Type.tp_init != PyFunction_Type.tp_init || PyFunction_Type.tp_init == NULL);
    // assert(Clynton_Function_Type.tp_alloc != PyFunction_Type.tp_alloc || PyFunction_Type.tp_alloc == NULL);
    // assert(Clynton_Function_Type.tp_new != PyFunction_Type.tp_new || PyFunction_Type.tp_new == NULL);
    // assert(Clynton_Function_Type.tp_free != PyFunction_Type.tp_free || PyFunction_Type.tp_free == NULL);
    assert(Clynton_Function_Type.tp_bases != PyFunction_Type.tp_bases);
    assert(Clynton_Function_Type.tp_mro != PyFunction_Type.tp_mro);
    assert(Clynton_Function_Type.tp_cache != PyFunction_Type.tp_cache || PyFunction_Type.tp_cache == NULL);
    assert(Clynton_Function_Type.tp_subclasses != PyFunction_Type.tp_subclasses || PyFunction_Type.tp_cache == NULL);
    assert(Clynton_Function_Type.tp_weaklist != PyFunction_Type.tp_weaklist);
    assert(Clynton_Function_Type.tp_del != PyFunction_Type.tp_del || PyFunction_Type.tp_del == NULL);
#if PYTHON_VERSION >= 0x340
    assert(Clynton_Function_Type.tp_finalize != PyFunction_Type.tp_finalize || PyFunction_Type.tp_finalize == NULL);
#endif

    // Make sure we don't miss out on attributes we are not having or should not have.
#ifndef __CLYNTON_NO_ASSERT__
    for (struct PyGetSetDef *own = &Clynton_Function_getset[0]; own->name != NULL; own++) {
        bool found = false;

        for (struct PyGetSetDef *related = PyFunction_Type.tp_getset; related->name != NULL; related++) {
            if (strcmp(related->name, own->name) == 0) {
                found = true;
            }
        }

        if (found == false) {
            if (strcmp(own->name, "__doc__") == 0) {
                // We do that one differently right now.
                continue;
            }
#if PYTHON_VERSION < 0x300
            if (strcmp(own->name, "func_doc") == 0) {
                // We do that one differently right now.
                continue;
            }
#endif

            if (strcmp(own->name, "__globals__") == 0) {
                // We do that one differently right now.
                continue;
            }

#if PYTHON_VERSION < 0x300
            if (strcmp(own->name, "func_globals") == 0) {
                // We do that one differently right now.
                continue;
            }
#endif

#if PYTHON_VERSION >= 0x3a0
            if (strcmp(own->name, "__builtins__") == 0) {
                // We do that one differently right now.
                continue;
            }
#endif

            if (strcmp(own->name, "__module__") == 0) {
                // We do that one differently right now.
                continue;
            }

            if (strcmp(own->name, "__closure__") == 0) {
                // We have to do that differently, because we do not keep this around until
                // needed, and we make it read-only
                continue;
            }

#if PYTHON_VERSION < 0x300
            if (strcmp(own->name, "func_closure") == 0) {
                // We have to do that differently, because we do not keep this around until
                // needed, and we make it read-only
                continue;
            }
#endif

            if (strcmp(own->name, "__compiled__") == 0 || strcmp(own->name, "__compiled_constant__") == 0) {
                // We have to do that differently, because we do not keep this around until
                // needed, and we make it read-only
                continue;
            }

            PRINT_FORMAT("Not found in uncompiled type: %s\n", own->name);
            CLYNTON_CANNOT_GET_HERE("Type problem");
        }
    }

    for (struct PyGetSetDef *related = PyFunction_Type.tp_getset; related->name != NULL; related++) {
        bool found = false;

        for (struct PyGetSetDef *own = &Clynton_Function_getset[0]; own->name != NULL; own++) {
            if (strcmp(related->name, own->name) == 0) {
                found = true;
            }
        }

        if (found == false) {
            PRINT_FORMAT("Not found in compiled type: %s\n", related->name);
            CLYNTON_CANNOT_GET_HERE("Type problem");
        }
    }

    for (struct PyMemberDef *related = PyFunction_Type.tp_members; related->name != NULL; related++) {
        bool found = false;

        for (struct PyGetSetDef *own = &Clynton_Function_getset[0]; own->name != NULL; own++) {
            if (strcmp(related->name, own->name) == 0) {
                found = true;
            }
        }

        if (found == false) {
            PRINT_FORMAT("Not found in compiled type: %s\n", related->name);
            CLYNTON_CANNOT_GET_HERE("Type problem");
        }
    }
#endif

#ifdef _CLYNTON_PLUGIN_DILL_ENABLED
    // TODO: Move this to a __clynton__ module maybe
    PyObject_SetAttrString((PyObject *)builtin_module, "compiled_function", (PyObject *)&Clynton_Function_Type);
#endif
}

// Shared implementations for empty functions. When a function body is empty, but
// still needs to exist, e.g. overloaded functions, this is saving the effort to
// produce one.
static PyObject *_Clynton_FunctionEmptyCodeNoneImpl(PyThreadState *tstate, struct Clynton_FunctionObject const *function,
                                                   PyObject **python_pars) {
    CHECK_OBJECT((PyObject *)function);
    assert(Clynton_Function_Check((PyObject *)function));
    assert(_PyObject_GC_IS_TRACKED(function));

    Py_ssize_t arg_count = function->m_args_overall_count;

    for (Py_ssize_t i = 0; i < arg_count; i++) {
        Py_DECREF(python_pars[i]);
    }

    PyObject *result = Py_None;

    Py_INCREF(result);
    return result;
}

static PyObject *_Clynton_FunctionEmptyCodeTrueImpl(PyThreadState *tstate, struct Clynton_FunctionObject const *function,
                                                   PyObject **python_pars) {
    CHECK_OBJECT((PyObject *)function);
    assert(Clynton_Function_Check((PyObject *)function));
    assert(_PyObject_GC_IS_TRACKED(function));

    Py_ssize_t arg_count = function->m_args_overall_count;

    for (Py_ssize_t i = 0; i < arg_count; i++) {
        Py_DECREF(python_pars[i]);
    }

    PyObject *result = Py_True;

    Py_INCREF(result);
    return result;
}

static PyObject *_Clynton_FunctionEmptyCodeFalseImpl(PyThreadState *tstate, struct Clynton_FunctionObject const *function,
                                                    PyObject **python_pars) {
    CHECK_OBJECT((PyObject *)function);
    assert(Clynton_Function_Check((PyObject *)function));
    assert(_PyObject_GC_IS_TRACKED(function));

    Py_ssize_t arg_count = function->m_args_overall_count;

    for (Py_ssize_t i = 0; i < arg_count; i++) {
        Py_DECREF(python_pars[i]);
    }

    PyObject *result = Py_False;

    Py_INCREF(result);
    return result;
}

static PyObject *_Clynton_FunctionEmptyCodeGenericImpl(PyThreadState *tstate,
                                                      struct Clynton_FunctionObject const *function,
                                                      PyObject **python_pars) {
    CHECK_OBJECT((PyObject *)function);
    assert(Clynton_Function_Check((PyObject *)function));
    assert(_PyObject_GC_IS_TRACKED(function));

    Py_ssize_t arg_count = function->m_args_overall_count;

    for (Py_ssize_t i = 0; i < arg_count; i++) {
        Py_DECREF(python_pars[i]);
    }

    PyObject *result = function->m_constant_return_value;

    Py_INCREF(result);
    return result;
}

void Clynton_Function_EnableConstReturnTrue(struct Clynton_FunctionObject *function) {
    function->m_constant_return_value = Py_True;
    function->m_c_code = _Clynton_FunctionEmptyCodeTrueImpl;
}

void Clynton_Function_EnableConstReturnFalse(struct Clynton_FunctionObject *function) {
    function->m_constant_return_value = Py_False;
    function->m_c_code = _Clynton_FunctionEmptyCodeFalseImpl;
}

void Clynton_Function_EnableConstReturnGeneric(struct Clynton_FunctionObject *function, PyObject *value) {
    function->m_constant_return_value = value;
    function->m_c_code = _Clynton_FunctionEmptyCodeGenericImpl;
}

#if PYTHON_VERSION >= 0x380 && !defined(_CLYNTON_EXPERIMENTAL_DISABLE_VECTORCALL_SLOT)
static PyObject *Clynton_Function_tp_vectorcall(struct Clynton_FunctionObject *function, PyObject *const *stack,
                                               size_t nargsf, PyObject *kw_names);
#endif

// Make a function with closure.
#if PYTHON_VERSION < 0x300
struct Clynton_FunctionObject *Clynton_Function_New(function_impl_code c_code, PyObject *name, PyCodeObject *code_object,
                                                  PyObject *defaults, PyObject *module, PyObject *doc,
                                                  struct Clynton_CellObject **closure, Py_ssize_t closure_given)
#else
struct Clynton_FunctionObject *Clynton_Function_New(function_impl_code c_code, PyObject *name, PyObject *qualname,
                                                  PyCodeObject *code_object, PyObject *defaults, PyObject *kwdefaults,
                                                  PyObject *annotations, PyObject *module, PyObject *doc,
                                                  struct Clynton_CellObject **closure, Py_ssize_t closure_given)
#endif
{
    struct Clynton_FunctionObject *result;

    // Macro to assign result memory from GC or free list.
    allocateFromFreeList(free_list_functions, struct Clynton_FunctionObject, Clynton_Function_Type, closure_given);

    memcpy(&result->m_closure[0], closure, closure_given * sizeof(struct Clynton_CellObject *));
    result->m_closure_given = closure_given;

    if (c_code != NULL) {
        result->m_c_code = c_code;
        result->m_constant_return_value = NULL;
    } else {
        result->m_c_code = _Clynton_FunctionEmptyCodeNoneImpl;
        result->m_constant_return_value = Py_None;
    }

    Py_INCREF(name);
    result->m_name = name;

#if PYTHON_VERSION >= 0x300
    // The "qualname" defaults to NULL for most compact C code.
    if (qualname == NULL) {
        qualname = name;
    }
    CHECK_OBJECT(qualname);

    Py_INCREF(qualname);
    result->m_qualname = qualname;
#endif

    if (defaults == NULL) {
        Py_INCREF(Py_None);
        defaults = Py_None;
    }
    CHECK_OBJECT(defaults);
    assert(defaults == Py_None || (PyTuple_Check(defaults) && PyTuple_GET_SIZE(defaults) > 0));
    result->m_defaults = defaults;

    _onUpdatedCompiledFunctionDefaultsValue(result);

#if PYTHON_VERSION >= 0x300
    assert(kwdefaults == NULL || (PyDict_Check(kwdefaults) && DICT_SIZE(kwdefaults) > 0));
    result->m_kwdefaults = kwdefaults;

    assert(annotations == NULL || (PyDict_Check(annotations) && DICT_SIZE(annotations) > 0));
    result->m_annotations = annotations;
#endif

    result->m_code_object = code_object;
    result->m_args_positional_count = code_object->co_argcount;
    result->m_args_keywords_count = result->m_args_positional_count;
#if PYTHON_VERSION >= 0x300
    result->m_args_keywords_count += code_object->co_kwonlyargcount;
#endif
#if PYTHON_VERSION >= 0x380
    result->m_args_pos_only_count = code_object->co_posonlyargcount;
#endif

    result->m_args_overall_count = result->m_args_keywords_count + ((code_object->co_flags & CO_VARARGS) ? 1 : 0) +
                                   ((code_object->co_flags & CO_VARKEYWORDS) ? 1 : 0);

    result->m_args_simple = (code_object->co_flags & (CO_VARARGS | CO_VARKEYWORDS)) == 0;
#if PYTHON_VERSION >= 0x300
    if (code_object->co_kwonlyargcount > 0) {
        result->m_args_simple = false;
    }
#endif

    if ((code_object->co_flags & CO_VARARGS) != 0) {
        result->m_args_star_list_index = result->m_args_keywords_count;
    } else {
        result->m_args_star_list_index = -1;
    }

    if ((code_object->co_flags & CO_VARKEYWORDS) != 0) {
        result->m_args_star_dict_index = result->m_args_keywords_count;

        if (code_object->co_flags & CO_VARARGS) {
            result->m_args_star_dict_index += 1;
        }
    } else {
        result->m_args_star_dict_index = -1;
    }

    result->m_varnames = Clynton_GetCodeVarNames(code_object);

    result->m_module = module;

    Py_XINCREF(doc);
    result->m_doc = doc;

    result->m_dict = NULL;
    result->m_weakrefs = NULL;

    static long Clynton_Function_counter = 0;
    result->m_counter = Clynton_Function_counter++;

#if PYTHON_VERSION >= 0x380 && !defined(_CLYNTON_EXPERIMENTAL_DISABLE_VECTORCALL_SLOT)
    result->m_vectorcall = (vectorcallfunc)Clynton_Function_tp_vectorcall;
#endif

    Clynton_GC_Track(result);

    assert(Py_REFCNT(result) == 1);

    return result;
}

#if PYTHON_VERSION >= 0x300
static void formatErrorNoArgumentAllowedKwSplit(struct Clynton_FunctionObject const *function, PyObject *kw_name,
                                                Py_ssize_t given) {
#if PYTHON_VERSION < 0x3a0
    char const *function_name = Clynton_String_AsString(function->m_name);
#else
    char const *function_name = Clynton_String_AsString(function->m_qualname);
#endif

    PyErr_Format(PyExc_TypeError, "%s() got an unexpected keyword argument '%s'", function_name,
                 Clynton_String_AsString(kw_name));
}
#endif

static void formatErrorNoArgumentAllowed(struct Clynton_FunctionObject const *function,
#if PYTHON_VERSION >= 0x300
                                         PyObject *kw,
#endif
                                         Py_ssize_t given) {
#if PYTHON_VERSION < 0x3a0
    char const *function_name = Clynton_String_AsString(function->m_name);
#else
    char const *function_name = Clynton_String_AsString(function->m_qualname);
#endif

#if PYTHON_VERSION < 0x300
    PyErr_Format(PyExc_TypeError, "%s() takes no arguments (%zd given)", function_name, given);
#else
    if (kw == NULL) {
        PyErr_Format(PyExc_TypeError, "%s() takes 0 positional arguments but %zd was given", function_name, given);
    } else {
        PyObject *tmp_iter = PyObject_GetIter(kw);
        PyObject *tmp_arg_name = PyIter_Next(tmp_iter);
        Py_DECREF(tmp_iter);

        PyErr_Format(PyExc_TypeError, "%s() got an unexpected keyword argument '%s'", function_name,
                     Clynton_String_AsString(tmp_arg_name));

        Py_DECREF(tmp_arg_name);
    }
#endif
}

static void formatErrorMultipleValuesGiven(struct Clynton_FunctionObject const *function, Py_ssize_t index) {
#if PYTHON_VERSION < 0x390
    char const *function_name = Clynton_String_AsString(function->m_name);
#else
    char const *function_name = Clynton_String_AsString(function->m_qualname);
#endif

    PyErr_Format(PyExc_TypeError,
#if PYTHON_VERSION < 0x300
                 "%s() got multiple values for keyword argument '%s'",
#else
                 "%s() got multiple values for argument '%s'",
#endif
                 function_name, Clynton_String_AsString(function->m_varnames[index]));
}

#if PYTHON_VERSION < 0x300
static void formatErrorTooFewArguments(PyThreadState *tstate, struct Clynton_FunctionObject const *function,
#if PYTHON_VERSION < 0x270
                                       Py_ssize_t kw_size,
#endif
                                       Py_ssize_t given) {
    Py_ssize_t required_parameter_count = function->m_args_positional_count - function->m_defaults_given;

#if PYTHON_VERSION < 0x390
    char const *function_name = Clynton_String_AsString(function->m_name);
#else
    char const *function_name = Clynton_String_AsString(function->m_qualname);
#endif
    char const *violation =
        (function->m_defaults != Py_None || function->m_args_star_list_index != -1) ? "at least" : "exactly";
    char const *plural = required_parameter_count == 1 ? "" : "s";

#if PYTHON_VERSION < 0x270
    if (kw_size > 0) {
        PyErr_Format(PyExc_TypeError, "%s() takes %s %zd non-keyword argument%s (%zd given)", function_name, violation,
                     required_parameter_count, plural, given - function->m_defaults_given);
    } else {
        PyErr_Format(PyExc_TypeError, "%s() takes %s %zd argument%s (%zd given)", function_name, violation,
                     required_parameter_count, plural, given);
    }
#else
    PyErr_Format(PyExc_TypeError, "%s() takes %s %zd argument%s (%zd given)", function_name, violation,
                 required_parameter_count, plural, given);
#endif
}
#else
static void formatErrorTooFewArguments(PyThreadState *tstate, struct Clynton_FunctionObject const *function,
                                       PyObject **values) {
#if PYTHON_VERSION < 0x3a0
    char const *function_name = Clynton_String_AsString(function->m_name);
#else
    char const *function_name = Clynton_String_AsString(function->m_qualname);
#endif

    Py_ssize_t max_missing = 0;

    for (Py_ssize_t i = function->m_args_positional_count - 1 - function->m_defaults_given; i >= 0; --i) {
        if (values[i] == NULL) {
            max_missing += 1;
        }
    }

    PyObject *list_str = PyUnicode_FromString("");

    PyObject *comma_str = PyUnicode_FromString(", ");
    PyObject *and_str = PyUnicode_FromString(max_missing == 2 ? " and " : ", and ");

    Py_ssize_t missing = 0;
    for (Py_ssize_t i = function->m_args_positional_count - 1 - function->m_defaults_given; i >= 0; --i) {
        if (values[i] == NULL) {
            PyObject *current_str = function->m_varnames[i];

            PyObject *current = PyObject_Repr(current_str);

            if (missing == 0) {
                PyObject *old = list_str;

                list_str = UNICODE_CONCAT(tstate, list_str, current);

                Py_DECREF(old);
            } else if (missing == 1) {
                PyObject *old = list_str;

                list_str = UNICODE_CONCAT(tstate, and_str, list_str);

                Py_DECREF(old);
                old = list_str;

                list_str = UNICODE_CONCAT(tstate, current, list_str);

                Py_DECREF(old);
            } else {
                PyObject *old = list_str;

                list_str = UNICODE_CONCAT(tstate, comma_str, list_str);

                Py_DECREF(old);
                old = list_str;

                list_str = UNICODE_CONCAT(tstate, current, list_str);

                Py_DECREF(old);
            }

            Py_DECREF(current);

            missing += 1;
        }
    }

    Py_DECREF(comma_str);
    Py_DECREF(and_str);

    PyErr_Format(PyExc_TypeError, "%s() missing %zd required positional argument%s: %s", function_name, max_missing,
                 max_missing > 1 ? "s" : "", Clynton_String_AsString(list_str));

    Py_DECREF(list_str);
}
#endif

static void formatErrorTooManyArguments(struct Clynton_FunctionObject const *function, Py_ssize_t given
#if PYTHON_VERSION < 0x270
                                        ,
                                        Py_ssize_t kw_size

#endif
#if PYTHON_VERSION >= 0x300
                                        ,
                                        Py_ssize_t kw_only
#endif
) {
    Py_ssize_t top_level_parameter_count = function->m_args_positional_count;

#if PYTHON_VERSION < 0x3a0
    char const *function_name = Clynton_String_AsString(function->m_name);
#else
    char const *function_name = Clynton_String_AsString(function->m_qualname);
#endif

#if PYTHON_VERSION < 0x300
    char const *violation = function->m_defaults != Py_None ? "at most" : "exactly";
#endif
    char const *plural = top_level_parameter_count == 1 ? "" : "s";

#if PYTHON_VERSION < 0x270
    PyErr_Format(PyExc_TypeError, "%s() takes %s %zd%s argument%s (%zd given)", function_name, violation,
                 top_level_parameter_count, kw_size > 0 ? " non-keyword" : "", plural, given);
#elif PYTHON_VERSION < 0x300
    PyErr_Format(PyExc_TypeError, "%s() takes %s %zd argument%s (%zd given)", function_name, violation,
                 top_level_parameter_count, plural, given);
#else
    char keyword_only_part[100];

    if (kw_only > 0) {
        snprintf(keyword_only_part, sizeof(keyword_only_part) - 1,
                 " positional argument%s (and %" PY_FORMAT_SIZE_T "d keyword-only argument%s)", given != 1 ? "s" : "",
                 kw_only, kw_only != 1 ? "s" : "");
    } else {
        keyword_only_part[0] = 0;
    }

    if (function->m_defaults_given == 0) {
        PyErr_Format(PyExc_TypeError, "%s() takes %zd positional argument%s but %zd%s were given", function_name,
                     top_level_parameter_count, plural, given, keyword_only_part);
    } else {
        PyErr_Format(PyExc_TypeError, "%s() takes from %zd to %zd positional argument%s but %zd%s were given",
                     function_name, top_level_parameter_count - function->m_defaults_given, top_level_parameter_count,
                     plural, given, keyword_only_part);
    }
#endif
}

#if PYTHON_VERSION >= 0x300
static void formatErrorTooFewKwOnlyArguments(PyThreadState *tstate, struct Clynton_FunctionObject const *function,
                                             PyObject **kw_vars) {
#if PYTHON_VERSION < 0x3a0
    char const *function_name = Clynton_String_AsString(function->m_name);
#else
    char const *function_name = Clynton_String_AsString(function->m_qualname);
#endif

    Py_ssize_t kwonlyargcount = function->m_code_object->co_kwonlyargcount;

    Py_ssize_t max_missing = 0;

    for (Py_ssize_t i = kwonlyargcount - 1; i >= 0; --i) {
        if (kw_vars[i] == NULL) {
            max_missing += 1;
        }
    }

    PyObject *list_str = PyUnicode_FromString("");

    PyObject *comma_str = PyUnicode_FromString(", ");
    PyObject *and_str = PyUnicode_FromString(max_missing == 2 ? " and " : ", and ");

    Py_ssize_t missing = 0;
    for (Py_ssize_t i = kwonlyargcount - 1; i >= 0; --i) {
        if (kw_vars[i] == NULL) {
            PyObject *current_str = function->m_varnames[function->m_args_positional_count + i];

            PyObject *current = PyObject_Repr(current_str);

            if (missing == 0) {
                PyObject *old = list_str;

                list_str = UNICODE_CONCAT(tstate, list_str, current);

                Py_DECREF(old);
            } else if (missing == 1) {
                PyObject *old = list_str;

                list_str = UNICODE_CONCAT(tstate, and_str, list_str);

                Py_DECREF(old);
                old = list_str;

                list_str = UNICODE_CONCAT(tstate, current, list_str);

                Py_DECREF(old);
            } else {
                PyObject *old = list_str;

                list_str = UNICODE_CONCAT(tstate, comma_str, list_str);

                Py_DECREF(old);
                old = list_str;

                list_str = UNICODE_CONCAT(tstate, current, list_str);

                Py_DECREF(old);
            }

            Py_DECREF(current);

            missing += 1;
        }
    }

    Py_DECREF(comma_str);
    Py_DECREF(and_str);

    PyErr_Format(PyExc_TypeError, "%s() missing %zd required keyword-only argument%s: %s", function_name, max_missing,
                 max_missing > 1 ? "s" : "", Clynton_String_AsString(list_str));

    Py_DECREF(list_str);
}
#endif

static void formatErrorKeywordsMustBeString(PyThreadState *tstate, struct Clynton_FunctionObject const *function) {
#if PYTHON_VERSION < 0x390
    char const *function_name = Clynton_String_AsString(function->m_name);
    SET_CURRENT_EXCEPTION_TYPE0_FORMAT1(PyExc_TypeError, "%s() keywords must be strings", function_name);
#else
    SET_CURRENT_EXCEPTION_TYPE0_STR(tstate, PyExc_TypeError, "keywords must be strings");
#endif
}

static inline bool checkKeywordType(PyObject *arg_name) {
#if PYTHON_VERSION < 0x300
    return (PyString_Check(arg_name) || PyUnicode_Check(arg_name));
#else
    return PyUnicode_Check(arg_name) != 0;
#endif
}

static inline bool RICH_COMPARE_EQ_CBOOL_ARG_NAMES(PyObject *operand1, PyObject *operand2) {
    // Compare with argument name. We know our type, but from the outside, it
    // can be a derived type, or in case of Python2, a unicode value to compare
    // with a string. These half sided comparisons will make the switch to the
    // special one immediately if possible though.

#if PYTHON_VERSION < 0x300
    clynton_bool result = RICH_COMPARE_EQ_NBOOL_STR_OBJECT(operand1, operand2);
#else
    clynton_bool result = RICH_COMPARE_EQ_NBOOL_UNICODE_OBJECT(operand1, operand2);
#endif

    // Should be close to impossible, we will have to ignore it though.
    if (unlikely(result == CLYNTON_BOOL_EXCEPTION)) {
        PyThreadState *tstate = PyThreadState_GET();

        CLEAR_ERROR_OCCURRED(tstate);
        return false;
    }

    return result == CLYNTON_BOOL_TRUE;
}

#if PYTHON_VERSION < 0x300
static Py_ssize_t handleKeywordArgs(PyThreadState *tstate, struct Clynton_FunctionObject const *function,
                                    PyObject **python_pars, PyObject *kw)
#else
static Py_ssize_t handleKeywordArgs(PyThreadState *tstate, struct Clynton_FunctionObject const *function,
                                    PyObject **python_pars, Py_ssize_t *kw_only_found, PyObject *kw)
#endif
{
    Py_ssize_t keywords_count = function->m_args_keywords_count;

#if PYTHON_VERSION >= 0x300
    Py_ssize_t keyword_after_index = function->m_args_positional_count;
#endif

    assert(function->m_args_star_dict_index == -1);

    Py_ssize_t kw_found = 0;
    Py_ssize_t pos = 0;
    PyObject *key, *value;

    while (Clynton_DictNext(kw, &pos, &key, &value)) {
        if (unlikely(!checkKeywordType(key))) {
            formatErrorKeywordsMustBeString(tstate, function);
            return -1;
        }

        CLYNTON_MAY_BE_UNUSED bool found = false;

        Py_INCREF(key);
        Py_INCREF(value);

#if PYTHON_VERSION < 0x380
        Py_ssize_t kw_arg_start = 0;
#else
        Py_ssize_t kw_arg_start = function->m_args_pos_only_count;
#endif

        for (Py_ssize_t i = kw_arg_start; i < keywords_count; i++) {
            if (function->m_varnames[i] == key) {
                assert(python_pars[i] == NULL);
                python_pars[i] = value;

#if PYTHON_VERSION >= 0x300
                if (i >= keyword_after_index) {
                    *kw_only_found += 1;
                }
#endif

                found = true;
                break;
            }
        }

        if (found == false) {
            PyObject **varnames = function->m_varnames;

            for (Py_ssize_t i = kw_arg_start; i < keywords_count; i++) {
                if (RICH_COMPARE_EQ_CBOOL_ARG_NAMES(varnames[i], key)) {
                    assert(python_pars[i] == NULL);
                    python_pars[i] = value;

#if PYTHON_VERSION >= 0x300
                    if (i >= keyword_after_index) {
                        *kw_only_found += 1;
                    }
#endif

                    found = true;
                    break;
                }
            }
        }

        if (unlikely(found == false)) {
            bool pos_only_error = false;

            for (Py_ssize_t i = 0; i < kw_arg_start; i++) {
                PyObject **varnames = function->m_varnames;

                if (RICH_COMPARE_EQ_CBOOL_ARG_NAMES(varnames[i], key)) {
                    pos_only_error = true;
                    break;
                }
            }

#if PYTHON_VERSION < 0x3a0
            char const *function_name = Clynton_String_AsString(function->m_name);
#else
            char const *function_name = Clynton_String_AsString(function->m_qualname);
#endif

            if (pos_only_error == true) {
                PyErr_Format(PyExc_TypeError,
                             "%s() got some positional-only arguments passed as keyword arguments: '%s'", function_name,
                             Clynton_String_Check(key) ? Clynton_String_AsString(key) : "<non-string>");

            } else {
                PyErr_Format(PyExc_TypeError, "%s() got an unexpected keyword argument '%s'", function_name,
                             Clynton_String_Check(key) ? Clynton_String_AsString(key) : "<non-string>");
            }

            Py_DECREF(key);
            Py_DECREF(value);

            return -1;
        }

        Py_DECREF(key);

        kw_found += 1;
    }

    return kw_found;
}

#if PYTHON_VERSION < 0x300
static Py_ssize_t handleKeywordArgsSplit(struct Clynton_FunctionObject const *function, PyObject **python_pars,
                                         PyObject *const *kw_values, PyObject *kw_names)
#else
static Py_ssize_t handleKeywordArgsSplit(struct Clynton_FunctionObject const *function, PyObject **python_pars,
                                         Py_ssize_t *kw_only_found, PyObject *const *kw_values, PyObject *kw_names)
#endif
{
    Py_ssize_t keywords_count = function->m_args_keywords_count;

#if PYTHON_VERSION >= 0x300
    Py_ssize_t keyword_after_index = function->m_args_positional_count;
#endif

    assert(function->m_args_star_dict_index == -1);

    Py_ssize_t kw_found = 0;

    Py_ssize_t kw_names_size = PyTuple_GET_SIZE(kw_names);

    for (Py_ssize_t kw_index = 0; kw_index < kw_names_size; kw_index++) {
        PyObject *key = PyTuple_GET_ITEM(kw_names, kw_index);
        PyObject *value = kw_values[kw_index];

        assert(checkKeywordType(key));

        CLYNTON_MAY_BE_UNUSED bool found = false;

#if PYTHON_VERSION < 0x380
        Py_ssize_t kw_arg_start = 0;
#else
        Py_ssize_t kw_arg_start = function->m_args_pos_only_count;
#endif

        Py_INCREF(value);

        for (Py_ssize_t i = kw_arg_start; i < keywords_count; i++) {
            if (function->m_varnames[i] == key) {
                assert(python_pars[i] == NULL);
                python_pars[i] = value;

#if PYTHON_VERSION >= 0x300
                if (i >= keyword_after_index) {
                    *kw_only_found += 1;
                }
#endif

                found = true;
                break;
            }
        }

        if (found == false) {
            PyObject **varnames = function->m_varnames;

            for (Py_ssize_t i = kw_arg_start; i < keywords_count; i++) {
                // TODO: Could do better here, STR/UNICODE key knowledge being there.
                if (RICH_COMPARE_EQ_CBOOL_ARG_NAMES(varnames[i], key)) {
                    assert(python_pars[i] == NULL);
                    python_pars[i] = value;

#if PYTHON_VERSION >= 0x300
                    if (i >= keyword_after_index) {
                        *kw_only_found += 1;
                    }
#endif

                    found = true;
                    break;
                }
            }
        }

        if (unlikely(found == false)) {
            bool pos_only_error = false;

            for (Py_ssize_t i = 0; i < kw_arg_start; i++) {
                PyObject **varnames = function->m_varnames;

                if (RICH_COMPARE_EQ_CBOOL_ARG_NAMES(varnames[i], key)) {
                    pos_only_error = true;
                    break;
                }
            }

#if PYTHON_VERSION < 0x3a0
            char const *function_name = Clynton_String_AsString(function->m_name);
#else
            char const *function_name = Clynton_String_AsString(function->m_qualname);
#endif

            if (pos_only_error == true) {
                PyErr_Format(PyExc_TypeError,
                             "%s() got some positional-only arguments passed as keyword arguments: '%s'", function_name,
                             Clynton_String_Check(key) ? Clynton_String_AsString(key) : "<non-string>");

            } else {
                PyErr_Format(PyExc_TypeError, "%s() got an unexpected keyword argument '%s'", function_name,
                             Clynton_String_Check(key) ? Clynton_String_AsString(key) : "<non-string>");
            }

            Py_DECREF(value);

            return -1;
        }

        kw_found += 1;
    }

    return kw_found;
}

static PyObject *COPY_DICT_KW(PyObject *dict_value);

static bool MAKE_STAR_DICT_DICTIONARY_COPY(PyThreadState *tstate, struct Clynton_FunctionObject const *function,
                                           PyObject **python_pars, PyObject *kw) {
    Py_ssize_t star_dict_index = function->m_args_star_dict_index;
    assert(star_dict_index != -1);

    if (kw == NULL || ((PyDictObject *)kw)->ma_used == 0) {
        python_pars[star_dict_index] = MAKE_DICT_EMPTY();
    } else {
        python_pars[star_dict_index] = COPY_DICT_KW(kw);

        if (unlikely(python_pars[star_dict_index] == NULL)) {
            formatErrorKeywordsMustBeString(tstate, function);
            return false;
        }
    }

    return true;
}

#if PYTHON_VERSION < 0x300
static Py_ssize_t handleKeywordArgsWithStarDict(PyThreadState *tstate, struct Clynton_FunctionObject const *function,
                                                PyObject **python_pars, PyObject *kw)
#else
static Py_ssize_t handleKeywordArgsWithStarDict(PyThreadState *tstate, struct Clynton_FunctionObject const *function,
                                                PyObject **python_pars, Py_ssize_t *kw_only_found, PyObject *kw)
#endif
{
    assert(function->m_args_star_dict_index != -1);

    if (unlikely(MAKE_STAR_DICT_DICTIONARY_COPY(tstate, function, python_pars, kw) == false)) {
        return -1;
    }

    Py_ssize_t kw_found = 0;
    Py_ssize_t keywords_count = function->m_args_keywords_count;
#if PYTHON_VERSION >= 0x300
    Py_ssize_t keyword_after_index = function->m_args_positional_count;
#endif

    Py_ssize_t star_dict_index = function->m_args_star_dict_index;

    PyObject **varnames = function->m_varnames;

#if PYTHON_VERSION < 0x380
    Py_ssize_t kw_arg_start = 0;
#else
    Py_ssize_t kw_arg_start = function->m_args_pos_only_count;
#endif

    for (Py_ssize_t i = kw_arg_start; i < keywords_count; i++) {
        PyObject *arg_name = varnames[i];

        PyObject *kw_arg_value = DICT_GET_ITEM1(tstate, python_pars[star_dict_index], arg_name);

        if (kw_arg_value != NULL) {
            assert(python_pars[i] == NULL);

            python_pars[i] = kw_arg_value;

            DICT_REMOVE_ITEM(python_pars[star_dict_index], arg_name);

            kw_found += 1;

#if PYTHON_VERSION >= 0x300
            if (i >= keyword_after_index) {
                *kw_only_found += 1;
            }
#endif
        }
    }

    return kw_found;
}

#if PYTHON_VERSION < 0x300
static Py_ssize_t
handleKeywordArgsSplitWithStarDict(PyThreadState *tstate, struct Clynton_FunctionObject const *function,
                                   PyObject **python_pars, PyObject *const *kw_values, PyObject *kw_names)
#else
static Py_ssize_t handleKeywordArgsSplitWithStarDict(PyThreadState *tstate,
                                                     struct Clynton_FunctionObject const *function,
                                                     PyObject **python_pars, Py_ssize_t *kw_only_found,
                                                     PyObject *const *kw_values, PyObject *kw_names)
#endif
{

    Py_ssize_t star_dict_index = function->m_args_star_dict_index;
    assert(star_dict_index != -1);

    Py_ssize_t kw_names_size = PyTuple_GET_SIZE(kw_names);

    python_pars[star_dict_index] = _PyDict_NewPresized(kw_names_size);

    for (Py_ssize_t i = 0; i < kw_names_size; i++) {
        PyObject *key = PyTuple_GET_ITEM(kw_names, i);
        PyObject *value = kw_values[i];

        DICT_SET_ITEM(python_pars[star_dict_index], key, value);
    }

    Py_ssize_t kw_found = 0;
    Py_ssize_t keywords_count = function->m_args_keywords_count;
#if PYTHON_VERSION >= 0x300
    Py_ssize_t keyword_after_index = function->m_args_positional_count;
#endif

    PyObject **varnames = function->m_varnames;

#if PYTHON_VERSION < 0x380
    Py_ssize_t kw_arg_start = 0;
#else
    Py_ssize_t kw_arg_start = function->m_args_pos_only_count;
#endif

    for (Py_ssize_t i = kw_arg_start; i < keywords_count; i++) {
        PyObject *arg_name = varnames[i];

        PyObject *kw_arg_value = DICT_GET_ITEM1(tstate, python_pars[star_dict_index], arg_name);

        if (kw_arg_value != NULL) {
            assert(python_pars[i] == NULL);

            python_pars[i] = kw_arg_value;

            DICT_REMOVE_ITEM(python_pars[star_dict_index], arg_name);

            kw_found += 1;

#if PYTHON_VERSION >= 0x300
            if (i >= keyword_after_index) {
                *kw_only_found += 1;
            }
#endif
        }
    }

    return kw_found;
}

static void makeStarListTupleCopy(struct Clynton_FunctionObject const *function, PyObject **python_pars,
                                  PyObject *const *args, Py_ssize_t args_size) {
    assert(function->m_args_star_list_index != -1);
    Py_ssize_t list_star_index = function->m_args_star_list_index;

    // Copy left-over argument values to the star list parameter given.
    if (args_size > function->m_args_positional_count) {
        python_pars[list_star_index] =
            MAKE_TUPLE(&args[function->m_args_positional_count], args_size - function->m_args_positional_count);
    } else {
        python_pars[list_star_index] = const_tuple_empty;
        Py_INCREF(const_tuple_empty);
    }
}

static void makeStarListTupleCopyMethod(struct Clynton_FunctionObject const *function, PyObject **python_pars,
                                        PyObject *const *args, Py_ssize_t args_size) {
    assert(function->m_args_star_list_index != -1);
    Py_ssize_t list_star_index = function->m_args_star_list_index;

    // Copy left-over argument values to the star list parameter given.
    if (args_size + 1 > function->m_args_positional_count) {
        python_pars[list_star_index] =
            MAKE_TUPLE(&args[function->m_args_positional_count - 1], args_size + 1 - function->m_args_positional_count);
    } else {
        python_pars[list_star_index] = const_tuple_empty;
        Py_INCREF(const_tuple_empty);
    }
}

static bool _handleArgumentsPlainOnly(PyThreadState *tstate, struct Clynton_FunctionObject const *function,
                                      PyObject **python_pars, PyObject *const *args, Py_ssize_t args_size) {
    Py_ssize_t arg_count = function->m_args_positional_count;

    // Check if too many arguments were given in case of non list star arg.
    // For Python3.3 it's done only later, when more knowledge has
    // been gained. TODO: Could be done this way for improved mode
    // on all versions.
#if PYTHON_VERSION < 0x300
    if (function->m_args_star_list_index == -1) {
        if (unlikely(args_size > arg_count)) {
#if PYTHON_VERSION < 0x270
            formatErrorTooManyArguments(function, args_size, 0);
#else
            formatErrorTooManyArguments(function, args_size);
#endif
            return false;
        }
    }
#endif

#if PYTHON_VERSION >= 0x300
    bool parameter_error = false;
#endif

    Py_ssize_t defaults_given = function->m_defaults_given;

    if (args_size + defaults_given < arg_count) {
#if PYTHON_VERSION < 0x270
        formatErrorTooFewArguments(tstate, function, 0, args_size);
        return false;
#elif PYTHON_VERSION < 0x300
        formatErrorTooFewArguments(tstate, function, args_size);
        return false;
#else
        parameter_error = true;
#endif
    }

    for (Py_ssize_t i = 0; i < args_size; i++) {
        if (i >= arg_count)
            break;

        assert(python_pars[i] == NULL);

        python_pars[i] = args[i];
        Py_INCREF(python_pars[i]);
    }

#if PYTHON_VERSION >= 0x300
    if (parameter_error == false) {
#endif
        PyObject *source = function->m_defaults;

        for (Py_ssize_t i = args_size; i < arg_count; i++) {
            assert(python_pars[i] == NULL);
            assert(i + defaults_given >= arg_count);

            python_pars[i] = PyTuple_GET_ITEM(source, defaults_given + i - arg_count);
            Py_INCREF(python_pars[i]);
        }
#if PYTHON_VERSION >= 0x300
    }
#endif

#if PYTHON_VERSION >= 0x300
    if (unlikely(parameter_error)) {
        formatErrorTooFewArguments(tstate, function, python_pars);
        return false;
    }

    if (function->m_args_star_list_index == -1) {
        // Check if too many arguments were given in case of non list star arg
        if (unlikely(args_size > arg_count)) {
            formatErrorTooManyArguments(function, args_size, 0);
            return false;
        }
    }
#endif

    if (function->m_args_star_list_index != -1) {
        makeStarListTupleCopy(function, python_pars, args, args_size);
    }

    return true;
}

static bool handleMethodArgumentsPlainOnly(PyThreadState *tstate, struct Clynton_FunctionObject const *function,
                                           PyObject **python_pars, PyObject *object, PyObject *const *args,
                                           Py_ssize_t args_size) {
    Py_ssize_t arg_count = function->m_args_positional_count;

    // There may be no self, otherwise we can directly assign it.
    if (arg_count >= 1) {
        python_pars[0] = object;
        Py_INCREF(object);
    } else {
        // Without self, there can only be star list to get the object as its
        // first element. Or we complain about illegal arguments.
        if (function->m_args_star_list_index == 0) {
            python_pars[0] = MAKE_TUPLE_EMPTY(args_size + 1);
            PyTuple_SET_ITEM0(python_pars[0], 0, object);

            for (Py_ssize_t i = 0; i < args_size; i++) {
                PyTuple_SET_ITEM0(python_pars[0], i + 1, args[i]);
            }

            return true;
        }
    }

    // Check if too many arguments were given in case of non list star arg.
    // For Python3.3 it's done only later, when more knowledge has
    // been gained. TODO: Could be done this way for improved mode
    // on all versions.
#if PYTHON_VERSION < 0x300
    if (function->m_args_star_list_index == -1) {
        if (unlikely(args_size + 1 > arg_count)) {
#if PYTHON_VERSION < 0x270
            formatErrorTooManyArguments(function, args_size + 1, 0);
#else
            formatErrorTooManyArguments(function, args_size + 1);
#endif
            return false;
        }
    }
#endif

#if PYTHON_VERSION >= 0x300
    bool parameter_error = false;
#endif
    Py_ssize_t defaults_given = function->m_defaults_given;

    if (args_size + 1 + defaults_given < arg_count) {
#if PYTHON_VERSION < 0x270
        formatErrorTooFewArguments(tstate, function, 0, args_size + 1);
        return false;
#elif PYTHON_VERSION < 0x300
        formatErrorTooFewArguments(tstate, function, args_size + 1);
        return false;
#else
        parameter_error = true;
#endif
    }

    for (Py_ssize_t i = 0; i < args_size; i++) {
        if (i + 1 >= arg_count)
            break;

        assert(python_pars[i + 1] == NULL);

        python_pars[i + 1] = args[i];
        Py_INCREF(python_pars[i + 1]);
    }

#if PYTHON_VERSION >= 0x300
    if (parameter_error == false) {
#endif
        for (Py_ssize_t i = args_size + 1; i < arg_count; i++) {
            assert(python_pars[i] == NULL);
            assert(i + defaults_given >= arg_count);

            python_pars[i] = PyTuple_GET_ITEM(function->m_defaults, defaults_given + i - arg_count);
            Py_INCREF(python_pars[i]);
        }
#if PYTHON_VERSION >= 0x300
    }
#endif

#if PYTHON_VERSION >= 0x300
    if (unlikely(parameter_error)) {
        formatErrorTooFewArguments(tstate, function, python_pars);
        return false;
    }

    if (function->m_args_star_list_index == -1) {
        // Check if too many arguments were given in case of non list star arg
        if (unlikely(args_size + 1 > arg_count)) {
            formatErrorTooManyArguments(function, args_size + 1, 0);
            return false;
        }
    }
#endif

    if (function->m_args_star_list_index != -1) {
        makeStarListTupleCopyMethod(function, python_pars, args, args_size);
    }

    return true;
}

#if PYTHON_VERSION < 0x270
static bool _handleArgumentsPlain(PyThreadState *tstate, struct Clynton_FunctionObject const *function,
                                  PyObject **python_pars, PyObject *const *args, Py_ssize_t args_size,
                                  Py_ssize_t kw_found, Py_ssize_t kw_size)
#elif PYTHON_VERSION < 0x300
static bool _handleArgumentsPlain(PyThreadState *tstate, struct Clynton_FunctionObject const *function,
                                  PyObject **python_pars, PyObject *const *args, Py_ssize_t args_size,
                                  Py_ssize_t kw_found)
#else
static bool _handleArgumentsPlain(PyThreadState *tstate, struct Clynton_FunctionObject const *function,
                                  PyObject **python_pars, PyObject *const *args, Py_ssize_t args_size,
                                  Py_ssize_t kw_found, Py_ssize_t kw_only_found)
#endif
{
    Py_ssize_t arg_count = function->m_args_positional_count;

    // Check if too many arguments were given in case of non list star arg.
    // For Python3.3 it's done only later, when more knowledge has
    // been gained. TODO: Could be done this way for improved mode
    // on all versions.
#if PYTHON_VERSION < 0x300
    if (function->m_args_star_list_index == -1) {
        if (unlikely(args_size > arg_count)) {
#if PYTHON_VERSION < 0x270
            formatErrorTooManyArguments(function, args_size, kw_size);
#else
            formatErrorTooManyArguments(function, args_size + kw_found);
#endif
            return false;
        }
    }
#endif

#if PYTHON_VERSION >= 0x300
    bool parameter_error = false;
#endif

    if (kw_found > 0) {
        Py_ssize_t i;
        for (i = 0; i < (args_size < arg_count ? args_size : arg_count); i++) {
            if (unlikely(python_pars[i] != NULL)) {
                formatErrorMultipleValuesGiven(function, i);
                return false;
            }

            python_pars[i] = args[i];
            Py_INCREF(python_pars[i]);
        }

        Py_ssize_t defaults_given = function->m_defaults_given;

        for (; i < arg_count; i++) {
            if (python_pars[i] == NULL) {

                if (i + defaults_given >= arg_count) {
                    python_pars[i] = PyTuple_GET_ITEM(function->m_defaults, defaults_given + i - arg_count);
                    Py_INCREF(python_pars[i]);
                } else {
#if PYTHON_VERSION < 0x270
                    formatErrorTooFewArguments(tstate, function, kw_size, args_size + kw_found);
                    return false;
#elif PYTHON_VERSION < 0x300
                    formatErrorTooFewArguments(tstate, function, args_size + kw_found);
                    return false;
#else
                    parameter_error = true;
#endif
                }
            }
        }
    } else {
        Py_ssize_t usable = (args_size < arg_count ? args_size : arg_count);
        Py_ssize_t defaults_given = function->m_defaults_given;

        if (defaults_given < arg_count - usable) {
#if PYTHON_VERSION < 0x270
            formatErrorTooFewArguments(tstate, function, kw_size, args_size + kw_found);
            return false;
#elif PYTHON_VERSION < 0x300
            formatErrorTooFewArguments(tstate, function, args_size + kw_found);
            return false;
#else
            parameter_error = true;
#endif
        }

        for (Py_ssize_t i = 0; i < usable; i++) {
            assert(python_pars[i] == NULL);

            python_pars[i] = args[i];
            Py_INCREF(python_pars[i]);
        }

#if PYTHON_VERSION >= 0x300
        if (parameter_error == false) {
#endif
            for (Py_ssize_t i = usable; i < arg_count; i++) {
                assert(python_pars[i] == NULL);
                assert(i + defaults_given >= arg_count);

                python_pars[i] = PyTuple_GET_ITEM(function->m_defaults, defaults_given + i - arg_count);
                Py_INCREF(python_pars[i]);
            }
#if PYTHON_VERSION >= 0x300
        }
#endif
    }

#if PYTHON_VERSION >= 0x300
    if (unlikely(parameter_error)) {
        formatErrorTooFewArguments(tstate, function, python_pars);
        return false;
    }

    if (function->m_args_star_list_index == -1) {
        // Check if too many arguments were given in case of non list star arg
        if (unlikely(args_size > arg_count)) {
            formatErrorTooManyArguments(function, args_size, kw_only_found);
            return false;
        }
    }
#endif

    if (function->m_args_star_list_index != -1) {
        makeStarListTupleCopy(function, python_pars, args, args_size);
    }

    return true;
}

// Release them all in case of an error.
static void releaseParameters(struct Clynton_FunctionObject const *function, PyObject *const *python_pars) {
    Py_ssize_t arg_count = function->m_args_overall_count;

    for (Py_ssize_t i = 0; i < arg_count; i++) {
        Py_XDECREF(python_pars[i]);
    }
}

static bool parseArgumentsPos(PyThreadState *tstate, struct Clynton_FunctionObject const *function,
                              PyObject **python_pars, PyObject *const *args, Py_ssize_t args_size) {
    bool result;

    Py_ssize_t arg_count = function->m_args_positional_count;

    if (unlikely(arg_count == 0 && function->m_args_simple && args_size != 0)) {
#if PYTHON_VERSION < 0x300
        formatErrorNoArgumentAllowed(function, args_size);
#else
        formatErrorNoArgumentAllowed(function, NULL, args_size);
#endif

        releaseParameters(function, python_pars);
        return false;
    }

    result = _handleArgumentsPlainOnly(tstate, function, python_pars, args, args_size);

    if (result == false) {
        releaseParameters(function, python_pars);
        return false;
    }

#if PYTHON_VERSION >= 0x300
    // For Python3.3 the keyword only errors are all reported at once.
    bool kw_only_error = false;

    for (Py_ssize_t i = function->m_args_positional_count; i < function->m_args_keywords_count; i++) {
        if (python_pars[i] == NULL) {
            PyObject *arg_name = function->m_varnames[i];

            if (function->m_kwdefaults != NULL) {
                python_pars[i] = DICT_GET_ITEM1(tstate, function->m_kwdefaults, arg_name);
            }

            if (unlikely(python_pars[i] == NULL)) {
                kw_only_error = true;
            }
        }
    }

    if (unlikely(kw_only_error)) {
        formatErrorTooFewKwOnlyArguments(tstate, function, &python_pars[function->m_args_positional_count]);

        releaseParameters(function, python_pars);
        return false;
    }

#endif

    if (function->m_args_star_dict_index != -1) {
        python_pars[function->m_args_star_dict_index] = MAKE_DICT_EMPTY();
    }

    return true;
}

// We leave it to partial inlining to specialize this.
static bool parseArgumentsEmpty(PyThreadState *tstate, struct Clynton_FunctionObject const *function,
                                PyObject **python_pars) {
    return parseArgumentsPos(tstate, function, python_pars, NULL, 0);
}

static bool parseArgumentsMethodPos(PyThreadState *tstate, struct Clynton_FunctionObject const *function,
                                    PyObject **python_pars, PyObject *object, PyObject *const *args,
                                    Py_ssize_t args_size) {
    bool result;

    result = handleMethodArgumentsPlainOnly(tstate, function, python_pars, object, args, args_size);

    if (result == false) {
        releaseParameters(function, python_pars);
        return false;
    }

#if PYTHON_VERSION >= 0x300
    // For Python3 the keyword only errors are all reported at once.
    bool kw_only_error = false;

    for (Py_ssize_t i = function->m_args_positional_count; i < function->m_args_keywords_count; i++) {
        if (python_pars[i] == NULL) {
            PyObject *arg_name = function->m_varnames[i];

            if (function->m_kwdefaults != NULL) {
                python_pars[i] = DICT_GET_ITEM1(tstate, function->m_kwdefaults, arg_name);
            }

            if (unlikely(python_pars[i] == NULL)) {
                kw_only_error = true;
            }
        }
    }

    if (unlikely(kw_only_error)) {
        formatErrorTooFewKwOnlyArguments(tstate, function, &python_pars[function->m_args_positional_count]);

        releaseParameters(function, python_pars);
        return false;
    }

#endif

    if (function->m_args_star_dict_index != -1) {
        python_pars[function->m_args_star_dict_index] = MAKE_DICT_EMPTY();
    }

    return true;
}

static bool parseArgumentsFullKwSplit(PyThreadState *tstate, struct Clynton_FunctionObject const *function,
                                      PyObject **python_pars, PyObject *const *args, Py_ssize_t args_size,
                                      PyObject *const *kw_values, PyObject *kw_names) {
    Py_ssize_t kw_size = PyTuple_GET_SIZE(kw_names);
    Py_ssize_t kw_found;
    bool result;

    Py_ssize_t arg_count = function->m_args_keywords_count;

    if (unlikely(arg_count == 0 && function->m_args_simple && args_size + kw_size > 0)) {
#if PYTHON_VERSION < 0x300
        formatErrorNoArgumentAllowed(function, args_size + kw_size);
#else
        formatErrorNoArgumentAllowedKwSplit(function, PyTuple_GET_ITEM(kw_names, 0), args_size);
#endif

        releaseParameters(function, python_pars);
        return false;
    }

#if PYTHON_VERSION >= 0x300
    Py_ssize_t kw_only_found = 0;
#endif
    if (function->m_args_star_dict_index != -1) {
#if PYTHON_VERSION < 0x300
        kw_found = handleKeywordArgsSplitWithStarDict(tstate, function, python_pars, kw_values, kw_names);
#else
        kw_found =
            handleKeywordArgsSplitWithStarDict(tstate, function, python_pars, &kw_only_found, kw_values, kw_names);
#endif
        if (unlikely(kw_found == -1)) {
            releaseParameters(function, python_pars);
            return false;
        }
    } else {
#if PYTHON_VERSION < 0x300
        kw_found = handleKeywordArgsSplit(function, python_pars, kw_values, kw_names);
#else
        kw_found = handleKeywordArgsSplit(function, python_pars, &kw_only_found, kw_values, kw_names);
#endif
        if (unlikely(kw_found == -1)) {
            releaseParameters(function, python_pars);
            return false;
        }
    }

#if PYTHON_VERSION < 0x270
    result = _handleArgumentsPlain(tstate, function, python_pars, args, args_size, kw_found, kw_size);
#elif PYTHON_VERSION < 0x300
    result = _handleArgumentsPlain(tstate, function, python_pars, args, args_size, kw_found);
#else
    result = _handleArgumentsPlain(tstate, function, python_pars, args, args_size, kw_found, kw_only_found);
#endif

    if (result == false) {
        releaseParameters(function, python_pars);
        return false;
    }

#if PYTHON_VERSION >= 0x300
    // For Python3.3 the keyword only errors are all reported at once.
    bool kw_only_error = false;

    for (Py_ssize_t i = function->m_args_positional_count; i < function->m_args_keywords_count; i++) {
        if (python_pars[i] == NULL) {
            PyObject *arg_name = function->m_varnames[i];

            if (function->m_kwdefaults != NULL) {
                python_pars[i] = DICT_GET_ITEM1(tstate, function->m_kwdefaults, arg_name);
            }

            if (unlikely(python_pars[i] == NULL)) {
                kw_only_error = true;
            }
        }
    }

    if (unlikely(kw_only_error)) {
        formatErrorTooFewKwOnlyArguments(tstate, function, &python_pars[function->m_args_positional_count]);

        releaseParameters(function, python_pars);
        return false;
    }

#endif

    return true;
}

static bool parseArgumentsFull(PyThreadState *tstate, struct Clynton_FunctionObject const *function,
                               PyObject **python_pars, PyObject *const *args, Py_ssize_t args_size, PyObject *kw) {
    Py_ssize_t kw_size = kw ? DICT_SIZE(kw) : 0;
    Py_ssize_t kw_found;
    bool result;

    Py_ssize_t arg_count = function->m_args_keywords_count;

    assert(kw == NULL || PyDict_CheckExact(kw));

    if (unlikely(arg_count == 0 && function->m_args_simple && args_size + kw_size > 0)) {
#if PYTHON_VERSION < 0x300
        formatErrorNoArgumentAllowed(function, args_size + kw_size);
#else
        formatErrorNoArgumentAllowed(function, kw_size > 0 ? kw : NULL, args_size);
#endif

        releaseParameters(function, python_pars);
        return false;
    }

#if PYTHON_VERSION >= 0x300
    Py_ssize_t kw_only_found = 0;
#endif
    if (function->m_args_star_dict_index != -1) {
#if PYTHON_VERSION < 0x300
        kw_found = handleKeywordArgsWithStarDict(tstate, function, python_pars, kw);
#else
        kw_found = handleKeywordArgsWithStarDict(tstate, function, python_pars, &kw_only_found, kw);
#endif
        if (unlikely(kw_found == -1)) {
            releaseParameters(function, python_pars);
            return false;
        }
    } else if (kw == NULL || DICT_SIZE(kw) == 0) {
        kw_found = 0;
    } else {
#if PYTHON_VERSION < 0x300
        kw_found = handleKeywordArgs(tstate, function, python_pars, kw);
#else
        kw_found = handleKeywordArgs(tstate, function, python_pars, &kw_only_found, kw);
#endif
        if (unlikely(kw_found == -1)) {
            releaseParameters(function, python_pars);
            return false;
        }
    }

#if PYTHON_VERSION < 0x270
    result = _handleArgumentsPlain(tstate, function, python_pars, args, args_size, kw_found, kw_size);
#elif PYTHON_VERSION < 0x300
    result = _handleArgumentsPlain(tstate, function, python_pars, args, args_size, kw_found);
#else
    result = _handleArgumentsPlain(tstate, function, python_pars, args, args_size, kw_found, kw_only_found);
#endif

    if (result == false) {
        releaseParameters(function, python_pars);
        return false;
    }

#if PYTHON_VERSION >= 0x300
    // For Python3.3 the keyword only errors are all reported at once.
    bool kw_only_error = false;

    for (Py_ssize_t i = function->m_args_positional_count; i < function->m_args_keywords_count; i++) {
        if (python_pars[i] == NULL) {
            PyObject *arg_name = function->m_varnames[i];

            if (function->m_kwdefaults != NULL) {
                python_pars[i] = DICT_GET_ITEM1(tstate, function->m_kwdefaults, arg_name);
            }

            if (unlikely(python_pars[i] == NULL)) {
                kw_only_error = true;
            }
        }
    }

    if (unlikely(kw_only_error)) {
        formatErrorTooFewKwOnlyArguments(tstate, function, &python_pars[function->m_args_positional_count]);

        releaseParameters(function, python_pars);
        return false;
    }

#endif

    return true;
}

PyObject *Clynton_CallFunctionNoArgs(PyThreadState *tstate, struct Clynton_FunctionObject const *function) {
    CLYNTON_DYNAMIC_ARRAY_DECL(python_pars, PyObject *, function->m_args_overall_count);
    memset(python_pars, 0, function->m_args_overall_count * sizeof(PyObject *));

    if (unlikely(!parseArgumentsEmpty(tstate, function, python_pars))) {
        return NULL;
    }

    return function->m_c_code(tstate, function, python_pars);
}

PyObject *Clynton_CallFunctionPosArgs(PyThreadState *tstate, struct Clynton_FunctionObject const *function,
                                     PyObject *const *args, Py_ssize_t args_size) {
    CLYNTON_DYNAMIC_ARRAY_DECL(python_pars, PyObject *, function->m_args_overall_count);
    memset(python_pars, 0, function->m_args_overall_count * sizeof(PyObject *));

    if (unlikely(!parseArgumentsPos(tstate, function, python_pars, args, args_size))) {
        return NULL;
    }

    return function->m_c_code(tstate, function, python_pars);
}

PyObject *Clynton_CallFunctionPosArgsKwArgs(PyThreadState *tstate, struct Clynton_FunctionObject const *function,
                                           PyObject *const *args, Py_ssize_t args_size, PyObject *kw) {
    CLYNTON_DYNAMIC_ARRAY_DECL(python_pars, PyObject *, function->m_args_overall_count);
    memset(python_pars, 0, function->m_args_overall_count * sizeof(PyObject *));

    if (unlikely(!parseArgumentsFull(tstate, function, python_pars, args, args_size, kw))) {
        return NULL;
    }

    return function->m_c_code(tstate, function, python_pars);
}

PyObject *Clynton_CallFunctionPosArgsKwSplit(PyThreadState *tstate, struct Clynton_FunctionObject const *function,
                                            PyObject *const *args, Py_ssize_t args_size, PyObject *const *kw_values,
                                            PyObject *kw_names) {
    CLYNTON_DYNAMIC_ARRAY_DECL(python_pars, PyObject *, function->m_args_overall_count);
    memset(python_pars, 0, function->m_args_overall_count * sizeof(PyObject *));

    if (unlikely(!parseArgumentsFullKwSplit(tstate, function, python_pars, args, args_size, kw_values, kw_names))) {
        return NULL;
    }

    return function->m_c_code(tstate, function, python_pars);
}

PyObject *Clynton_CallMethodFunctionNoArgs(PyThreadState *tstate, struct Clynton_FunctionObject const *function,
                                          PyObject *object) {
    CLYNTON_DYNAMIC_ARRAY_DECL(python_pars, PyObject *, function->m_args_overall_count);
    memset(python_pars, 0, function->m_args_overall_count * sizeof(PyObject *));

    if (unlikely(!parseArgumentsMethodPos(tstate, function, python_pars, object, NULL, 0))) {
        return NULL;
    }

    return function->m_c_code(tstate, function, python_pars);
}

PyObject *Clynton_CallMethodFunctionPosArgs(PyThreadState *tstate, struct Clynton_FunctionObject const *function,
                                           PyObject *object, PyObject *const *args, Py_ssize_t args_size) {
    CLYNTON_DYNAMIC_ARRAY_DECL(python_pars, PyObject *, function->m_args_overall_count);
    memset(python_pars, 0, function->m_args_overall_count * sizeof(PyObject *));

    if (unlikely(!parseArgumentsMethodPos(tstate, function, python_pars, object, args, args_size))) {
        return NULL;
    }

    return function->m_c_code(tstate, function, python_pars);
}

PyObject *Clynton_CallMethodFunctionPosArgsKwArgs(PyThreadState *tstate, struct Clynton_FunctionObject const *function,
                                                 PyObject *object, PyObject *const *args, Py_ssize_t args_size,
                                                 PyObject *kw) {
    CLYNTON_DYNAMIC_ARRAY_DECL(new_args, PyObject *, args_size + 1);

    new_args[0] = object;
    memcpy(new_args + 1, args, args_size * sizeof(PyObject *));

    // TODO: Specialize implementation for massive gains.
    return Clynton_CallFunctionPosArgsKwArgs(tstate, function, new_args, args_size + 1, kw);
}

static Py_ssize_t _handleVectorcallKeywordArgs(PyThreadState *tstate, struct Clynton_FunctionObject const *function,
                                               PyObject **python_pars, Py_ssize_t *kw_only_found,
                                               PyObject *const *kw_names, PyObject *const *kw_values,
                                               Py_ssize_t kw_size) {
    Py_ssize_t keywords_count = function->m_args_keywords_count;

    Py_ssize_t keyword_after_index = function->m_args_positional_count;

    assert(function->m_args_star_dict_index == -1);

    Py_ssize_t kw_found = 0;

    for (Py_ssize_t pos = 0; pos < kw_size; pos++) {
        PyObject *key = kw_names[pos];

        if (unlikely(!checkKeywordType(key))) {
            formatErrorKeywordsMustBeString(tstate, function);
            return -1;
        }

        CLYNTON_MAY_BE_UNUSED bool found = false;

#if PYTHON_VERSION < 0x380
        Py_ssize_t kw_arg_start = 0;
#else
        Py_ssize_t kw_arg_start = function->m_args_pos_only_count;
#endif

        for (Py_ssize_t i = kw_arg_start; i < keywords_count; i++) {
            if (function->m_varnames[i] == key) {
                assert(python_pars[i] == NULL);
                python_pars[i] = kw_values[pos];
                Py_INCREF(python_pars[i]);

                if (i >= keyword_after_index) {
                    *kw_only_found += 1;
                }

                found = true;
                break;
            }
        }

        if (found == false) {
            PyObject **varnames = function->m_varnames;

            for (Py_ssize_t i = kw_arg_start; i < keywords_count; i++) {
                if (RICH_COMPARE_EQ_CBOOL_ARG_NAMES(varnames[i], key)) {
                    assert(python_pars[i] == NULL);
                    python_pars[i] = kw_values[pos];
                    Py_INCREF(python_pars[i]);

                    if (i >= keyword_after_index) {
                        *kw_only_found += 1;
                    }

                    found = true;
                    break;
                }
            }
        }

        if (unlikely(found == false)) {
            bool pos_only_error = false;

            for (Py_ssize_t i = 0; i < kw_arg_start; i++) {
                PyObject **varnames = function->m_varnames;

                if (RICH_COMPARE_EQ_CBOOL_ARG_NAMES(varnames[i], key)) {
                    pos_only_error = true;
                    break;
                }
            }

#if PYTHON_VERSION < 0x3a0
            char const *function_name = Clynton_String_AsString(function->m_name);
#else
            char const *function_name = Clynton_String_AsString(function->m_qualname);
#endif

            if (pos_only_error == true) {
                PyErr_Format(PyExc_TypeError,
                             "%s() got some positional-only arguments passed as keyword arguments: '%s'", function_name,
                             Clynton_String_Check(key) ? Clynton_String_AsString(key) : "<non-string>");

            } else {
                PyErr_Format(PyExc_TypeError, "%s() got an unexpected keyword argument '%s'", function_name,
                             Clynton_String_Check(key) ? Clynton_String_AsString(key) : "<non-string>");
            }

            return -1;
        }

        kw_found += 1;
    }

    return kw_found;
}

static bool MAKE_STAR_DICT_DICTIONARY_COPY38(PyThreadState *tstate, struct Clynton_FunctionObject const *function,
                                             PyObject **python_pars, PyObject *const *kw_names,
                                             PyObject *const *kw_values, Py_ssize_t kw_size) {
    Py_ssize_t star_dict_index = function->m_args_star_dict_index;
    assert(star_dict_index != -1);

    python_pars[star_dict_index] = _PyDict_NewPresized(kw_size);

    for (int i = 0; i < kw_size; i++) {
        PyObject *key = kw_names[i];

        if (unlikely(!checkKeywordType(key))) {
            formatErrorKeywordsMustBeString(tstate, function);
            return false;
        }

        bool result = DICT_SET_ITEM(python_pars[star_dict_index], key, kw_values[i]);

        if (unlikely(result == false)) {
            return false;
        }
    }

    return true;
}

static Py_ssize_t handleVectorcallKeywordArgsWithStarDict(PyThreadState *tstate,
                                                          struct Clynton_FunctionObject const *function,
                                                          PyObject **python_pars, Py_ssize_t *kw_only_found,
                                                          PyObject *const *kw_names, PyObject *const *kw_values,
                                                          Py_ssize_t kw_size) {
    assert(function->m_args_star_dict_index != -1);

    if (unlikely(MAKE_STAR_DICT_DICTIONARY_COPY38(tstate, function, python_pars, kw_names, kw_values, kw_size) ==
                 false)) {
        return -1;
    }

    Py_ssize_t kw_found = 0;
    Py_ssize_t keywords_count = function->m_args_keywords_count;
    Py_ssize_t keyword_after_index = function->m_args_positional_count;

    Py_ssize_t star_dict_index = function->m_args_star_dict_index;

    PyObject **varnames = function->m_varnames;

#if PYTHON_VERSION < 0x380
    Py_ssize_t kw_arg_start = 0;
#else
    Py_ssize_t kw_arg_start = function->m_args_pos_only_count;
#endif

    for (Py_ssize_t i = kw_arg_start; i < keywords_count; i++) {
        PyObject *arg_name = varnames[i];

        PyObject *kw_arg_value = DICT_GET_ITEM1(tstate, python_pars[star_dict_index], arg_name);

        if (kw_arg_value != NULL) {
            assert(python_pars[i] == NULL);

            python_pars[i] = kw_arg_value;

            DICT_REMOVE_ITEM(python_pars[star_dict_index], arg_name);

            kw_found += 1;

            if (i >= keyword_after_index) {
                *kw_only_found += 1;
            }
        }
    }

    return kw_found;
}

static bool parseArgumentsVectorcall(PyThreadState *tstate, struct Clynton_FunctionObject const *function,
                                     PyObject **python_pars, PyObject *const *args, Py_ssize_t args_size,
                                     PyObject *const *kw_names, Py_ssize_t kw_size) {
    Py_ssize_t kw_found;
    bool result;
    Py_ssize_t kw_only_found;

    Py_ssize_t arg_count = function->m_args_keywords_count;

    // TODO: Create different the vector call slot entries for different function types for extra
    // performance.

    if (unlikely(arg_count == 0 && function->m_args_simple && args_size + kw_size > 0)) {
#if PYTHON_VERSION < 0x3a0
        char const *function_name = Clynton_String_AsString(function->m_name);
#else
        char const *function_name = Clynton_String_AsString(function->m_qualname);
#endif

        if (kw_size == 0) {
            PyErr_Format(PyExc_TypeError, "%s() takes 0 positional arguments but %zd was given", function_name,
                         args_size);
        } else {
            PyErr_Format(PyExc_TypeError, "%s() got an unexpected keyword argument '%s'", function_name,
                         Clynton_String_AsString(kw_names[0]));
        }

        releaseParameters(function, python_pars);
        return false;
    }

    kw_only_found = 0;
    if (function->m_args_star_dict_index != -1) {
        kw_found = handleVectorcallKeywordArgsWithStarDict(tstate, function, python_pars, &kw_only_found, kw_names,
                                                           &args[args_size], kw_size);
        if (unlikely(kw_found == -1)) {
            releaseParameters(function, python_pars);
            return false;
        }
    } else if (kw_size == 0) {
        kw_found = 0;
    } else {
        kw_found = _handleVectorcallKeywordArgs(tstate, function, python_pars, &kw_only_found, kw_names,
                                                &args[args_size], kw_size);

        if (unlikely(kw_found == -1)) {
            releaseParameters(function, python_pars);
            return false;
        }
    }

#if PYTHON_VERSION < 0x270
    result = _handleArgumentsPlain(tstate, function, python_pars, args, args_size, kw_found, kw_size);
#elif PYTHON_VERSION < 0x300
    result = _handleArgumentsPlain(tstate, function, python_pars, args, args_size, kw_found);
#else
    result = _handleArgumentsPlain(tstate, function, python_pars, args, args_size, kw_found, kw_only_found);
#endif

    if (result == false) {
        releaseParameters(function, python_pars);
        return false;
    }

#if PYTHON_VERSION >= 0x300
    // For Python3 the keyword only errors are all reported at once.
    bool kw_only_error = false;

    for (Py_ssize_t i = function->m_args_positional_count; i < function->m_args_keywords_count; i++) {
        if (python_pars[i] == NULL) {
            PyObject *arg_name = function->m_varnames[i];

            if (function->m_kwdefaults != NULL) {
                python_pars[i] = DICT_GET_ITEM1(tstate, function->m_kwdefaults, arg_name);
            }

            if (unlikely(python_pars[i] == NULL)) {
                kw_only_error = true;
            }
        }
    }

    if (unlikely(kw_only_error)) {
        formatErrorTooFewKwOnlyArguments(tstate, function, &python_pars[function->m_args_positional_count]);

        releaseParameters(function, python_pars);
        return false;
    }
#endif

    return true;
}

PyObject *Clynton_CallFunctionVectorcall(PyThreadState *tstate, struct Clynton_FunctionObject const *function,
                                        PyObject *const *args, Py_ssize_t args_size, PyObject *const *kw_names,
                                        Py_ssize_t kw_size) {
    CLYNTON_DYNAMIC_ARRAY_DECL(python_pars, PyObject *, function->m_args_overall_count);
    memset(python_pars, 0, function->m_args_overall_count * sizeof(PyObject *));

    if (unlikely(!parseArgumentsVectorcall(tstate, function, python_pars, args, args_size, kw_names, kw_size))) {
        return NULL;
    }
    return function->m_c_code(tstate, function, python_pars);
}

static PyObject *Clynton_Function_tp_call(struct Clynton_FunctionObject *function, PyObject *tuple_args, PyObject *kw) {
    CHECK_OBJECT(tuple_args);
    assert(PyTuple_CheckExact(tuple_args));

    PyThreadState *tstate = PyThreadState_GET();

    if (kw == NULL) {
        PyObject **args = &PyTuple_GET_ITEM(tuple_args, 0);
        Py_ssize_t args_size = PyTuple_GET_SIZE(tuple_args);

        if (function->m_args_simple && args_size == function->m_args_positional_count) {
            for (Py_ssize_t i = 0; i < args_size; i++) {
                Py_INCREF(args[i]);
            }

            return function->m_c_code(tstate, function, args);
        } else if (function->m_args_simple &&
                   args_size + function->m_defaults_given == function->m_args_positional_count) {
            CLYNTON_DYNAMIC_ARRAY_DECL(python_pars, PyObject *, function->m_args_overall_count);
            memcpy(python_pars, args, args_size * sizeof(PyObject *));
            memcpy(python_pars + args_size, &PyTuple_GET_ITEM(function->m_defaults, 0),
                   function->m_defaults_given * sizeof(PyObject *));

            for (Py_ssize_t i = 0; i < function->m_args_overall_count; i++) {
                Py_INCREF(python_pars[i]);
            }

            return function->m_c_code(tstate, function, python_pars);
        } else {
            CLYNTON_DYNAMIC_ARRAY_DECL(python_pars, PyObject *, function->m_args_overall_count);
            memset(python_pars, 0, function->m_args_overall_count * sizeof(PyObject *));

            if (parseArgumentsPos(tstate, function, python_pars, args, args_size)) {
                return function->m_c_code(tstate, function, python_pars);
            } else {
                return NULL;
            }
        }
    } else {
        return Clynton_CallFunctionPosArgsKwArgs(tstate, function, &PyTuple_GET_ITEM(tuple_args, 0),
                                                PyTuple_GET_SIZE(tuple_args), kw);
    }
}

#if PYTHON_VERSION >= 0x380 && !defined(_CLYNTON_EXPERIMENTAL_DISABLE_VECTORCALL_SLOT)
static PyObject *Clynton_Function_tp_vectorcall(struct Clynton_FunctionObject *function, PyObject *const *stack,
                                               size_t nargsf, PyObject *kw_names) {
    assert(kw_names == NULL || PyTuple_CheckExact(kw_names));
    Py_ssize_t nkwargs = (kw_names == NULL) ? 0 : PyTuple_GET_SIZE(kw_names);

    Py_ssize_t nargs = PyVectorcall_NARGS(nargsf);
    assert(nargs >= 0);
    assert((nargs == 0 && nkwargs == 0) || stack != NULL);

    PyThreadState *tstate = PyThreadState_GET();
    return Clynton_CallFunctionVectorcall(tstate, function, stack, nargs,
                                         kw_names ? &PyTuple_GET_ITEM(kw_names, 0) : NULL, nkwargs);
}
#endif

#include "CompiledMethodType.c"

#include "CompiledGeneratorType.c"

#include "CompiledCellType.c"

#include "CompiledCodeHelpers.c"

#include "InspectPatcher.c"