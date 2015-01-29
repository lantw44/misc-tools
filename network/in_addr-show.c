#include <arpa/inet.h>
#include <stdint.h>
#include <stdio.h>
#include <netinet/in.h>
#include <sys/socket.h>

int main (int argc, char *argv[]) {
	char ipstr[INET_ADDRSTRLEN];
	unsigned long ipbin;

	for (int i = 1; i < argc; i++) {
		if (sscanf (argv[i], "%lx", &ipbin) <= 0) {
			return 1;
		}
		struct in_addr ipaddr = { .s_addr = ipbin };
		if (inet_ntop (AF_INET, &ipaddr, ipstr, INET_ADDRSTRLEN) == NULL) {
			return 2;
		}
		puts (ipstr);
	}

	return 0;
}
