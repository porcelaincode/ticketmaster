# ticketmaster

## Features

- Loads configuration from `config.json`
- Spins up Selenium WebDriver instances based on configuration
- Follows customizable steps for ticket booking
- Handles multiple instances and synchronizes the payment process
- Emits events via RabbitMQ when the payment page is reached
- Graceful shutdown and cleanup on exit
- Dockerized for easy setup and deployment

## Table of Contents

1. [Requirements](#requirements)
2. [Configuration](#configuration)
3. [Running Locally](#running-locally)
4. [Docker Setup](#docker-setup)
5. [Usage](#usage)
6. [License](#license)

## Requirements

- Python 3.9+
- Google Chrome
- ChromeDriver
- RabbitMQ (for event handling)
- Docker (for containerized setup)

## Configuration

The application uses a `config.json` file for defining the steps and preferences. Below is a sample `config.json`:

```json
{
  "base_url": "https://example.com",
  "number_of_instances": 10,
  "steps": [
    { "action": "click", "locator": { "type": "text", "value": "Book" } },
    {
      "action": "input",
      "locator": { "type": "css", "value": ".ticket-class" },
      "value": "2"
    },
    { "action": "click", "locator": { "type": "text", "value": "Proceed" } },
    { "action": "wait", "time": 5 },
    { "action": "click", "locator": { "type": "text", "value": "Payment" } }
  ],
  "payment_preferred_type": "upi"
}
```

### Configurable Fields

- `base_url`: The URL where the ticket booking process begins.
- `number_of_instances`: Number of Selenium WebDriver instances to spin up.
- `steps`: An array of steps that each driver will follow. The steps support actions like `click`, `input`, and `wait`.
- `payment_preferred_type`: Preferred payment method (e.g., "upi").

## Running Locally

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/ticket-booking-automation.git
cd ticket-booking-automation
```

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 3. Install ChromeDriver

Ensure that `chromedriver` is installed and available in your system path. You can download it from [here](https://sites.google.com/chromium.org/driver/).

### 4. Start RabbitMQ (Locally or via Docker)

To run RabbitMQ locally, you can use Docker:

```bash
docker run -d --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:3-management
```

### 5. Run the Application

```bash
python main.py
```

## Docker Setup

### 1. Build Docker Image

```bash
docker build -t selenium-ticket-automation .
```

### 2. Run with Docker Compose

To easily manage RabbitMQ and the application, use `docker-compose`:

```bash
docker-compose up --build
```

This will build the Docker image, set up the necessary services (like RabbitMQ), and run the app.

## Usage

1. **Base URL:** The browser instances will start by navigating to the `base_url` defined in the `config.json`.
2. **Following Steps:** Each instance will follow the sequence of actions defined in the `steps` array.
3. **Payment Handling:** Once the first instance reaches the payment page, it will emit an event, and all other instances will be terminated.
4. **Sleeping:** After payment initiation, the application sleeps for 60 minutes before gracefully terminating.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
