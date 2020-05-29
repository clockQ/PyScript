#!/usr/bin/python2.7
#coding=utf-8
#
# Need to install Kubernetes-Client `pip install kubernetes`
# Demo Site：https://ops-coffee.cn/t/kubernetes-python-api-demo

import sys, getopt, uuid
from kubernetes import client, config

def initContext():
    # Configs can be set in Configuration class directly or using helper
    # utility. If no argument provided, the config will be loaded from
    # default location.
    # eg： config.load_kube_config()
    configuration = client.Configuration()
    configuration.host = "http://127.0.0.1:8001"
    client.Configuration.set_default(configuration)

class k8sObj(object):
    def create(self):
        print("Not Implemented")
        pass
    def delete(self):
        print("Not Implemented")
        pass
    def update(self):
        print("Not Implemented")
        pass
    def getAll(self):
        print("Not Implemented")
        pass

def ns():
    class InnerClass(k8sObj):
        def create(self, name):
            v1 = client.CoreV1Api()
            body = {
                "apiVersion": "v1",
                "kind": "Namespace",
                "metadata": {
                    "name": name,
                }
            }
            ret = v1.create_namespace(body=body)
            print (ret)

        def delete(self, name):
            v1 = client.CoreV1Api()
            body = client.V1DeleteOptions()
            body.api_version = "v1"
            body.grace_period_seconds = 0
            ret = v1.delete_namespace(name, body=body)
            print(ret)

        def getAll(self):
            v1 = client.CoreV1Api()
            api_response = v1.list_namespace(limit=56,timeout_seconds=56, watch=False)
            for namespace in api_response.items:
                print(namespace.metadata.name)

    return InnerClass()

def pod():
    class InnerClass(k8sObj):
        def getAll(self, ns="default"):
            v1 = client.CoreV1Api()
            resp = v1.list_namespaced_pod(ns)
            for pod in resp.items:
                print(pod.metadata.name)

    return InnerClass()

def deploy():
    class InnerClass(k8sObj):
        def create(self, name, image, ns="default"):
            v1veta2 = client.AppsV1beta2Api()
            body = {
                "apiVersion": "apps/v1beta2",
                "kind": "Deployment",
                "metadata": {
                    "name": name,
                    "labels": {
                        "app": name,
                    },
                },
                "spec": {
                    "replicas": 1,
                    "selector": {
                        "matchLabels": {
                            "app": name,
                        },
                    },
                    "template": {
                        "metadata": {
                            "labels": {
                                "app": name,
                            },
                        },
                        "spec": {
                            "containers": [
                                {
                                    "name": name,
                                    "image": image,
                                    # "ports": [
                                    #     {
                                    #         "containerPort": 80,
                                    #     },
                                    # ]
                                },
                            ]
                        }
                    }
                }
            }
            resp = v1veta2.create_namespaced_deployment(body=body, namespace=ns)
            print(resp)

        def delete(self, name, ns="default"):
            v1veta2 = client.AppsV1beta2Api()
            resp = v1veta2.delete_namespaced_deployment(name=name,
                                                        namespace=ns,
                                                        body=client.V1DeleteOptions(
                                                            propagation_policy="Foreground",
                                                            grace_period_seconds=0,
                                                        ),
                                                        )
            print(resp)

        def getAll(self, ns="default"):
            v1beta2 = client.AppsV1beta2Api()
            resp = v1beta2.list_namespaced_deployment(ns)
            for deployment in resp.items:
                print(deployment.metadata.name)

    return InnerClass()

def job():
    class InnerClass(k8sObj):

        """
        job().create("test-job"+"-"+str(uuid.uuid4()), "busybox", ["sh", "-c", "sleep 5"])
        """
        def create(self, name, image, cmds, ns="default"):
            long_name = name+"-"+str(uuid.uuid4())
            batchv1 = client.BatchV1Api()

            job_manifest = {
                "apiVersion": "batch/v1",
                "kind": "Job",
                "metadata": {
                    "name": long_name,
                    "labels": {
                        "app": name,
                    },
                },
                "spec": {
                    "template": {
                        "metadata": {
                            "name": long_name,
                            "labels": {
                                "app": name,
                            },
                        },
                        "spec": {
                            "containers": [
                                {
                                    "name": long_name,
                                    "image": image,
                                    "command": cmds,
                                 },
                            ],
                            "restartPolicy": "Never",
                        },
                    },
                },
            }

            resp = batchv1.create_namespaced_job(body=job_manifest, namespace=ns)
            print(resp)

    return InnerClass()

def print_help():
    print("Kubernetes 简单控制脚本")
    print("用法: ./ctrl-k8s.py --name <name> --image <image> --cmds <cmds>")

# if __name__ == "__main__":
#     name = ''
#     image = ''
#     cmds = []
#
#     operate = sys.argv[1]
#     resource = sys.argv[2]
#
#     resource_inst = None
#     if resource == "ns":
#         resource_inst = ns()
#     elif resource == "job":
#         resource_inst = job()
#
#     operate_inst = None
#     if operate == 'create':
#         operate_inst = resource_inst.create
#     elif operate == 'delete':
#         operate_inst = resource_inst.delete
#
#     try:
#         opts, args = getopt.getopt(sys.argv[3:], '', [
#             'help', 'name=', 'image=', 'cmds=',
#         ])
#     except getopt.GetoptError:
#         print_help()
#         sys.exit(2)
#
#     for opt, arg in opts:
#         if opt in ('--help'):
#             print_help()
#             sys.exit()
#         if opt in ('-n','--name'):
#             name = arg
#             continue
#         if opt in ("-i", "--image"):
#             image = arg
#             continue
#         if opt in ("-c", "--cmds"):
#             cmds = eval(arg)
#             continue
#
#     initContext()
#     operate_inst(name, image, cmds)

if __name__ == "__main__":
    initContext()
    model = client.models.v1_non_resource_attributes.V1NonResourceAttributes()
    print(model)
