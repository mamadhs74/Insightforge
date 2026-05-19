# InsightForge Engineering Edition

**InsightForge Engineering Edition** is a self-hosted Python/Streamlit app that turns CSV and Excel engineering/research data into quick technical reports.

It helps users inspect messy datasets, find data-quality issues, detect anomaly candidates, view correlations, generate plots, and export a clean HTML report.

This is useful for:

- engineering students
- PhD researchers
- test engineers
- lab assistants
- data analysts
- consultants
- people working with telemetry, sensor logs, simulation exports, or experiment data

---

## What It Does

Upload a `.csv`, `.xls`, or `.xlsx` file and get:

- dataset overview
- row/column count
- missing-value checks
- duplicate-row checks
- constant-column detection
- numeric summary statistics
- top correlation pairs
- anomaly candidate detection
- interactive charts
- downloadable HTML report
- downloadable CSV with anomaly flags

---

## What It Is Not

InsightForge is not a replacement for Power BI, Tableau, MATLAB, or full statistical software.

It is a lightweight first-pass technical reporting tool.

It is designed to help users quickly understand a dataset before doing deeper analysis.

---

## Requirements

You need:

- Windows, macOS, or Linux
- Python 3.10 or newer
- Internet connection for first installation only

---

## Installation on Windows

### 1. Unzip the project

Unzip the downloaded file.

Example location:

```text
C:\Users\YourName\Downloads\insightforge_engineering_edition_v1
```

Open the project folder.

If the real project is inside another folder called:

```text
insightforge_seller_kit
```

open that folder.

You should see files like:

```text
app.py
requirements.txt
README.md
sample_data
insightforge
tests
```

---

### 2. Open terminal in the project folder

In Windows File Explorer, open the folder that contains `app.py`.

Click the address bar, type:

```text
cmd
```

Then press Enter.

A terminal window should open inside the project folder.

---

### 3. Create a virtual environment

Run:

```bash
python -m venv .venv
```

If that does not work, run:

```bash
py -m venv .venv
```

---

### 4. Activate the virtual environment

Run:

```bash
.venv\Scripts\activate
```

You should now see this at the beginning of the terminal line:

```text
(.venv)
```

Example:

```text
(.venv) C:\Users\YourName\Downloads\insightforge_engineering_edition_v1\insightforge_seller_kit>
```

---

### 5. Install dependencies

Run:

```bash
pip install -r requirements.txt
```

Wait until the installation finishes.

If `requirements.txt` is not found, you are probably in the wrong folder. Make sure you are inside the folder that contains `app.py` and `requirements.txt`.

---

### 6. Start the app

Run:

```bash
streamlit run app.py
```

Streamlit may ask for your email address.

You can leave it blank and press Enter.

After that, your browser should open automatically.

If the browser does not open, manually open:

```text
http://localhost:8501
```

---

## Installation on macOS or Linux

Open a terminal inside the project folder.

Run:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Then open:

```text
http://localhost:8501
```

---

## Quick Start

### Step 1: Run the app

```bash
streamlit run app.py
```

### Step 2: Upload a file

Click **Browse files** and upload a `.csv`, `.xls`, or `.xlsx` file.

You can test the app using the included sample file:

```text
sample_data/sample_telemetry.csv
```

### Step 3: Review the automatic analysis

The app will show:

- dataset shape
- column overview
- missing values
- duplicate rows
- constant columns
- summary statistics
- correlations
- anomaly candidates
- plots

### Step 4: Export results

Use the download buttons to export:

- HTML technical report
- CSV file with anomaly flags

---

## Example Use Cases

### Engineering lab data

Upload experiment data from sensors or lab equipment and quickly check:

- missing readings
- unusual values
- strong correlations
- suspicious measurement periods

### Vehicle or telemetry data

Upload speed, acceleration, temperature, pressure, current, voltage, or sensor logs and generate a first-pass technical report.

### Simulation exports

Upload CSV/XLSX tables exported from simulation or post-processing tools and inspect the dataset before writing a report.

### Research projects

Upload thesis or research data and create a structured overview for documentation.

### Consulting reports

Use the generated HTML report as a first-pass analysis before preparing a client-facing report.

---

## Supported File Types

Supported:

- `.csv`
- `.xls`
- `.xlsx`

Recommended first test:

- less than 10 MB
- clean column names
- at least some numeric columns

Very large files may be slow depending on your computer.

---

## Running Tests

To check that the core functions work, run:

```bash
pytest
```

Expected result:

```text
4 passed
```

If `pytest` is missing, run:

```bash
pip install pytest
pytest
```

---

## Troubleshooting

### Problem: `requirements.txt` not found

You are probably in the wrong folder.

On Windows, run:

```bash
dir
```

On macOS/Linux, run:

```bash
ls
```

Make sure you are in the folder that contains:

```text
requirements.txt
app.py
```

If you see a folder called `insightforge_seller_kit`, go into it:

```bash
cd insightforge_seller_kit
```

Then run:

```bash
pip install -r requirements.txt
```

---

### Problem: `streamlit` command not found

Run:

```bash
pip install streamlit
```

Then try again:

```bash
streamlit run app.py
```

---

### Problem: Excel file does not load

Install Excel support:

```bash
pip install openpyxl
```

Then restart the app:

```bash
streamlit run app.py
```

---

### Problem: Browser does not open automatically

Open this manually in your browser:

```text
http://localhost:8501
```

---

### Problem: App is running but nothing happens

Make sure you uploaded a supported file:

```text
.csv
.xls
.xlsx
```

For a first test, use:

```text
sample_data/sample_telemetry.csv
```

---

### Problem: File is too large or app is slow

Try a smaller file first.

Recommended first test size:

```text
under 10 MB
```

Large files may require more memory and processing time.

---

## Privacy

InsightForge runs locally on your own machine.

Uploaded files are processed in the local Streamlit session.

No external cloud upload is required by default.

---

## Suggested Product Description

You can use this description on a sales page:

```text
InsightForge Engineering Edition is a self-hosted Python/Streamlit app that turns CSV/XLSX engineering and research data into data-quality checks, anomaly candidates, correlations, plots, and downloadable technical HTML reports.

It is designed for engineers, researchers, students, data analysts, and technical consultants who need a fast first-pass report from messy measurement, telemetry, simulation, or experiment data.
```

---

## Suggested Audience

This product is most suitable for:

- engineering students
- PhD researchers
- test engineers
- lab engineers
- data analysts
- technical consultants
- developers building internal reporting tools

It is not intended as a full enterprise BI system.

---

## Suggested Pricing

Recommended launch price:

```text
$29
```

Recommended price after adding screenshots, demo video, PDF export, Docker setup, and more examples:

```text
$49–99
```

Recommended custom setup price:

```text
$300–1000+
```

---

## License

This package is sold as a self-hosted source-code product.

The buyer may use it locally for personal, academic, research, or internal business workflows.

The buyer may modify the code for their own use.

The buyer may not resell, redistribute, repackage, or publish this product as a competing source-code product unless explicitly permitted by the seller.

---

## Support

For support, contact the seller through the platform where you purchased the product.

Please include:

- your operating system
- Python version
- screenshot of the error
- terminal output
- example file structure if installation fails

---

## Basic Command Summary

Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Run tests:

```bash
pytest
```

Open app:

```text
http://localhost:8501
```