//     Copyright 2023, Kay Hayen, mailto:kay.hayen@gmail.com
//
//     Part of "Clynton", an optimizing Python compiler that is compatible and
//     integrates with CPython, but also works on its own.
//
//     Licensed under the Apache License, Version 2.0 (the "License");
//     you may not use this file except in compliance with the License.
//     You may obtain a copy of the License at
//
//        http://www.apache.org/licenses/LICENSE-2.0
//
//     Unless required by applicable law or agreed to in writing, software
//     distributed under the License is distributed on an "AS IS" BASIS,
//     WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
//     See the License for the specific language governing permissions and
//     limitations under the License.
//
#ifndef __CLYNTON_COMPILED_FRAME_H__
#define __CLYNTON_COMPILED_FRAME_H__

/* This file is included from another C file, help IDEs to still parse it on its own. */
#ifdef __IDE_ONLY__
#include "clynton/prelude.h"
#endif

// Removed flag in 3.11, but we keep code compatible for now. We do not use old
// value, but 0 because it might get re-used. TODO: Probably better to #ifdef
// usages of it away.
#if PYTHON_VERSION >= 0x3b0
#define CO_NOFREE 0
#endif

// With Python 3.11 or higher, a lightweight object needs to be put into thread
// state, rather than the full blown frame, that is more similar to current
// Clynton frames.
#if PYTHON_VERSION < 0x3b0
typedef PyFrameObject Clynton_ThreadStateFrameType;
#else
typedef _PyInterpreterFrame Clynton_ThreadStateFrameType;
#endif

// Print a description of given frame objects in frame debug mode
#if _DEBUG_FRAME
extern void PRINT_TOP_FRAME(char const *prefix);
extern void PRINT_PYTHON_FRAME(char const *prefix, PyFrameObject *frame);
extern void PRINT_COMPILED_FRAME(char const *prefix, struct Clynton_FrameObject *frame);
extern void PRINT_INTERPRETER_FRAME(char const *prefix, Clynton_ThreadStateFrameType *frame);
#else
#define PRINT_TOP_FRAME(prefix)
#define PRINT_PYTHON_FRAME(prefix, frame)
#define PRINT_COMPILED_FRAME(prefix, frame)
#define PRINT_INTERPRETER_FRAME(prefix, frame)
#endif

// Create a frame object for the given code object, frame or module.
extern struct Clynton_FrameObject *MAKE_MODULE_FRAME(PyCodeObject *code, PyObject *module);
extern struct Clynton_FrameObject *MAKE_FUNCTION_FRAME(PyThreadState *tstate, PyCodeObject *code, PyObject *module,
                                                      Py_ssize_t locals_size);
extern struct Clynton_FrameObject *MAKE_CLASS_FRAME(PyThreadState *tstate, PyCodeObject *code, PyObject *module,
                                                   PyObject *f_locals, Py_ssize_t locals_size);

// Create a code object for the given filename and function name

#if PYTHON_VERSION < 0x300
#define MAKE_CODE_OBJECT(filename, line, flags, function_name, function_qualname, argnames, freevars, arg_count,       \
                         kw_only_count, pos_only_count)                                                                \
    makeCodeObject(filename, line, flags, function_name, argnames, freevars, arg_count)
extern PyCodeObject *makeCodeObject(PyObject *filename, int line, int flags, PyObject *function_name,
                                    PyObject *argnames, PyObject *freevars, int arg_count);
#elif PYTHON_VERSION < 0x380
#define MAKE_CODE_OBJECT(filename, line, flags, function_name, function_qualname, argnames, freevars, arg_count,       \
                         kw_only_count, pos_only_count)                                                                \
    makeCodeObject(filename, line, flags, function_name, argnames, freevars, arg_count, kw_only_count)
extern PyCodeObject *makeCodeObject(PyObject *filename, int line, int flags, PyObject *function_name,
                                    PyObject *argnames, PyObject *freevars, int arg_count, int kw_only_count);
