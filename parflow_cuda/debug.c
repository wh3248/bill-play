#include <stdio.h>
#include <time.h>

void logMessage(const char * message) {
    const char * debugFilePath = "/home/wh3248/workspaces/bill-play/parflow_cuda/debug.txt";

    char timeText[100];
    time_t now = time(NULL);
    struct tm *t = localtime(&now);


    strftime(timeText, sizeof(timeText)-1, "%Y-%m-%d %H:%M:%S", t);

    FILE * fp = fopen(debugFilePath, "a");
    fprintf(fp, "%s: %s\n", timeText, message);
    fclose(fp);
}

int main() {
    logMessage("this is a message");
    logMessage("second message");
}