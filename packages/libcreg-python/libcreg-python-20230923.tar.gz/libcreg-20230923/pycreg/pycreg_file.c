/*
 * Python object wrapper of libcreg_file_t
 *
 * Copyright (C) 2013-2023, Joachim Metz <joachim.metz@gmail.com>
 *
 * Refer to AUTHORS for acknowledgements.
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Lesser General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU Lesser General Public License
 * along with this program.  If not, see <https://www.gnu.org/licenses/>.
 */

#include <common.h>
#include <narrow_string.h>
#include <types.h>

#if defined( HAVE_STDLIB_H ) || defined( HAVE_WINAPI )
#include <stdlib.h>
#endif

#include "pycreg_codepage.h"
#include "pycreg_error.h"
#include "pycreg_file.h"
#include "pycreg_file_object_io_handle.h"
#include "pycreg_key.h"
#include "pycreg_libbfio.h"
#include "pycreg_libcerror.h"
#include "pycreg_libclocale.h"
#include "pycreg_libcreg.h"
#include "pycreg_python.h"
#include "pycreg_unused.h"

#if !defined( LIBCREG_HAVE_BFIO )

LIBCREG_EXTERN \
int libcreg_file_open_file_io_handle(
     libcreg_file_t *file,
     libbfio_handle_t *file_io_handle,
     int access_flags,
     libcreg_error_t **error );

#endif /* !defined( LIBCREG_HAVE_BFIO ) */

PyMethodDef pycreg_file_object_methods[] = {

	{ "signal_abort",
	  (PyCFunction) pycreg_file_signal_abort,
	  METH_NOARGS,
	  "signal_abort() -> None\n"
	  "\n"
	  "Signals the file to abort the current activity." },

	{ "open",
	  (PyCFunction) pycreg_file_open,
	  METH_VARARGS | METH_KEYWORDS,
	  "open(filename, mode='r') -> None\n"
	  "\n"
	  "Opens a file." },

	{ "open_file_object",
	  (PyCFunction) pycreg_file_open_file_object,
	  METH_VARARGS | METH_KEYWORDS,
	  "open_file_object(file_object, mode='r') -> None\n"
	  "\n"
	  "Opens a file using a file-like object." },

	{ "close",
	  (PyCFunction) pycreg_file_close,
	  METH_NOARGS,
	  "close() -> None\n"
	  "\n"
	  "Closes a file." },

	{ "is_corrupted",
	  (PyCFunction) pycreg_file_is_corrupted,
	  METH_NOARGS,
	  "is_corrupted() -> Boolean\n"
	  "\n"
	  "Determines if the file is corrupted." },

	{ "get_ascii_codepage",
	  (PyCFunction) pycreg_file_get_ascii_codepage,
	  METH_NOARGS,
	  "get_ascii_codepage() -> String\n"
	  "\n"
	  "Retrieves the codepage for ASCII strings used in the file." },

	{ "set_ascii_codepage",
	  (PyCFunction) pycreg_file_set_ascii_codepage,
	  METH_VARARGS | METH_KEYWORDS,
	  "set_ascii_codepage(codepage) -> None\n"
	  "\n"
	  "Sets the codepage for ASCII strings used in the file.\n"
	  "Expects the codepage to be a string containing a Python codec definition." },

	{ "get_format_version",
	  (PyCFunction) pycreg_file_get_format_version,
	  METH_NOARGS,
	  "get_format_version() -> Unicode string\n"
	  "\n"
	  "Retrieves the format version." },

	{ "get_type",
	  (PyCFunction) pycreg_file_get_type,
	  METH_NOARGS,
	  "get_type() -> Integer\n"
	  "\n"
	  "Retrieves the type." },

	{ "get_root_key",
	  (PyCFunction) pycreg_file_get_root_key,
	  METH_NOARGS,
	  "get_root_key() -> Object\n"
	  "\n"
	  "Retrieves the root key." },

	{ "get_key_by_path",
	  (PyCFunction) pycreg_file_get_key_by_path,
	  METH_VARARGS | METH_KEYWORDS,
	  "get_key_by_path(path) -> Object or None\n"
	  "\n"
	  "Retrieves the key specified by the path." },

	/* Sentinel */
	{ NULL, NULL, 0, NULL }
};

