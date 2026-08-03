from pathlib import Path

import toml

zt_root = Path("ZeroTierOne")

# ZeroTier moved the Rust crate from rustybits/zeroidc to rustybits. Keep the
# cross-compile settings compatible with both layouts.
cargo_candidates = [zt_root / "rustybits" / "zeroidc" / "Cargo.toml", zt_root / "rustybits" / "Cargo.toml"]
cargo_toml_path = next((path for path in cargo_candidates if path.exists()), None)
if cargo_toml_path is not None:
    cargo_toml = toml.load(cargo_toml_path)
    cargo_toml.setdefault("dependencies", {})["openssl-sys"] = {
        "version": ">=0.9",
        "features": ["vendored"],
    }
    with cargo_toml_path.open("w") as file:
        toml.dump(cargo_toml, file)

config_candidates = [zt_root / "rustybits" / "zeroidc" / ".cargo" / "config.toml", zt_root / "rustybits" / ".cargo" / "config.toml"]
config_toml_path = next((path for path in config_candidates if path.exists()), config_candidates[-1])
if config_toml_path.exists():
    config_toml = toml.load(config_toml_path)
else:
    config_toml = {}
config_toml.setdefault("target", {})["aarch64-unknown-linux-gnu"] = {"linker": "aarch64-linux-gnu-gcc"}
config_toml_path.parent.mkdir(parents=True, exist_ok=True)
with config_toml_path.open("w") as file:
    toml.dump(config_toml, file)

# -------------------------------------------------------------------------------------------------------

# Patch ZeroTierOne/osdep/LinuxEthernetTap.cpp

linux_tap_path = zt_root / "osdep" / "LinuxEthernetTap.cpp"

linux_tap_match1 = 'int rc = pthread_setaffinity_np(self, sizeof(cpu_set_t), &cpuset);'
linux_tap_replace1 = 'int rc = sched_setaffinity(pthread_gettid_np(self), sizeof(cpu_set_t), &cpuset);'

linux_tap_match2 = '#include <sys/utsname.h>'
linux_tap_replace2 = '#include <sys/utsname.h>\n#include <sched.h>'

with linux_tap_path.open("r") as file:
    data = file.read()
    patch_NDK = data.replace(linux_tap_match1, linux_tap_replace1).replace(linux_tap_match2, linux_tap_replace2)

with linux_tap_path.open("w") as file:
    file.write(patch_NDK)

# -------------------------------------------------------------------------------------------------------

# Patch make-linux.mk

make_linux_path = zt_root / "make-linux.mk"
with make_linux_path.open("r") as file:
    data = file.read() 
    patch_aarch64 = data.replace(
                        '$(ZT_CARGO_FLAGS)', '$(ZT_CARGO_FLAGS) --target aarch64-unknown-linux-gnu --quiet'
                    )
    for library_name in ("libzeroidc.a", "librustybits.a"):
        patch_aarch64 = patch_aarch64.replace(
            f"rustybits/target/release/{library_name}",
            f"rustybits/target/aarch64-unknown-linux-gnu/release/{library_name}",
        )
    patch_arm = data.replace(
                        "$(shell $(CC) -dumpmachine | cut -d '-' -f 1)", 'armhf'
                    ).replace(
                        'override CFLAGS+=-mfloat-abi=hard -march=armv6zk -marm -mfpu=vfp -mno-unaligned-access -mtp=cp15 -mcpu=arm1176jzf-s',
                        'override CFLAGS+=-mfloat-abi=hard -march=armv7-a -marm -mfpu=vfp'
                    ).replace(
                        'override CXXFLAGS+=-mfloat-abi=hard -march=armv6zk -marm -mfpu=vfp -fexceptions -mno-unaligned-access -mtp=cp15 -mcpu=arm1176jzf-s',
                        'override CXXFLAGS+=-mfloat-abi=hard -march=armv7-a -marm -mfpu=vfp -fexceptions'
                    )
    patch_arm_ndk = data.replace(
                        "$(shell $(CC) -dumpmachine | cut -d '-' -f 1)", 'armhf'
                    ).replace(
                        'override CFLAGS+=-mfloat-abi=hard -march=armv6zk -marm -mfpu=vfp -mno-unaligned-access -mtp=cp15 -mcpu=arm1176jzf-s',
                        'override CFLAGS+=-march=armv7-a -marm -mfpu=vfp'
                    ).replace(
                        'override CXXFLAGS+=-mfloat-abi=hard -march=armv6zk -marm -mfpu=vfp -fexceptions -mno-unaligned-access -mtp=cp15 -mcpu=arm1176jzf-s',
                        'override CXXFLAGS+=-march=armv7-a -marm -mfpu=vfp -fexceptions'
                    )
    
with (make_linux_path.parent / (make_linux_path.name + ".aarch64")).open("w") as file:
    file.write(patch_aarch64)
with (make_linux_path.parent / (make_linux_path.name + ".arm")).open("w") as file:
    file.write(patch_arm)
with (make_linux_path.parent / (make_linux_path.name + ".arm.ndk")).open("w") as file:
    file.write(patch_arm_ndk)

# Patch ZeroTierOne/osdep/OSUtils.cpp

osutil_path = zt_root / "osdep" / "OSUtils.cpp"
with osutil_path.open("r") as file:
    data = file.read().replace('/var/lib/zerotier-one', '/data/adb/zerotier/home')
with osutil_path.open("w") as file:
    file.write(data)
