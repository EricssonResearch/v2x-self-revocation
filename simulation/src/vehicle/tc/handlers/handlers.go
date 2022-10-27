package handlers

import (
	"net/http"
	"encoding/json"
	"crypto/rsa"
	"crypto/rand"
	"crypto/x509"
	"encoding/pem"
	"encoding/hex"
	"io"
	"time"
	"errors"
	"fmt"

	//"tc/utils"

	log "github.com/sirupsen/logrus"
	"github.com/thanhpk/randstr"
	"github.com/lestrrat-go/jwx/v2/jwa"
	"github.com/lestrrat-go/jwx/v2/jwe"
	"github.com/lestrrat-go/jwx/v2/jwk"
	"github.com/lestrrat-go/jwx/v2/jwt"
)

type Config struct {
	Host			string		  `env:"HOSTNAME"`
	LogLevel		string        `env:"LOG_LEVEL"`
	LogToFile		bool		  `env:"LOG_TO_FILE"`
	UseEpochs	 	bool          `env:"USE_EPOCHS"`
	NumPseudonyms 	int			  `env:"NUM_PSEUDONYMS"`
	PsSize			int			  `env:"PSEUDONYM_SIZE"`
	MinPsLifetime   int64		  `env:"MIN_PSEUDONYM_LIFETIME"`
	HardRevocation  bool		  `env:"HARD_REVOCATION"`
	StorePrl		bool		  `env:"TC_STORE_LAST_PRL"`
	T_R      	 	int64         `env:"T_R"`
	T_V      	 	int64         `env:"T_V"`
	T_E      	 	int64         `env:"T_E"`
	E_TOL      	 	int64         `env:"E_TOL"`
}

type TCState struct {
	Ltp			string // long-term pseudonym
	KeyRA		*jwk.Key // RA's public key
	GroupKey 	[]byte // group key for V2V messages
	PsMap		map[string]int64 // pseudonyms currently in use, with their creation time/epoch
	PsOld		map[string]bool // pseudonyms expired or revoked
	Epoch		int64 // epoch (used if UseEpochs is true)
	TOut		int64 // auto-revocation timeout (used if UseEpochs is false)
	LastPrl		map[string]bool // PRL from last heartbeat received
}

type JoinData struct {
	Ltp			string // long-term pseudonym
	KeyRA		string // RA's public key
	GroupKey 	string // group key for V2V messages
	Epoch		int64 // initial epoch (used if UseEpochs is true)
}

var state *TCState
var privkey *rsa.PrivateKey

func init() {
	key, err := rsa.GenerateKey(rand.Reader, 2048)
	if err != nil {
		panic(fmt.Sprintf("failed to generate private key: %s\n", err))
	}
	
	privkey = key
}

func (c Config) PublicKey(w http.ResponseWriter, r *http.Request) {
	pubkey := &privkey.PublicKey

	pubkey_bytes, err := x509.MarshalPKIXPublicKey(pubkey)
    if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
    }

    pubkey_pem := pem.EncodeToMemory(
            &pem.Block{
                    Type:  "RSA PUBLIC KEY",
                    Bytes: pubkey_bytes,
            },
    )

	w.Write(pubkey_pem)
}

func (c Config) Join(w http.ResponseWriter, r *http.Request) {
	// calculate timestamp immediately to mitigate TOCTOU attacks
	now := c.getTime()

	if !c.hasTimeoutExpired() {
		http.Error(w, "TC already enrolled in the network", http.StatusBadRequest)
        return
	}

	var j JoinData

	defer r.Body.Close()
    buf, err := io.ReadAll(r.Body)
    if err != nil {
        http.Error(w, err.Error(), http.StatusBadRequest)
        return
    }

	decrypted, err := jwe.Decrypt(buf, jwe.WithKey(jwa.RSA_OAEP_256, privkey))
    if err != nil {
	  http.Error(w, err.Error(), http.StatusBadRequest)
      return
    }

	if err := json.Unmarshal(decrypted, &j); err != nil {
        http.Error(w, err.Error(), http.StatusBadRequest)
		return
    }

	key, err := jwk.ParseKey([]byte(j.KeyRA), jwk.WithPEM(true))

	if err != nil {
        http.Error(w, err.Error(), http.StatusBadRequest)
        return
    }

	groupKey, err := hex.DecodeString(j.GroupKey)

	if err != nil {
        http.Error(w, err.Error(), http.StatusBadRequest)
        return
	}

	state = &TCState {
		j.Ltp,
		&key,
		groupKey,
		map[string]int64{},
		map[string]bool{},
		j.Epoch, now + c.T_R,
		map[string]bool{},
	}

	log.Info(fmt.Sprintf("JOIN %v", state.Ltp))
	w.Write([]byte(state.Ltp))
}