PyGetSetDef pycreg_file_object_get_set_definitions[] = {

	{ "corrupted",
	  (getter) pycreg_file_is_corrupted,
	  (setter) 0,
	  "Value to indicate the file is corrupted.",
	  NULL },

	{ "ascii_codepage",
	  (getter) pycreg_file_get_ascii_codepage,
	  (setter) pycreg_file_set_ascii_codepage_setter,
	  "The codepage used for ASCII strings in the file.",
	  NULL },

	{ "format_version",
	  (getter) pycreg_file_get_format_version,
	  (setter) 0,
	  "The format version.",
	  NULL },

	{ "type",
	  (getter) pycreg_file_get_type,
	  (setter) 0,
	  "The type.",
	  NULL },

	{ "root_key",
	  (getter) pycreg_file_get_root_key,
	  (setter) 0,
	  "The root key.",
	  NULL },

	/* Sentinel */
	{ NULL, NULL, NULL, NULL, NULL }
};

PyTypeObject pycreg_file_type_object = {
	PyVarObject_HEAD_INIT( NULL, 0 )

	/* tp_name */
	"pycreg.file",
	/* tp_basicsize */
	sizeof( pycreg_file_t ),
	/* tp_itemsize */
	0,
	/* tp_dealloc */
	(destructor) pycreg_file_free,
	/* tp_print */
	0,
	/* tp_getattr */
	0,
	/* tp_setattr */
	0,
	/* tp_compare */
	0,
	/* tp_repr */
	0,
	/* tp_as_number */
	0,
	/* tp_as_sequence */
	0,
	/* tp_as_mapping */
	0,
	/* tp_hash */
	0,
	/* tp_call */
	0,
	/* tp_str */
	0,
	/* tp_getattro */
	0,
	/* tp_setattro */
	0,
	/* tp_as_buffer */
	0,
	/* tp_flags */
	Py_TPFLAGS_DEFAULT,
	/* tp_doc */
	"pycreg file object (wraps libcreg_file_t)",
	/* tp_traverse */
	0,
	/* tp_clear */
	0,
	/* tp_richcompare */
	0,
	/* tp_weaklistoffset */
	0,
	/* tp_iter */
	0,
	/* tp_iternext */
	0,
	/* tp_methods */
	pycreg_file_object_methods,
	/* tp_members */
	0,
	/* tp_getset */
	pycreg_file_object_get_set_definitions,
	/* tp_base */
	0,
	/* tp_dict */
	0,
	/* tp_descr_get */
	0,
	/* tp_descr_set */
	0,
	/* tp_dictoffset */
	0,
	/* tp_init */
	(initproc) pycreg_file_init,
	/* tp_alloc */
	0,
	/* tp_new */
	0,
	/* tp_free */
	0,
	/* tp_is_gc */
	0,
	/* tp_bases */
	NULL,
	/* tp_mro */
	NULL,
	/* tp_cache */
	NULL,
	/* tp_subclasses */
	NULL,
	/* tp_weaklist */
	NULL,
	/* tp_del */
	0
};

/* Initializes a file object
 * Returns 0 if successful or -1 on error
 */
int pycreg_file_init(
     pycreg_file_t *pycreg_file )
{
	libcerror_error_t *error = NULL;
	static char *function    = "pycreg_file_init";

	if( pycreg_file == NULL )
	{
		PyErr_Format(
		 PyExc_ValueError,
		 "%s: invalid file.",
		 function );

		return( -1 );
	}
	/* Make sure libcreg file is set to NULL
	 */
	pycreg_file->file           = NULL;
	pycreg_file->file_io_handle = NULL;

	if( libcreg_file_initialize(
	     &( pycreg_file->file ),
	     &error ) != 1 )
	{
		pycreg_error_raise(
		 error,
		 PyExc_MemoryError,
		 "%s: unable to initialize file.",
		 function );

		libcerror_error_free(
		 &error );

		return( -1 );
	}
	return( 0 );
}

/* Frees a file object
 */
void pycreg_file_free(
      pycreg_file_t *pycreg_file )
{
	struct _typeobject *ob_type = NULL;
	libcerror_error_t *error    = NULL;
	static char *function       = "pycreg_file_free";
	int result                  = 0;

	if( pycreg_file == NULL )
	{
		PyErr_Format(
		 PyExc_ValueError,
		 "%s: invalid file.",
		 function );

		return;
	}
	ob_type = Py_TYPE(
	           pycreg_file );

	if( ob_type == NULL )
	{
		PyErr_Format(
		 PyExc_ValueError,
		 "%s: missing ob_type.",
		 function );

		return;
	}
	if( ob_type->tp_free == NULL )
	{
		PyErr_Format(
		 PyExc_ValueError,
		 "%s: invalid ob_type - missing tp_free.",
		 function );

		return;
	}
	if( pycreg_file->file_io_handle != NULL )
	{
		if( pycreg_file_close(
		     pycreg_file,
		     NULL ) == NULL )
		{
			return;
		}
	}
	if( pycreg_file->file != NULL )
	{
		Py_BEGIN_ALLOW_THREADS

		result = libcreg_file_free(
		          &( pycreg_file->file ),
		          &error );

		Py_END_ALLOW_THREADS

		if( result != 1 )
		{
			pycreg_error_raise(
			 error,
			 PyExc_MemoryError,
			 "%s: unable to free libcreg file.",
			 function );

			libcerror_error_free(
			 &error );
		}
	}
	ob_type->tp_free(
	 (PyObject*) pycreg_file );
}

