#include <stdio.h>
#include <unistd.h>

int main (int argc, char* argv[]) {
	if (argc < 2){
		fprintf (stderr, "One Argument required.\n");
		return 1;
	}
	printf ("setlogin(%s)\n", argv[1]);
	if (setlogin (argv[1]) < 0){
		perror("setlogin");
		return 2;
	}
	return 0;
}
