# AIOI PTLController
This project implements a real-time Put-to-Light (PTL) sorting and order consolidation system with Kafka integration, designed to optimize warehouse operations and improve order fulfillment efficiency.

✅ Key Features

⚡ Real-time order and item tracking using Apache Kafka.

📦 Automated Put-to-Light sorting logic.

🔄 Dynamic order consolidation for efficient packing.

👥 Multi-user support: Handles multiple operators or zones simultaneously.

🌈 Multi-color signaling: Assigns unique light colors to users/zones for clear, error-free sorting.

🔌 Hardware communication using sockets.

🔍 Logs and tracks sorting events and exceptions.

🌐 REST API built with FastAPI for control and monitoring.


⚙️ How It Works

1️⃣ Kafka Integration

Uses confluent_kafka.Consumer to subscribe to real-time order and item topics.

Processes messages, validates data, and triggers sorting actions.

2️⃣ Put-to-Light Sorting

Determines which bin/light to activate based on item info and order details.

Controls hardware via socket connections.

3️⃣ Order Consolidation

Combines partial picks into consolidated orders for packing.

4️⃣ FastAPI Service

Exposes API endpoints for:

    Monitoring system health

    Triggering manual sorting actions

    Retrieving logs and processing status