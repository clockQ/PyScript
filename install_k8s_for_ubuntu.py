#!/usr/bin/python2.7
#coding=utf-8

import os

ARCH='amd64'
SYSTEM_NAME='Ubuntu'
SYSTEM_VERSION='16.04'
DOCKER_VERSION='18.06.3~ce~3-0~ubuntu'
K8S_VERSION='1.14.8-00'
DOCKER_DAEMON_PATH="/etc/docker/daemon.json"
DOCKER_ALIYUN_PROXY="https://bf3dh9r6.mirror.aliyuncs.com"

def execCmd(cmds):
    for cmd in cmds:
        os.system(cmd)


def change_aliyun_rep():
    '更换原本的应用仓库为阿里云仓库'

    execCmd((
        'mv -i /etc/apt/sources.list /etc/apt/sources.list.bk',
    ))

    f = open("/etc/apt/sources.list", "w")
    f.write('''deb-src http://archive.ubuntu.com/ubuntu xenial main restricted #Added by software-properties
deb http://mirrors.aliyun.com/ubuntu/ xenial main restricted
deb-src http://mirrors.aliyun.com/ubuntu/ xenial main restricted multiverse universe #Added by software-properties
deb http://mirrors.aliyun.com/ubuntu/ xenial-updates main restricted
deb-src http://mirrors.aliyun.com/ubuntu/ xenial-updates main restricted multiverse universe #Added by software-properties
deb http://mirrors.aliyun.com/ubuntu/ xenial universe
deb http://mirrors.aliyun.com/ubuntu/ xenial-updates universe
deb http://mirrors.aliyun.com/ubuntu/ xenial multiverse
deb http://mirrors.aliyun.com/ubuntu/ xenial-updates multiverse
deb http://mirrors.aliyun.com/ubuntu/ xenial-backports main restricted universe multiverse
deb-src http://mirrors.aliyun.com/ubuntu/ xenial-backports main restricted universe multiverse #Added by software-properties
deb http://archive.canonical.com/ubuntu xenial partner
deb-src http://archive.canonical.com/ubuntu xenial partner
deb http://mirrors.aliyun.com/ubuntu/ xenial-security main restricted
deb-src http://mirrors.aliyun.com/ubuntu/ xenial-security main restricted multiverse universe #Added by software-properties
deb http://mirrors.aliyun.com/ubuntu/ xenial-security universe
deb http://mirrors.aliyun.com/ubuntu/ xenial-security multiverse
    ''')
    f.close()

    execCmd((
        'apt-get update',
    ))


def delete_old_docker():
    '删除原有docker'

    cmds = (
        'apt-get remove docker docker-engine docker.io containerd runc', # 1.1 删除安装包
        'apt-get autoremove',
        'rm -rf /etc/docker', # 1.2 删除本地残留
        'rm -rf /var/lib/docker',
    )
    execCmd(cmds)


def install_docker():
    '添加 Docker 的仓库，并安装 Docker'

    # Ubuntu 14.04 需要手动安装 util-linux 中的 nsenter
    # if not os.path.exists("util-linux-2.24/"):
    #     cmds = (
    #         'apt-get install make autopoint autoconf libtool automake',
    #         'wget https://www.kernel.org/pub/linux/utils/util-linux/v2.24/util-linux-2.24.tar.gz',
    #         'tar -xzvf util-linux-2.24.tar.gz',
    #         'cd util-linux-2.24/ && ./configure --without-python --disable-all-programs --enable-nsenter --without-ncurses && make nsenter && cp nsenter /usr/local/bin/',
    #     )
    #     execCmd(cmds)

    cmds = (
        'apt-get update', # 2.1 更新index
        'apt-get install -y apt-transport-https ca-certificates curl gnupg-agent software-properties-common', # 2.2 支持 https 型存储库
        'curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -', # 2.3 添加 Docker 官方秘钥
        'add-apt-repository \"deb [arch=%s] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable\"' % (ARCH), # 2.4 添加适合机器发行版本的 Docker 仓库
        'apt-get update', # 2.5 再次更新index

        'rm -rf libltdl7_2.4.6-0.1_amd64.deb', # Ubuntu 16 需要手动安装高版本的 libltdl7
        'wget http://launchpadlibrarian.net/236916213/libltdl7_2.4.6-0.1_amd64.deb',
        'dpkg -i libltdl7_2.4.6-0.1_amd64.deb',

        'apt-cache madison docker-ce', # 2.6 查看可用版本
        'apt-get install -y docker-ce=%s' % (DOCKER_VERSION), # 2.7 安装 $DOCKER_VERSION 的 Docker
        'usermod -aG docker $USER', # 2.8 将当前用户加入 docker groups
    )
    execCmd(cmds)


