import subprocess
import sys
import asyncio

failed = ""
outdatedCount = 0
finishedCount = 0

def progress_ring(complete = False, intermediate = False):
    global outdatedCount
    global finishedCount

    if sys.platform != "win32":
        return
    
    if outdatedCount == 0:
        progress = 0
    else:
        progress = int((finishedCount / outdatedCount) * 100)
    state = 0

    if complete:
        state = 0
    elif intermediate:
        state = 3
    elif failed == "":
        state = 1
    else:
        state = 2
    
    print(f"{chr(27)}]9;4;{state};{progress}{chr(7)}", end="")
        

async def update(name: str):
    global failed
    global outdatedCount
    global finishedCount

    # subprocess.call([sys.executable, "-m", "pip", "install", "--upgrade", name])
    process = await asyncio.create_subprocess_shell('"' + sys.executable + '"' + " -m pip install --upgrade " + name,
                                                    stdout=asyncio.subprocess.PIPE,
                                                    stderr=asyncio.subprocess.PIPE)
    
    return_code = await process.wait()
    
    finishedCount += 1
    progress_ring()

    if return_code == 0:
        print("Successfully updated " + name)
    else:
        print(await process.communicate())
        if failed == "":
            failed = name
        else:
            failed = failed + ", " + name

def update_packages():
    global outdatedCount

    """
        If calling from a python file, please use a subprocess instead.
    """
    
    progress_ring(intermediate = True)

    print("Getting outdated pip packages...")

    # Run pip list command to get the outdated packages
    outdated_packages = subprocess.check_output([sys.executable, '-m', 'pip', 'list', '--outdated']).decode('utf-8')

    # Split the output into lines and ignore the header
    lines = outdated_packages.strip().split('\n')[2:]

    if len(lines) <= 0:
        progress_ring(complete = True)
        print("No outdated packages found.")
        return
    
    outdatedCount = len(lines)

    print("Updating packages using pip...")
    # Update each package
    for line in lines:
        package_info = line.split()
        package_name = package_info[0]
        # subprocess.call([sys.executable, '-m', 'pip', 'install', '--upgrade', package_name])
        asyncio.run(update(package_name))

    print()

    if len(failed) == 0:
        print("All outdated packages have been updated. Thank you for using this package.")
    else:
        print("The following packages failed to install: " + failed)
    
    progress_ring(complete = True)