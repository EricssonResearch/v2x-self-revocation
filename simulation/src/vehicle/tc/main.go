package main

import (
	"net/http"
	"fmt"
	"os"
	"io"
    "os/signal"
    "syscall"
	"context"

	"tc/utils"
	"tc/handlers"

	"github.com/caarlos0/env/v6"
	log "github.com/sirupsen/logrus"
)

var cfg handlers.Config

func init() {
	// parse env
	if err := env.Parse(&cfg); err != nil {
		log.Fatal("Could not parse env variables.")
	}
	
	// parse log level
	utils.ParseLogLevel(cfg.LogLevel)

	if cfg.LogToFile {
		// set log output
		err := os.Mkdir("/logs", 0750)
		if err != nil && !os.IsExist(err) {
			log.Fatal(err)
		}

		f, err := os.OpenFile(
			fmt.Sprintf("/logs/%v-tc.log", cfg.Host),
			os.O_WRONLY | os.O_CREATE | os.O_APPEND,
			0644,
		)

		if err != nil {
			log.Fatal(err)
		}

		mw := io.MultiWriter(os.Stdout, f)
		log.SetOutput(mw)
	}
}

func main() {
	log.Debug("TC running")
	log.Info(fmt.Sprintf("%+v", cfg))

	// Create HTTP server.
	http.HandleFunc("/pubkey", cfg.PublicKey)
	http.HandleFunc("/join", cfg.Join)
	http.HandleFunc("/create", cfg.Create)
	http.HandleFunc("/heartbeat", cfg.ProcessHeartbeat)
	http.HandleFunc("/sign", cfg.SignMessage)
	http.HandleFunc("/verify", cfg.VerifyMessage)

	server := http.Server{Addr: "0.0.0.0:9090"}

	idleConnsClosed := make(chan struct{})
    go func() {
        sigint := make(chan os.Signal, 1)

        // interrupt signal sent from terminal
        signal.Notify(sigint, os.Interrupt)
        // sigterm signal sent from kubernetes
        signal.Notify(sigint, syscall.SIGTERM)

        <-sigint

        // We received an interrupt signal, shut down.
        if err := server.Shutdown(context.Background()); err != nil {
            // Error from closing listeners, or context timeout:
            log.Warning("HTTP server Shutdown: %v", err)
        }
        close(idleConnsClosed)
		log.Info("Shutting down")
    }()

    if err := server.ListenAndServe(); err != http.ErrServerClosed {
        // Error starting or closing listener:
        log.Warning("HTTP server ListenAndServe: %v", err)
    }

    <-idleConnsClosed
}