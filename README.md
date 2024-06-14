## About Amazon Connect Flow Parser Tool
This solution can be used to search and display flows with parameters in Amazon Connect.

### Installation

Clone the repo

```bash
git clone https://github.com/photosphere/connect-flow-parser.git
```

cd into the project root folder

```bash
cd connect-flow-parser
```

#### Create virtual environment

##### via python

Then you should create a virtual environment named .venv

```bash
python -m venv .venv
```

and activate the environment.

On Linux, or OsX 

```bash
source .venv/bin/activate
```
On Windows

```bash
source.bat
```

Then you should install the local requirements

```bash
pip install -r requirements.txt
```
### Build and run the Application Locally

```bash
streamlit run connect_flow_parser.py
```
#### Configuration screenshot
<img width="1044" alt="Flow Parser" src="https://github.com/photosphere/connect-flow-parser/assets/3398595/ab5d6a9e-4e37-4547-9c17-28bb44aed00f">