func (c Config) Create(w http.ResponseWriter, r *http.Request) {
	// calculate timestamp immediately to mitigate TOCTOU attacks
	now := c.getTime()

	if c.hasTimeoutExpired() {
		http.Error(w, "TC not enrolled in the network", http.StatusForbidden)
        return
	}

	if !c.isCreatePossible() {
		http.Error(w, "It is too early to refresh pseudonyms", http.StatusUnauthorized)
        return
	}

	ps := randstr.String(c.PsSize)
	state.PsMap[ps] = now

	// return pseudonym identifier
	log.Info(fmt.Sprintf("CREATE %v", ps))
	w.Write([]byte(ps))
}

func (c Config) ProcessHeartbeat(w http.ResponseWriter, r *http.Request) {
	// calculate timestamp immediately to mitigate TOCTOU attacks
	now := c.getTime()

	if c.hasTimeoutExpired() {
		http.Error(w, "TC not enrolled in the network", http.StatusForbidden)
        return
	}

	defer r.Body.Close()
    buf, err := io.ReadAll(r.Body)
    if err != nil {
		log.Error("Failed to read heartbeat data: %v", err)
        http.Error(w, err.Error(), http.StatusBadRequest)
        return
    }

	//log.Debug("Received: %v", string(buf))

	token, err := jwt.Parse(buf, jwt.WithKey(jwa.ES256, *state.KeyRA))

	if err != nil {
		log.Error("Failed to verify heartbeat: %v", err)
        http.Error(w, err.Error(), http.StatusBadRequest)
        return
	}

	// check issuer
	if token.Issuer() != "RA" {
        http.Error(w, "Bad Issuer", http.StatusBadRequest)
        return
	}

	iat := token.IssuedAt().Unix()

	// check freshness
	if ok, err := c.isHeartbeatFresh(iat); err != nil {
		if !ok {
			autoRevoke()
			http.Error(w, err.Error(), http.StatusForbidden)
		} else {
			http.Error(w, err.Error(), http.StatusBadRequest)
		}

        return
	}

	// update timeout and epoch
	state.TOut = now + c.T_R
	state.Epoch = iat

	log.Info(fmt.Sprintf("HEARTBEAT"))

	// check PRL
	prlRaw, ok := token.Get("prl")
	if !ok {
        http.Error(w, "No PRL in heartbeat", http.StatusBadRequest)
        return
	}

	prl, err := parsePrl(prlRaw)

	if err != nil {
        http.Error(w, err.Error(), http.StatusBadRequest)
        return
	}

	if c.StorePrl {
		state.LastPrl = map[string]bool{}
	}

	for _, ps := range prl {
		parsedPs, err := parsePseudonym(ps)

		if err != nil {
			log.Debug(err.Error)
			continue
		}

		if c.StorePrl {
			state.LastPrl[parsedPs] = true
		}

		// check if is long-term identifier first
		if parsedPs == state.Ltp {
			log.Info(fmt.Sprintf("HARD_REVOKE %v", state.Ltp))
			state = nil
			return
		}
		
		// check among active pseudonyms
		if _, found := state.PsMap[parsedPs]; found {
			if c.HardRevocation {
				log.Info(fmt.Sprintf("HARD_REVOKE %v", parsedPs))
				state = nil
				return
			} else {
				log.Info(fmt.Sprintf("SOFT_REVOKE %v", parsedPs))
				delete(state.PsMap, parsedPs)
				state.PsOld[parsedPs] = true
			}
		}

		// check among old pseudonyms if hard revocation is enabled
		if c.HardRevocation {
			if _, found := state.PsOld[parsedPs]; found {
				log.Info(fmt.Sprintf("HARD_REVOKE %v", parsedPs))
				state = nil
				return
			}
		}
	}
}

func (c Config) SignMessage(w http.ResponseWriter, r *http.Request) {
	// calculate timestamp immediately to mitigate TOCTOU attacks
	now := c.getTime()

	if c.hasTimeoutExpired() {
		http.Error(w, "TC not enrolled in the network", http.StatusForbidden)
        return
	}

	var token = jwt.New()

	if err := json.NewDecoder(r.Body).Decode(&token); err != nil {
        http.Error(w, err.Error(), http.StatusBadRequest)
        return
    }

	// check if pseudonym is valid
	if _, found := state.PsMap[token.Issuer()]; !found {
        http.Error(w, "Pseudonym not valid", http.StatusUnauthorized)
        return
	}
	
	// add timestamp
	token.Set("iat", now)

	ss, err := jwt.Sign(token, jwt.WithKey(jwa.HS256, state.GroupKey))

	if err != nil {
        http.Error(w, err.Error(), http.StatusInternalServerError)
        return
	}

	log.Info(fmt.Sprintf("SIGN %v", token.Issuer()))
	w.Write([]byte(ss))
}

