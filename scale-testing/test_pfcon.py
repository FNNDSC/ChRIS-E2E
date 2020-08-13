import os
import time
import subprocess
import shlex
from subprocess import Popen, PIPE
import configparser

config = configparser.ConfigParser()
config.read('config.cfg')
file_names = ["/tmp/pfcon.log", "/tmp/pfioh.log", "/tmp/pman.log"]

working_directory = os.path.join(config.get('ConfigInfo', 'CHRIS_PATH'), "ChRIS-E2E/scripts")
HOST_IP = config.get('ConfigInfo', 'PFCON_IP')
concurrent_threads = int(config.get('ConfigInfo', 'RANGE'))
# dicom_files_path = config.get('ConfigInfo', 'DICOM_FILES_PATH')

specific_dicom_file = config.get('ConfigInfo', 'DICOM_FILE')
counter_limit = int(int(config.get('ConfigInfo', 'MAX_DELAY')) / 10)


def keep_logs():
    subprocess.call([f"{working_directory}/log_service.sh pfcon"], shell=True)
    subprocess.call([f"{working_directory}/log_service.sh pman"], shell=True)
    subprocess.call([f"{working_directory}/log_service.sh pfioh"], shell=True)


def end_logs():
    subprocess.call([f"{working_directory}/end_log.sh"], shell=True)


def get_status_job(job_id):
    status_job_cmd = f'bash {working_directory}/pfcon_job_status.sh {HOST_IP} {job_id}'
    process = Popen(shlex.split(status_job_cmd), stdout=PIPE, stderr=PIPE, shell=False, close_fds=True)
    stdout, stderr = process.communicate()
    index_status = str(stdout).rfind('status')
    return 'true' in str(stdout)[index_status:]


# Run FS Plugin
print("Starting FS Plugin")
start = time.time()
success_rate = 0

keep_logs()
subprocess.call([f"{working_directory}/fs_feed.sh {HOST_IP} {concurrent_threads}"], shell=True)

this_counter = 0
done_status = True
while not get_status_job(concurrent_threads):
    if this_counter > counter_limit:
        print(f"FS Plugin {concurrent_threads} was unsuccessful")
        done_status = False
        break
    time.sleep(10)
    this_counter += 1
if done_status:
    success_rate += 1
    print(f"FS Plugin was successful")
else:
    print(f"FS Plugin was not successful")

end_logs()
runtime = time.time() - start

for individual_file in file_names:
    count = 0
    cpu = []
    mem = 0
    f = open(individual_file, "r")

    for line in f:
        try:
            curr = line.split()
            cpu.append(float(curr[0]))
            mem += float(curr[1])
            count += 1
        except Exception:
            continue
    f.close()

    service_name = os.path.splitext(os.path.basename(individual_file))[0]
    cpu_util = max(cpu)
    mem_util = mem / count

    service_results = "FS PLUGIN: \n____________\nSuccess Rate is: %s\nCPU utilization is: %s\nMemory utilization is: " \
                      "%s\nRuntime is %s\n" \
                      % (str(100 * success_rate), str(cpu_util), str(mem_util), str(runtime))

    results = open(f"{service_name}_fs.txt", "w+")
    results.write(service_results)

# Run DS Plugin
start = time.time()
keep_logs()
# list_files = [f for f in os.listdir(dicom_files_path) if f.endswith('.dcm')]
success_rate = 0

for thread in range(concurrent_threads):
    print(f"Starting DS Plugin {10 * 1 + concurrent_threads + thread}")
    subprocess.call([
        f"{working_directory}/ds_feed.sh {HOST_IP} {10 * 1 + concurrent_threads + thread} {specific_dicom_file}"
    ], shell=True)

for thread in range(concurrent_threads):
    this_counter = 0
    done_status = True
    while not get_status_job(10 * 1 + concurrent_threads + thread):
        if this_counter > counter_limit:
            print(f"DS Plugin {10 * 1 + concurrent_threads + thread} was unsuccessful")
            done_status = False
            break
        time.sleep(10)
        this_counter += 1
    if done_status:
        success_rate += 1
        print(f"DS Plugin {10 * 1 + concurrent_threads + thread} was successful")

end_logs()
runtime = time.time() - start

for individual_file in file_names:
    count = 0
    cpu = []
    mem = 0
    f = open(individual_file, "r")

    for line in f:
        try:
            curr = line.split()
            cpu.append(float(curr[0]))
            mem += float(curr[1])
            count += 1
        except Exception:
            continue
    f.close()

    service_name = os.path.splitext(os.path.basename(individual_file))[0]
    cpu_util = max(cpu)
    mem_util = mem / count

    service_results = "DS PLUGIN: \n____________\nSuccess Rate is: %s\nCPU utilization is: %s\nMemory utilization is: " \
                      "%s\nRuntime is %s\n" \
                      % (str(100 * success_rate / concurrent_threads), str(cpu_util), str(mem_util), str(runtime))

    results = open(f"{service_name}_ds.txt", "w+")
    results.write(service_results)
