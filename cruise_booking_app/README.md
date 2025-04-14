## Running RabbitMQ

To start the RabbitMQ service and the cruise booking application, use the following command:

```bash
docker-compose up --build
```

Or, to run the services in detached mode, use:

```bash
docker-compose up --build -d
```


## Accessing UIs via Browser

- **Cruise Booking Application UI**: Accessible at [http://localhost:5000](http://localhost:5000). This is the main interface for managing cruise bookings.
- **RabbitMQ Management UI**: Accessible at [http://localhost:15672](http://localhost:15672). Use this interface to monitor and manage RabbitMQ queues and exchanges.

Ensure that Docker and Docker Compose are installed on your system before running the application.
