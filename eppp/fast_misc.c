#include <Python.h>
#include <stdio.h>

static PyObject* polish_eval(PyObject *self, PyObject *args) {
	// TODO Do the actual thing instead of printing 'Hello World'
	printf("Hello World\n");
	Py_RETURN_NONE;
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
		METH_NOARGS,
		"", // No doc string
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
PyMODINIT_FUNC PyInit_fast_misc(void)
{
	Py_Initialize();
	return PyModule_Create(&module_def);
}
