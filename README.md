# Real-Time Chat Application with Horizontal Scalability

This is a real-time chat application built using **FastAPI**, **Redis**, **MongoDB**, **Pub/Sub** for scalability, and integrated monitoring with **Prometheus** and **Grafana**. The application is designed to be horizontally scalable, allowing it to handle increasing traffic and large numbers of users efficiently.

## Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Requirements](#requirements)
- [Setup](#setup)
  - [Clone the Repository](#1-clone-the-repository)
  - [Install Dependencies](#2-install-dependencies)
  - [Create `.env` File](#3-create-env-file)
  - [Docker Compose Setup](#4-docker-compose-setup)
  - [Access the Application](#5-access-the-application)
- [Architecture Overview](#architecture-overview)
  - [Horizontal Scalability](#horizontal-scalability)
  - [Pub/Sub Messaging with Redis](#pubsub-messaging-with-redis)
  - [Data Persistence with MongoDB](#data-persistence-with-mongodb)
  - [Monitoring with Prometheus and Grafana](#monitoring-with-prometheus-and-grafana)
  - [Online Status with Redis Hash](#online-status-with-redis-hash)
- [Scaling the Application](#scaling-the-application)
  - [Scale FastAPI](#scale-fastapi)
  - [Scale Redis and MongoDB](#scale-redis-and-mongodb)
- [License](#license)

## Features

- **Real-time messaging**: Chat messages are delivered instantly to users.
- **Horizontal scalability**: The application can scale by running multiple instances to handle increased load.
The application is designed to scale horizontally by running multiple instances of the FastAPI backend. Load balancing can be achieved using tools like Nginx 

- **Pub/Sub messaging**: Redis is used to implement the Pub/Sub messaging pattern for real-time communication.
- **Persistent data**: MongoDB stores chat data persistently.
- **Monitoring**: Integrated **Prometheus** for metrics collection and **Grafana** for visualization and monitoring.
- **Scalable online status**: Redis String is used to manage user online status across multiple instances, ensuring that the status is accurately reflected in a horizontally scalable setup.

## Tech Stack

- **FastAPI**: A modern Python web framework for building APIs.
- **Redis**: In-memory data store used for Pub/Sub messaging and managing online status.
- **MongoDB**: NoSQL database used for storing chat history and user data.
- **Prometheus**: Monitoring and alerting toolkit for collecting metrics.
- **Grafana**: Open-source platform for visualizing and analyzing metrics collected by Prometheus.

## Requirements

All components (FastAPI, Redis, MongoDB, Prometheus, Grafana) will run in **Docker** containers, so there is no need to manually install or configure these services. Docker Compose is used to manage and run all the containers in one unified environment.

### Prerequisites

- **Docker** and **Docker Compose** installed on your machine.

## Setup

### 1. Clone the Repository

Start by cloning the repository:

```bash
git clone https://github.com/yourusername/chatapp.git
cd chatapp

```
```bash
cp .example_env .env # copy to env 
 
docker-compose up --build
```

### Explanation:
- **`docker-compose up --build`**: This command builds and starts the Docker containers as defined in your `docker-compose.yml` file.
- **Access the Application**: After the containers are running, you'll be able to access the FastAPI backend at `localhost:8000` on your browser.

This should help you quickly get up and running with the application!



### 2. Architecture Overview

The architecture of the chat application is designed to be scalable and efficient. It leverages several technologies to ensure real-time messaging, high availability, and seamless monitoring. Below are the key components and how they work together:

### Horizontal Scalability

The application is designed to be **horizontally scalable**. This means that as the load increases, additional instances of the FastAPI application can be spun up to handle the increased traffic. This is accomplished using **Docker** and **Docker Compose**, which allow you to easily scale the application by increasing the number of FastAPI service replicas.

- **FastAPI** instances are stateless, so multiple instances can run behind a load balancer without any issues.
- **Redis** and **MongoDB** are both designed to handle multiple clients and instances simultaneously, ensuring the scalability of the system.

As the application scales, Redis handles Pub/Sub messaging across multiple FastAPI instances, and MongoDB ensures persistence across instances.

### Pub/Sub Messaging with Redis

The real-time chat functionality relies heavily on Redis' **Pub/Sub** (Publish/Subscribe) messaging pattern. Redis is used to handle the distribution of chat messages between users in real-time. Here's how it works:

- When a user sends a message, the message is published to a Redis channel.
- All FastAPI instances (subscribers) are subscribed to this channel and immediately receive the new messages.
- As new messages are published, all connected clients (through FastAPI) will receive updates in real-time.

This system allows for a **highly responsive, real-time chat experience** while maintaining horizontal scalability. Since Redis is in-memory, it can handle a large number of messages per second with low latency.

### Data Persistence with MongoDB

While Redis handles real-time message delivery, **MongoDB** is used to store chat history and user data. MongoDB is a **NoSQL database** that offers flexibility in storing unstructured or semi-structured data, such as chat messages and user profiles. 

- All chat messages are saved persistently to MongoDB, which ensures that even if a service crashes or restarts, messages will not be lost.
- The chat history is stored in collections, and MongoDB's **replication** and **sharding** features can be used to ensure high availability and performance, especially as the application scales.

### Monitoring with Prometheus and Grafana

To monitor the health and performance of the application, **Prometheus** and **Grafana** are integrated.

- **Prometheus** is used to collect metrics from the application, such as request count, error rates, response times, and system resource usage (CPU, memory, etc.).

### Prometheus Metrics

The application exposes various Prometheus metrics to monitor the performance of the system, including HTTP request statistics, WebSocket metrics, and system resource usage. These metrics are collected by Prometheus and can be visualized in Grafana.

#### Metrics Overview

1. **HTTP Metrics**:
   - **`http_requests_total`**: Total number of HTTP requests received. It is a counter with labels for HTTP method, endpoint, and status code.
   - **`http_request_duration_seconds`**: The duration of HTTP requests in seconds. It is a summary metric that measures the time taken for HTTP requests.

2. **WebSocket Metrics**:
   - **`ws_connections_active`**: Number of currently active WebSocket connections. This is a gauge that tracks the current count of active WebSocket connections.
   - **`ws_connections_total`**: Total number of WebSocket connections. This is a counter that tracks the total number of WebSocket connections made since the application started.
   - **`ws_message_latency_seconds`**: The latency of WebSocket messages, measured in seconds. It is a histogram that tracks the distribution of message latency with defined buckets: [0.1, 0.5, 1, 2, 5, 10].
   - **`ws_messages_total`**: Total number of WebSocket messages sent. This is a counter that tracks the total number of WebSocket messages.

3. **System Metrics**:
   - **`cpu_usage_percent`**: The percentage of CPU usage. This is a gauge that represents the current CPU usage of the system.
   - **`memory_usage_percent`**: The percentage of memory usage. This is a gauge that represents the current memory usage of the system.
- **Grafana** is used to visualize these metrics. It provides interactive and customizable dashboards, allowing you to monitor the real-time performance of the system.
- With this integration, you can easily track the performance of FastAPI instances, Redis, MongoDB, and other services. Grafana's dashboards provide real-time insights into the system’s health.

### Online Status with Redis 

To handle **online user status** in a scalable and efficient manner, Redis is used with **Redis strings (key -values) **.

- Each user’s online status (whether they are online or offline) is stored as a key-value pair in a Redis .
- The key is the **user ID**, and the value is the **status** (e.g., `True` for online, `False` for offline).
- The Redis is shared across all FastAPI instances, ensuring that the online status is consistent and synchronized across the system, even as it scales horizontally.

This approach allows the application to manage and track the status of thousands or even millions of users without performance degradation. Redis' fast read and write operations make it an ideal choice for managing real-time online status in a large-scale application.

## Summary

This architecture ensures that the chat application is:

- **Real-time**: Messages are delivered to users instantly via Redis Pub/Sub.
- **Scalable**: The application can scale horizontally by adding more FastAPI instances. Redis and MongoDB support scalability to handle increased traffic and large amounts of data.
- **Resilient**: MongoDB ensures that chat data is persistent, and Redis efficiently manages real-time status updates.
- **Monitored**: Prometheus and Grafana allow you to keep track of system metrics and health in real-time.

With this design, the chat application can handle a large number of users while providing real-time messaging, persistent data storage, and robust monitoring.








####  Architecture Overview


The chat application is designed with scalability in mind. By leveraging Docker and Docker Compose, you can easily scale different components of the system, ensuring that the application can handle increasing traffic and load.

### 3. Scale FastAPI



FastAPI is stateless and can easily be scaled horizontally. To scale FastAPI, you can increase the number of replicas running behind a load balancer. Since FastAPI is stateless, additional instances can be added without disrupting the service. 

#### Scaling FastAPI in Docker

1. Open your `docker-compose.yml` file.
2. Under the `fastapi` service, you can modify the `replicas` setting to scale the application horizontally. For example:

```yaml
services:
  fastapi:
    deploy:
      replicas: 3  # Increase or decrease the number of replicas here
```

