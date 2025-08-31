# Titan Windows Tweaks

I built this tool to make it easy to apply a bunch of common Windows performance tweaks for gaming and general use. It's a simple GUI application that runs `.cmd` scripts to modify the registry, power settings, network stack, and more.

### What it Does:

*   **Easy-to-use GUI:** All tweaks are organized into tabs and can be selected with a simple switch.
*   **Apply & Revert:** You can apply a group of selected tweaks at once, and more importantly, you can revert them using the included `revert.cmd` script.
*   **Categories Covered:** Includes tweaks for Power/CPU, Input/USB, Network, Storage, GPU, and Memory.
*   **Debloating:** Has options to disable telemetry, uninstall bloatware apps, and stop unnecessary background services.
*   **Admin Permissions:** The tool will automatically ask for the Administrator permissions it needs to run.

### How to Run:

1.  Make sure you have Python 3 installed.
2.  Install the required libraries:
    ```bash
    pip install customtkinter Pillow
    ```
    *Note: The tool also tries to use a library to handle `.svg` icons. If you see errors in the log, you might need to install `cairosvg`.*

3.  Run the main script from your terminal as an administrator:
    ```bash
    python titan_tweak_tool.py
    ```

### **Disclaimer**

This tool makes significant changes to your Windows system settings. While there is a revert script, things can still go wrong. Please use this at your own risk. I'm not responsible for any issues that may arise from using this tool.
