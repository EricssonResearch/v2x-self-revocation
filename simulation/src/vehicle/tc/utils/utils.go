package utils

import (
    "strings"

	log "github.com/sirupsen/logrus"
)

func ParseLogLevel(level string) {
	switch l := strings.ToLower(level); l {
	case "debug":
		log.SetLevel(log.DebugLevel)
	case "info":
		log.SetLevel(log.InfoLevel)
	case "warning":
		log.SetLevel(log.WarnLevel)
	case "error":
		log.SetLevel(log.ErrorLevel)
	case "critical":
		log.SetLevel(log.FatalLevel)
	default:
		log.Fatal("Error while parsing log level %v", level)
	}
}