/* Signals the file to abort the current activity
 * Returns a Python object if successful or NULL on error
 */
PyObject *pycreg_file_signal_abort(
           pycreg_file_t *pycreg_file,
           PyObject *arguments PYCREG_ATTRIBUTE_UNUSED )
{
	libcerror_error_t *error = NULL;
	static char *function    = "pycreg_file_signal_abort";
	int result               = 0;

	PYCREG_UNREFERENCED_PARAMETER( arguments )

	if( pycreg_file == NULL )
	{
		PyErr_Format(
		 PyExc_ValueError,
		 "%s: invalid file.",
		 function );

		return( NULL );
	}
	Py_BEGIN_ALLOW_THREADS

	result = libcreg_file_signal_abort(
	          pycreg_file->file,
	          &error );

	Py_END_ALLOW_THREADS

	if( result != 1 )
	{
		pycreg_error_raise(
		 error,
		 PyExc_IOError,
		 "%s: unable to signal abort.",
		 function );

		libcerror_error_free(
		 &error );

		return( NULL );
	}
	Py_IncRef(
	 Py_None );

	return( Py_None );
}

/* Opens a file
 * Returns a Python object if successful or NULL on error
 */
PyObject *pycreg_file_open(
           pycreg_file_t *pycreg_file,
           PyObject *arguments,
           PyObject *keywords )
{
	PyObject *string_object      = NULL;
	libcerror_error_t *error     = NULL;
	const char *filename_narrow  = NULL;
	static char *function        = "pycreg_file_open";
	static char *keyword_list[]  = { "filename", "mode", NULL };
	char *mode                   = NULL;
	int result                   = 0;

#if defined( HAVE_WIDE_SYSTEM_CHARACTER )
	const wchar_t *filename_wide = NULL;
#else
	PyObject *utf8_string_object = NULL;
#endif

	if( pycreg_file == NULL )
	{
		PyErr_Format(
		 PyExc_ValueError,
		 "%s: invalid file.",
		 function );

		return( NULL );
	}
	/* Note that PyArg_ParseTupleAndKeywords with "s" will force Unicode strings to be converted to narrow character string.
	 * On Windows the narrow character strings contains an extended ASCII string with a codepage. Hence we get a conversion
	 * exception. This will also fail if the default encoding is not set correctly. We cannot use "u" here either since that
	 * does not allow us to pass non Unicode string objects and Python (at least 2.7) does not seems to automatically upcast them.
	 */
	if( PyArg_ParseTupleAndKeywords(
	     arguments,
	     keywords,
	     "O|s",
	     keyword_list,
	     &string_object,
	     &mode ) == 0 )
	{
		return( NULL );
	}
	if( ( mode != NULL )
	 && ( mode[ 0 ] != 'r' ) )
	{
		PyErr_Format(
		 PyExc_ValueError,
		 "%s: unsupported mode: %s.",
		 function,
		 mode );

		return( NULL );
	}
	PyErr_Clear();

	result = PyObject_IsInstance(
	          string_object,
	          (PyObject *) &PyUnicode_Type );

	if( result == -1 )
	{
		pycreg_error_fetch_and_raise(
		 PyExc_RuntimeError,
		 "%s: unable to determine if string object is of type Unicode.",
		 function );

		return( NULL );
	}
	else if( result != 0 )
	{
		PyErr_Clear();

#if defined( HAVE_WIDE_SYSTEM_CHARACTER )
#if PY_MAJOR_VERSION >= 3 && PY_MINOR_VERSION >= 3
		filename_wide = (wchar_t *) PyUnicode_AsWideCharString(
		                             string_object,
		                             NULL );
#else
		filename_wide = (wchar_t *) PyUnicode_AsUnicode(
		                             string_object );
#endif
		Py_BEGIN_ALLOW_THREADS

		result = libcreg_file_open_wide(
		          pycreg_file->file,
		          filename_wide,
		          LIBCREG_OPEN_READ,
		          &error );

		Py_END_ALLOW_THREADS

#if PY_MAJOR_VERSION >= 3 && PY_MINOR_VERSION >= 3
		PyMem_Free(
		 filename_wide );
#endif
#else
		utf8_string_object = PyUnicode_AsUTF8String(
		                      string_object );

		if( utf8_string_object == NULL )
		{
			pycreg_error_fetch_and_raise(
			 PyExc_RuntimeError,
			 "%s: unable to convert Unicode string to UTF-8.",
			 function );

			return( NULL );
		}
#if PY_MAJOR_VERSION >= 3
		filename_narrow = PyBytes_AsString(
		                   utf8_string_object );
#else
		filename_narrow = PyString_AsString(
		                   utf8_string_object );
#endif
		Py_BEGIN_ALLOW_THREADS

		result = libcreg_file_open(
		          pycreg_file->file,
		          filename_narrow,
		          LIBCREG_OPEN_READ,
		          &error );

		Py_END_ALLOW_THREADS

		Py_DecRef(
		 utf8_string_object );
#endif
		if( result != 1 )
		{
			pycreg_error_raise(
			 error,
			 PyExc_IOError,
			 "%s: unable to open file.",
			 function );

			libcerror_error_free(
			 &error );

			return( NULL );
		}
		Py_IncRef(
		 Py_None );

		return( Py_None );
	}
	PyErr_Clear();

#if PY_MAJOR_VERSION >= 3
	result = PyObject_IsInstance(
	          string_object,
	          (PyObject *) &PyBytes_Type );
#else
	result = PyObject_IsInstance(
	          string_object,
	          (PyObject *) &PyString_Type );
#endif
	if( result == -1 )
	{
		pycreg_error_fetch_and_raise(
		 PyExc_RuntimeError,
		 "%s: unable to determine if string object is of type string.",
		 function );

		return( NULL );
	}
	else if( result != 0 )
	{
		PyErr_Clear();

#if PY_MAJOR_VERSION >= 3
		filename_narrow = PyBytes_AsString(
		                   string_object );
#else
		filename_narrow = PyString_AsString(
		                   string_object );
#endif
		Py_BEGIN_ALLOW_THREADS

		result = libcreg_file_open(
		          pycreg_file->file,
		          filename_narrow,
		          LIBCREG_OPEN_READ,
		          &error );

		Py_END_ALLOW_THREADS

		if( result != 1 )
		{
			pycreg_error_raise(
			 error,
			 PyExc_IOError,
			 "%s: unable to open file.",
			 function );

			libcerror_error_free(
			 &error );

			return( NULL );
		}
		Py_IncRef(
		 Py_None );

		return( Py_None );
	}
	PyErr_Format(
	 PyExc_TypeError,
	 "%s: unsupported string object type.",
	 function );

	return( NULL );
}

