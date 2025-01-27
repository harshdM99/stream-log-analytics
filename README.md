# Real-Time Data Streaming and Visualization Project

This project demonstrates real-time data streaming, processing, and visualization using **Apache Kafka**, **PySpark**, **Cassandra** and an interactive Python **Dash dashboard** that visualizes the processed data. Initially, the visualization was hosted on an EC2 instance to provide real-time updates. For cost-effectiveness and simplicity in presentation, a static version of the dashboard was later hosted online.

## Overview

Here you want to write a short overview of the goals of your project and how it works at a high level. If possible, include one or two images of the end product and architecture diagram (see examples below). diagrams.net is a great tool for creating architecture diagrams.

<!-- ### Data Visualization
![Example dashboard image](example-dashboard.png) -->

### Data Architecture

![Example architecture image](log-project-architecture.png)

The project simulates a real-time system to generate logs, process them, and visualize the insights through a dashboard. It includes:
1. **Data Ingestion**: Logs are generated at 2 logs/second and sent to Kafka.
2. **Data Processing**: PySpark Structured Streaming processes logs from Kafka every 10 seconds.
3. **Data Storage**: Transformed data is stored in Amazon Keyspaces (Cassandra) for real-time querying and in s3 as a data lake for future querying.
4. **Data Visualization**: A Python Dash dashboard visualizes stored data in real-time.

## Technologies Used

### **1. Data Streaming and Processing**
- **Apache Kafka**: For real-time log ingestion.
- **PySpark Structured Streaming**: For scalable stream processing.

### **2. Data Storage**
- **Amazon Keyspaces (Cassandra)**: For low-latency, distributed data storage.
- **Amazon S3**: For storing raw data for batch processing.

### **3. Visualization**
- **Dash**: For building interactive dashboards.
- **Plotly**: For creating visually engaging graphs.

### **4. Hosting**
- **Amazon EC2**: For hosting Kafka, Spark, and the Dash web application.

## Directory Structure
```
├── kafka/
│   └── log_generator.py        # Script to generate logs and send to Kafka
│
├── spark/
│   ├── process_logs.py         # Spark Structured Streaming script to process logs
│   ├── application.conf        # Configuration file for Keyspaces-Spark Connector
│   └── config.py               # Configuration file for Spark
│
├── visualization/
│   ├── app.py                  # Dash web application for visualization
│   └── assets/                 # Static CSS, images, etc.
│
├── architecture-diagram.png    # Architecture diagram for the project
│
└── README.md                   # Documentation for the project
```

## **Prerequisites**

### **Steps to Recreate the Project on AWS Free Tier:**
- **Launch EC2 Instances (t2.micro or larger depending on data volume)**
   - Kafka and Zookeeper
        - Create a topic named `logs` in Kafka.
        - Update the configuration file.
   - Spark cluster for both real-time and batch processing
        - Update the configuration file.
   - Dash web application

- **Key Setup Steps:**
   - Install and configure Kafka and Zookeeper on the first instance.
   - Install Spark on the second instance and configure it for both structured streaming and batch jobs.
   - Install Dash and Plotly on the third instance for visualizing the processed data.

---

## Future Improvements

To make this project easier to deploy, replicate, and scale, the following enhancements are planned:

1. Cloud Infrastructure Automation with Terraform: Automate the provisioning of EC2 instances, Amazon Keyspaces, and other AWS resources.
2. Containerization with Docker: Use Docker containers to encapsulate various components like Kafka, Spark, and the Dash app.
3. Streamlined Deployment: Combine Terraform and Docker for end-to-end automation.
