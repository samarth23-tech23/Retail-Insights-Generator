# Retail Insight Generator

A Streamlit-based application that processes retail data and generates insights using natural language queries. The application integrates PostgreSQL for data storage, GPT-4o for generating analytical insights, and Plotly for interactive visualizations.

## Features

- **CSV File Upload and Processing**: Upload retail data in CSV format for analysis.
- **Automatic Database and Table Creation**: Seamlessly creates PostgreSQL database and tables based on uploaded data.
- **Natural Language Query Processing**: Ask business questions in plain English to receive insights.
- **Interactive Chat Interface**: Engage with the application through a user-friendly Streamlit interface.
- **SQL Query Generation and Execution**: Automatically generates and executes SQL queries based on user queries.
- **Real-Time Data Analysis**: Provides immediate insights from the processed data.
- **Dynamic Visualizations**: Generates bar, line, or pie charts using Plotly based on query results.
- **Markdown-Formatted Responses**: Delivers clean, well-formatted analysis in markdown.

## Prerequisites

- **Python 3.8+**: Ensure Python is installed on your system.
- **PostgreSQL Database Server**: A running PostgreSQL instance (version 12 or higher recommended).
- **pip Package Manager**: For installing Python dependencies.
- **Git**: For cloning the repository.

## Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/samarth23-tech23/retail-insight-generator.git
   cd retail-insight-generator
   ```

2. **Set Up a Virtual Environment** (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure PostgreSQL**:
   - Ensure PostgreSQL is running locally or on a specified host.
   - Create a PostgreSQL user and note the credentials (default in code: user=`postgres`, password=`samplepass`).
   - Update the database connection settings in the application if different from defaults (`host=localhost`, `port=5432`).

5. **Set Up Environment Variables** (if required for GPT-4o API):
   - Create a `.env` file in the project root.
   - Add API keys or other sensitive configurations (e.g., for GPT-4o integration):
     ```env
     GPT4O_API_KEY=your-api-key
     ```

## Dependencies

The project relies on the following Python packages (listed in `requirements.txt`):
- `streamlit`: For the web interface.
- `psycopg2-binary`: For PostgreSQL database connectivity.
- `pandas`: For data manipulation.
- `clevercsv`: For robust CSV parsing.
- `plotly`: For interactive visualizations.
- `g4f`: For GPT-4o integration.
- `sqlalchemy`: For database operations.
- `python-dotenv`: For environment variable management.

Install them using:
```bash
pip install streamlit psycopg2-binary pandas clevercsv plotly g4f sqlalchemy python-dotenv
```

## Running the Application

1. **Start the Streamlit Application**:
   ```bash
   streamlit run app.py
   ```

2. **Access the Application**:
   - Open your browser and navigate to `http://localhost:8501`.
   - Upload a retail CSV file and start asking natural language questions.

## Usage

1. **Upload Data**:
   - Use the Streamlit interface to upload a CSV file containing retail data (e.g., columns like `date`, `product_name`, `total_amount`).
   - The application automatically processes the file, cleans the data, and stores it in a PostgreSQL database.

2. **Ask Questions**:
   - Enter natural language queries such as:
     - "Show monthly sales trend"
     - "What's the distribution of sales by product?"
   - The system generates SQL queries, executes them, and provides insights with visualizations.

3. **View Results**:
   - Insights are displayed in markdown format.
   - Visualizations (bar, line, or pie charts) appear based on the query type.

### Example Queries and Outputs

- **Query**: "Show monthly sales trend"
  - **Output**:
    ```json
    {
        "sql_query": "SELECT DATE_TRUNC('month', date::timestamp) as month, SUM(CAST(total_amount AS NUMERIC)) as total_sales FROM retail_ingest_data GROUP BY month ORDER BY month",
        "answer": "Monthly sales show an upward trend with a peak in December at $50,000",
        "visualization": {
            "type": "line",
            "x_axis": "month",
            "y_axis": "total_sales",
            "title": "Monthly Sales Trend",
            "description": "Line chart shows sales progression over time"
        }
    }
    ```

- **Query**: "What's the distribution of sales by product?"
  - **Output**:
    ```json
    {
        "sql_query": "SELECT product_name, SUM(CAST(total_amount AS NUMERIC)) as total_sales FROM retail_ingest_data GROUP BY product_name ORDER BY total_sales DESC",
        "answer": "Product sales distribution shows Product A leading with 45% market share",
        "visualization": {
            "type": "pie",
            "x_axis": "product_name",
            "y_axis": "total_sales",
            "title": "Sales Distribution by Product",
            "description": "Pie chart shows relative market share of each product"
        }
    }
    ```

## Project Structure

```
retail-insight-generator/
├── app.py                  # Main Streamlit application
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables (not tracked)
├── src/
│   ├── data_processor.py   # Handles CSV processing and database operations
│   ├── llm_handler.py      # Manages GPT-4o interactions
│   ├── visualization_handler.py  # Generates Plotly visualizations
└── README.md               # Project documentation
```

## Contributing

Contributions are welcome! To contribute:

1. Fork the repository.
2. Create a new branch (`git checkout -b feature/your-feature`).
3. Make your changes and commit (`git commit -m "Add your feature"`).
4. Push to the branch (`git push origin feature/your-feature`).
5. Open a pull request.

Please ensure your code follows the project's coding standards and includes tests where applicable.

## Limitations

- **Database**: Assumes a local PostgreSQL instance and uses a single-table design.
- **Visualizations**: Limited to bar, line, and pie charts with basic styling.
- **LLM**: Dependent on GPT-4o availability and requires structured column names.
- **Data Size**: Optimized for reasonable dataset sizes; large datasets may require indexing.

## Best Practices

- **Data Preparation**: Use clean CSV files with consistent column names and proper data types.
- **Querying**: Ask clear, specific questions focusing on one analysis at a time.
- **Performance**: Index important columns and monitor query complexity for large datasets.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contact

For questions or support, please open an issue on the GitHub repository or contact the project maintainer at [samarth.codes@gmail.com].