/* Opens a file using a file-like object
 * Returns a Python object if successful or NULL on error
 */
PyObject *pycreg_file_open_file_object(
           pycreg_file_t *pycreg_file,
           PyObject *arguments,
           PyObject *keywords )
{
	PyObject *file_object       = NULL;
	libcerror_error_t *error    = NULL;
	static char *function       = "pycreg_file_open_file_object";
	static char *keyword_list[] = { "file_object", "mode", NULL };
	char *mode                  = NULL;
	int result                  = 0;

	if( pycreg_file == NULL )
	{
		PyErr_Format(
		 PyExc_ValueError,
		 "%s: invalid file.",
		 function );

		return( NULL );
	}
	if( PyArg_ParseTupleAndKeywords(
	     arguments,
	     keywords,
	     "O|s",
	     keyword_list,
	     &file_object,
	     &mode ) == 0 )
	{
		return( NULL );
	}
	if( ( mode != NULL )
	 && ( mode[ 0 ] != 'r' ) )
	{
		PyErr_Format(
		 PyExc_ValueError,
		 "%s: unsupported mode: %s.",
		 function,
		 mode );

		return( NULL );
	}
	PyErr_Clear();

	result = PyObject_HasAttrString(
	          file_object,
	          "read" );

	if( result != 1 )
	{
		PyErr_Format(
		 PyExc_TypeError,
		 "%s: unsupported file object - missing read attribute.",
		 function );

		return( NULL );
	}
	PyErr_Clear();

	result = PyObject_HasAttrString(
	          file_object,
	          "seek" );

	if( result != 1 )
	{
		PyErr_Format(
		 PyExc_TypeError,
		 "%s: unsupported file object - missing seek attribute.",
		 function );

		return( NULL );
	}
	if( pycreg_file->file_io_handle != NULL )
	{
		pycreg_error_raise(
		 error,
		 PyExc_IOError,
		 "%s: invalid file - file IO handle already set.",
		 function );

		goto on_error;
	}
	if( pycreg_file_object_initialize(
	     &( pycreg_file->file_io_handle ),
	     file_object,
	     &error ) != 1 )
	{
		pycreg_error_raise(
		 error,
		 PyExc_MemoryError,
		 "%s: unable to initialize file IO handle.",
		 function );

		libcerror_error_free(
		 &error );

		goto on_error;
	}
	Py_BEGIN_ALLOW_THREADS

	result = libcreg_file_open_file_io_handle(
	          pycreg_file->file,
	          pycreg_file->file_io_handle,
	          LIBCREG_OPEN_READ,
	          &error );

	Py_END_ALLOW_THREADS

	if( result != 1 )
	{
		pycreg_error_raise(
		 error,
		 PyExc_IOError,
		 "%s: unable to open file.",
		 function );

		libcerror_error_free(
		 &error );

		goto on_error;
	}
	Py_IncRef(
	 Py_None );

	return( Py_None );

on_error:
	if( pycreg_file->file_io_handle != NULL )
	{
		libbfio_handle_free(
		 &( pycreg_file->file_io_handle ),
		 NULL );
	}
	return( NULL );
}

