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
#ifndef __CLYNTON_HELPER_INTS_H__
#define __CLYNTON_HELPER_INTS_H__

typedef enum {
    CLYNTON_INT_UNASSIGNED = 0,
    CLYNTON_INT_OBJECT_VALID = 1,
    CLYNTON_INT_VALUE_VALID = 2,
    CLYNTON_INT_BOTH_VALID = 3
} clynton_int_validity;

typedef struct {
    clynton_int_validity validity;

    PyObject *int_object;
    long int_value;
} clynton_int;

typedef enum {
    CLYNTON_LONG_UNASSIGNED = 0,
    CLYNTON_LONG_OBJECT_VALID = 1,
    CLYNTON_LONG_VALUE_VALID = 2,
    CLYNTON_LONG_BOTH_VALID = 3
} clynton_long_validity;

typedef struct {
    clynton_long_validity validity;

    PyObject *long_object;
    long long_value;
} clynton_long;

#if PYTHON_VERSION < 0x300
typedef enum {
    CLYNTON_ILONG_UNASSIGNED = 0,
    CLYNTON_ILONG_OBJECT_VALID = 1,
    CLYNTON_ILONG_VALUE_VALID = 2,
    CLYNTON_ILONG_BOTH_VALID = 3
} clynton_ilong_validity;

typedef struct {
    clynton_ilong_validity validity;

    PyObject *ilong_object;
    long ilong_value;
} clynton_ilong;

CLYNTON_MAY_BE_UNUSED static void ENFORCE_ILONG_OBJECT_VALUE(clynton_ilong *value) {
    assert(value->validity != CLYNTON_ILONG_UNASSIGNED);

    if ((value->validity & CLYNTON_ILONG_OBJECT_VALID) == 0) {
        value->ilong_object = PyLong_FromLong(value->ilong_value);

        value->validity = CLYNTON_ILONG_BOTH_VALID;
    }
}

#endif

// TODO: Use this from header files, although they have changed.
#define CLYNTON_STATIC_SMALLINT_VALUE_MIN -5
#define CLYNTON_STATIC_SMALLINT_VALUE_MAX 257

#define CLYNTON_TO_SMALL_VALUE_OFFSET(value) (value - CLYNTON_STATIC_SMALLINT_VALUE_MIN)

#if PYTHON_VERSION < 0x3b0

#if PYTHON_VERSION >= 0x300

#if PYTHON_VERSION >= 0x390
extern PyObject **Clynton_Long_SmallValues;
#else
extern PyObject *Clynton_Long_SmallValues[CLYNTON_STATIC_SMALLINT_VALUE_MAX - CLYNTON_STATIC_SMALLINT_VALUE_MIN + 1];
#endif

CLYNTON_MAY_BE_UNUSED static inline PyObject *Clynton_Long_GetSmallValue(int ival) {
    return Clynton_Long_SmallValues[CLYNTON_TO_SMALL_VALUE_OFFSET(ival)];
}

#endif

#else
CLYNTON_MAY_BE_UNUSED static inline PyObject *Clynton_Long_GetSmallValue(int ival) {
    return (PyObject *)&_PyLong_SMALL_INTS[CLYNTON_TO_SMALL_VALUE_OFFSET(ival)];
}
#endif

#endif