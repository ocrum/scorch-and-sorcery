# Scorch & Sorcery

A code repository for a playground game designed to teach elementary schools computational thinking featuring an animatronic dragon puzzle and a wizard-vs.-dragon tag game. For more information look at [the full documentation page](https://www.notion.so/15b656a7201080cab277ed366d993347?pvs=21).

## Getting Started

### **Prerequisites**

- Hardware:
    - XIAO ESP32 boards for each component
    - Servos, LEDs, buzzers and other electronics as described in the portfolio
- Software:
    - Thonny IDE (or similar) to upload code to ESP boards
- Libraries:
    - Machine, time, and other built-in MicroPython libraries

### **Installation & Setup**

Clone the repo:

```bash
git clone https://github.com/ocrum/scorch-and-sorcery.git 
```

Load Code onto Devices:

- Connect each ESP board via USB
- Open the desired script in Thonny
- Upload the code to the board’s filesystem

Code for each system:

- **Every system needs `networking.py` and a `config.py` file**
- Animatronic Dragon: `puppet.py` as `main.py` and `servo.py`
- Wand: `wand.py` as `main.py` and all files in the `wand` folder
- Spinner: `spinner.py` as `main.py`
- Hidden button: `hidden_button.py` as `main.py`
- Wizard Amulet: `amulet_wizard.py` as `main.py`
- Dragon Amulet: `amulet_dragon.py` as `main.py`

## Usage

`data_processing` : used to parse out accelerometer data and generate charts to visualize how movements change accelerometer and gyroscope sensor values.

- `data_processing.py`: Main file for generating charts. Upload your csv and it will generate charts for its data

`dragon`: code specific to the animatronic dragon

- `puppet.py`: Main code for dragon control
- `servo.py`: A servo library written by [Radomir Dopieralski](https://bitbucket.org/thesheep/micropython-servo)

`tag`: code used for the tag game

- `amulet_dragon.py`: Main code used for the dragon amulet
- `amulet_wizard.py`: Main code used for the wizard amulet
- `hidden_button.py`: Main code used for the hidden button
- `spinner.py`: Main code used for the spinner

`wand`: code used for the wand

- `button.py`: A custom library for reading button data
- `config.py`: Configuration file for the networking library
- `led.py`: A custom library for controlling LEDs
- `lsm6ds3.py`: A library for the LSM6DS3 accelerator & gyroscope sensor [found online](https://github.com/pimoroni/lsm6ds3-micropython)
- `networking.py`: A library for communication between ESP written by [Nick](https://github.com/tuftsceeo/Smart-System-Platform/tree/main)
- `wand.py`: Main code used for controlling the wand.