/* Closes a file
 * Returns a Python object if successful or NULL on error
 */
PyObject *pycreg_file_close(
           pycreg_file_t *pycreg_file,
           PyObject *arguments PYCREG_ATTRIBUTE_UNUSED )
{
	libcerror_error_t *error = NULL;
	static char *function    = "pycreg_file_close";
	int result               = 0;

	PYCREG_UNREFERENCED_PARAMETER( arguments )

	if( pycreg_file == NULL )
	{
		PyErr_Format(
		 PyExc_ValueError,
		 "%s: invalid file.",
		 function );

		return( NULL );
	}
	Py_BEGIN_ALLOW_THREADS

	result = libcreg_file_close(
	          pycreg_file->file,
	          &error );

	Py_END_ALLOW_THREADS

	if( result != 0 )
	{
		pycreg_error_raise(
		 error,
		 PyExc_IOError,
		 "%s: unable to close file.",
		 function );

		libcerror_error_free(
		 &error );

		return( NULL );
	}
	if( pycreg_file->file_io_handle != NULL )
	{
		Py_BEGIN_ALLOW_THREADS

		result = libbfio_handle_free(
		          &( pycreg_file->file_io_handle ),
		          &error );

		Py_END_ALLOW_THREADS

		if( result != 1 )
		{
			pycreg_error_raise(
			 error,
			 PyExc_MemoryError,
			 "%s: unable to free libbfio file IO handle.",
			 function );

			libcerror_error_free(
			 &error );

			return( NULL );
		}
	}
	Py_IncRef(
	 Py_None );

	return( Py_None );
}

/* Determines if the file is corrupted
 * Returns a Python object if successful or NULL on error
 */
PyObject *pycreg_file_is_corrupted(
           pycreg_file_t *pycreg_file,
           PyObject *arguments PYCREG_ATTRIBUTE_UNUSED )
{
	libcerror_error_t *error = NULL;
	static char *function    = "pycreg_file_is_corrupted";
	int result               = 0;

	PYCREG_UNREFERENCED_PARAMETER( arguments )

	if( pycreg_file == NULL )
	{
		PyErr_Format(
		 PyExc_ValueError,
		 "%s: invalid file.",
		 function );

		return( NULL );
	}
	Py_BEGIN_ALLOW_THREADS

	result = libcreg_file_is_corrupted(
	          pycreg_file->file,
	          &error );

	Py_END_ALLOW_THREADS

	if( result == -1 )
	{
		pycreg_error_raise(
		 error,
		 PyExc_IOError,
		 "%s: unable to determine if file is corrupted.",
		 function );

		libcerror_error_free(
		 &error );

		return( NULL );
	}
	if( result != 0 )
	{
		Py_IncRef(
		 (PyObject *) Py_True );

		return( Py_True );
	}
	Py_IncRef(
	 (PyObject *) Py_False );

	return( Py_False );
}

/* Retrieves the codepage used for ASCII strings in the file
 * Returns a Python object if successful or NULL on error
 */
