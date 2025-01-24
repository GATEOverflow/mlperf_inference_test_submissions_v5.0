# Copyright 2024-25 MLCommons. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# =============================================================================


import json
import os
import time
import sys
sys.path.insert(0, os.path.join("inference", "tools", "submission"))
import submission_checker as checker # noqa

with open('summary_results.json') as f:
    data = json.load(f)
#print(models_all)
#print(platforms)

def get_header():
    css = """
    /* General table styles */
table {
    width: 100%;
    border-collapse: collapse;
    margin: 20px 0;
    border: none;
}

table.titlebarcontainer,.titlebar {
    text-align: center !important;
}
td.headerbar {
    text-align: center;
    font-size: x-large;
}
th, td {
    padding: 8px;
    text-align: left;
    vertical-align: top;
}

/* Styling for the first table to make it stand out */
table:first-of-type {
    background-color: #e8e8e8; /* Light grey background */
    color: #333; /* Darker text for contrast */
    font-weight: bold; /* Makes text bold */
}

/* Styling inner tables to have borders */
table table {
    border: 1px solid #ccc;
}

/* More specific styling for headers and rows of inner tables */
table table th, table table td {
    border: 1px solid #ccc;
}

th {
    background-color: #f4f4f4;
}

tr:nth-child(even) {
    background-color: #f9f9f9;
}

tr:nth-child(odd) {
    background-color: #ffffff;
}

/* Adjust column widths if necessary */
th:nth-child(1), td:nth-child(1) { width: 20%; }
th:nth-child(2), td:nth-child(2) { width: 30%; }
    """
    html_header = f"""
<head>
<style type="text/css">
{css}
</style>
</head>
"""
    return html_header

def get_availability_string(version: str) -> str:
    """
    Generate availability string based on the version.
    
    Args:
        version (str): Version string (e.g., 'v1.0', 'v1.1', 'v2.0', ..., 'v9.1')
        
    Returns:
        str: Availability string (e.g., "Available as of February 2024")
    """
    # Define version-to-month mapping
    version_month_map = {
        "0": "February",
        "1": "August"
    }
    
    try:
        if not version.startswith('v'):
            raise ValueError("Version must start with 'v'")
        
        major, minor = version[1:].split('.')
        major = int(major)
        minor = minor.strip()
        
        if minor not in version_month_map:
            raise ValueError("Invalid minor version. Expected '0' or '1'.")
        
        if not (1 <= major <= 9):
            raise ValueError("Major version out of range (expected 1-9).")
        
        # Calculate year, starting from 2024 for v1.0
        year = 2021 + (major - 1)
        month = version_month_map[minor]
        
        return f" as of {month} {year}"
    
    except (ValueError, IndexError) as e:
        return f"Error: Invalid version format - {e}"




def get_header_table(system_json, version):
    submitter = system_json.get('submitter')
    system_name = system_json.get('system_name')
    division = system_json.get('division')
    category = system_json.get('system_type')
    status = system_json.get('status')

    availability_string = get_availability_string(version)
    if status.lower() == "available":
        availability_string = f"""Available {availability_string}"""
    elif status.lower() == "preview":
        availability_string = f"""Preview {availability_string}, should be avaiable within 180 days"""
    else:
        availability_string = f"""Research and Internal {availability_string}"""
    
    html =  f"""
<div class="resultpage">
 <div class="titlebarcontainer">
  <div class="logo">
   <a href="/" style="border: none"><img src="" alt="" /></a>
  </div>
  <div class="titlebar">
   <h1 class="title">MLPerf Inference {version}</h1>
   <p style="font-size: smaller">Copyright 2019-2025 MLCommons</p>
  </div>
 </div>
 <table class="titlebarcontainer">
  <tr>
   <td class="headerbar" rowspan="2">
    <p>{submitter}     </p>
    <p>{system_name}    </p>
   </td>
  </tr>
 </table>
 <table class="datebar">
  <tbody>
   <tr>
    <th id="license_num"><a href="">MLPerf Inference Category:</a></th>
    <td id="license_num_val">{category}</td>
    <th id="test_date"><a href="">MLPerf Inference Division:</a></th>
    <td id="test_date_val">{division}</td>
   </tr>
   <tr>
    <th id="tester"><a href="">Submitted by:</a></th>
    <td id="tester_val">{submitter}</td>
    <th id="sw_avail"><a href="">Availability:</a></th>
    <td id="sw_avail_val">{availability_string}</td>
   </tr>
  </tbody>
 </table>
  """
    return html


