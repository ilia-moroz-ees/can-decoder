# Usage

In an empty folder run
```bash
git clone https://github.com/ilia-moroz-ees/can-decoder.git
```
Then to create virtual environment, run

On Windows:
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

On UNIX or Mac:
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

To run the program, run:
```bash
python main.py <folder> <dbc_paths...> --start <start_time> --end <end_time> --filename <decoded_filename>
```

To get more information on how to use the script:
```bash
python main.py --help
```

To deactivate virtual environment, run
```bash
deactivate
```
