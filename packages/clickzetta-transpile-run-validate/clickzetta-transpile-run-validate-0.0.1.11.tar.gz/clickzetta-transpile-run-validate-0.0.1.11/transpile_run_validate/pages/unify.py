from __future__ import absolute_import, unicode_literals
import os
import sys
import io
import json
import streamlit as st
import sqlglot

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from low_touch_tool.util import connect_util, validation_util

TEXT_INPUT_KEY = 0

st.set_page_config(
    page_title="ClickZetta Low Touch Tool",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'About': 'https://github.com/tobymao/sqlglot'
    }
)

dialects = ['bigquery', 'clickhouse', 'databricks', 'doris', 'drill', 'duckdb', 'hive', 'mysql', 'oracle',
            'postgres', 'presto', 'redshift', 'snowflake', 'spark', 'spark2', 'sqlite', 'starrocks',
            'tableau', 'teradata', 'trino', 'tsql', 'clickzetta']

st.title('ClickZetta Low Touch Tool')

st.subheader("Database Configuration", divider='rainbow')
config_col1, config_col2 = st.columns(2)

with config_col1:
    src_db = st.selectbox('source db', dialects, index=dialects.index('doris'))
    config = None
    if src_db == "mysql" or src_db == "doris":
        config = st.file_uploader('source config file', type=['json'])
        if config:
            config = json.load(io.BytesIO(config.getvalue()))
            host = config['host']
            port = config['port']
            username = config['username']
            password = config['password']
            config = {'fe_servers': [host + ':' + port], 'user': username,
                      'password': password, 'db_type': src_db}
        src_button = st.button('Connect Testing', key=TEXT_INPUT_KEY + 12)

        if src_button:
            connect_util.source_connection_test(config)
    else:
        # url = st.text_input('URL', value='', key=TEXT_INPUT_KEY + 14)
        st.error('Not supported yet')

with config_col2:
    dest_db = st.selectbox('destination db', ['clickzetta'], index=0)

    uploader = st.file_uploader('destination config file', type=['json'])

    if uploader:
        config = json.load(io.BytesIO(uploader.getvalue()))
        service = config['service']
        workspace = config['workspace']
        instance = config['instance']
        vcluster = config['vcluster']
        username = config['username']
        password = config['password']
        schema = config['schema']
        instance_id = config['instanceId']
        if instance_id is None or len(instance_id) == 0:
            st.text("instanceId is empty, will use the first instanceId")
            instance_id = 0

    dest_button = st.button('Connect Testing', key=TEXT_INPUT_KEY + 13)

    if dest_button:
        config = {'service': service, 'workspace': workspace, 'instance': instance,
                  'vcluster': vcluster, 'username': username, 'password': password, 'schema': schema,
                  'db_type': dest_db, 'instanceId': 300}
        connect_util.destination_connection_test(config)

st.subheader('SQL Transpile', divider='rainbow')
transpile_col1, transpile_col2 = st.columns(2)

with transpile_col1:
    src_dialect = st.selectbox('from dialect', dialects, index=dialects.index('doris'))
    src_sql = st.text_area('source sql', label_visibility='collapsed', height=300)
    transpile_button = st.button('Testing Transpiled SQL', key=TEXT_INPUT_KEY + 15)

with transpile_col2:
    dest_dialect = st.selectbox('to dialect', dialects, index=dialects.index('clickzetta'))
    dest_sql = st.empty()


def replace_des_sql():
    st.text(des_result)
    st.session_state['ret'] = des_result


if src_sql:
    if transpile_button:
        try:
            ret = sqlglot.transpile(src_sql, read=src_dialect, write=dest_dialect, pretty=True)
            # dest_sql.code(ret[0], language='python')
            st.session_state['ret'] = ret[0]
        except Exception as e:
            st.error(f'Transpile from {src_dialect} SQL to {dest_dialect} SQL Failed!')
            st.error(e)
if 'ret' not in st.session_state:
    st.session_state['ret'] = ''

des_result = dest_sql.text_area('des_sql', label_visibility='collapsed', height=300, value=st.session_state['ret'])

st.subheader("Query Validation", divider='rainbow')

validation_col1, validation_col2 = st.columns(2)

validate_level = ['Basic verification', 'Multidimensional verification', 'Line by line verification']
level = st.selectbox('validate level', validate_level, index=0)

exe_validation = st.button('Execute Validation', key=TEXT_INPUT_KEY + 16)

if exe_validation:
    st.subheader("Validation Result", divider='rainbow')
    if des_result:
        st.session_state['ret'] = des_result
    if level == 'Basic verification':
        try:
            source_df_result, destination_df_result = validation_util.gen_basic_validation_result(
                st.session_state['src_connection'],
                st.session_state['destination_connection'],
                src_sql, st.session_state['ret'])
            validation_util.display_validation_result(source_df_result, destination_df_result)

        except Exception as e:
            st.error(e)

    elif level == 'Multidimensional verification':
        try:
            source_df_result, destination_df_result = validation_util.multidimensional_validation(
                st.session_state['src_connection'],
                st.session_state['destination_connection'],
                src_sql, st.session_state['ret'])
            validation_util.display_validation_result(source_df_result, destination_df_result)

        except Exception as e:
            st.error(e)
    elif level == 'Line by line verification':
        try:
            source_df_result, destination_df_result = validation_util.line_by_line_validation(
                st.session_state['src_connection'],
                st.session_state['destination_connection'],
                src_sql, st.session_state['ret'])
            validation_util.display_validation_result(source_df_result, destination_df_result)

        except Exception as e:
            st.error(e)
    else:
        st.error('Not supported yet')
