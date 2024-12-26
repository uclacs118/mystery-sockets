trap 'quit=1' SIGTERM

quit=0
while [ "$quit" -ne 1 ]; do
    sleep 1
done

rc-service sshd stop

# Delete all old containers
docker rm -f `docker ps -q --filter "ancestor=player"`