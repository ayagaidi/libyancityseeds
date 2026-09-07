package main

import (
    "encoding/json"
    "fmt"
    "log"
    "net/http"
)

type Location struct {
    ID     int    `json:"id"`
    Slug   string `json:"slug"`
    NameAR string `json:"name_ar"`
    NameEN string `json:"name_en"`
    Type   string `json:"type"`
}

func main() {
    const url = "https://raw.githubusercontent.com/ayagaidi/libyancityseeds/v1.1.0/data/municipalities.json"

    response, err := http.Get(url)
    if err != nil {
        log.Fatal(err)
    }
    defer response.Body.Close()

    var municipalities []Location
    if err := json.NewDecoder(response.Body).Decode(&municipalities); err != nil {
        log.Fatal(err)
    }

    fmt.Printf("%+v\n", municipalities[0])
}
