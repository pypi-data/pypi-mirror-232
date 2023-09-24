/*
 * Python object definition of the sequence and iterator object of keys
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

#if !defined( _PYCREG_KEYS_H )
#define _PYCREG_KEYS_H

#include <common.h>
#include <types.h>

#include "pycreg_libcreg.h"
#include "pycreg_python.h"

#if defined( __cplusplus )
extern "C" {
#endif

typedef struct pycreg_keys pycreg_keys_t;

struct pycreg_keys
{
	/* Python object initialization
	 */
	PyObject_HEAD

	/* The parent object
	 */
	PyObject *parent_object;

	/* The get item by index callback function
	 */
	PyObject* (*get_item_by_index)(
	             PyObject *parent_object,
	             int index );

	/* The current index
	 */
	int current_index;

	/* The number of items
	 */
	int number_of_items;
};

extern PyTypeObject pycreg_keys_type_object;

PyObject *pycreg_keys_new(
           PyObject *parent_object,
           PyObject* (*get_item_by_index)(
                        PyObject *parent_object,
                        int index ),
           int number_of_items );

int pycreg_keys_init(
     pycreg_keys_t *sequence_object );

void pycreg_keys_free(
      pycreg_keys_t *sequence_object );

Py_ssize_t pycreg_keys_len(
            pycreg_keys_t *sequence_object );

PyObject *pycreg_keys_getitem(
           pycreg_keys_t *sequence_object,
           Py_ssize_t item_index );

PyObject *pycreg_keys_iter(
           pycreg_keys_t *sequence_object );

PyObject *pycreg_keys_iternext(
           pycreg_keys_t *sequence_object );

#if defined( __cplusplus )
}
#endif

#endif /* !defined( _PYCREG_KEYS_H ) */