#elif PYTHON_VERSION < 0x3b0
#define MAKE_CODE_OBJECT(filename, line, flags, function_name, function_qualname, argnames, freevars, arg_count,       \
                         kw_only_count, pos_only_count)                                                                \
    makeCodeObject(filename, line, flags, function_name, argnames, freevars, arg_count, kw_only_count, pos_only_count)
extern PyCodeObject *makeCodeObject(PyObject *filename, int line, int flags, PyObject *function_name,
                                    PyObject *argnames, PyObject *freevars, int arg_count, int kw_only_count,
                                    int pos_only_count);
#else
#define MAKE_CODE_OBJECT(filename, line, flags, function_name, function_qualname, argnames, freevars, arg_count,       \
                         kw_only_count, pos_only_count)                                                                \
    makeCodeObject(filename, line, flags, function_name, function_qualname, argnames, freevars, arg_count,             \
                   kw_only_count, pos_only_count)
extern PyCodeObject *makeCodeObject(PyObject *filename, int line, int flags, PyObject *function_name,
                                    PyObject *function_qualname, PyObject *argnames, PyObject *freevars, int arg_count,
                                    int kw_only_count, int pos_only_count);
#endif

CLYNTON_MAY_BE_UNUSED static inline bool isFakeCodeObject(PyCodeObject *code) {
#if PYTHON_VERSION < 0x300
    return code->co_code == const_str_empty;
#elif PYTHON_VERSION < 0x3B0
    return code->co_code == const_str_empty;
#else
    return _PyCode_CODE(code)[0] == 0;
#endif
}

extern PyTypeObject Clynton_Frame_Type;

static inline bool Clynton_Frame_Check(PyObject *object) {
    CHECK_OBJECT(object);
    return Py_TYPE(object) == &Clynton_Frame_Type;
}

struct Clynton_FrameObject {
    PyFrameObject m_frame;

#if PYTHON_VERSION >= 0x3b0
    PyObject *m_generator;
    PyFrameState m_frame_state;
    _PyInterpreterFrame m_interpreter_frame;

    // In Python 3.11, the frame object is no longer variable size, and as such
    // we inherit the wrong kind of header, not PyVarObject, leading to f_back
    // the PyFrameObject and and ob_size aliasing, which is not good, but we
    // want to expose the same binary interface, while still being variable size,
    // so what we do is to preserve the size in this field instead.
    Py_ssize_t m_ob_size;

#endif

    // Our own extra stuff, attached variables.
    char const *m_type_description;
    char m_locals_storage[1];
};

inline static void CHECK_CODE_OBJECT(PyCodeObject *code_object) { CHECK_OBJECT(code_object); }

CLYNTON_MAY_BE_UNUSED static inline bool isFrameUnusable(struct Clynton_FrameObject *frame_object) {
    CHECK_OBJECT_X(frame_object);

    bool result =
        // Never used.
        frame_object == NULL ||
        // Still in use
        Py_REFCNT(frame_object) > 1 ||
#if PYTHON_VERSION < 0x340
        // Last used by another thread (TODO: Could just set it when re-using)
        frame_object->m_frame.f_tstate != PyThreadState_GET() ||
#endif
        // Not currently linked.
        frame_object->m_frame.f_back != NULL;

#if _DEBUG_REFRAME
    if (result && frame_object != NULL) {
        PRINT_COMPILED_FRAME("NOT REUSING FRAME:", frame_object);
    }
#endif

    return result;
}

#if _DEBUG_REFCOUNTS
extern int count_active_frame_cache_instances;
extern int count_allocated_frame_cache_instances;
extern int count_released_frame_cache_instances;
extern int count_hit_frame_cache_instances;
#endif

#if _DEBUG_FRAME
extern void dumpFrameStack(void);
#endif

inline static PyCodeObject *Clynton_Frame_GetCodeObject(PyFrameObject *frame) {
#if PYTHON_VERSION >= 0x3b0
    assert(frame->f_frame);
    return frame->f_frame->f_code;
#else
    return frame->f_code;
#endif
}

