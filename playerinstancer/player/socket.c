/* Credits: Xinyu Ma */

#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <errno.h>
#include <arpa/inet.h>
#include <sys/socket.h>
#include "rl.h"
#include "getip.h"

// char line_read[65537];
char ip_str[65537];
char buf[65537];

int tmp_errno;

void lineSleep() {
  usleep(100 * 1000);
}

void printStr(char* s) {
  printf("$ printf(\"%s\\n\")\n< %s\n", s, s);
  lineSleep();
}

void printCode(char* s) {
  printf("$ %s\n", s);
  lineSleep();
}

void printVal(int val, char* n) {
  printf("$ printf(\"%s: %%d\\n\", %s)\n< %s: %d\n", n, n, n, val);
  lineSleep();
}

void printErr() {
  printf("%s", "$ printf(\"Error with code %d: %s\\n\", errno, strerror(errno));\n");
  printf("< Error with code %d: %s\n", tmp_errno, strerror(tmp_errno));
  lineSleep();
}


void replace_escape_sequences_in_place(char *str) {
    int write_index = 0; // Index to write into
    int read_index = 0;  // Index to read from

    while (str[read_index] != '\0') {
        if (str[read_index] == '\\' && str[read_index + 1] == 'n') {
            str[write_index++] = '\n'; // Replace \n with newline
            read_index += 2;           // Skip past \ and n
        } else if (str[read_index] == '\\' && str[read_index + 1] == 'r') {
            str[write_index++] = '\r'; // Replace \r with carriage return
            read_index += 2;           // Skip past \ and r
        } else {
            str[write_index++] = str[read_index++]; // Copy character as-is
        }
    }
    str[write_index] = '\0'; // Null-terminate the string
}