def install_k8s():
    '添加 Kubernetes 的仓库，并安装 Kubernetes'

    cmds = (
        'apt-get update', # 3.1 更新index
        'apt-get install -y apt-transport-https ca-certificates curl gnupg-agent software-properties-common', # 3.2 支持 https 型存储库
        'curl https://mirrors.aliyun.com/kubernetes/apt/doc/apt-key.gpg | sudo apt-key add -', # 3.3 添加 K8S aliyun 秘钥
        'add-apt-repository "deb https://mirrors.aliyun.com/kubernetes/apt/ kubernetes-$(lsb_release -cs) main"', # 3.4 添加 aliyun 的 K8S 仓库
        'apt-get update', # 3.5 再次更新index
        'apt-cache madison kubectl', # 3.6 查看可用版本
        'apt-cache madison kubelet', # 3.6 查看可用版本
        'apt-cache madison kubeadm', # 3.6 查看可用版本
        'apt-get install -y kubectl=%s' % (K8S_VERSION), # 3.7 安装 $K8S_VERSION 的 K8S
        'apt-get install -y kubelet=%s' % (K8S_VERSION), # 3.7 安装 $K8S_VERSION 的 K8S
        'apt-get install -y kubeadm=%s' % (K8S_VERSION), # 3.7 安装 $K8S_VERSION 的 K8S
        'apt-mark hold kubectl kubelet kubeadm', # 3.8 禁用更新
    )
    execCmd(cmds)


def k8s_cluster_start():
    '启动 K8S 集群'

    def write_docker_daemon():
        if os.path.exists(DOCKER_DAEMON_PATH) and os.stat(DOCKER_DAEMON_PATH).st_size > 0:
            pass
        else:
            if not os.path.exists(DOCKER_DAEMON_PATH[:DOCKER_DAEMON_PATH.rfind("/")]):
                os.makedirs(DOCKER_DAEMON_PATH[:DOCKER_DAEMON_PATH.rfind("/")])
            f = open(DOCKER_DAEMON_PATH, "w")
            f.write('''{
  "exec-opts": ["native.cgroupdriver=systemd"],
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "100m"
  },
  "storage-driver": "overlay2",
  "registry-mirrors" : [
    "%s"
  ]
}''' % (DOCKER_ALIYUN_PROXY))
            f.close()


    write_docker_daemon()
    cmds = (
        # Docker 相关设置
        "swapoff -a",
        "systemctl daemon-reload && systemctl restart docker",
    )

    if not os.path.exists("k8s-for-docker-desktop/"):
        cmds = cmds + (
            "git clone https://github.com/AliyunContainerService/k8s-for-docker-desktop.git",
        )


    cmds = cmds + (
        # 使用 https://github.com/AliyunContainerService/k8s-for-docker-desktop/tree/v1.14.8 预先下载 K8S 需要的镜像
        "cd k8s-for-docker-desktop/ && git checkout -b v1.14.8 remotes/origin/v1.14.8 && ./load_images.sh",

        # 启动 Master 节点
        "echo ''",
        "echo ''",
        "echo ''",
        'echo "请手动启动 Master 节点"',
        'echo "下列步骤中，出现错误可以查看日志 \`journalctl -f -u kubelet.service\`"',
        'echo "\t 1. 初始化 Master \`sudo kubeadm init --kubernetes-version=v1.14.8 --pod-network-cidr=10.244.0.0/16 --apiserver-advertise-address=192.168.100.14\`"',
        'echo "\t 2. 如果需要，安装flannel网络 \`kubectl apply -f https://github.com/PharbersDeveloper/BP-Server-Deploy/blob/master/core-compose/kube-flannel.yml\`"',
    )
    execCmd(cmds)


