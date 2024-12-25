FROM gcc:14-bookworm AS build

WORKDIR /app

COPY socket.c rl.c rl.h Makefile /app/
RUN make

FROM debian:bookworm-slim
RUN apt-get update && apt-get install -y libreadline-dev

WORKDIR /app

COPY --from=build /app/player /app/player
RUN chmod +x /app/player

CMD ["sh", "-c", "/app/player"]
