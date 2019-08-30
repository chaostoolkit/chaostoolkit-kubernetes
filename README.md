
# chaosToolkit-nimble (Guavus Chaos Test automation framework)

- [ChaosToolkit Overview](#ChaosToolkit Overview)
- [Jio Use Cases Implemented](#Jio Use Cases Implemented)
- [Installation](#Installation of chaostoolkit-nimble on the local system (MAC))
- [Resolving dependency issues on local system (MAC)](#Resolving dependency issues on the local system (MAC))

## ChaosToolkit Overview

*The end goal of using chaostoolkit is to practice chaos engineering, and discover how your system reacts when certain anomalies are injected in it. 

*By doing this in a controlled fashion, you may learn how to change the system accordingly and make it more resilient on multiple levels like application, network and platform.


### The Various Sections of an Experiment
##### `Controls`
```
*Here you declare the the control module, which is simply a set of functions that are called by the Chaos Toolkit when executing the experiment. 

*The Controls are applied per experiment.
https://docs.chaostoolkit.org/reference/extending/create-control-extension/
```
##### `The steady state hypothesis`
```
*The steady state hypothesis declares the various probes that will be applied as part of the hypothesis check.

*The hypothesis is played twice. The first time before we do anything else to ensure the system is indeed in a normal state,
The second time the hypothesis is applied is after the conditions were changed in the system, to validate it is still in a normal state.

*Hypothesis probes expect a tolerance property which tells the Chaos Toolkit how to validate a certain aspect of the state
```

##### `Method`
```
*The method is the anomaly injection block which changes the conditions of our system/application.

* This section is executed only if Hypothesis (above) is successfully met, else this section would be skipped.
```
##### `Rollbacks`
```
*Finally, the rollback section (which is optional) tries to remediate to the changes we made on/off the system during the anomaly injection.

*This block will be executed always irrespective of the fact that Hypothesis was met or not in the first time. 
```

#### `Sample Experiment json file` 
```
{
	"version": "1.0.0",
	"title": "What is the impact of an expired certificate on our application chain?",
	"description": "If a certificate expires, we should gracefully deal with the issue.",
	"tags": ["tls"],
	"controls": [{
		"name": "spark-related-controls",
		"provider": {
			"type": "python",
			"module": "chaostoolkit_nimble.controllers.spark.control"
		}
	}],
	"steady-state-hypothesis": {
		"title": "Application responds",
		"probes": [{
				"type": "probe",
				"name": "the-astre-service-must-be-running",
				"tolerance": true,
				"provider": {
					"type": "python",
					"module": "os.path",
					"func": "exists",
					"arguments": {
						"path": "astre.pid"
					}
				}
			},
			{
				"type": "probe",
				"name": "the-sunset-service-must-be-running",
				"tolerance": true,
				"provider": {
					"type": "python",
					"module": "os.path",
					"func": "exists",
					"arguments": {
						"path": "sunset.pid"
					}
				}
			},
			{
				"type": "probe",
				"name": "we-can-request-sunset",
				"tolerance": 200,
				"provider": {
					"type": "http",
					"timeout": 3,
					"verify_tls": false,
					"url": "https://localhost:8443/city/Paris"
				}
			}
		]
	},
	"method": [{
			"type": "action",
			"name": "swap-to-expired-cert",
			"provider": {
				"type": "process",
				"path": "cp",
				"arguments": "expired-cert.pem cert.pem"
			}
		},
		{
			"type": "probe",
			"name": "read-tls-cert-expiry-date",
			"provider": {
				"type": "process",
				"path": "openssl",
				"arguments": "x509 -enddate -noout -in cert.pem"
			}
		},
		{
			"type": "action",
			"name": "restart-astre-service-to-pick-up-certificate",
			"provider": {
				"type": "process",
				"path": "pkill",
				"arguments": "--echo -HUP -F astre.pid"
			}
		},
		{
			"type": "action",
			"name": "restart-sunset-service-to-pick-up-certificate",
			"provider": {
				"type": "process",
				"path": "pkill",
				"arguments": "--echo -HUP -F sunset.pid"
			},
			"pauses": {
				"after": 1
			}
		}
	],
	"rollbacks": [{
			"type": "action",
			"name": "swap-to-vald-cert",
			"provider": {
				"type": "process",
				"path": "cp",
				"arguments": "valid-cert.pem cert.pem"
			}
		},
		{
			"ref": "restart-astre-service-to-pick-up-certificate"
		},
		{
			"ref": "restart-sunset-service-to-pick-up-certificate"
		}
	]
}
```


## Jio Use Cases Implemented 
Job Name : Media Plane

Job frequency : 15min

Number of job instances being run: 1

Assumption : Job is already running on the cluster.

** NOTE:  No custom code required here by the user. These three use cases (i.e experiments) have been templatized and these templates have been stored on fileserver at location: 
`http://192.168.192.201/guavus/automation/chaos/exp_templates/spark/`
You need to provide this template path as an input to run your chaos experiments.


### Use case 1: Kill n number of spark executors for a spark job running on yarn and validate data for that job instance.
```
Chaos Experiment Template path (exp_template_file) = "automation/chaos/exp_templates/spark/executor_kill_exp.json"

------Before experiment control:
Read the user given testbed and initialize nimble `node_obj` object.

------Hypothesis section:
Check job is running on yarn

------Method section (Anomaly injection):
Kill spark job any active executors for the last spark driver attempt.

------After experiment control:
Wait for the job to complete on yarn and then fetch the job total execution time from yarn. (Time fetched: 1.33 minutes)


User inputs required: 
* Testbed config yaml
* Validation config yaml
* Chaos Experiment Template path:
* Num of executors to kill. Default is 1.

Pytest command:
python -m pytest -k "test_chaos_on_executor_kill  or test_data_validation_post_chaos" --testbed=chaostoolkit_nimble/resources/testbeds/open_nebula_135_35.yml  --componentAttributesConfig=chaostoolkit_nimble/resources/components/component_attributes_kerberos.yml --validationConfig=chaostoolkit_nimble/resources/validation/sample_validation_config.yml chaostoolkit_nimble/tests/sample/test_jio_spark_job.py
```

### Use case 2: Kill the spark driver for a spark job running on yarn and validate data for that job instance.
```
Chaos Experiment Template path (exp_template_file) = "automation/chaos/exp_templates/spark/driver_kill_exp.json"

------Before experiment control:
Read the user given testbed and initialize nimble `node_obj` object.

------Hypothesis section:
Check job is running on yarn

------Method section (Anomaly injection):
Kill the spark driver for this spark job.

------After experiment control:
Wait for the job to complete on yarn and then fetch the job total execution time from yarn. (Time fetched: 1.74 minutes)


User inputs required: 
* Testbed config yaml
* Validation config yaml
* Chaos Experiment Template path:

Pytest command:
python -m pytest -k "not(test_chaos_on_executor_kill  or test_chaos_on_driver_and_executor_kill)" --testbed=chaostoolkit_nimble/resources/testbeds/open_nebula_135_35.yml  --componentAttributesConfig=chaostoolkit_nimble/resources/components/component_attributes_kerberos.yml --validationConfig=chaostoolkit_nimble/resources/validation/sample_validation_config.yml chaostoolkit_nimble/tests/sample/test_jio_spark_job.py

```

### Use case 3: Kill the driver and n number of executors for a spark job running on yarn and validate data for that job instance.
```
Chaos Experiment Template path (exp_template_file) = "automation/chaos/exp_templates/spark/driver_and_executor_kill_exp.json"

------Before experiment control:
Read the user given testbed and initialize nimble `node_obj` object.

------Hypothesis section:
Check job is running on yarn

------Method section (Anomaly injection):
Kill the spark driver for this spark job and then kill any active executors for the new spark attempt.

------After experiment control:
Wait for the job to complete on yarn and then fetch the job total execution time from yarn. (Time fetched 1.76 minutes: )


User inputs required: 
* Testbed config yaml
* Validation config yaml
* Chaos Experiment Template path:
* Num of executors to kill. Default is 1.

Pytest command:
python -m pytest -k "test_chaos_on_driver_and_executor_kill or test_data_validation_post_chaos" --testbed=chaostoolkit_nimble/resources/testbeds/open_nebula_135_35.yml  --componentAttributesConfig=chaostoolkit_nimble/resources/components/component_attributes_kerberos.yml --validationConfig=chaostoolkit_nimble/resources/validation/sample_validation_config.yml chaostoolkit_nimble/tests/sample/test_jio_spark_job.py

```

## Installation of chaostoolkit-nimble on the local system (MAC)

`Assumptions` : 

* Python 3 is already installed on the system.

* Automation code from your own solution repo is already checked out on the system.

##### 1. Install chaostoolkit-nimble package
```
1.1 cd ../ ; mkdir chaos_virenv ; cd chaos_virenv
1.2 virtualenv --python=python3 venv
1.3 source venv/bin/activate
1.4 Remove nimble and add chaostoolkit-nimble in your requirements.txt
1.5 Install chaostoolkit-nimble in their virtualenv using command: 
1.6 pip install -r <PATH-TO_REQUIREMENTS.txt> --extra-index-url http://192.168.192.201:5050/simple/ --trusted-host 192.168.192.201
```

##### 2. Add this virtual env in pycharm
```
Pycharm --> Preferences --> Project interpreter --> settings --> show all --> add the chaos_virenv
```

##### 3. Post installation changes

3.1 Make sure the testbed file name follow the nomenclature `open_nebula_*`. If not then remane it accoridingly.
3.2 Add the chaos test case in the corresponding job's test file.
3.3 Update conftest.py with below piece of code

```
parser.addoption("--experimentsPath",
                     help="Relative path (to the project root) of the file containing chaos experiment json files. E.g. python -m pytest --validationConfig=resources/validation/chaos_exp_config.yml")
```

```
@pytest.fixture(scope="session", autouse=True)
def initialize_node_obj(request):
    testbed_file = request.config.getoption("--testbed")
    component_arttributes_file = request.config.getoption("--componentAttributesConfig")
    if not component_arttributes_file:
        component_arttributes_file = "nimble/resources/components/component_attributes.yml"
    setup_files_base_path = "%s/setup" % global_constants.DEFAULT_LOCAL_TMP_PATH
    if testbed_file:
        NodeManager.initialize(testbed_file, component_arttributes_file)
        ShellUtils.execute_shell_command(
            ShellUtils.remove_and_create_directory(setup_files_base_path))
        testbed_file_tmp_path = "%s/%s" % (setup_files_base_path, testbed_file.rsplit("/", 1)[1])
        component_arttributes_file_tmp_path = "%s/%s" % (
            setup_files_base_path, component_arttributes_file.rsplit("/", 1)[1])
        ShellUtils.execute_shell_command(ShellUtils.copy(testbed_file, testbed_file_tmp_path))
        ShellUtils.execute_shell_command(
            ShellUtils.copy(component_arttributes_file, component_arttributes_file_tmp_path))
    yield
    ShellUtils.execute_shell_command(ShellUtils.remove(setup_files_base_path, recursive=True))
```

## Resolving dependency issues on local system (MAC)
* `Install python 3 using below command`
```
brew install python3
```
* `Chaos html report generation issue`
```
pip install cairocffi  --- already satisfied
brew uninstall py2cairo   --- this will not install properly but one of its dependencies will get installed successfully. 'i.e'  "cairo"
export PKG_CONFIG_PATH="/usr/local/opt/libffi/lib/pkgconfig"
pip install pycairo
brew install pandoc
```

```
# Chaos Toolkit Kubernetes Support

[![Build Status](https://travis-ci.org/chaostoolkit/chaostoolkit-kubernetes.svg?branch=master)](https://travis-ci.org/chaostoolkit/chaostoolkit-kubernetes)
[![codecov](https://codecov.io/gh/chaostoolkit/chaostoolkit-kubernetes/branch/master/graph/badge.svg)](https://codecov.io/gh/chaostoolkit/chaostoolkit-kubernetes)
[![Python versions](https://img.shields.io/pypi/pyversions/chaostoolkit-kubernetes.svg)](https://www.python.org/)
[![Downloads](https://pepy.tech/badge/chaostoolkit-kubernetes)](https://pepy.tech/project/chaostoolkit-kubernetes)

This project contains activities, such as probes and actions, you can call from
your experiment through the Chaos Toolkit.

## Install

To be used from your experiment, this package must be installed in the Python
environment where [chaostoolkit][] already lives.

[chaostoolkit]: https://github.com/chaostoolkit/chaostoolkit

```
$ pip install chaostoolkit-kubernetes
```

## Usage

To use the probes and actions from this package, add the following to your
experiment file:

```json
{
    "name": "all-our-microservices-should-be-healthy",
    "type": "probe",
    "tolerance": "true",
    "provider": {
        "type": "python",
        "module": "chaosk8s.probes",
        "func": "microservice_available_and_healthy",
        "arguments": {
            "name": "myapp",
            "ns": "myns"
        }
    }
},
{
    "type": "action",
    "name": "terminate-db-pod",
    "provider": {
        "type": "python",
        "module": "chaosk8s.pod.actions",
        "func": "terminate_pods",
        "arguments": {
            "label_selector": "app=my-app",
            "name_pattern": "my-app-[0-9]$",
            "rand": true,
            "ns": "default"
        }
    },
    "pauses": {
        "after": 5
    }
}
```

That's it! Notice how the action gives you the way to kill one pod randomly.

Please explore the code to see existing probes and actions.

### Discovery

You may use the Chaos Toolkit to discover the capabilities of this extension:

```
$ chaos discover chaostoolkit-kubernetes --no-install
```

## Configuration

This extension to the Chaos Toolkit can use the Kubernetes configuration 
found at the usual place in your HOME directory under `~/.kube/`, or, when
run from a Pod in a Kubernetes cluster, it will use the local service account.
In that case, make sure to set the `CHAOSTOOLKIT_IN_POD` environment variable
to `"true"`.

You can also pass the credentials via secrets as follows:

```json
{
    "secrets": {
        "kubernetes": {
            "KUBERNETES_HOST": "http://somehost",
            "KUBERNETES_API_KEY": {
                "type": "env",
                "key": "SOME_ENV_VAR"
            }
        }
    }
}
```

Then in your probe or action:

```json
{
    "name": "all-our-microservices-should-be-healthy",
    "provider": {
        "type": "python",
        "module": "chaosk8s.probes",
        "func": "microservice_available_and_healthy",
        "secrets": ["kubernetes"],
        "arguments": {
            "name": "myapp",
            "ns": "myns"
        }
    }
}
```

You may specify the Kubernetes context you want to use as follows:

```json
{
    "secrets": {
        "kubernetes": {
            "KUBERNETES_CONTEXT": "minikube"
        }
    }
}
```

Or via the environment:

```
$ export KUBERNETES_CONTEXT=minikube
```

In the same spirit, you can specify where to find your Kubernetes configuration
with:

```
$ export KUBECONFIG=some/path/config
```

## Contribute

If you wish to contribute more functions to this package, you are more than
welcome to do so. Please fork this project, make your changes following the
usual [PEP 8][pep8] code style, add appropriate tests and submit a PR for
review.

[pep8]: https://pycodestyle.readthedocs.io/en/latest/

The Chaos Toolkit projects require all contributors must sign a
[Developer Certificate of Origin][dco] on each commit they would like to merge
into the master branch of the repository. Please, make sure you can abide by
the rules of the DCO before submitting a PR.

[dco]: https://github.com/probot/dco#how-it-works


