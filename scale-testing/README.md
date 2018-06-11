#ChRIS Performance and Scale Testing

Scripts to test the scalability, durability, and overall performance of the ChRIS system

## Setup:
### Prerequisites:
* running instances of [pman](https://github.com/FNNDSC/pman) and [pfioh](https://github.com/FNNDSC/pfioh), either locally or on the MOC (Mass Open Cloud)

### Configuration:
* **PLUGIN**: the image plugin to be tested
* **SWIFT_PATH**: the path to the swift-credentials.cfg file (only necessary if using swift storage)
* **CHRIS_PATH**: the path to the ChRIS-E2E directory
* **PMAN_IP**: the IP address on which pman is running (sudo oc get route pman)
* **PFIOH_IP**: the IP address on which pman is running (sudo oc get route pfioh)
* **MAX_DELAY**: how many seconds to continue running pman status requests before declaring the job failed
  - also accounts for the variable time that pman requests will take on different image plugins
* **CAPTURE**: whether or not to compute and capture resource utilization. Note that this is done by periodically logging resource utilization displayed by the top command, and therefore only computes resource utilization on an individual machine, and will not work if ChRIS is running on the MOC. Therefore only set CAPTURE to True when running ChRIS locally, otherwise set to False.
* **SIZE**: the size of the directory to test ("small", "medium", or "large", corresponding to 1MB, 25MB, and 100MB, respectively)

## Testing

### Configuration:
* **PLUGIN**, **CHRIS_PATH**, and **SIZE** always need to be set
* **PFIOH_IP** and **PMAN_IP** need to be set if pfioh and/or pman are being tested
* **SWIFT_PATH** needs to be set if swift backend is being implemented
* test-specific configuration variables are explained below


### test_local:
* Executes a push, performs a pman request, pulls, and computes resource utilization
* Output is written to file test\_local\_output_<date and time>.txt in current directory
* **Config:**
  * **RANGE**: number of requests to perform
* **To Run:**

        $ python3 test_local.py 

### test_time:
* Computes performance metrics after running the system under load over a given amount of time
* **Config:**
  * **RANGE**: number of concurrent requests to perform
  * **TIME**: how long, in minutes, to run the test for
* **To Run:**

        $ python3 test_pfioh_time.py 
        $ python3 test_pman_time.py

### test_request:
* Computes system performance of the system under load at an increasing number of concurrent requests
* For example, setting **RANGE** to 30 means the test will run the system at 1 - 30 requests and calculate resource utilization after each is completed
* Output is written to test\_pfioh\_request\_<date and time>.txt and test\_pman\_request\_<date and time>.txt, respectively
* **Config**
  * **RANGE** : number of requests to scale up to
* **To Run:**

        $ python3 test_pfioh_request.py 
        $ python3 test_pman_request.py