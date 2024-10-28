# Busbits

Effortlessly generate libraries and documentation for I2C and SPI devices based on datasheet specifications.

## Development

Follow these steps to set up your development environment:

1. **Clone the Repository**:
   Clone the repository to your local machine using Git:

   ```bash
   git clone https://github.com/aircey/busbits.git
   cd busbits
   ```

2. **Create a Virtual Environment**:
   Create a virtual environment to isolate your project dependencies:

   ```bash
   python3 -m venv venv
   ```

3. **Activate the Virtual Environment**:
   Activate the virtual environment:

   - **On Windows**:
     ```bash
     venv\Scripts\activate
     ```
   - **On macOS/Linux**:
     ```bash
     source venv/bin/activate
     ```

4. **Install Dependencies**:
   With the virtual environment activated, install the project dependencies:

   ```bash
   pip install -e .
   ```

   This will install the package in editable mode along with any dependencies listed in `requirements.txt`.

## Usage

Once the environment is set up, you can run the Busbits command-line tool with:

```bash
busbits
```
