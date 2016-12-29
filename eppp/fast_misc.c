#include <Python.h>
#include <stdio.h>

// Operation constants
#define OP_VAL 0
#define OP_PAR 1
#define OP_SER 2

// TODO: Support complex numbers

// Pointers to Python functions
static PyObject* parallel_imp_func_pointer;
static PyObject* add_func_pointer;

// Inititalize Python function pointers
static PyObject* polish_eval_init(PyObject *self, PyObject *args) {
	if (!PyArg_ParseTuple(args, "OO", &parallel_imp_func_pointer, &add_func_pointer)) {
		return NULL;
	}

	Py_RETURN_NONE;
}

// Evaluates a polish expression
static PyObject* polish_eval_non_strict(PyObject *self, PyObject *expr) {
	// Size of expression
	long len = PyList_Size(expr);

	// Arrays to operate on
	int    ops[len]; // Operations (parallel, series, value)
	double els[len]; // Elements (only used by value)

	
	// Index variables
	int i, j;

	// Convert Python objects to C types
	for (i = 0; i < len; i++) {
		PyObject* el = PyList_GetItem(expr, i);
		if (el == parallel_imp_func_pointer) {
			ops[i] = OP_PAR;
		} else if (el == add_func_pointer) {
			ops[i] = OP_SER;
		} else {
			ops[i] = OP_VAL;
			els[i] = PyFloat_AsDouble(PyNumber_Float(el));
		}
	}

	// Initialize pointers
	i = len - 1; // Expression pointer
	j = i - 1;   // Stack pointer

	// While there are elements left in the expression
	while (i > 0) {
		switch (ops[--i]) {
			// If parallel operator
			case OP_PAR:
				j++;
				int k = j + 1;
				double a = els[k];
				double b = els[j];
				els[k] = a * b / (a + b);
				break;

			// If series operator
			case OP_SER:
				j++;
				els[j+1] = els[j+1] + els[j];
				break;

			// If value
			default:
				els[j--] = els[i];
				break;
		}
	}

	// Return the remaining element
	PyObject* ret = PyFloat_FromDouble(els[j+1]);
	return ret;
}

// Method definitions
static PyMethodDef module_methods[] = {
	{
		"polish_eval_non_strict",
		polish_eval_non_strict,
		METH_O,
		"",
	},
	{
		"polish_eval_non_strict_init",
		polish_eval_init,
		METH_VARARGS,
		"",
	},
	{NULL, NULL, 0, NULL}
};

// Module definition
static struct PyModuleDef module_def = {
	PyModuleDef_HEAD_INIT,
	"",
	"",
	-1,
	module_methods,
};

// Initialize module
PyMODINIT_FUNC PyInit_fast_misc(void) {
	Py_Initialize();
	return PyModule_Create(&module_def);
}
