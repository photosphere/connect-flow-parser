import os
import streamlit as st
import pandas as pd
import boto3
import json
import os
import csv

connect_client = boto3.client("connect")


def analysis_action_types(flow_name, flow_content):
    st.write(flow_name)
    data = json.loads(flow_content)

    for action in data["Actions"]:
        action_type = action["Type"]
        action_parameters = action["Parameters"]

    df = pd.DataFrame(data["Actions"])
    st.write(df)


st.set_page_config(
    page_title="Amazon Connect Flow Analysis Tool!", layout="wide")

# app title
st.header(f"Amazon Connect Contact Flow Analysis Tool!")

connect_instance_id = ''

if os.path.exists('connect.json'):
    with open('connect.json') as f:
        connect_data = json.load(f)
        connect_instance_id = connect_data['Id']
        connect_instance_arn = connect_data['Arn']

# connect configuration
connect_instance_id = st.text_input(
    'Connect Instance Id', value=connect_instance_id)

# flow type configuration
flow_types = ["CONTACT_FLOW", "AGENT_WHISPER", "AGENT_TRANSFER",
              "AGENT_HOLD", "CUSTOMER_QUEUE", "QUEUE_TRANSFER", "OUTBOUND_WHISPER"]
contact_flow_types = st.multiselect(
    'Contact Flow Type', flow_types, default="CONTACT_FLOW")

load_flow_button = st.button('Load Flow')
if load_flow_button:
    with st.spinner('Loading......'):
        # connect configuration
        res = connect_client.describe_instance(
            InstanceId=connect_instance_id)
        connect_filtered = {k: v for k, v in res['Instance'].items() if k in [
            'Id', 'Arn']}

        # attributes
        with open('connect.json', 'w') as f:
            json.dump(connect_filtered, f)

        # load flows
        res = connect_client.list_contact_flows(
            InstanceId=connect_instance_id)
        df = pd.DataFrame(res['ContactFlowSummaryList'])
        df = df[df['ContactFlowState'] == 'ACTIVE']
        df = df[df['ContactFlowType'].str.upper().isin(contact_flow_types)]
        if len(df) > 0:
            df.to_csv("flows.csv", index=False)

if os.path.exists('flows.csv'):
    df = pd.read_csv("flows.csv")
    df.insert(0, 'Select', False)
    edited_data = st.data_editor(df)

    col1, col2, col3 = st.columns([1, 1, 8])
    with col1:
        display_button = st.button('Display')
        if display_button:
            selected_rows = edited_data[edited_data['Select']].index.tolist()
            df.loc[selected_rows].to_csv('selected_flows.csv', index=False)

if os.path.exists('selected_flows.csv'):
    df = pd.read_csv("selected_flows.csv")
    with open("selected_flow_contents.csv", "w", newline="") as file:
        # Create a CSV writer object
        writer = csv.writer(file)
        # Write the header row
        writer.writerow(["Name", "Content"])

        # Write each row to the CSV file
        for index, row in df.iterrows():
            res = connect_client.describe_contact_flow(
                InstanceId=connect_instance_id, ContactFlowId=row['Id'])
            flow_name = res['ContactFlow']['Name']
            flow_content = res['ContactFlow']['Content']
            writer.writerow([flow_name, flow_content])


if os.path.exists('selected_flow_contents.csv'):
    df = pd.read_csv("selected_flow_contents.csv")

    # Read each row from the CSV file
    for index, row in df.iterrows():
        flow_name = row['Name']
        flow_content = row['Content']
        analysis_action_types(flow_name, flow_content)
