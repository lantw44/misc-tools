#ifdef __FreeBSD__
# define _WITH_GETLINE
#else
# define _POSIX_C_SOURCE 200809L
# define _XOPEN_SOURCE 700
#endif

#include <assert.h>
#include <errno.h>
#include <grp.h>
#include <locale.h>
#include <pwd.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/types.h>
#include <sys/acl.h>
#include <unistd.h>

// Needed to access non-portable functions on Linux
#ifdef __SYS_ACL_H
# include <acl/libacl.h>
#endif

typedef enum {
	CMD_MODIFY_ACTION_EDIT,
	CMD_MODIFY_ACTION_DELETE,
	CMD_MODIFY_ACTION_LAST,
} CmdModifyAction;


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

static acl_type_t read_acl_type (void) {
#define READ_ACL_TYPE_INVALID (-1)
	static_assert (ACL_TYPE_ACCESS != READ_ACL_TYPE_INVALID, "ACL_TYPE_ACCESS == READ_ACL_TYPE_INVALID");
	static_assert (ACL_TYPE_DEFAULT != READ_ACL_TYPE_INVALID, "ACL_TYPE_DEFAULT == READ_ACL_TYPE_INVALID");
#ifdef ACL_TYPE_NFS4
	static_assert (ACL_TYPE_NFS4 != READ_ACL_TYPE_INVALID, "ACL_TYPE_NFS4 == READ_ACL_TYPE_INVALID");
	const char* input = read_input ("Mode [1=access 2=default 3=nfsv4]: ");
#else
	const char* input = read_input ("Mode [1=access 2=default]: ");
#endif

	switch (input[0]) {
		case '1':
			return ACL_TYPE_ACCESS;
		case '2':
			return ACL_TYPE_DEFAULT;
#ifdef ACL_TYPE_NFS4
		case '3':
			return ACL_TYPE_NFS4;
#endif
		default:
			return READ_ACL_TYPE_INVALID;
	}

	return READ_ACL_TYPE_INVALID;
}

static void entry_display (acl_entry_t entry, unsigned int count) {
	acl_tag_t tag;
	acl_permset_t permset;

	void* qualifier_ptr;
	uid_t* uid_ptr;
	gid_t* gid_ptr;

	if (check_error_int (acl_get_tag_type (entry, &tag), "acl_get_tag_type")) {
		return;
	}
	if (tag == ACL_USER || tag == ACL_GROUP) {
		if (check_error_ptr (qualifier_ptr = acl_get_qualifier (entry), "acl_get_qualifier")) {
			return;
		}
	}
	if (check_error_int (acl_get_permset (entry, &permset), "acl_get_permset")) {
		return;
	}

	printf ("%u: ", count);
	switch (tag) {
		case ACL_USER:
		case ACL_USER_OBJ:
			putchar ('u');
			break;
		case ACL_GROUP:
		case ACL_GROUP_OBJ:
			putchar ('g');
			break;
		case ACL_OTHER:
			putchar ('o');
			break;
		case ACL_MASK:
			putchar ('m');
	}
	putchar (':');

	if (tag == ACL_USER) {
		struct passwd* pwd;
		uid_ptr = qualifier_ptr;
		errno = 0;
		if ((pwd = getpwuid (*uid_ptr)) == NULL) {
			printf ("\033[1;31m%lu\033[0m", (unsigned long)*uid_ptr);
		} else {
			printf ("%s(%lu)", pwd->pw_name, (unsigned long)*uid_ptr);
		}
	} else if (tag == ACL_GROUP) {
		struct group* grp;
		gid_ptr = qualifier_ptr;
		errno = 0;
		if ((grp = getgrgid (*gid_ptr)) == NULL) {
			printf ("\033[1;31m%lu\033[0m", (unsigned long)*gid_ptr);
		} else {
			printf ("%s(%lu)", grp->gr_name, (unsigned long)*gid_ptr);
		}
	}
	putchar (':');

#ifdef _SYS_ACL_H_ // TrustedBSD and FreeBSD
	putchar (acl_get_perm_np (permset, ACL_READ) ? 'r' : '-');
	putchar (acl_get_perm_np (permset, ACL_WRITE) ? 'w' : '-');
	putchar (acl_get_perm_np (permset, ACL_EXECUTE) ? 'x' : '-');
#elif defined(__SYS_ACL_H) // Linux and possibly Hurd or other GNU systems
	putchar (acl_get_perm (permset, ACL_READ) ? 'r' : '-');
	putchar (acl_get_perm (permset, ACL_WRITE) ? 'w' : '-');
	putchar (acl_get_perm (permset, ACL_EXECUTE) ? 'x' : '-');
#else
# error "Sorry, your operating system is not supported."
#endif
}

