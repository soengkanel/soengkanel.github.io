---
layout: post
title: "Building a Simple Grab Clone Microservice in Golang"
date: 2025-12-02
categories: [Microservice]
tags: [Golang, Microservice, Backend]
---

Microservices are a popular architectural style where an application is structured as a collection of loosely coupled services. Today, we'll build a practical, simplified version of a **Grab** (or Uber) backend service using **Golang**.

We will focus on the **Booking Service**, which is the core component responsible for handling ride requests.

## The Goal

We want to create a service that:
1.  Accepts a ride request from a user.
2.  "Finds" a driver (we'll simulate this).
3.  Returns a booking confirmation.

## Architecture

Here is a simple view of where our service fits:

<div class="mermaid">
graph LR
    Client[Mobile App] -->|POST /book| BookingService[Booking Service]
    BookingService -->|Find Driver| DriverService[Driver Service / Database]
    DriverService -->|Driver Found| BookingService
    BookingService -->|Confirmation| Client
</div>

For this tutorial, we will mock the "Driver Service" logic inside our Booking Service to keep things simple.

## Prerequisites

-   Basic knowledge of [Go (Golang)](https://go.dev/).
-   Go installed on your machine.

## Implementation

We will use the standard `net/http` package in Go, which is powerful enough for this microservice.

### 1. Project Setup

Create a new directory for your project:

```bash
mkdir grab-clone-booking
cd grab-clone-booking
go mod init grab-clone-booking
```

### 2. The Code (`main.go`)

Create a file named `main.go` and add the following code. I have added comments to explain every part.

```go
package main

import (
	"encoding/json"
	"fmt"
	"log"
	"math/rand"
	"net/http"
	"time"
)

// BookingRequest represents the JSON body sent by the client
type BookingRequest struct {
	UserID    string `json:"user_id"`
	Pickup    string `json:"pickup"`
	Dropoff   string `json:"dropoff"`
	RideType  string `json:"ride_type"` // e.g., "JustGrab", "GrabCar"
}

// BookingResponse represents the JSON response sent back to the client
type BookingResponse struct {
	BookingID string `json:"booking_id"`
	DriverID  string `json:"driver_id"`
	Status    string `json:"status"`
	ETA       string `json:"eta"` // Estimated Time of Arrival
	Message   string `json:"message"`
}

func main() {
	// Define our handler for the /book endpoint
	http.HandleFunc("/book", bookRideHandler)

	// Start the server on port 8080
	fmt.Println("🚖 Booking Service started on :8080")
	if err := http.ListenAndServe(":8080", nil); err != nil {
		log.Fatal(err)
	}
}

// bookRideHandler handles the incoming booking requests
func bookRideHandler(w http.ResponseWriter, r *http.Request) {
	// 1. Only allow POST methods
	if r.Method != http.MethodPost {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	// 2. Decode the JSON request body
	var req BookingRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		http.Error(w, "Invalid request body", http.StatusBadRequest)
		return
	}

	// 3. Simulate "Business Logic" (Finding a driver)
	// In a real app, this would call a Driver Service or query a geospatial database.
	fmt.Printf("Received booking request from User: %s for %s -> %s\n", req.UserID, req.Pickup, req.Dropoff)
	
	// Simulate processing delay
	time.Sleep(500 * time.Millisecond)

	driverID := findDriver()

	// 4. Create the response
	resp := BookingResponse{
		BookingID: fmt.Sprintf("BK-%d", time.Now().Unix()),
		DriverID:  driverID,
		Status:    "CONFIRMED",
		ETA:       "5 mins",
		Message:   "Your driver is on the way!",
	}

	// 5. Send JSON response
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(resp)
}

// findDriver simulates finding a nearby driver
func findDriver() string {
	drivers := []string{"Driver-A", "Driver-B", "Driver-C", "Driver-D"}
	randomIndex := rand.Intn(len(drivers))
	return drivers[randomIndex]
}
```

### Explanation

1.  **Structs**: We define `BookingRequest` and `BookingResponse` to map our JSON data. Go's `encoding/json` package makes this easy.
2.  **Handler**: `bookRideHandler` is the core function. It checks the method, decodes the input, runs logic, and encodes the output.
3.  **Simulation**: Instead of a complex algorithm, `findDriver` randomly picks a driver from a list. This is perfect for a prototype.

## Running the Service

Open your terminal in the project folder and run:

```bash
go run main.go
```

You should see:
```
🚖 Booking Service started on :8080
```

## Testing

You can test this using `curl` or Postman. Here is a `curl` command:

```bash
curl -X POST http://localhost:8080/book \
     -H "Content-Type: application/json" \
     -d '{
           "user_id": "user_123",
           "pickup": "Central Market",
           "dropoff": "Royal Palace",
           "ride_type": "JustGrab"
         }'
```

**Expected Output:**

```json
{
  "booking_id": "BK-1701485000",
  "driver_id": "Driver-B",
  "status": "CONFIRMED",
  "eta": "5 mins",
  "message": "Your driver is on the way!"
}
```

## Conclusion

You have just built a functional microservice! While simple, it demonstrates the core pattern: **Receive Request -> Process Logic -> Return Response**.

In a real-world scenario, you would add:
-   **Database**: To store booking history (PostgreSQL/MongoDB).
-   **gRPC**: For communication between internal services.
-   **Kafka/RabbitMQ**: For asynchronous tasks (like sending push notifications).

This is the foundation. From here, you can expand to build the next Super App! 🚀
