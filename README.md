<h1>Sensor Data Ingestion Pipeline for EELabs</h1>

<p>
A lightweight Python pipeline for retrieving, processing, and exporting scientific sensor data from an InfluxDB database.
</p>

<h2>Overview</h2>

<p>
This repository contains two scripts designed to support data retrieval and management workflows for environmental monitoring and scientific analysis.
</p>

<ul>
    <li><strong>active_devices.py</strong> – Identifies active sensors within a specified time window and generates a metadata inventory.</li>
    <li><strong>query_sensor_data.py</strong> – Performs full or incremental queries to retrieve sensor measurements and export them to CSV format.</li>
</ul>

<h2>Features</h2>

<ul>
    <li>InfluxDB integration</li>
    <li>Incremental querying to reduce database load</li>
    <li>Sensor discovery and metadata enrichment</li>
    <li>Time-series data processing with Pandas</li>
    <li>Automated CSV export</li>
    <li>Environment variable configuration</li>
</ul>

<h2>Project Structure</h2>

<pre>
sensor-data-pipeline/
│
├── active_devices.py
├── query_sensor_data.py
├── .env.example
├── requirements.txt
└── README.md
</pre>

<h2>Requirements</h2>

<ul>
    <li>Python 3.9+</li>
    <li>Pandas</li>
    <li>InfluxDB</li>
    <li>python-dotenv</li>
</ul>

<h2>Usage</h2>

<pre><code>
python active_devices.py
python query_sensor_data.py
</code></pre>

<h2>Notes</h2>

<p>
Database names, sensor identifiers, locations, and credentials have been anonymized for demonstration purposes. The repository reflects the data-ingestion and processing workflow used in a scientific research environment.
</p>

<h2>License</h2>

<p>
MIT License
</p>