PyObject *pycreg_file_get_ascii_codepage(
           pycreg_file_t *pycreg_file,
           PyObject *arguments PYCREG_ATTRIBUTE_UNUSED )
{
	PyObject *string_object     = NULL;
	libcerror_error_t *error    = NULL;
	const char *codepage_string = NULL;
	static char *function       = "pycreg_file_get_ascii_codepage";
	int ascii_codepage          = 0;
	int result                  = 0;

	PYCREG_UNREFERENCED_PARAMETER( arguments )

	if( pycreg_file == NULL )
	{
		PyErr_Format(
		 PyExc_ValueError,
		 "%s: invalid file.",
		 function );

		return( NULL );
	}
	Py_BEGIN_ALLOW_THREADS

	result = libcreg_file_get_ascii_codepage(
	          pycreg_file->file,
	          &ascii_codepage,
	          &error );

	Py_END_ALLOW_THREADS

	if( result != 1 )
	{
		pycreg_error_raise(
		 error,
		 PyExc_IOError,
		 "%s: unable to retrieve ASCII codepage.",
		 function );

		libcerror_error_free(
		 &error );

		return( NULL );
	}
	codepage_string = pycreg_codepage_to_string(
	                   ascii_codepage );

	if( codepage_string == NULL )
	{
		PyErr_Format(
		 PyExc_ValueError,
		 "%s: unsupported ASCII codepage: %d.",
		 function,
		 ascii_codepage );

		return( NULL );
	}
#if PY_MAJOR_VERSION >= 3
	string_object = PyBytes_FromString(
	                 codepage_string );
#else
	string_object = PyString_FromString(
	                 codepage_string );
#endif
	if( string_object == NULL )
	{
		PyErr_Format(
		 PyExc_IOError,
		 "%s: unable to convert codepage string into string object.",
		 function );

		return( NULL );
	}
	return( string_object );
}

/* Sets the codepage used for ASCII strings in the file
 * Returns 1 if successful or -1 on error
 */
int pycreg_file_set_ascii_codepage_from_string(
     pycreg_file_t *pycreg_file,
     const char *codepage_string )
{
	libcerror_error_t *error      = NULL;
	static char *function         = "pycreg_file_set_ascii_codepage_from_string";
	size_t codepage_string_length = 0;
	uint32_t feature_flags        = 0;
	int ascii_codepage            = 0;
	int result                    = 0;

	if( pycreg_file == NULL )
	{
		PyErr_Format(
		 PyExc_ValueError,
		 "%s: invalid file.",
		 function );

		return( -1 );
	}
	if( codepage_string == NULL )
	{
		PyErr_Format(
		 PyExc_ValueError,
		 "%s: invalid codepage string.",
		 function );

		return( -1 );
	}
	codepage_string_length = narrow_string_length(
	                          codepage_string );

	feature_flags = LIBCLOCALE_CODEPAGE_FEATURE_FLAG_HAVE_WINDOWS;

	if( libclocale_codepage_copy_from_string(
	     &ascii_codepage,
	     codepage_string,
	     codepage_string_length,
	     feature_flags,
	     &error ) != 1 )
	{
		pycreg_error_raise(
		 error,
		 PyExc_RuntimeError,
		 "%s: unable to determine ASCII codepage.",
		 function );

		libcerror_error_free(
		 &error );

		return( -1 );
	}
	Py_BEGIN_ALLOW_THREADS

	result = libcreg_file_set_ascii_codepage(
	          pycreg_file->file,
	          ascii_codepage,
	          &error );

	Py_END_ALLOW_THREADS

	if( result != 1 )
	{
		pycreg_error_raise(
		 error,
		 PyExc_IOError,
		 "%s: unable to set ASCII codepage.",
		 function );

		libcerror_error_free(
		 &error );

		return( -1 );
	}
	return( 1 );
}

/* Sets the codepage used for ASCII strings in the file
 * Returns a Python object if successful or NULL on error
 */
PyObject *pycreg_file_set_ascii_codepage(
           pycreg_file_t *pycreg_file,
           PyObject *arguments,
           PyObject *keywords )
{
	char *codepage_string       = NULL;
	static char *keyword_list[] = { "codepage", NULL };
	int result                  = 0;

	if( PyArg_ParseTupleAndKeywords(
	     arguments,
	     keywords,
	     "s",
	     keyword_list,
	     &codepage_string ) == 0 )
	{
		return( NULL );
	}
	result = pycreg_file_set_ascii_codepage_from_string(
	          pycreg_file,
	          codepage_string );

	if( result != 1 )
	{
		return( NULL );
	}
	Py_IncRef(
	 Py_None );

	return( Py_None );
}

/* Sets the codepage used for ASCII strings in the file
 * Returns a Python object if successful or NULL on error
 */
