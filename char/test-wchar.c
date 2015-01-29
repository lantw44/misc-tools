#define _POSIX_C_SOURCE 200809L
#define _XOPEN_SOURCE 700

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <locale.h>
#include <wchar.h>

int main () {
	setlocale (LC_ALL, "");

	char *line = NULL;
	ssize_t str_len = getline (&line, &(size_t){ 0 }, stdin);

	mbstate_t mbs;
	wchar_t wc;
	size_t mbrlen_result;
	int wcwidth_result;

	memset (&mbs, 0, sizeof (mbs));
	mbrlen_result = mbrlen (line, str_len, &mbs);

	memset (&mbs, 0, sizeof (mbs));
	mbrtowc (&wc, line, str_len, &mbs);
	wcwidth_result = wcwidth (wc);

	printf ("mbrlen = %zu, wcwidth = %d\n", mbrlen_result, wcwidth_result);
	free (line);
	return 0;
}