inline static void assertPythonFrameObject(PyFrameObject *frame_object) {

    // TODO: Need to do this manually, as this is making frame caching code
    // vulnerable to mistakes, but so far the compiled frame type is private
    // assert(PyObject_IsInstance((PyObject *)frame_object, (PyObject *)&PyFrame_Type));

    CHECK_CODE_OBJECT(Clynton_Frame_GetCodeObject(frame_object));
}

inline static void assertFrameObject(struct Clynton_FrameObject *frame_object) {
    CHECK_OBJECT(frame_object);

    // TODO: Need to do this manually, as this is making frame caching code
    // vulnerable to mistakes, but so far the compiled frame type is private
    // assert(PyObject_IsInstance((PyObject *)frame_object, (PyObject *)&PyFrame_Type));

    assertPythonFrameObject(&frame_object->m_frame);
}

inline static void assertThreadFrameObject(Clynton_ThreadStateFrameType *frame) {
#if PYTHON_VERSION < 0x3B0
    assertPythonFrameObject(frame);
#else
    // For uncompiled frames of Python 3.11 these often do not exist. TODO: Figure
    // out what to check or how to know it's a compiled one.
    if (frame->frame_obj) {
        assertPythonFrameObject(frame->frame_obj);
    }
#endif
}

// Mark frame as currently executed. Starting with Python 3.4 that means it
// can or cannot be cleared, or should lead to a generator close. For Python2
// this is a no-op. Using a define to spare the compile from inlining an empty
// function.
#if PYTHON_VERSION >= 0x340

#if PYTHON_VERSION < 0x3b0

static inline void Clynton_PythonFrame_MarkAsExecuting(PyFrameObject *frame) {
#if PYTHON_VERSION >= 0x3a0
    frame->f_state = FRAME_EXECUTING;
#else
    frame->f_executing = 1;
#endif
}

#endif

static inline void Clynton_Frame_MarkAsExecuting(struct Clynton_FrameObject *frame) {
    CHECK_OBJECT(frame);
#if PYTHON_VERSION >= 0x3b0
    frame->m_frame_state = FRAME_EXECUTING;
#elif PYTHON_VERSION >= 0x3a0
    frame->m_frame.f_state = FRAME_EXECUTING;
#else
    frame->m_frame.f_executing = 1;
#endif
}
#else
#define Clynton_Frame_MarkAsExecuting(frame) ;
#endif

#if PYTHON_VERSION >= 0x340
static inline void Clynton_Frame_MarkAsNotExecuting(struct Clynton_FrameObject *frame) {
    CHECK_OBJECT(frame);
#if PYTHON_VERSION >= 0x3b0
    frame->m_frame_state = FRAME_SUSPENDED;
#elif PYTHON_VERSION >= 0x3a0
    frame->m_frame.f_state = FRAME_SUSPENDED;
#else
    frame->m_frame.f_executing = 0;
#endif
}
#else
#define Clynton_Frame_MarkAsNotExecuting(frame) ;
#define Clynton_PythonFrame_MarkAsExecuting(frame) ;
#endif

#if PYTHON_VERSION >= 0x340
static inline bool Clynton_Frame_IsExecuting(struct Clynton_FrameObject *frame) {
    CHECK_OBJECT(frame);
#if PYTHON_VERSION >= 0x3b0
    return frame->m_frame_state == FRAME_EXECUTING;
#elif PYTHON_VERSION >= 0x3a0
    return frame->m_frame.f_state == FRAME_EXECUTING;
#else
    return frame->m_frame.f_executing == 1;
#endif
}
#endif

