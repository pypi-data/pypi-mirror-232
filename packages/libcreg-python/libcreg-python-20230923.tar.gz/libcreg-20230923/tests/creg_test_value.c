/*
 * Library value type test program
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
#include <file_stream.h>
#include <types.h>

#if defined( HAVE_STDLIB_H ) || defined( WINAPI )
#include <stdlib.h>
#endif

#include "creg_test_libcerror.h"
#include "creg_test_libcreg.h"
#include "creg_test_macros.h"
#include "creg_test_memory.h"
#include "creg_test_unused.h"

#include "../libcreg/libcreg_value.h"

/* Tests the libcreg_value_free function
 * Returns 1 if successful or 0 if not
 */
int creg_test_value_free(
     void )
{
	libcerror_error_t *error = NULL;
	int result               = 0;

	/* Test error cases
	 */
	result = libcreg_value_free(
	          NULL,
	          &error );

	CREG_TEST_ASSERT_EQUAL_INT(
	 "result",
	 result,
	 -1 );

	CREG_TEST_ASSERT_IS_NOT_NULL(
	 "error",
	 error );

	libcerror_error_free(
	 &error );

	return( 1 );

on_error:
	if( error != NULL )
	{
		libcerror_error_free(
		 &error );
	}
	return( 0 );
}

#if defined( __GNUC__ ) && !defined( LIBCREG_DLL_IMPORT )

#endif /* defined( __GNUC__ ) && !defined( LIBCREG_DLL_IMPORT ) */

/* The main program
 */
#if defined( HAVE_WIDE_SYSTEM_CHARACTER )
int wmain(
     int argc CREG_TEST_ATTRIBUTE_UNUSED,
     wchar_t * const argv[] CREG_TEST_ATTRIBUTE_UNUSED )
#else
int main(
     int argc CREG_TEST_ATTRIBUTE_UNUSED,
     char * const argv[] CREG_TEST_ATTRIBUTE_UNUSED )
#endif
{
	CREG_TEST_UNREFERENCED_PARAMETER( argc )
	CREG_TEST_UNREFERENCED_PARAMETER( argv )

#if defined( __GNUC__ ) && !defined( LIBCREG_DLL_IMPORT )

	/* TODO: add tests for libcreg_value_initialize */

#endif /* defined( __GNUC__ ) && !defined( LIBCREG_DLL_IMPORT ) */

	CREG_TEST_RUN(
	 "libcreg_value_free",
	 creg_test_value_free );

#if defined( __GNUC__ ) && !defined( LIBCREG_DLL_IMPORT )

	/* TODO: add tests for libcreg_value_is_corrupted */

	/* TODO: add tests for libcreg_value_get_offset */

	/* TODO: add tests for libcreg_value_get_name_size */

	/* TODO: add tests for libcreg_value_get_name */

	/* TODO: add tests for libcreg_value_get_utf8_name_size */

	/* TODO: add tests for libcreg_value_get_utf8_name */

	/* TODO: add tests for libcreg_value_get_utf16_name_size */

	/* TODO: add tests for libcreg_value_get_utf16_name */

	/* TODO: add tests for libcreg_value_get_value_type */

	/* TODO: add tests for libcreg_value_get_value_data_size */

	/* TODO: add tests for libcreg_value_get_value_data */

	/* TODO: add tests for libcreg_value_get_value_32bit */

	/* TODO: add tests for libcreg_value_get_value_64bit */

	/* TODO: add tests for libcreg_value_get_value_utf8_string_size */

	/* TODO: add tests for libcreg_value_get_value_utf8_string */

	/* TODO: add tests for libcreg_value_get_value_utf16_string_size */

	/* TODO: add tests for libcreg_value_get_value_utf16_string */

	/* TODO: add tests for libcreg_value_get_value_binary_data_size */

	/* TODO: add tests for libcreg_value_get_value_binary_data */

#endif /* defined( __GNUC__ ) && !defined( LIBCREG_DLL_IMPORT ) */

	return( EXIT_SUCCESS );

on_error:
	return( EXIT_FAILURE );
}

