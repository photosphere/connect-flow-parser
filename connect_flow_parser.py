import os
import streamlit as st
import pandas as pd
import boto3
import json
import os
import csv

# Connect to Amazon Connect client
connect_client = boto3.client("connect")

# Define function to analyze action types in a flow


def analyze_action_types(flow_name, flow_content):
    st.write(flow_name)
    data = json.loads(flow_content)

    actions_df = pd.DataFrame(data["Actions"])
    st.write(actions_df)


# Set Streamlit page configuration
st.set_page_config(
    page_title="Amazon Connect Flow Analysis Tool!", layout="wide")
st.header(f"Amazon Connect Contact Flow Analysis Tool!")

# Load Connect instance ID from a local file, if available
connect_instance_id = ''
if os.path.exists('connect.json'):
    with open('connect.json', 'r') as f:
        connect_data = json.load(f)
        connect_instance_id = connect_data['Id']

# Get Connect instance ID from user input
connect_instance_id = st.text_input(
    'Connect Instance Id', value=connect_instance_id)

# Define flow types for filtering
flow_types = ["CONTACT_FLOW", "AGENT_WHISPER", "AGENT_TRANSFER",
              "AGENT_HOLD", "CUSTOMER_QUEUE", "QUEUE_TRANSFER", "OUTBOUND_WHISPER"]
contact_flow_types = st.multiselect(
    'Contact Flow Type', flow_types, default="CONTACT_FLOW")

# Load flows when the button is clicked
load_flow_button = st.button('Load Flow')
if load_flow_button:
    with st.spinner('Loading...'):
        # Get Connect instance details and save to a local file
        res = connect_client.describe_instance(InstanceId=connect_instance_id)
        connect_filtered = {k: v for k, v in res['Instance'].items() if k in [
            'Id', 'Arn']}
        with open('connect.json', 'w') as f:
            json.dump(connect_filtered, f)

        # List active flows of selected types
        res = connect_client.list_contact_flows(InstanceId=connect_instance_id)
        flows_df = pd.DataFrame(res['ContactFlowSummaryList'])
        flows_df = flows_df[flows_df['ContactFlowState'] == 'ACTIVE']
        flows_df = flows_df[flows_df['ContactFlowType'].str.upper().isin(
            contact_flow_types)]
        if not flows_df.empty:
            flows_df.to_csv("flows.csv", index=False)

# Display flows in a data editor if the file exists
if os.path.exists('flows.csv'):
    flows_df = pd.read_csv("flows.csv")
    flows_df.insert(0, 'Select', False)
    edited_data = st.data_editor(flows_df)

    display_button = st.button('Display')
    if display_button:
        selected_rows = edited_data[edited_data['Select']].index.tolist()
        flows_df.loc[selected_rows].to_csv('selected_flows.csv', index=False)

# Save selected flow contents to a CSV file
if os.path.exists('selected_flows.csv'):
    selected_flows_df = pd.read_csv("selected_flows.csv")
    with open("selected_flow_contents.csv", "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Name", "Content"])

        for index, row in selected_flows_df.iterrows():
            res = connect_client.describe_contact_flow(
                InstanceId=connect_instance_id, ContactFlowId=row['Id'])
            flow_name = res['ContactFlow']['Name']
            flow_content = res['ContactFlow']['Content']
            writer.writerow([flow_name, flow_content])

# Analyze action types for selected flows
if os.path.exists('selected_flow_contents.csv'):
    flow_contents_df = pd.read_csv("selected_flow_contents.csv")
    for index, row in flow_contents_df.iterrows():
        flow_name = row['Name']
        flow_content = row['Content']
        analyze_action_types(flow_name, flow_content)