#if PYTHON_VERSION >= 0x3B0
CLYNTON_MAY_BE_UNUSED inline static void pushFrameStackInterpreterFrame(PyThreadState *tstate,
                                                                       _PyInterpreterFrame *interpreter_frame) {
    _PyInterpreterFrame *old = tstate->cframe->current_frame;
    interpreter_frame->previous = old;
    tstate->cframe->current_frame = interpreter_frame;

    if (old != NULL && interpreter_frame->frame_obj) {
        interpreter_frame->frame_obj->f_back = old->frame_obj;
        Py_XINCREF(old->frame_obj);
    }
}
#else
// Put frame at the top of the frame stack and mark as executing.
CLYNTON_MAY_BE_UNUSED inline static void pushFrameStackPythonFrame(PyThreadState *tstate, PyFrameObject *frame_object) {
    PRINT_TOP_FRAME("Normal push entry top frame:");
    PRINT_COMPILED_FRAME("Pushing:", frame_object);

    // Make sure it's healthy.
    assertPythonFrameObject(frame_object);

    PyFrameObject *old = tstate->frame;
    CHECK_OBJECT_X(old);

    if (old) {
        assertPythonFrameObject(old);
        CHECK_CODE_OBJECT(old->f_code);
    }

    // No recursion with identical frames allowed, assert against it.
    assert(old != frame_object);

    // Push the new frame as the currently active one.
    tstate->frame = frame_object;

    // Transfer ownership of old frame.
    if (old != NULL) {

        frame_object->f_back = old;
    }

    Clynton_PythonFrame_MarkAsExecuting(frame_object);
    Py_INCREF(frame_object);

    PRINT_TOP_FRAME("Normal push exit top frame:");
}
#endif

CLYNTON_MAY_BE_UNUSED inline static void pushFrameStackCompiledFrame(PyThreadState *tstate,
                                                                    struct Clynton_FrameObject *frame_object) {
#if PYTHON_VERSION < 0x3b0
    pushFrameStackPythonFrame(tstate, &frame_object->m_frame);
#else
    pushFrameStackInterpreterFrame(tstate, &frame_object->m_interpreter_frame);

    Clynton_Frame_MarkAsExecuting(frame_object);
    Py_INCREF(frame_object);
#endif
}

CLYNTON_MAY_BE_UNUSED inline static void popFrameStack(PyThreadState *tstate) {
#if _DEBUG_FRAME
    PRINT_TOP_FRAME("Normal pop entry top frame:");
#endif

#if PYTHON_VERSION < 0x3b0
    struct Clynton_FrameObject *frame_object = (struct Clynton_FrameObject *)(tstate->frame);
    CHECK_OBJECT(frame_object);

#if _DEBUG_FRAME
    printf("Taking off frame %s %s\n", Clynton_String_AsString(PyObject_Str((PyObject *)frame_object)),
           Clynton_String_AsString(PyObject_Repr((PyObject *)Clynton_Frame_GetCodeObject(&frame_object->m_frame))));
#endif

    // Put previous frame on top.
    tstate->frame = frame_object->m_frame.f_back;
    frame_object->m_frame.f_back = NULL;

    Clynton_Frame_MarkAsNotExecuting(frame_object);
    Py_DECREF(frame_object);
#else
    assert(tstate->cframe);
    assert(tstate->cframe->current_frame);

    struct Clynton_FrameObject *frame_object = (struct Clynton_FrameObject *)tstate->cframe->current_frame->frame_obj;
    CHECK_OBJECT(frame_object);

    tstate->cframe->current_frame = tstate->cframe->current_frame->previous;

    Clynton_Frame_MarkAsNotExecuting(frame_object);

    CHECK_OBJECT_X(frame_object->m_frame.f_back);
    Py_CLEAR(frame_object->m_frame.f_back);

    Py_DECREF(frame_object);

    frame_object->m_interpreter_frame.previous = NULL;
#endif

#if _DEBUG_FRAME
    PRINT_TOP_FRAME("Normal pop exit top frame:");
#endif
}