int main() {
  initialize_readline();

  int sock = -1;
  struct sockaddr_in addr;
  socklen_t socklen;
  int port, buflen;

  setbuf(stdout, NULL);

  printf("INITIALIZING NETSIFT TOOLCHAIN...\n");
  printCode("int sock = -1;");
  printCode("struct sockaddr_in addr;");
  printCode("socklen_t socklen;");
  printCode("int port, buflen;");
  

  printf("INTERNAL NETSIFT TOOLCHAIN. Type help for available commands.\n");

  //printErr(5);
  
  char* line_read = NULL;
  while ((line_read = rl_gets()) != NULL) {

    if(strncmp(line_read, "exit", 4) == 0){
      break;
    } else if (strncmp(line_read, "getip", 5) == 0) {
      get_ip_address();
    } else if(strncmp(line_read, "socket", 6) == 0){
      // Print code
      printCode("sock = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);");

      // Create socket: IPv4 family, Stream socket, TCP protocol
      // Document: https://man7.org/linux/man-pages/man2/socket.2.html
      sock = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);
      tmp_errno = errno;
      printVal(sock, "sock");
      // -1 means error
      if (sock == -1) {
        printErr();
      }
    } else if(strncmp(line_read, "connect", 7) == 0) {
      if(sscanf(line_read, "connect %d %s %d", &sock, ip_str, &port) != 3){
        printf("Usage: connect SOCKET IP PORT\n");
        printf("Example: connect 3 192.168.1.1 1234\n");
        continue;
      }

      // Print code
      //printf("$ sockaddr_in addr;\n");
      //lineSleep();
      printf("$ addr.sin_family = AF_INET;\n");
      lineSleep();
      printf("$ addr.sin_port = htons(%d);\n", port);
      lineSleep();
      printf("$ ret = inet_pton(AF_INET, %s, &addr.sin_addr);\n", ip_str);
      lineSleep();

      // IPv4 family
      addr.sin_family = AF_INET;
      // Port number. Note that IP uses big-endian.
      addr.sin_port = htons(port);
      // Convert IP address from string to binary form
      int ret = inet_pton(AF_INET, ip_str, &addr.sin_addr);
      printVal(ret, "ret");
      if(!ret) {
        printStr("Invalid IP address");
        continue;
      }

      // Print code
      printf("$ ret = connect(%d, (sockaddr*)&addr, sizeof(addr));\n", sock);
      lineSleep();

      // Connect to a server
      // Document: https://man7.org/linux/man-pages/man2/connect.2.html
      ret = connect(sock, (struct sockaddr*)&addr, sizeof(addr));
      tmp_errno = errno;
      printVal(ret, "ret");
      if(ret == -1) {
        printErr();
      }
    } else if(strncmp(line_read, "bind", 4) == 0) {
      if(sscanf(line_read, "bind %d %s %d", &sock, ip_str, &port) != 3){
        printf("Usage: bind SOCKET IP PORT\n");
        printf("  use `any` for 0.0.0.0\n");
        printf("Example: bind 3 any 1234\n");
        continue;
      }

      // Print code
      //printf("$ struct sockaddr_in addr;\n");
      //lineSleep();
      printf("$ addr.sin_family = AF_INET;\n");
      lineSleep();
      printf("$ addr.sin_port = htons(%d);\n", port);
      lineSleep();

      addr.sin_family = AF_INET;
      addr.sin_port = htons(port);

      if(strcmp(ip_str, "any") == 0){
        printf("$ addr.sin_addr.s_addr = INADDR_ANY;\n");
        lineSleep();
        addr.sin_addr.s_addr = htonl(INADDR_ANY);
      } else {
        printf("$ ret = inet_pton(AF_INET, %s, &addr.sin_addr);\n", ip_str);
        int ret = inet_pton(AF_INET, ip_str, &addr.sin_addr);
        lineSleep();
        printVal(ret, "ret");
        lineSleep();
        if(!ret) {
          printStr("Invalid IP address");
          lineSleep();
          continue;
        }
      }

      // Print code
      printf("$ ret = bind(%d, (sockaddr*)&addr, sizeof(addr));\n", sock);
      lineSleep();

      // Bind the address with the socket, as a server
      // Document: https://man7.org/linux/man-pages/man2/bind.2.html
      int ret = bind(sock, (struct sockaddr*)&addr, sizeof(addr));
      tmp_errno = errno;
      printVal(ret, "ret");
      // printf("ret == %d\n", ret);
      if(ret == -1){
        printErr();
      }
    } else if(strncmp(line_read, "listen", 6) == 0) {
      if(sscanf(line_read, "listen %d", &sock) != 1){
        printf("Usage: listen SOCKET\n");
        printf("Example: listen 3\n");
        continue;
      }

      // Print code
      printf("$ ret = listen(%d, 0);\n", sock);

      // Listen to connection, with minimal backup queue
      int ret = listen(sock, 0);
      tmp_errno = errno;
      printVal(ret, "ret");
      // printf("ret == %d\n", ret);
      if(ret == -1){
        printErr();
      }
    } else if(strncmp(line_read, "accept", 6) == 0) {
      if(sscanf(line_read, "accept %d", &sock) != 1){
        printf("Usage: accept SOCKET\n");
        printf("Example: accept 3\n");
        continue;
      }



      // Print code
      printf("$ socklen = sizeof(addr);\n");
      lineSleep();
      printf("$ new_sock = accept(%d, (sockaddr*)&addr, &socklen);\n", sock);
      lineSleep();


      fcntl(sock, F_SETFL, fcntl(sock, F_GETFL, 0) | O_NONBLOCK);
      // Accept a connection
      // Document: https://man7.org/linux/man-pages/man2/accept.2.html
      // addr will contain the client's IP address and port
      socklen = sizeof(addr);

      
      int new_sock = accept(sock, (struct sockaddr*)&addr, &socklen);
      tmp_errno = errno;
      printVal(new_sock, "new_sock");
      if(new_sock == -1) {
        printErr();
        continue;
      }
      printCode("inet_ntop(AF_INET, &addr.sin_addr, ip_str, socklen);");
      inet_ntop(AF_INET, &addr.sin_addr, ip_str, socklen);

      printf("$ printf(\"IP: %%s\", ip_str);\n");
      lineSleep();
      printf("< IP: %s\n", ip_str);
      lineSleep();

      printf("$ printf(\"Port: %%d\", ntohs(addr.sin_port));\n");
      lineSleep();
      printf("< Port: %d\n", ntohs(addr.sin_port));
      lineSleep();

      // printVal("ntohs(addr.sin_port)", ntohs(addr.sin_port));
      // printf("Client IP address: %s port: %d\n", ip_str, ntohs(addr.sin_port));
      // printf("Now use socket %d to communicate with the client\n", new_sock);
      printVal(new_sock, "new_sock");
      printStr("Now use this new socket to communicate with the client");
    } else if(strncmp(line_read, "send", 4) == 0) {
      if(sscanf(line_read, "send %d %[^\n]", &sock, buf) != 2){
        printf("Usage: send SOCKET STRING\n");
        printf("Example: send 3 GET /\\r\\n\n");
        printf("Note: only \\n, \\r, and \\\\ escape sequences are supported\n");
        continue;
      }


      // Print code
      printf("$ ret = send(%d, \"%s\", %lu, 0);\n", sock, buf, strlen(buf));
      replace_escape_sequences_in_place(buf);
      // Send data to the socket (you may also use write)
      // Document: https://man7.org/linux/man-pages/man2/send.2.html
      // Length is strlen(buf)
      // The last argument is flag, can be ignored for now
      int ret = send(sock, buf, strlen(buf), 0);
      tmp_errno = errno;


      printVal(ret, "ret");
      // printf("ret == %d\n", ret);
      if(ret == -1){
        printErr();
        // printf("Error with code %d: %s\n", errno, strerror(errno));
      }
    } else if(strncmp(line_read, "recv", 4) == 0) {
      if(sscanf(line_read, "recv %d %d", &sock, &buflen) != 2){
        printf("Usage: recv SOCKET BUFFER-LENGTH\n");
        printf("Example: recv 3 2000\n");
        continue;
      }
      if(buflen < 0){
        buflen = 0;
      } else if (buflen > (int)sizeof(buf)) {
        buflen = sizeof(buf);
      }

      // Print code
      printf("$ ret = recv(%d, buf, %d, MSG_DONTWAIT);\n", sock, buflen);

      // Receive data from the socket (you may also use read)
      // Document: https://man7.org/linux/man-pages/man2/recv.2.html
      // The last argument is flag, can be ignored for now
      int ret = recv(sock, buf, buflen, MSG_DONTWAIT);
      tmp_errno = errno;
      printVal(ret, "ret");
      // printf("ret == %d\n", ret);
      if(ret == -1){
        printErr();
        // printf("Error with code %d: %s\n", errno, strerror(errno));
      } else {
        buf[ret] = 0;  // Adding a tailing '\0' for print
        // printf("Received %d bytes\n", ret);
        // printStr(buf)
        printCode("buf[ret] = 0; // Add tailing \\0 for print");
        printf("$ printf(\"buf: %%s\\n\")\n");
        printf("buf: %s\n", buf);
      }
    } else if(strncmp(line_read, "close", 5) == 0) {
      if(sscanf(line_read, "close %d", &sock) != 1){
        printf("Usage: close SOCKET\n");
        printf("Example: close 3\n");
        continue;
      }

      // Print code
      printf("$ ret = close(%d);\n", sock);
      lineSleep();
      // Shutdown socket
      int ret = close(sock);
      tmp_errno = errno;
      printVal(ret, "ret");
      if(ret == -1){
        printErr();
      }
      sock = -1;
    } else {
      if (strncmp(line_read, "help", 4) != 0) {
        printf("Unknown command: %s\n", line_read);
      }
      printf("Supported syscalls: socket, bind, listen, accept, connect, send, recv, close\n");
      printf("Supported commands: getip, exit\n");
    }
  }
  printf("Exiting...\n");
  return 0;
}
