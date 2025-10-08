# SynOS Kernel Build Instructions

## Overview

The SynOS kernel has both a library (`syn-kernel`) and a bootable binary (`kernel`). Due to the no_std nature of the kernel binary, it requires special build configuration.

## Building

### Library Only (Default)

The kernel library is built automatically as part of the workspace:

```bash
cargo check --workspace
cargo build --workspace
```

### Kernel Binary

The kernel binary requires the `kernel-binary` feature and must be built for the `x86_64-unknown-none` target:

```bash
# Using the convenient alias (recommended):
cargo kernel-check  # Check compilation
cargo kernel-build  # Build the kernel binary

# Or manually:
cargo check --manifest-path=src/kernel/Cargo.toml \
  --bin kernel \
  --features kernel-binary \
  --target x86_64-unknown-none
```

## Why This Configuration?

1. **Separate Library and Binary**: The kernel library is used by other workspace members and should build normally. The binary is a standalone bootable kernel.

2. **Target Specification**: The kernel binary must be built for `x86_64-unknown-none` (bare metal) to avoid pulling in `std` library dependencies.

3. **Feature Flag**: The `kernel-binary` feature prevents the binary from being built during normal workspace operations, which would fail due to target mismatch.

4. **No Default Target**: We don't set a default target in the kernel's cargo config because it would affect all workspace members when building.

## Dependencies

The kernel uses carefully configured no_std dependencies:

-   `spin` with `mutex`, `rwlock`, `once`, `spin_mutex`, `lazy` features
-   `linked_list_allocator` with `use_spin` feature
-   `x86_64` with `abi_x86_interrupt` feature
-   `ahash` with `compile-time-rng` (no getrandom, no runtime RNG)
-   `bootloader` for initial bootstrap

## Troubleshooting

### "duplicate lang item `panic_impl`" error

This means std is being pulled in. Check:

-   Are you building for `x86_64-unknown-none`?
-   Are all dependencies configured with `default-features = false`?
-   Is any dependency using `getrandom` or other std-only crates?

### "requires more registers than available" error

This can occur in release mode with aggressive optimization. Options:

-   Build in dev mode (check only)
-   Adjust optimization level in Cargo.toml
-   Refactor the offending inline assembly

## Creating a Bootable Image

Once built, create a bootable ISO:

```bash
./scripts/build-simple-kernel-iso.sh
```

This will create `build/syn_os.iso` that can be booted in QEMU or on real hardware.