static void entry_edit(acl_entry_t* entry){
	acl_tag_t tag;
	const char* input;

	input = read_input ("Tag [u g uo go o m]: ");
	switch (input[0]) {
		case 'u':
			switch (input[1]) {
				case '\0':
					tag = ACL_USER;
					break;
				case 'o':
					tag = ACL_USER_OBJ;
					break;
				default:
					return;
			}
			break;
		case 'g':
			switch (input[1]){
				case '\0':
					tag = ACL_GROUP;
					break;
				case 'o':
					tag = ACL_GROUP_OBJ;
					break;
				default:
					return;
			}
			break;
		case 'o':
			tag = ACL_OTHER;
			break;
		case 'm':
			tag = ACL_MASK;
			break;
		default:
			return;
	}

	if (check_error_int (acl_set_tag_type (*entry, tag), "acl_set_tag_type")) {
		return;
	}

	if (tag == ACL_USER) {
		input = read_input ("User [user name or #uid]: ");
		uid_t uid;
		if (input[0] == '#') {
			uid = (uid_t)atol (&input[1]);
		} else {
			struct passwd* pwd;
			errno = 0;
			if (check_error_ptr (pwd = getpwnam (input), "getpwnam")) {
				return;
			}
			uid = pwd->pw_uid;
		}
		if (check_error_int (acl_set_qualifier (*entry, &uid), "acl_set_qualifier")) {
			return;
		}
	} else if (tag == ACL_GROUP) {
		input = read_input ("Group [group name or #gid]: ");
		gid_t gid;
		if (input[0] == '#') {
			gid = (gid_t)atol (&input[1]);
		} else {
			struct group* grp;
			errno = 0;
			if (check_error_ptr (grp = getgrnam (input), "getgrnam")) {
				return;
			}
			gid = grp->gr_gid;
		}
		if (check_error_int (acl_set_qualifier (*entry, &gid), "acl_set_qualifier")) {
			return;
		}
	}

	input = read_input ("Permission: ");
	size_t len = strlen (input);

	acl_permset_t permset;
	if (check_error_int (acl_get_permset (*entry, &permset), "acl_get_permset")) {
		return;
	}
	if (check_error_int (acl_clear_perms (permset), "acl_clear_perms")) {
		return;
	}
	for (size_t i = 0; i < len; i++) {
		switch (input[i]) {
			case 'r':
				if (check_error_int (acl_add_perm (permset, ACL_READ), "acl_add_perm")) {
					return;
				}
				break;
			case 'w':
				if (check_error_int (acl_add_perm (permset, ACL_WRITE), "acl_add_perm")) {
					return;
				}
				break;
			case 'x':
				if (check_error_int (acl_add_perm (permset, ACL_EXECUTE), "acl_add_perm")) {
					return;
				}
		}
	}
}

static void cmd_add (acl_t* alist) {
	acl_entry_t entry;

	if (check_error_int (acl_create_entry (alist, &entry), "acl_create_entry")) {
		return;
	}
	entry_edit (&entry);
}

