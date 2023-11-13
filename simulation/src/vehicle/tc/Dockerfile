## Build
FROM golang:1.19-buster AS build

WORKDIR /app

COPY . .

RUN go get tc && go build -o /tc

## Deploy
FROM gcr.io/distroless/base-debian10

WORKDIR /

COPY --from=build /tc /tc

CMD ["/tc"]