// TODO: These can be moved to private code, once all C library is included by
// compiled code helpers, but generators are currently not.
#if PYTHON_VERSION >= 0x340
CLYNTON_MAY_BE_UNUSED static void Clynton_SetFrameGenerator(struct Clynton_FrameObject *clynton_frame,
                                                          PyObject *generator) {
#if PYTHON_VERSION < 0x3b0
    clynton_frame->m_frame.f_gen = generator;
#else
    clynton_frame->m_generator = generator;
#endif

    // Mark the frame as executing
    if (generator) {
        Clynton_Frame_MarkAsExecuting(clynton_frame);
    }
}

CLYNTON_MAY_BE_UNUSED static PyObject *Clynton_GetFrameGenerator(struct Clynton_FrameObject *clynton_frame) {
#if PYTHON_VERSION < 0x3b0
    return clynton_frame->m_frame.f_gen;
#else
    return clynton_frame->m_generator;
#endif
}
#endif

CLYNTON_MAY_BE_UNUSED static PyCodeObject *Clynton_GetFrameCodeObject(struct Clynton_FrameObject *clynton_frame) {
#if PYTHON_VERSION < 0x3b0
    return clynton_frame->m_frame.f_code;
#else
    return clynton_frame->m_interpreter_frame.f_code;
#endif
}

CLYNTON_MAY_BE_UNUSED static int Clynton_GetFrameLineNumber(struct Clynton_FrameObject *clynton_frame) {
    return clynton_frame->m_frame.f_lineno;
}

CLYNTON_MAY_BE_UNUSED static PyObject **Clynton_GetCodeVarNames(PyCodeObject *code_object) {
#if PYTHON_VERSION < 0x3b0
    return &PyTuple_GET_ITEM(code_object->co_varnames, 0);
#else
    // TODO: Might get away with co_names which will be much faster, that functions
    // that build a new tuple, that we would have to keep around, but it might be
    // merged with closure variable names, etc. as as such might become wrong.
    return &PyTuple_GET_ITEM(code_object->co_localsplusnames, 0);
#endif
}

// Attach locals to a frame object. TODO: Upper case, this is for generated code only.
extern void Clynton_Frame_AttachLocals(struct Clynton_FrameObject *frame, char const *type_description, ...);

CLYNTON_MAY_BE_UNUSED static Clynton_ThreadStateFrameType *_Clynton_GetThreadStateFrame(PyThreadState *tstate) {
#if PYTHON_VERSION < 0x3b0
    return tstate->frame;
#else
    return tstate->cframe->current_frame;
#endif
}

CLYNTON_MAY_BE_UNUSED inline static void pushFrameStackGenerator(PyThreadState *tstate,
                                                                Clynton_ThreadStateFrameType *frame_object) {
#if PYTHON_VERSION < 0x3b0
    Clynton_ThreadStateFrameType *return_frame = _Clynton_GetThreadStateFrame(tstate);

    Py_XINCREF(return_frame);
    // Put the generator back on the frame stack.
    pushFrameStackPythonFrame(tstate, frame_object);
    Py_DECREF(frame_object);
#else
    pushFrameStackInterpreterFrame(tstate, frame_object);
#endif
}

CLYNTON_MAY_BE_UNUSED inline static void pushFrameStackGeneratorCompiledFrame(PyThreadState *tstate,
                                                                             struct Clynton_FrameObject *frame_object) {
#if PYTHON_VERSION < 0x3b0
    pushFrameStackGenerator(tstate, &frame_object->m_frame);
#else
    pushFrameStackGenerator(tstate, &frame_object->m_interpreter_frame);
#endif
}

// Codes used for type_description.
#define CLYNTON_TYPE_DESCRIPTION_NULL 'N'
#define CLYNTON_TYPE_DESCRIPTION_CELL 'c'
#define CLYNTON_TYPE_DESCRIPTION_OBJECT 'o'
#define CLYNTON_TYPE_DESCRIPTION_OBJECT_PTR 'O'
#define CLYNTON_TYPE_DESCRIPTION_BOOL 'b'

#if _DEBUG_REFCOUNTS
extern int count_active_Clynton_Frame_Type;
extern int count_allocated_Clynton_Frame_Type;
extern int count_released_Clynton_Frame_Type;
#endif

#endif
