import sys
import os


def check_resolve_connection():
    print("=== DaVinci Resolve Connection Check ===")

    # Standard paths for macOS
    RESOLVE_SCRIPT_API = "/Library/Application Support/Blackmagic Design/DaVinci Resolve/Developer/Scripting"
    RESOLVE_SCRIPT_LIB = "/Library/Application Support/Blackmagic Design/DaVinci Resolve/Developer/Scripting/Modules"
    RESOLVE_MODULES_PATH = "/Library/Application Support/Blackmagic Design/DaVinci Resolve/Developer/Scripting/Modules"

    os.environ["RESOLVE_SCRIPT_API"] = RESOLVE_SCRIPT_API
    os.environ["RESOLVE_SCRIPT_LIB"] = RESOLVE_SCRIPT_LIB

    print(f"Setting Env Vars:")
    print(f"RESOLVE_SCRIPT_API={os.environ['RESOLVE_SCRIPT_API']}")
    print(f"RESOLVE_SCRIPT_LIB={os.environ['RESOLVE_SCRIPT_LIB']}")

    print(f"Expected Modules Path: {RESOLVE_MODULES_PATH}")

    # Check if paths exist
    if os.path.exists(RESOLVE_MODULES_PATH):
        print("✅ Modules path exists")
    else:
        print("❌ Modules path NOT found")
        return

    # Add to sys.path
    if RESOLVE_MODULES_PATH not in sys.path:
        sys.path.insert(0, RESOLVE_MODULES_PATH)
        print("Added Modules path to sys.path")

    try:
        import DaVinciResolveScript as dvr_script

        print("✅ Successfully imported DaVinciResolveScript")
    except ImportError as e:
        print(f"❌ Failed to import DaVinciResolveScript: {e}")
        return

    try:
        resolve = dvr_script.scriptapp("Resolve")
        if resolve:
            print(f"✅ Connected to Resolve!")
            print(f"Product: {resolve.GetProductName()}")
            print(f"Version: {resolve.GetVersionString()}")

            pm = resolve.GetProjectManager()
            if pm:
                project = pm.GetCurrentProject()
                if project:
                    print(f"Current Project: {project.GetName()}")
                else:
                    print("No project currently open")
            else:
                print("Could not get Project Manager")
        else:
            print("❌ dvr_script.scriptapp('Resolve') returned None")
            print("Is DaVinci Resolve running?")
    except Exception as e:
        print(f"❌ Exception during connection: {e}")


if __name__ == "__main__":
    check_resolve_connection()