def get_system_json(path):
    #import requests
    # Send a GET request to the URL
    #response = requests.get(url)

    with open(path, "r") as f:
        data = json.load(f)
    # Check if the request was successful
    #if response.status_code == 200:
    #    # Parse the JSON content
    #    data = response.json()
        
    return data

def get_accelerator_details_table(system_json):
    table = '<h3>Accelerator Details</h3><table>'
    for key,value in system_json.items():
        if not key.startswith("accelerator"):
            continue
        table += f"""<tr><td>{key}</td><td>{value}</td></tr>"""

    table += "</table>"
    return table

def get_cpu_details_table(system_json):
    table = '<h3>Processor and Memory Details</h3><table>'
    hardware_fields = [ "processor", "cpu", "memory" ]
    for key,value in system_json.items():
        if any (a in key for a in hardware_fields) and "accelerator" not in key:
            table += f"""<tr><td>{key}</td><td>{value}</td></tr>"""

    table += "</table>"
    return table
def get_network_details_table(system_json):
    table = '<h3>Network and Interconnect Details</h3><table>'
    hardware_fields = [ "network", "nics" ]
    for key,value in system_json.items():
        if any (a in key for a in hardware_fields) and "accelerator" not in key:
            table += f"""<tr><td>{key}</td><td>{value}</td></tr>"""

    table += "</table>"
    return table
def get_hardware_details_table(system_json):
    table = '<h3>Other Hardware Details</h3><table>'
    hardware_fields = [ "hardware", "disk", "cooling",  "power", "hw_" ]
    for key,value in system_json.items():
        if any (a in key for a in hardware_fields) and "accelerator" not in key:
            table += f"""<tr><td>{key}</td><td>{value}</td></tr>"""

    table += "</table>"
    return table

def get_software_details_table(system_json):
    table = '<h3>Software Details</h3><table>'
    software_fields = [ "software", "framework", "firmware", "sw_", "operating_" ]
    for key,value in system_json.items():
        if any (a in key for a in software_fields):
            table += f"""<tr><td>{key}</td><td>{value}</td></tr>"""

    table += "</table>"
    return table

def get_table_header(division, category):
    if division == "open":
        accuracy_achieved_header = '<td> Accuracy </td>'
        colspan = "3"
    else:
        accuracy_achieved_header = "" #dont show accuracy as submitters are only expected to achieve the target
        colspan = "2"

    num_scenarios = 1
    html_table_head = f"""
<h3>Results Table</h3>
<table>
    <tr>
        <th rowspan="2">Model</th>
        <th rowspan="2">Accuracy Target</th>"""
    if "datacenter" in category:
        num_scenarios += 1
        html_table_head += f"""
        <th colspan="{colspan}">Server</th>"""

    html_table_head += f"""
        <th colspan="{colspan}">Offline</th>"""

    if "edge" in category:
        num_scenarios += 2
        html_table_head += f"""
        <th colspan="{colspan}">SingleStream</th>
        <th colspan="{colspan}">MultiStream</th>"""
    html_table_head += f"""
    </tr>
    <tr>"""

    for i in range(num_scenarios):
        html_table_head += f"""{accuracy_achieved_header}
    <td>Metric</td>
    <td>Performance</td>"""

    html_table_head += f"""
    </tr>"""
    return html_table_head

