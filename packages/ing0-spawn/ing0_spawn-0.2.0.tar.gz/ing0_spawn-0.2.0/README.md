# ing0's spawn

## Usage

```s
Usage:

  ing0 available
  ing0 create NAME DISTRIBUTION RELEASE ARCH
  ing0 exec NAME [EXTRA ...]
```

## Getting started

```s
sudo apt install systemd-container qemu-user-static
sudo ing0 create my-arch-arm64-release-env arch current arm64
sudo ing0 exec my-arch-arm64-release-env pacman -Sy --noconfirm base-devel git lz4 util-linux-libs zlib
sudo ing0 exec my-arch-arm64-release-env --chdir=/mnt ./configure'
sudo ing0 exec my-arch-arm64-release-env --chdir=/mnt make -j7
```
