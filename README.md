# CASIO Calculator

A simple web-based calculator built with Flask that mimics the design and functionality of a CASIO calculator.

## Features

- Basic arithmetic operations (addition, subtraction, multiplication, division)
- Clean CASIO-style interface
- Single display screen that shows expressions and results
- Clear functionality to reset the calculator
- Responsive design

## Screenshots

The calculator features a black background with green accents, similar to CASIO calculator designs.

## Installation

1. Clone this repository:
```bash
git clone <your-repository-url>
cd calculator
```

2. Install Flask:
```bash
pip install flask
```

3. Run the application:
```bash
python app.py
```

4. Open your browser and go to `http://127.0.0.1:5000`

## Usage

- Click number buttons (0-9) to input numbers
- Click operator buttons (+, -, ×, ÷) to perform operations
- Click "=" to calculate the result
- Click "C" to clear the display

## Example

1. Click "2" → Display shows "2"
2. Click "+" → Display shows "2+"
3. Click "3" → Display shows "2+3"
4. Click "=" → Display shows "5"

## Technologies Used

- **Backend**: Python Flask
- **Frontend**: HTML, CSS
- **Templates**: Jinja2

## Project Structure

```
calculator/
├── app.py              # Flask application
├── templates/
│   └── index.html     # Calculator interface
├── .gitignore         # Git ignore file
└── README.md          # Project documentation
```

## Contributing

Feel free to fork this project and submit pull requests for any improvements.

## License

This project is open source and available under the MIT License.
