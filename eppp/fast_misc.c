#include <Python.h>
#include <stdio.h>

// Operation constants
#define OP_VAL 0
#define OP_PAR 1
#define OP_SER 2

// TODO Comment everything

static PyObject* parallel_imp_func_pointer;
static PyObject* add_func_pointer;

static PyObject* polish_eval_init(PyObject *self, PyObject *args) {
	if (!PyArg_ParseTuple(args, "OO", &parallel_imp_func_pointer, &add_func_pointer)) {
		return NULL;
	}

	Py_RETURN_NONE;
}

static PyObject* polish_eval(PyObject *self, PyObject *expr) {
	long len = PyList_Size(expr);

	int    ops[len];
	double els[len];

	int i, j;
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

	i = len - 1;
	j = i - 1;

	while (i > 0) {
		switch (ops[--i]) {
			case OP_PAR:
				j++;
				int k = j + 1;
				double a = els[k];
				double b = els[j];
				els[k] = a * b / (a + b);
				break;
			case OP_SER:
				j++;
				els[j+1] = els[j+1] + els[j];
				break;
			default:
				els[j--] = els[i];
				break;
		}
	}

	PyObject* ret = PyList_New(1);
	PyList_SetItem(ret, 0, PyFloat_FromDouble(els[j+1]));
	return ret;
}

// Method definition object for this extension, these arguments mean:
// ml_name:  The name of the method
// ml_meth:  Function pointer to the method implementation
// ml_flags: Flags indicating special features of this method, such as accepting arguments, accepting keyword arguments, being a class method, or being a static method of a class.
// ml_doc:   Contents of this method's docstring
static PyMethodDef module_methods[] = {
	{
		"polish_eval",
		polish_eval,
		METH_O,
		"",
	},
	{
		"polish_eval_init",
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