static void cmd_modify (const acl_t* alist, CmdModifyAction action) {
	acl_entry_t entry;
	int rval = acl_get_entry (*alist, ACL_FIRST_ENTRY, &entry);
	unsigned int count = 0;

	do {
		count++;
		switch (rval) {
			case 1:
				check_error_int (rval, "acl_get_entry");
				break;
			case 0:
				return;
			case -1:
				check_error_int (rval, "acl_get_entry");
				return;
		}

		entry_display (entry, count);
		putchar(' ');

		switch (action) {
			case CMD_MODIFY_ACTION_DELETE: {
				const char* input = read_input ("Delete [y/n/q]? ");
				switch (input[0]) {
					case 'q':
						return;
					case 'y':
						check_error_int (acl_delete_entry (*alist, entry), "acl_delete_entry");
				}
			} break;

			case CMD_MODIFY_ACTION_EDIT: {
				const char* input = read_input ("Edit [y/n/q]? ");
				switch (input[0]) {
					case 'q':
						return;
					case 'y':
						entry_edit (&entry);
				}
			} break;

			default:
				puts ("This should never happen");
				return;
		}
	} while ((rval = acl_get_entry (*alist, ACL_NEXT_ENTRY, &entry)) == 1);
}

static void cmd_read (acl_t* alist){
	acl_t alist_new;

	char* name = strdup (read_input ("File name= "));
	acl_type_t type = read_acl_type ();

	if (type == READ_ACL_TYPE_INVALID) {
		free (name);
		return;
	}

	if (!check_error_ptr (alist_new = acl_get_file (name, type), "acl_get_file")) {
		check_error_int (acl_free (*alist), "acl_free");
		*alist = alist_new;
	}
	free (name);
}

static void cmd_write(const acl_t* alist){
	char* name = strdup (read_input ("File name= "));
	acl_type_t type = read_acl_type ();

	if (type == READ_ACL_TYPE_INVALID) {
		free (name);
		return;
	}

	check_error_int (acl_set_file (name, type, *alist), "acl_set_file");
	free (name);
}

static void cmd_zzz (void){
	const char* name = read_input ("File name= ");
	check_error_int (acl_delete_def_file (name), "acl_delete_def_file");
}

int main (int argc, char* argv[]) {
	setlocale (LC_ALL, "");

	acl_t alist;

	if (check_error_ptr (alist = acl_init (4), "acl_init")) {
		return 1;
	}

	while (true) {
		const char* input = read_input ("\033[1;33macl>\033[0m ");

		if (feof (stdin)) {
			goto loop_end;
		}

		switch (input[0]) {
			case 'a':
				cmd_add (&alist);
				break;
			case 'c':
				check_error_int (acl_calc_mask (&alist), "acl_calc_mask");
				break;
			case 'd':
				cmd_modify (&alist, CMD_MODIFY_ACTION_DELETE);
				break;
			case 'e':
				cmd_modify (&alist, CMD_MODIFY_ACTION_EDIT);
				break;
			case 'i': {
				acl_t alist_new;
				int count;
				input = read_input ("Count= ");
				count = atoi (input);
				if (!check_error_ptr (alist_new = acl_init (count), "acl_init")) {
					check_error_int (acl_free (alist), "acl_free");
					alist = alist_new;
				}
			} break;
			case 'p': {
				char* atext;
				if (!check_error_ptr (atext = acl_to_text (alist, NULL), "acl_to_text")) {
					fputs (atext, stdout);
					if (atext[strlen (atext) - 1] != '\n') {
						putchar ('\n');
					}
					check_error_int (acl_free (atext), "acl_free");
				}
			} break;
			case 'q':
				goto loop_end;
			case 'r':
				cmd_read (&alist);
				break;
			case 'v':
				if (acl_valid (alist) == 0) {
					puts ("Current ACL structure is \033[1;32mvalid\033[0m.");
				} else {
					puts ("Current ACL structure is \033[1;31minvalid\033[0m.");
				}
				break;
			case 'w':
				cmd_write (&alist);
				break;
			case 'z':
				cmd_zzz ();
				break;
			default:
				fputs (
					"  a     Add an ACL entry\n"
					"  c     Automatically generate the mask value\n"
					"  d     Delete ACL entries\n"
					"  e     Edit ACL entries\n"
					"  i     Clear and initialize an empty ACL structure\n"
					"  p     Print current ACL structure\n"
					"  q     Quit this program\n"
					"  r     Read ACL structure from file\n"
					"  v     Verify current ACL\n"
					"  w     Write ACL structure to file\n"
					"  z     Delete default ACL entries from file\n"
					, stdout);
		}
	}

loop_end:
	check_error_int (acl_free (alist), "acl_free");
	return 0;
}
