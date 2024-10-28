![Снимок экрана 2024-10-28 в 23 55 02](https://github.com/user-attachments/assets/2018ca09-13b7-442c-b8d8-243cef524eb2)



# HandyMan

HandyMan is a desktop application designed to help you manage and organize your photos and videos efficiently. It provides features to move short videos and screenshots to designated folders, and organize files by date.

## Features

- **Move Short Videos**: Automatically move videos shorter than 3 seconds to a specified destination folder. These short videos are often created from Live Photos on iPhones.
- **Move Screenshots**: Identify and move screenshots based on EXIF data to a specified destination folder.
  
## Requirements

- Python 3.8 or higher
- macOS (for building the application with py2app)
- The following Python packages:
  - Pillow
  - PyQt6
  - PyInstaller

## Installation

1. **Clone the repository**:

   ```bash
   git clone https://github.com/KleoPadre/HandyMan.git
   cd HandyMan
   ```

2. **Install dependencies**:

   Use pip to install the required packages:

   ```bash
   pip install -r requirements.txt
   ```

3. **Build the application**:

   Ensure you have `py2app` installed:

   ```bash
   pip install py2app
   ```

   Then, run the build script:

   ```bash
   chmod +x build_app.sh
   ./build_app.sh
   ```

4. **Run the application**:

   After building, you can run the application using:

   ```bash
   open dist/HandyMan.app
   ```

   Or, for debugging:

   ```bash
   dist/HandyMan.app/Contents/MacOS/HandyMan
   ```

## Usage

1. **Select Source and Destination Folders**: Use the interface to select the source folder containing your media files and the destination folder where you want to organize them.

2. **Move Short Videos**: Click the "3 sec video" button to move videos shorter than 3 seconds.

3. **Move Screenshots**: Click the "Screenshots" button to move identified screenshots.

4. **Organize by Date**: (Feature to be implemented) Organize files by their creation date.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request for any improvements or bug fixes.

## Acknowledgments

This application was developed with the assistance of GPT models, which provided guidance and support throughout the development process.