def write_flannel():
    flannel_conf_path = "/etc/cni/net.d/10-flannel.conf"
    if os.path.exists(flannel_conf_path) and os.stat(flannel_conf_path).st_size > 0:
        pass
    else:
        if not os.path.exists(flannel_conf_path[:flannel_conf_path.rfind("/")]):
            os.makedirs(flannel_conf_path[:flannel_conf_path.rfind("/")])
        f1 = open(flannel_conf_path, "w")
        f1.write('''{"name":"cbr0","type":"flannel","delegate": {"isDefaultGateway": true}}''')
        f1.close()

    if not os.path.exists("/usr/share/oci-umount/oci-umount.d/"):
        os.makedirs("/usr/share/oci-umount/oci-umount.d/")
    if not os.path.exists("/run/flannel/"):
        os.makedirs("/run/flannel/")

    flannel_subnet_path = "/run/flannel/subnet.env"
    if os.path.exists(flannel_subnet_path) and os.stat(flannel_subnet_path).st_size > 0:
        pass
    else:
        if not os.path.exists(flannel_subnet_path[:flannel_subnet_path.rfind("/")]):
            os.makedirs(flannel_subnet_path[:flannel_subnet_path.rfind("/")])
        f2 = open(flannel_subnet_path, "w")
        f2.write('''FLANNEL_NETWORK=10.244.0.0/16
FLANNEL_SUBNET=10.244.0.1/24
FLANNEL_MTU=1450
FLANNEL_IPMASQ=true''')
        f2.close()


def k8s_cluster_reset():
    cmds = (
        "kubeadm reset",
        "systemctl restart kubelet",
        "systemctl restart docker",
        "rm -rf /var/lib/cni/",
        "rm -rf /var/lib/kubelet/*",
        "rm -rf /etc/cni/",
        "ifconfig cni0 down",
        "ifconfig flannel.1 down",
        "ifconfig docker0 down",
    )
    execCmd(cmds)


helpers = (
    {"desc": "更换原本的应用仓库为阿里云仓库", "func": change_aliyun_rep},
    {"desc": "删除原有 Docker", "func": delete_old_docker},
    {"desc": "安装 "+DOCKER_VERSION+" 版本的 Docker", "func": install_docker},
    {"desc": "安装 "+K8S_VERSION+" 版本的 Kubernetes", "func": install_k8s},
    {"desc": "（废弃）设置 flannel 环境", "func": install_k8s},
    {"desc": "K8S 集群的启动", "func": k8s_cluster_start},
    {"desc": "K8S 集群的完全 reset", "func": k8s_cluster_reset},
)


print("目前该脚本只适用于 %s-%s" % (SYSTEM_NAME, SYSTEM_VERSION))
print("CentOs 请参考 https://docs.docker.com/install/linux/docker-ce/centos/")
raw_input("按任意键继续...")
print("")

switch = 0
while(switch >= 0):
    for index, helper in enumerate(helpers):
        print("\t %d. %s" % (index, helper["desc"]))

    print("")
    print("输入非选项中的值即可退出脚本。")
    switch = int(raw_input("请选择要执行的操作: "))
    print("")

    if switch < 0 or switch >= len(helpers):
        print("没有此选项，脚本停止")
        break
    else:
        sure = raw_input("请输入'yes'确认: ")
        print("")
        if sure == "yes":
            helpers[switch]["func"]()
            print("")
            print("")
            print("")
            print("执行完成，可继续选择下列选项: ")
        else:
            print("未确认，请重新选择")
            print("")
