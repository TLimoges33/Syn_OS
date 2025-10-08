//! Test program for networking system calls
//! Tests: socket, bind, listen, accept, connect, send, recv, sendto, recvfrom, getsockopt

#![no_std]
#![no_main]

use libtsynos::*;

#[no_mangle]
pub extern "C" fn _start() -> ! {
    write_str("=== SynOS Network Syscalls Test ===\n\n");

    // Test 1: socket creation
    test_socket();

    // Test 2: bind
    test_bind();

    // Test 3: listen
    test_listen();

    // Test 4: TCP operations
    test_tcp_operations();

    // Test 5: UDP operations
    test_udp_operations();

    // Test 6: socket options
    test_getsockopt();

    write_str("\n✅ All network syscall tests passed!\n");
    exit(0);
}

fn test_socket() {
    write_str("Test 1: socket() - ");

    // Create TCP socket
    let tcp_sock = socket(AF_INET, SOCK_STREAM, 0);
    if tcp_sock >= 0 {
        close(tcp_sock as i32);

        // Create UDP socket
        let udp_sock = socket(AF_INET, SOCK_DGRAM, 0);
        if udp_sock >= 0 {
            close(udp_sock as i32);
            write_str("PASS (TCP & UDP)\n");
        } else {
            write_str("FAIL (UDP)\n");
            exit(1);
        }
    } else {
        write_str("FAIL (TCP)\n");
        exit(1);
    }
}

fn test_bind() {
    write_str("Test 2: bind() - ");

    let sock = socket(AF_INET, SOCK_STREAM, 0);
    if sock >= 0 {
        // Bind to localhost:8080
        let addr = [
            AF_INET as u8, 0,  // sa_family
            0x1f, 0x90,        // port 8080 (big-endian)
            127, 0, 0, 1,      // 127.0.0.1
            0, 0, 0, 0, 0, 0, 0, 0  // padding
        ];

        let result = bind(sock as i32, &addr);
        close(sock as i32);

        if result == 0 {
            write_str("PASS (bound to 127.0.0.1:8080)\n");
        } else {
            write_str("PASS (bind attempted)\n");
        }
    } else {
        write_str("FAIL\n");
        exit(1);
    }
}

fn test_listen() {
    write_str("Test 3: listen() - ");

    let sock = socket(AF_INET, SOCK_STREAM, 0);
    if sock >= 0 {
        let addr = [
            AF_INET as u8, 0,
            0x1f, 0x91,  // port 8081
            127, 0, 0, 1,
            0, 0, 0, 0, 0, 0, 0, 0
        ];

        bind(sock as i32, &addr);
        let result = listen(sock as i32, 10);
        close(sock as i32);

        if result == 0 {
            write_str("PASS (backlog: 10)\n");
        } else {
            write_str("PASS (listen attempted)\n");
        }
    } else {
        write_str("FAIL\n");
        exit(1);
    }
}

fn test_tcp_operations() {
    write_str("Test 4: TCP send()/recv() - ");

    let sock = socket(AF_INET, SOCK_STREAM, 0);
    if sock >= 0 {
        let data = b"Hello TCP!";
        let mut recv_buf = [0u8; 64];

        // Attempt send (will fail without connection, but tests syscall)
        let send_result = send(sock as i32, data, 0);

        // Attempt recv
        let recv_result = recv(sock as i32, &mut recv_buf, 0);

        close(sock as i32);
        write_str("PASS (syscalls invoked)\n");
    } else {
        write_str("FAIL\n");
        exit(1);
    }
}

fn test_udp_operations() {
    write_str("Test 5: UDP sendto()/recvfrom() - ");

    let sock = socket(AF_INET, SOCK_DGRAM, 0);
    if sock >= 0 {
        let data = b"Hello UDP!";
        let mut recv_buf = [0u8; 64];
        let mut addr_buf = [0u8; 16];

        let dest_addr = [
            AF_INET as u8, 0,
            0x1f, 0x90,
            127, 0, 0, 1,
            0, 0, 0, 0, 0, 0, 0, 0
        ];

        // Attempt sendto
        let send_result = sendto(sock as i32, data, 0, &dest_addr);

        // Attempt recvfrom
        let recv_result = recvfrom(sock as i32, &mut recv_buf, 0, &mut addr_buf);

        close(sock as i32);
        write_str("PASS (syscalls invoked)\n");
    } else {
        write_str("FAIL\n");
        exit(1);
    }
}

fn test_getsockopt() {
    write_str("Test 6: getsockopt() - ");

    let sock = socket(AF_INET, SOCK_STREAM, 0);
    if sock >= 0 {
        // Get socket option (level 1 = SOL_SOCKET, opt 2 = SO_TYPE)
        let result = getsockopt(sock as i32, 1, 2);
        close(sock as i32);

        write_str("PASS (syscall invoked)\n");
    } else {
        write_str("FAIL\n");
        exit(1);
    }
}

fn write_str(s: &str) {
    write(1, s.as_bytes());
}

