import toml
import os

def patch_toml_file(file_path, updates):
    """更新 TOML 文件的指定内容"""
    try:
        data = toml.load(file_path)
        for key, value in updates.items():
            if key not in data or data[key] != value:
                data[key] = value
        with open(file_path, 'w') as f:
            toml.dump(data, f)
        print(f"Updated TOML file: {file_path}")
    except Exception as e:
        print(f"Error updating TOML file {file_path}: {e}")

def patch_text_file(file_path, patches, output_path=None):
    """更新文本文件的指定内容"""
    try:
        with open(file_path, 'r') as file:
            data = file.read()
        
        for old, new in patches.items():
            if old in data:
                data = data.replace(old, new)
        
        output_path = output_path or file_path
        with open(output_path, 'w') as file:
            file.write(data)
        print(f"Updated text file: {file_path} -> {output_path}")
    except Exception as e:
        print(f"Error updating text file {file_path}: {e}")

def main():
    # 配置补丁内容
    patches = [
        {
            "file": "ZeroTierOne/rustybits/zeroidc/Cargo.toml",
            "type": "toml",
            "updates": {
                'dependencies': {
                    'openssl-sys': { 'version': ">=0.9", 'features': ["vendored"] }
                }
            }
        },
        {
            "file": "ZeroTierOne/rustybits/zeroidc/.cargo/config.toml",
            "type": "toml",
            "updates": {
                'target': {
                    'aarch64-unknown-linux-gnu': { "linker": "aarch64-linux-gnu-gcc" }
                }
            }
        },
        {
            "file": "ZeroTierOne/make-linux.mk",
            "type": "text",
            "patches": {
                # Patch for aarch64
                "$(ZT_CARGO_FLAGS)": '$(ZT_CARGO_FLAGS) --target aarch64-unknown-linux-gnu --quiet',
                'rustybits/target/release/libzeroidc.a': 'rustybits/target/aarch64-unknown-linux-gnu/release/libzeroidc.a',
            },
            "output": "ZeroTierOne/make-linux.mk.aarch64"
        },
        {
            "file": "ZeroTierOne/make-linux.mk",
            "type": "text",
            "patches": {
                # Patch for ARM
                "$(shell $(CC) -dumpmachine | cut -d '-' -f 1)": 'armhf',
                'override CFLAGS+=-mfloat-abi=hard -march=armv6zk -marm -mfpu=vfp -mno-unaligned-access -mtp=cp15 -mcpu=arm1176jzf-s':
                'override CFLAGS+=-mfloat-abi=hard -march=armv7-a -marm -mfpu=vfp',
                'override CXXFLAGS+=-mfloat-abi=hard -march=armv6zk -marm -mfpu=vfp -fexceptions -mno-unaligned-access -mtp=cp15 -mcpu=arm1176jzf-s':
                'override CFLAGS+=-mfloat-abi=hard -march=armv7-a -marm -mfpu=vfp -fexceptions'
            },
            "output": "ZeroTierOne/make-linux.mk.arm"
        },
        {
            "file": "ZeroTierOne/osdep/OSUtils.cpp",
            "type": "text",
            "patches": {
                '/var/lib/zerotier-one': '/data/adb/zerotier/home'
            }
        }
    ]

    # 执行补丁
    for patch in patches:
        file_path = patch["file"]
        if patch["type"] == "toml":
            patch_toml_file(file_path, patch["updates"])
        elif patch["type"] == "text":
            patch_text_file(file_path, patch["patches"], patch.get("output"))

if __name__ == "__main__":
    main()