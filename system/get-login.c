#include <stdio.h>
#include <unistd.h>

int main () {
	printf ("getlogin() = %s\n", getlogin());
	return 0;
}
