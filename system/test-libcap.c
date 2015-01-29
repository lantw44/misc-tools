#define _POSIX_C_SOURCE 200809L
#define _XOPEN_SOURCE 700

#include <ctype.h>
#include <errno.h>
#include <locale.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/capability.h>

static void print_function_result (bool success, const char* function){
	if (success) {
		printf ("\033[1;32m%s\033[0m: OK\n", function);
	} else {
		printf ("\033[1;31m%s\033[0m: %s\n", function, strerror (errno));
	}
}

static bool check_error_int (int rval, const char* function) {
	if (rval < 0){
		print_function_result (false, function);
		return true;
	} else {
		print_function_result (true, function);
		return false;
	}
}

static bool check_error_ptr (void* rval, const char* function) {
	if (rval == NULL) {
		print_function_result (false, function);
		return true;
	} else {
		print_function_result (true, function);
		return false;
	}
}

static const char* read_input (const char* prompt) {
	static char* buffer_ptr = NULL;
	static size_t buffer_len = 0;

	clearerr (stdin);
	fputs (prompt, stdout);
	fflush (stdout);

	ssize_t str_len = getline (&buffer_ptr, &buffer_len, stdin);
	if (str_len < 0) {
		free (buffer_ptr);
		buffer_ptr = NULL;
		buffer_len = 0;
		return "";
	}

	buffer_ptr[str_len - 1] = '\0';
	return buffer_ptr;
}

int main (int argc, char* argv[]) {
	setlocale (LC_ALL, "");

	cap_t store = NULL;

	while (true) {
		const char* input = read_input ("\033[1;33mcap>\033[m ");

		if (feof (stdin)) {
			goto loop_end;
		}

		switch (input[0]){
			case 'c': {
				cap_flag_t flag;
				input = read_input ("[E]ffective [P]ermitted [I]nheritable ? ");
				switch (toupper (input[0])) {
					case 'E':
						flag = CAP_EFFECTIVE;
						break;
					case 'P':
						flag = CAP_PERMITTED;
						break;
					case 'I':
						flag = CAP_INHERITABLE;
						break;
					default:
						continue;
				}
				check_error_int (cap_clear_flag (store, flag), "cap_clear_flag");
			} break;
			case 'e': {
				cap_flag_t flag;
				input = read_input ("[E]ffective [P]ermitted [I]nheritable ? ");
				switch (toupper (input[0])) {
					case 'E':
						flag = CAP_EFFECTIVE;
						break;
					case 'P':
						flag = CAP_PERMITTED;
						break;
					case 'I':
						flag = CAP_INHERITABLE;
						break;
					default:
						continue;
				}

				cap_value_t value;
				input = read_input ("Capability= ");
				if (check_error_int (cap_from_name (input, &value), "cap_from_name")) {
					break;
				}

				cap_flag_value_t flag_value;
				input = read_input ("[C]lear [S]et ? ");
				switch (toupper (input[0])) {
					case 'C':
					case 'R':
					case '0':
						flag_value = CAP_CLEAR;
						break;
					case 'S':
					case '1':
						flag_value = CAP_SET;
						break;
				}

				check_error_int (
					cap_set_flag (store, flag, 1, &value, flag_value),
					"cap_set_flag");
			} break;
			case 'i':
				if (store != NULL) {
					check_error_int (cap_free (store), "cap_free");
					store = NULL;
				}
				check_error_ptr (store = cap_init (), "cap_init");
				break;
			case 'f':
				if (store == NULL) {
					break;
				}
				check_error_int (cap_free (store), "cap_free");
				store = NULL;
				break;
			case 'r':
				if (store != NULL){
					check_error_int (cap_free(store), "cap_free");
					store = NULL;
				}
				input = read_input ("[P]rocess [F]ile ? ");
				switch(toupper (input[0])){
					case 'P':
					case '1':
						input = read_input ("PID= ");
						check_error_ptr (
							store = cap_get_pid ((pid_t)atol (input)),
							"cap_get_pid");
						break;
					case 'F':
					case '2':
						input = read_input ("File= ");
						check_error_ptr (
							store = cap_get_file (input),
							"cap_set_file");
						break;
				}
				break;
			case 'w':
				if (store != NULL) {
					input = read_input ("File= ");
					check_error_int (cap_set_file (input, store), "cap_set_file");
				}
				break;
			case 'p': {
				char *ctext;
				if (store == NULL) {
					break;
				}
				check_error_ptr (ctext = cap_to_text (store, NULL), "cap_to_text");
				if (ctext != NULL) {
					puts (ctext);
					check_error_int (cap_free (ctext), "cap_free");
				}
			} break;
			default:
				fputs (
					"  c\tClear a capability set\n"
					"  e\tEdit the capability data structure\n"
					"  f\tFree the capability data structure\n"
					"  i\tClear and Initialize a new capability\n"
					"  p\tPrint the current capability\n"
					"  r\tRead and Replace the capability\n"
					"  w\tSet the current capability to a process or a file\n",
					stdout);
		}
	}

loop_end:
	if (store != NULL) {
		check_error_int (cap_free (store), "cap_free");
		store = NULL;
	}
	return 0;
}
