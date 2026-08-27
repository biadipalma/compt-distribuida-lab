FROM ubuntu:22.04
RUN apt update && \
    apt install -y openmpi-bin libopenmpi-dev openssh-server sudo figlet net-tools iputils-ping && \
    useradd -m -s /bin/bash mpiuser && \
    echo "mpiuser:mpi123" | chpasswd && \
    adduser mpiuser sudo && \
    mkdir /var/run/sshd
EXPOSE 22
CMD service ssh start && sleep infinity