# Initialize a dictionary to organize the data by 'Details'
tables = {}
version = os.environ.get('INFERENCE_RESULTS_VERSION')

# Populate the dictionary with data
for entry in data:
    details = entry['Details']
    if details not in tables:
        tables[details] = {}
    categories = [ "edge", "datacenter" ]
    for category in categories:
        if category not in entry['Suite']:
            continue
        if category not in tables[details]:
            tables[details][category] = {}
        if entry['Category'] not in tables[details][category]:
            tables[details][category][entry['Category']] = {}

        if entry['Model'] not in tables[details][category][entry['Category']]:
            tables[details][category][entry['Category']] [entry['Model']] = {}
        if entry['Scenario'] not in tables[details][category][entry['Category']][entry['Model']]:
            tables[details][category][entry['Category']][entry['Model']][entry['Scenario']] = entry

# Now you can format each group in 'tables' as a markdown table
for details, entries in tables.items():
            
    details_split = details.split("/")
    details_split[9] = "systems"
    system = os.path.sep.join(details_split[7:11])
    #details_split[0] = "https://raw.githubusercontent.com"
    #system = details.replace("github.com", "raw.githubusercontent.com").replace("tree/", "refs/heads/").replace("results/", "systems/")
    system_json_path = f"""{system}.json"""
    system_json = get_system_json(system_json_path)
    header_table = get_header_table(system_json, version)
    accelerator_details = get_accelerator_details_table(system_json)
    cpu_details = get_cpu_details_table(system_json)
    hardware_details = get_hardware_details_table(system_json)
    software_details = get_software_details_table(system_json)
    network_details = get_network_details_table(system_json)
    
    out = f"## {details}"

    #models_edge = [ "gptj-99", "gptj-99.9", "bert-99", "bert-99.9", "stable-diffusion-xl", "retinanet", "resnet", "3d-unet-99", "3d-unet-99.9"  ]
    #if "datacenter" in entries:
    #    models = [ "llama2-70b-99", "llama2-70b-99.9", "gptj-99", "gptj-99.9", "bert-99", "bert-99.9", "stable-diffusion-xl",  "dlrm-v2-99", "dlrm-v2-99.9", "retinanet", "resnet", "3d-unet-99", "3d-unet-99.9"  ]

    models = checker.MODEL_CONFIG[version]["models"]

    for category in entries:
        for division, data in entries[category].items():
    
            html_table = get_table_header(division, category)
            if division == "open":
                colspan="3"
                scenario_missing_td = "<td></td><td></td><td></td>"
            else:
                colspan="2"
                scenario_missing_td = "<td></td><td></td>"

            for model in models:
                        
                if model in data:
                    html_table += f"""<tr><td>{model}</td>"""
                    
                    #version = data[model]["Offline"]["version"]
                    acc_target = checker.MODEL_CONFIG[version]["accuracy-target"][model]
                    if model in checker.MODEL_CONFIG[version]["required-scenarios-datacenter"]:
                        required_scenarios_datacenter = checker.MODEL_CONFIG[version]["required-scenarios-datacenter"][model]
                    else:
                        required_scenarios_datacenter = []
                    if model in checker.MODEL_CONFIG[version]["required-scenarios-edge"]:
                        required_scenarios_edge = checker.MODEL_CONFIG[version]["required-scenarios-edge"][model]
                    else:
                        required_scenarios_edge = []

                    i = 0
                    acc_targets = []
                    key = None
                    for item in acc_target:
                        if i%2 == 0:
                            key = item
                        else:
                            acc_targets.append( (key, item))
                        i+=1

                    acc_targets_list = []
                    for item in acc_targets:
                        acc_targets_list.append(f"""{item[0]}: {round(item[1], 4)}""")
                    acc_targets_string = ", ".join(acc_targets_list)
                    html_table += f"""<td>{acc_targets_string}</td>"""


                    if "datacenter" in category:
                        if "Server" in data[model]:
                            if division == "open":
                                html_table += f"""<td>{data[model]["Server"]["Accuracy"]}</td>"""
                            html_table += f"""<td>{data[model]["Server"]["Performance_Units"]}</td> <td>{data[model]["Server"]["Performance_Result"]}</td>"""
                        else:
                            if "Server" in required_scenarios_datacenter: #must be open
                                html_table += scenario_missing_td
                            else:
                                html_table += f"""<td colspan="{colspan}"> N/A </td>"""

                    if "Offline" in data[model]:
                        if division == "open":
                            html_table += f"""<td>{data[model]["Offline"]["Accuracy"]}</td>"""
                        html_table += f"""<td>{data[model]["Offline"]['Performance_Units']}</td> <td>{data[model]["Offline"]["Performance_Result"]}</td>"""
                    else:
                        html_table += scenario_missing_td
                    if "edge" in category:
                        if "SingleStream" in data[model]:
                            scenario = "SingleStream"
                            if division == "open":
                                html_table += f"""<td>{data[model][scenario]["Accuracy"]}</td>"""
                            html_table += f"""<td>{data[model][scenario]["Performance_Units"]}</td> <td>{data[model][scenario]["Performance_Result"]}</td>"""
                        else:
                            if "SingleStream" in required_scenarios_edge: #must be open
                                html_table += scenario_missing_td
                            else:
                                html_table += f"""<td colspan="{colspan}"> N/A </td>"""
                        if "MultiStream" in data[model]:
                            scenario = "MultiStream"
                            if division == "open":
                                html_table += f"""<td>{data[model][scenario]["Accuracy"]}</td>"""
                            html_table += f"""<td>{data[model][scenario]["Performance_Units"]}</td> <td>{data[model][scenario]["Performance_Result"]}</td>"""
                        else:
                            if "MultiStream" in required_scenarios_edge: #must be open
                                html_table += scenario_missing_td
                            else:
                                html_table += f"""<td colspan="{colspan}"> N/A </td>"""
                else:
                    pass
                    #html_table += "<td></td> <td></td>"
                    #html_table += "<td></td> <td></td>"
                    #html_table += "</tr>"
            html_table += "</table>"
            sut_name = os.path.basename(details)
            tmp_path = os.path.dirname(details)
            tmp_path = os.path.dirname(tmp_path)
            submitter = os.path.basename(tmp_path)
            out_path = os.path.join(division, submitter, "results", sut_name, "README.md")
            os.makedirs(os.path.dirname(out_path), exist_ok=True)

            html_table = f"""

{header_table}
<table>
            <tr><td>{accelerator_details}</td> <td>{cpu_details}</td> </tr>
            <tr><td >{hardware_details}</td> <td>{network_details}</td> </tr>
            <tr><td colspan="2">{software_details}</td> </tr>
            </table>
{html_table}
"""
            repo_name = os.environ.get('INFERENCE_RESULTS_REPO_NAME', "mlperf_inference_test_submissions_v5.0")
            repo_branch = os.environ.get('INFERENCE_RESULTS_REPO_BRANCH', "main")
            repo_owner = os.environ.get('INFERENCE_RESULTS_REPO_OWNER', 'mlcommons')

            readme_content = f"""
See the HTML preview [here](https://htmlpreview.github.io/?https://github.com/{repo_owner}/{repo_name}/blob/{repo_branch}/{division}/{submitter}/results/{sut_name}/summary.html)
{html_table}
"""
            with open(out_path, "w") as f:
                f.write(readme_content)
            html_out_path = os.path.join(division, submitter, "results", sut_name, "summary.html")
            html_header = get_header()
            html = f"""
<html>
{html_header}
<body>
{html_table}
</body>
</html>
            """
            with open(html_out_path, "w") as f:
                f.write(html)
            print(html_table)
            #sys.exit()
    
    
