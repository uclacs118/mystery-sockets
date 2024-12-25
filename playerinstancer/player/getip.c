#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <ifaddrs.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include "getip.h"

void get_ip_address() {
    struct ifaddrs *ifaddr, *ifa;
    char ip[INET6_ADDRSTRLEN];
    printf("List of ALL associated IP Addresses:\n");

    // Get the list of network interfaces
    if (getifaddrs(&ifaddr) == -1) {
        perror("getifaddrs");
        return;
    }

    // Loop through the linked list of interfaces
    for (ifa = ifaddr; ifa != NULL; ifa = ifa->ifa_next) {
        // Check if the interface is up and has an IP address
        if (ifa->ifa_addr && (ifa->ifa_addr->sa_family == AF_INET)) {
            // Convert the IP address to a readable format (IPv4)
            void *tmp_addr_ptr = &((struct sockaddr_in *)ifa->ifa_addr)->sin_addr;
            inet_ntop(AF_INET, tmp_addr_ptr, ip, sizeof(ip));
            printf("IP Address: %s\n", ip);
        }
    }

    // Free the memory allocated by getifaddrs
    freeifaddrs(ifaddr);
}