int pycreg_file_set_ascii_codepage_setter(
     pycreg_file_t *pycreg_file,
     PyObject *string_object,
     void *closure PYCREG_ATTRIBUTE_UNUSED )
{
	PyObject *utf8_string_object = NULL;
	char *codepage_string        = NULL;
	static char *function        = "pycreg_file_set_ascii_codepage_setter";
	int result                   = 0;

	PYCREG_UNREFERENCED_PARAMETER( closure )

	PyErr_Clear();

	result = PyObject_IsInstance(
	          string_object,
	          (PyObject *) &PyUnicode_Type );

	if( result == -1 )
	{
		pycreg_error_fetch_and_raise(
		 PyExc_RuntimeError,
		 "%s: unable to determine if string object is of type Unicode.",
		 function );

		return( -1 );
	}
	else if( result != 0 )
	{
		/* The codepage string should only contain ASCII characters.
		 */
		utf8_string_object = PyUnicode_AsUTF8String(
		                      string_object );

		if( utf8_string_object == NULL )
		{
			pycreg_error_fetch_and_raise(
			 PyExc_RuntimeError,
			 "%s: unable to convert Unicode string to UTF-8.",
			 function );

			return( -1 );
		}
#if PY_MAJOR_VERSION >= 3
		codepage_string = PyBytes_AsString(
		                   utf8_string_object );
#else
		codepage_string = PyString_AsString(
		                   utf8_string_object );
#endif
		if( codepage_string == NULL )
		{
			return( -1 );
		}
		result = pycreg_file_set_ascii_codepage_from_string(
		          pycreg_file,
		          codepage_string );

		if( result != 1 )
		{
			return( -1 );
		}
		return( 0 );
	}
	PyErr_Clear();

#if PY_MAJOR_VERSION >= 3
	result = PyObject_IsInstance(
	          string_object,
	          (PyObject *) &PyBytes_Type );
#else
	result = PyObject_IsInstance(
	          string_object,
	          (PyObject *) &PyString_Type );
#endif
	if( result == -1 )
	{
		pycreg_error_fetch_and_raise(
		 PyExc_RuntimeError,
		 "%s: unable to determine if string object is of type string.",
		 function );

		return( -1 );
	}
	else if( result != 0 )
	{
#if PY_MAJOR_VERSION >= 3
		codepage_string = PyBytes_AsString(
		                   string_object );
#else
		codepage_string = PyString_AsString(
		                   string_object );
#endif
		if( codepage_string == NULL )
		{
			return( -1 );
		}
		result = pycreg_file_set_ascii_codepage_from_string(
		          pycreg_file,
		          codepage_string );

		if( result != 1 )
		{
			return( -1 );
		}
		return( 0 );
	}
	PyErr_Format(
	 PyExc_TypeError,
	 "%s: unsupported string object type.",
	 function );

	return( -1 );
}

/* Retrieves the format version
 * Returns a Python object if successful or NULL on error
 */
PyObject *pycreg_file_get_format_version(
           pycreg_file_t *pycreg_file,
           PyObject *arguments PYCREG_ATTRIBUTE_UNUSED )
{
	char utf8_string[ 4 ];

	PyObject *string_object  = NULL;
	libcerror_error_t *error = NULL;
	static char *function    = "pycreg_file_get_format_version";
	uint16_t major_version   = 0;
	uint16_t minor_version   = 0;
	int result               = 0;

	PYCREG_UNREFERENCED_PARAMETER( arguments )

	if( pycreg_file == NULL )
	{
		PyErr_Format(
		 PyExc_ValueError,
		 "%s: invalid file.",
		 function );

		return( NULL );
	}
	Py_BEGIN_ALLOW_THREADS

	result = libcreg_file_get_format_version(
	          pycreg_file->file,
	          &major_version,
	          &minor_version,
	          &error );

	Py_END_ALLOW_THREADS

	if( result != 1 )
	{
		pycreg_error_raise(
		 error,
		 PyExc_IOError,
		 "%s: unable to retrieve format version.",
		 function );

		libcerror_error_free(
		 &error );

		return( NULL );
	}
	if( major_version > 9 )
	{
		PyErr_Format(
		 PyExc_ValueError,
		 "%s: major version out of bounds.",
		 function );

		return( NULL );
	}
	if( minor_version > 9 )
	{
		PyErr_Format(
		 PyExc_ValueError,
		 "%s: minor version out of bounds.",
		 function );

		return( NULL );
	}
	utf8_string[ 0 ] = '0' + (char) major_version;
	utf8_string[ 1 ] = '.';
	utf8_string[ 2 ] = '0' + (char) minor_version;
	utf8_string[ 3 ] = 0;

	/* Pass the string length to PyUnicode_DecodeUTF8 otherwise it makes
	 * the end of string character is part of the string.
	 */
	string_object = PyUnicode_DecodeUTF8(
	                 utf8_string,
	                 (Py_ssize_t) 3,
	                 NULL );

	if( string_object == NULL )
	{
		PyErr_Format(
		 PyExc_IOError,
		 "%s: unable to convert UTF-8 string into Unicode object.",
		 function );

		return( NULL );
	}
	return( string_object );
}

/* Retrieves the type
 * Returns a Python object if successful or NULL on error
 */
