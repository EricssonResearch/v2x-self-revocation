## Build
FROM golang:1.23.1-bookworm AS build

WORKDIR /app

COPY go.mod ./
COPY . .

RUN go get tc && go build -o /tc

## Deploy
FROM gcr.io/distroless/base-debian12

WORKDIR /

COPY --from=build /tc /tc

CMD ["/tc"]