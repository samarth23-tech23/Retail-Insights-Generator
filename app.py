import streamlit as st
from data_processor import DataProcessor
from llm_handler import LLMHandler
from visualization_handler import VisualizationHandler
import re
import pandas as pd

def main():
    st.set_page_config(page_title="Retail Insight Generator", layout="wide")
    
    st.markdown("""
        <style>
        .stApp {
            max-width: 1200px;
            margin: 0 auto;
        }
        </style>
    """, unsafe_allow_html=True)

    st.title("📊 Retail Insight Generator")

    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "processors" not in st.session_state:
        st.session_state.processors = []

    with st.sidebar:
        st.header("📁 Data Upload")
        uploaded_files = st.file_uploader("Upload your CSV files", type="csv", accept_multiple_files=True)
        st.markdown("---")
        st.markdown("### 💡 Tips")
        st.markdown("""
        - Upload one or more retail CSV files
        - Ask questions about your data
        - Get insights with visualizations
        - Use table names: retail_ingest_data_1, retail_ingest_data_2, etc.
        """)

    if uploaded_files:
        try:
            # Process new files only if they differ from previously uploaded ones
            current_files = {file.name: file for file in uploaded_files}
            if not st.session_state.processors or len(st.session_state.processors) != len(uploaded_files):
                st.session_state.processors = []
                for idx, file in enumerate(uploaded_files, 1):
                    processor = DataProcessor(file, table_suffix=f"_{idx}")
                    processor.process_data()
                    st.session_state.processors.append(processor)
            
            llm_handler = LLMHandler()
            viz_handler = VisualizationHandler()
            # Use the engine from the first processor for multi-table queries
            engine = st.session_state.processors[0].engine if st.session_state.processors else None
            
            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])
                    if "visualization" in message:
                        st.plotly_chart(message["visualization"], use_container_width=True)
            
            if prompt := st.chat_input("💭 Ask a question about your data..."):
                st.session_state.messages.append({"role": "user", "content": prompt})
                with st.chat_message("user"):
                    st.markdown(prompt)

                with st.chat_message("assistant"):
                    try:
                        with st.spinner("🤔 Analyzing data..."):
                            # Combine schema info from all processors
                            schema_info = {}
                            for idx, processor in enumerate(st.session_state.processors, 1):
                                schema_info[f"retail_ingest_data_{idx}"] = processor.get_schema()
                            
                            insights = llm_handler.generate_insights(prompt, schema_info)
                            
                            if insights.get('sql_query') and insights.get('sql_query').lower() != 'none':
                                # Extract all table names from the query
                                table_names = re.findall(r'retail_ingest_data_\d+', insights['sql_query'], re.IGNORECASE)
                                
                                if len(table_names) == 1:
                                    # Single-table query: use the specific processor
                                    table_name = table_names[0]
                                    processor_idx = int(table_name.split('_')[-1]) - 1
                                    processor = st.session_state.processors[processor_idx]
                                    results = processor.execute_analysis_query(insights['sql_query'])
                                else:
                                    # Multi-table query: execute directly on the engine
                                    from sqlalchemy import text
                                    with engine.connect() as connection:
                                        results = pd.read_sql(text(insights['sql_query']), connection)
                                
                                final_insights = llm_handler.generate_insights(
                                    prompt, schema_info, results.to_markdown()
                                )
                                
                                fig = None
                                if final_insights.get('visualization') and final_insights['visualization']['type'] != 'none':
                                    fig = viz_handler.create_visualization(results, final_insights['visualization'])
                                
                                answer = final_insights.get('answer', 'No insights generated.')
                                st.markdown(answer)
                                if fig:
                                    st.plotly_chart(fig, use_container_width=True)
                                
                                message_data = {"role": "assistant", "content": answer}
                                if fig:
                                    message_data["visualization"] = fig
                                st.session_state.messages.append(message_data)
                            
                            else:
                                answer = insights.get('answer', 'Unable to generate insights.')
                                st.markdown(answer)
                                st.session_state.messages.append({"role": "assistant", "content": answer})
                                
                    except Exception as e:
                        st.error(f"❌ Analysis error: {str(e)}")

        except Exception as e:
            st.error(f"❌ Error processing files: {str(e)}")
    else:
        st.info("👆 Please upload CSV files to get started!")

if __name__ == "__main__":
    main()