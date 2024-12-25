FROM alpine:3.19

ENV USER=networking
ENV PASSWORD=isfun

WORKDIR /$USER

RUN mkdir -p /$USER \
    && echo -e "$PASSWORD\n$PASSWORD\n" | adduser --gecos "" --home "/$USER" --no-create-home $USER \
    && mkdir -p /$USER/.ssh \
    && chmod 0700 /$USER/.ssh \
    && apk add openrc openssh \
    && ssh-keygen -A \
    && mkdir -p /run/openrc \
    && touch /run/openrc/softlevel \
    && echo -e "" > /etc/motd \
    && apk add --update bind-tools \
    && apk add --update nodejs npm docker-cli docker-cli-buildx \
    && echo -e "trap 'exit' 0 SIGINT EXIT SIGSTOP \n/$USER/run.sh \nexit" >> /etc/profile 

COPY playerinstancer/run.sh playerinstancer/init.sh wait-stop-ssh.sh ./
RUN chmod +x run.sh init.sh wait-stop-ssh.sh

RUN chmod +s /usr/bin/docker

# RUN addgroup --system docker
# RUN adduser $USER docker

COPY playerinstancer/player/ /player/

CMD ["sh", "-c", "rc-status; ./init.sh; rc-service sshd start; ./wait-stop-ssh.sh"]