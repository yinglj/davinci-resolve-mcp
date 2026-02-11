#!/usr/bin/env python3
import os
import sys
import platform


def diagnose():
    print("--- DaVinci Resolve Connection Diagnostic ---")

    # 1. Check Platform
    system = platform.system()
    print(f"OS: {system}")

    # 2. Check Resolve Paths
    if system == "Darwin":  # macOS
        api_path = "/Library/Application Support/Blackmagic Design/DaVinci Resolve/Developer/Scripting"
        lib_path = "/Applications/DaVinci Resolve/DaVinci Resolve.app/Contents/Libraries/Fusion/fusionscript.so"
    elif system == "Windows":
        api_path = "C:\\ProgramData\\Blackmagic Design\\DaVinci Resolve\\Support\\Developer\\Scripting"
        lib_path = (
            "C:\\Program Files\\Blackmagic Design\\DaVinci Resolve\\fusionscript.dll"
        )
    else:
        print("Unsupported platform for this diagnostic.")
        return

    print(f"Expected API Path: {api_path}")
    print(f"Expected Lib Path: {lib_path}")

    if os.path.exists(api_path):
        print(f"✅ API Path exists")
    else:
        print(f"❌ API Path NOT found")

    if os.path.exists(lib_path):
        print(f"✅ Lib Path exists")
    else:
        print(f"❌ Lib Path NOT found")

    # 3. Check Environment Variables
    print(f"RESOLVE_SCRIPT_API: {os.environ.get('RESOLVE_SCRIPT_API', 'Not Set')}")
    print(f"RESOLVE_SCRIPT_LIB: {os.environ.get('RESOLVE_SCRIPT_LIB', 'Not Set')}")
    print(f"PYTHONPATH: {os.environ.get('PYTHONPATH', 'Not Set')}")

    # 4. Try Import
    modules_path = os.path.join(api_path, "Modules")
    if modules_path not in sys.path:
        sys.path.append(modules_path)

    os.environ["RESOLVE_SCRIPT_API"] = api_path
    os.environ["RESOLVE_SCRIPT_LIB"] = lib_path

    print("\nAttempting to import DaVinciResolveScript...")
    try:
        import DaVinciResolveScript as dvr_script

        print("✅ Import successful")

        print("Attempting to connect to Resolve application instance...")
        resolve = dvr_script.scriptapp("Resolve")
        if resolve:
            print(f"✅ Connection successful!")
            print(f"   Product: {resolve.GetProductName()}")
            print(f"   Version: {resolve.GetVersionString()}")
        else:
            print("❌ Connection failed: dvr_script.scriptapp('Resolve') returned None")
            print("   Possible reasons:")
            print("   1. DaVinci Resolve is not running.")
            print("   2. Scripting is not enabled in Resolve Preferences.")
            print(
                "      (Preferences -> System -> Control Panels -> External Control -> Scripting -> set to 'Local' or 'Network')"
            )
    except ImportError as e:
        print(f"❌ Import failed: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")


if __name__ == "__main__":
    diagnose()
