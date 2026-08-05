#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/types.h>

#define BUFSIZE 128

void vuln(){
    char buf[BUFSIZE];
    // helpful leak to allow ret to payload on stack
    printf("buf: %p\n", buf);
    gets(buf);
    puts(buf);
    fflush(stdout);
}

int main(int argc, char **argv){
    // prevent IO buffering
    setvbuf(stdout, NULL, _IONBF, 0);
    setvbuf(stdin, NULL, _IONBF, 0);
    setvbuf(stderr, NULL, _IONBF, 0);

    vuln();
    return 0;
}