func (c Config) VerifyMessage(w http.ResponseWriter, r *http.Request) {
	if c.hasTimeoutExpired() {
		http.Error(w, "TC not enrolled in the network", http.StatusForbidden)
        return
	}
	
	defer r.Body.Close()
    buf, err := io.ReadAll(r.Body)
    if err != nil {
        http.Error(w, err.Error(), http.StatusBadRequest)
        return
    }

	//log.Debug("Received: %v", string(buf))

	token, err := jwt.Parse(buf, jwt.WithKey(jwa.HS256, state.GroupKey))

	if err != nil {
        http.Error(w, err.Error(), http.StatusBadRequest)
        return
	}

	senderPs := token.Issuer()
	iat := token.IssuedAt().Unix()

	// check freshness
	if ok, err := c.isV2VMessageFresh(iat); err != nil {
		if !ok {
			autoRevoke()
			http.Error(w, err.Error(), http.StatusForbidden)
		} else {
			http.Error(w, err.Error(), http.StatusBadRequest)
		}

		return
	}

	// check if pseudonym is revoked
	if c.StorePrl {
		if _, found := state.LastPrl[senderPs]; found {
			http.Error(
				w, 
				fmt.Sprintf("Pseudonym %v is revoked", senderPs), 
				http.StatusBadRequest,
			)

			return
		}
	}

	log.Info(fmt.Sprintf("VERIFY %v", senderPs))
}

func (c Config) getTime() int64 {
	if c.UseEpochs && state != nil {
		return state.Epoch
	}

	return time.Now().Unix()
}

func (c Config) isHeartbeatFresh(iat int64) (bool, error) {
	if c.UseEpochs {
		// epoch "too old" -> discard
		if iat < state.Epoch {
			return true, errors.New("Invalid epoch")
		}
		// epoch "too new" -> discard & auto-revoke
		if iat > state.Epoch + c.E_TOL + 1 {
			return false, errors.New("Auto-revocation triggered")
		}

		// all good
		return true, nil
	} else {
		now := c.getTime()

		// timestamp "too old" or "too new" -> discard
		if iat < now - c.T_V || iat > now {
			return true, errors.New("Invalid timestamp")
		}

		// all good
		return true, nil
	}
}

func (c Config) isV2VMessageFresh(iat int64) (bool, error) {
	if c.UseEpochs {
		// epoch "too old" -> discard
		if iat < state.Epoch - c.E_TOL {
			return true, errors.New("Invalid epoch")
		}
		// epoch "too new" -> discard. Bonus: auto-revoke
		if iat > state.Epoch + c.E_TOL + 1 {
			return false, errors.New("Auto-revocation triggered")
		}
		if iat > state.Epoch + c.E_TOL {
			return true, errors.New("Invalid epoch")
		}


		// all good
		return true, nil
	} else {
		now := c.getTime()

		// timestamp "too old" or "too new" -> discard
		if iat < now - c.T_V || iat > now {
			return true, errors.New("Invalid timestamp")
		}

		// all good
		return true, nil
	}
}

func (c Config) hasTimeoutExpired() bool {
	if state == nil {
		// already revoked or never joined
		return true
	}

	if !c.UseEpochs && c.getTime() >= state.TOut {
		// timeout expired
		autoRevoke()
		return true
	}

	return false
}

func (c Config) isCreatePossible() bool {
	if len(state.PsMap) < c.NumPseudonyms {
		log.Debug(fmt.Sprintf("Map has space: %v/%v", len(state.PsMap), c.NumPseudonyms))
		return true
	}

	now := c.getTime()
	// find a pseudonym we can delete
	for ps, crTime := range state.PsMap {
		if now >= crTime + c.MinPsLifetime {
			log.Debug(fmt.Sprintf("Deleting %v: %v/%v", ps, now, crTime))
			delete(state.PsMap, ps)
			state.PsOld[ps] = true
			return true
		}
	}

	return false
}

func autoRevoke() {
	log.Info("AUTO_REVOKE")
	state = nil
}

func parsePrl(val interface{}) ([]interface{}, error) {
	switch t := val.(type) {
	default:
		return nil, errors.New(fmt.Sprintf("unexpected type for PRL: %T", t))
	case []interface{}:
		return t[:], nil
	}
}

func parsePseudonym(val interface{}) (string, error) {
	switch t := val.(type) {
	default:
		return "", errors.New(fmt.Sprintf("unexpected type for pseudonym: %T", t))
	case string:
		return t, nil
	}
}