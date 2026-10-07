import subprocess, sys

print("Starting docker build...", flush=True)
result = subprocess.run(
    ['docker', 'build', '-t', 'cost-optimized-ml-app', 'c:/Users/Administrator/Desktop/ps4'],
    capture_output=True,
    text=True
)

with open('c:/Users/Administrator/Desktop/ps4/docker_build.txt', 'w') as f:
    f.write("=== STDOUT ===\n")
    f.write(result.stdout or "(empty)\n")
    f.write("\n=== STDERR ===\n")
    f.write(result.stderr or "(empty)\n")
    f.write(f"\n=== RETURN CODE: {result.returncode} ===\n")

print("Return code:", result.returncode)
print("Output saved to docker_build.txt")
