import g4f
import json
from json_repair import repair_json
from typing import Dict, Optional

class LLMHandler:
    def __init__(self):
        g4f.debug.logging = False
        g4f.check_version = False
        
    def generate_insights(self, question: str, schema_info: dict, query_results: Optional[Dict] = None) -> Dict:
        # First pass - get initial insights
        initial_response = self._get_raw_insights(question, schema_info, query_results)
        
        # Second pass - clean up formatting
        cleanup_prompt = f"""Clean up and format this analysis response, fixing any spacing, formatting, or text artifacts.
        Ensure proper spacing between sentences and maintain the exact same data/numbers.
        Keep the response concise and well-formatted.

        Original response:
        {initial_response}

        Return the cleaned response in the exact same JSON format, but with improved formatting.
        """
        
        try:
            cleaned_response = g4f.ChatCompletion.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": cleanup_prompt}],
                temperature=0.1,  # Lower temperature for more consistent formatting
                stream=False
            )
            
            try:
                result = json.loads(cleaned_response)
                return result
            except json.JSONDecodeError:
                cleaned_json = repair_json(cleaned_response)
                return json.loads(cleaned_json)
                
        except Exception as e:
            # If cleanup fails, return original response
            return initial_response

    def _get_raw_insights(self, question: str, schema_info: dict, query_results: Optional[Dict] = None) -> Dict:
        # Build schema information for all tables
        tables_info = ""
        for table_name, info in schema_info.items():
            columns_detail = info.get('columns_detail', [])
            tables_info += f"\nTable: {table_name}\nAvailable Columns with Types:\n{chr(10).join(columns_detail)}\nSample Data:\n{info.get('sample_data', 'No sample data available')}\n"

        base_prompt = f"""You are a data analyst expert in SQL. Analyze this PostgreSQL database with multiple tables:

{tables_info}

CRITICAL RULES:
1. ONLY use columns from the listed tables
2. If the available columns are insufficient to answer the question, clearly state that
3. Keep answers concise and focused
4. For numeric calculations, CAST string columns to NUMERIC using CAST(column_name AS NUMERIC)
5. Use exact table names as shown above (e.g., retail_ingest_data_1, retail_ingest_data_2, etc.)
6. If the question doesn't specify a table and multiple tables exist, either infer the most relevant table or state that clarification is needed

VISUALIZATION RULES:
- Only suggest bar, line, or pie charts
- ONLY use column names that exist in the data
- Bar charts: For comparing categories or groups
- Line charts: For time-based trends
- Pie charts: For showing composition/distribution

Example Responses:

1. Time-based Question: "Show monthly sales trend from retail_ingest_data_1"
{{
    "sql_query": "SELECT DATE_TRUNC('month', date::timestamp) as month, SUM(CAST(total_amount AS NUMERIC)) as total_sales FROM retail_ingest_data_1 GROUP BY month ORDER BY month",
    "answer": "Monthly sales show an upward trend with peak in December at $50,000",
    "visualization": {{
        "type": "line",
        "x_axis": "month",
        "y_axis": "total_sales",
        "title": "Monthly Sales Trend",
        "description": "Line chart shows sales progression over time"
    }}
}}

2. Category Question: "What's the distribution of sales by product in retail_ingest_data_2?"
{{
    "sql_query": "SELECT product_name, SUM(CAST(total_amount AS NUMERIC)) as total_sales FROM retail_ingest_data_2 GROUP BY product_name ORDER BY total_sales DESC",
    "answer": "Product sales distribution shows Product A leading with 45% market share",
    "visualization": {{
        "type": "pie",
        "x_axis": "product_name",
        "y_axis": "total_sales",
        "title": "Sales Distribution by Product",
        "description": "Pie chart shows relative market share of each product"
    }}
}}

Question: {question}

Remember: Only use columns that exist in the data and match table and column names exactly as shown above.

Respond in this JSON format:
{{
    "sql_query": "Your PostgreSQL query here (or 'None' if columns are insufficient)",
    "answer": "Provide clear business insights from the query results",
    "visualization": {{
        "type": "none | bar | line | pie",
        "x_axis": "column_name",
        "y_axis": "column_name",
        "title": "Chart title",
        "description": "Why this visualization is relevant"
    }}
}}"""

        if query_results is not None:
            base_prompt += f"\n\nQuery Results:\n{query_results}"

        print("\nPrompt sent to LLM:")
        print(base_prompt)
            
        try:
            response = g4f.ChatCompletion.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": base_prompt}],
                temperature=0.5,
                stream=False
            )
            
            print("\nLLM Response:")
            print(response)
            
            try:
                result = json.loads(response)
                # Clean up the answer text
                if 'answer' in result:
                    result['answer'] = result['answer'].replace('  ', ' ').replace(' ,', ',')
                    result['answer'] = ' '.join(result['answer'].split())  # Fix spacing issues
                return result
            except json.JSONDecodeError:
                cleaned_response = repair_json(response)
                result = json.loads(cleaned_response)
                return result
            
        except Exception as e:
            raise ValueError(f"Error generating insights: {str(e)}")