PyObject *pycreg_file_get_type(
           pycreg_file_t *pycreg_file,
           PyObject *arguments PYCREG_ATTRIBUTE_UNUSED )
{
	PyObject *integer_object = NULL;
	libcerror_error_t *error = NULL;
	static char *function    = "pycreg_file_get_type";
	uint32_t value_32bit     = 0;
	int result               = 0;

	PYCREG_UNREFERENCED_PARAMETER( arguments )

	if( pycreg_file == NULL )
	{
		PyErr_Format(
		 PyExc_ValueError,
		 "%s: invalid file.",
		 function );

		return( NULL );
	}
	Py_BEGIN_ALLOW_THREADS

	result = libcreg_file_get_type(
	          pycreg_file->file,
	          &value_32bit,
	          &error );

	Py_END_ALLOW_THREADS

	if( result != 1 )
	{
		pycreg_error_raise(
		 error,
		 PyExc_IOError,
		 "%s: unable to retrieve type.",
		 function );

		libcerror_error_free(
		 &error );

		return( NULL );
	}
	integer_object = PyLong_FromUnsignedLong(
	                  (unsigned long) value_32bit );

	return( integer_object );
}

/* Retrieves the root key
 * Returns a Python object if successful or NULL on error
 */
PyObject *pycreg_file_get_root_key(
           pycreg_file_t *pycreg_file,
           PyObject *arguments PYCREG_ATTRIBUTE_UNUSED )
{
	PyObject *key_object     = NULL;
	libcerror_error_t *error = NULL;
	libcreg_key_t *root_key  = NULL;
	static char *function    = "pycreg_file_get_root_key";
	int result               = 0;

	PYCREG_UNREFERENCED_PARAMETER( arguments )

	if( pycreg_file == NULL )
	{
		PyErr_Format(
		 PyExc_ValueError,
		 "%s: invalid file.",
		 function );

		return( NULL );
	}
	Py_BEGIN_ALLOW_THREADS

	result = libcreg_file_get_root_key(
	          pycreg_file->file,
	          &root_key,
	          &error );

	Py_END_ALLOW_THREADS

	if( result == -1 )
	{
		pycreg_error_raise(
		 error,
		 PyExc_IOError,
		 "%s: unable to retrieve root key.",
		 function );

		libcerror_error_free(
		 &error );

		goto on_error;
	}
	else if( result == 0 )
	{
		Py_IncRef(
		 Py_None );

		return( Py_None );
	}
	key_object = pycreg_key_new(
	              root_key,
	              (PyObject *) pycreg_file );

	if( key_object == NULL )
	{
		PyErr_Format(
		 PyExc_MemoryError,
		 "%s: unable to create root key object.",
		 function );

		goto on_error;
	}
	return( key_object );

on_error:
	if( root_key != NULL )
	{
		libcreg_key_free(
		 &root_key,
		 NULL );
	}
	return( NULL );
}

/* Retrieves the key specified by the path
 * Returns a Python object if successful or NULL on error
 */
PyObject *pycreg_file_get_key_by_path(
           pycreg_file_t *pycreg_file,
           PyObject *arguments,
           PyObject *keywords )
{
	PyObject *key_object        = NULL;
	libcerror_error_t *error    = NULL;
	libcreg_key_t *key          = NULL;
	static char *function       = "pycreg_file_get_key_by_path";
	static char *keyword_list[] = { "path", NULL };
	char *utf8_path             = NULL;
	size_t utf8_path_length     = 0;
	int result                  = 0;

	if( pycreg_file == NULL )
	{
		PyErr_Format(
		 PyExc_ValueError,
		 "%s: invalid file.",
		 function );

		return( NULL );
	}
	if( PyArg_ParseTupleAndKeywords(
	     arguments,
	     keywords,
	     "s",
	     keyword_list,
	     &utf8_path ) == 0 )
	{
		goto on_error;
	}
	utf8_path_length = narrow_string_length(
	                    utf8_path );

	Py_BEGIN_ALLOW_THREADS

	result = libcreg_file_get_key_by_utf8_path(
	          pycreg_file->file,
	          (uint8_t *) utf8_path,
	          utf8_path_length,
	          &key,
	          &error );

	Py_END_ALLOW_THREADS

	if( result == -1 )
	{
		pycreg_error_raise(
		 error,
		 PyExc_IOError,
		 "%s: unable to retrieve key.",
		 function );

		libcerror_error_free(
		 &error );

		goto on_error;
	}
	else if( result == 0 )
	{
		Py_IncRef(
		 Py_None );

		return( Py_None );
	}
	key_object = pycreg_key_new(
	              key,
	              (PyObject *) pycreg_file );

	if( key_object == NULL )
	{
		PyErr_Format(
		 PyExc_MemoryError,
		 "%s: unable to create key object.",
		 function );

		goto on_error;
	}
	return( key_object );

on_error:
	if( key != NULL )
	{
		libcreg_key_free(
		 &key,
		 NULL );
	}
	return( NULL );
}

