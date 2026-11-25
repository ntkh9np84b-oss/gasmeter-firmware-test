# AI-on-the-Edge v16.1.0 – 8 MHz browser-flasher

This repository builds two ESP32-CAM firmware variants from the official `jomjol/AI-on-the-edge-device` tag `v16.1.0`:

- `stock`: unchanged upstream build (20 MHz camera XCLK default)
- `8mhz`: same source and build environment, with only `-D XCLK_FREQ_MHZ=8` added to the `esp32cam` PlatformIO environment

GitHub Actions builds both images and deploys a small ESP Web Tools page to GitHub Pages. No local PlatformIO installation is required.

## One-time setup

1. Create a new GitHub repository for this project. A public repository is the simplest option for GitHub Pages on a free account; the source is public upstream code plus this small build script.
2. Upload the complete contents of this folder to the repository's `main` branch, preserving `.github/workflows/build-and-deploy.yml`.
3. In **Settings → Pages**, set **Build and deployment → Source** to **GitHub Actions**.
4. Open **Actions → Build AI-on-the-Edge browser flasher** and run the workflow once (or push a commit to `main`).
5. When the deployment succeeds, open the Pages URL shown in the deployment summary. It will contain buttons for both firmware variants.

The workflow checks out upstream tag `v16.1.0` with recursive submodules, builds the original `esp32cam` environment, builds it again with `XCLK_FREQ_MHZ=8`, and publishes manifests plus flash images.

## Flash procedure

1. Back up the entire microSD card before flashing.
2. Use Chrome or Edge on Windows and connect the ESP32-CAM by USB.
3. Open the GitHub Pages URL and select **8 MHz camera clock**.
4. When the installer asks to erase, choose full erase. This clears the ESP32's internal flash/NVS and old OTA selection; it does **not** erase the microSD card. The page explains this before the buttons.
5. If needed, enter the ESP32 bootloader mode: hold GPIO0/FLASH low, pulse RESET, then release FLASH. Exact button sequence depends on the USB-C carrier board.
6. Flash and reset. Confirm camera initialization and a working live image before assessing Wi-Fi.
7. To return to stock, use the **Original 20 MHz** button. Full erase is again recommended.

## Technical notes

- Upstream source: `jomjol/AI-on-the-edge-device`, tag `v16.1.0`.
- Camera implementation in that tag honors `XCLK_FREQ_MHZ`; without the define it uses 20 MHz.
- PlatformIO environment: `esp32cam`.
- Board profile: `esp32cam` / AI Thinker ESP32-CAM, with 4 MB flash as declared by the upstream configuration.
- ESP Web Tools uses a merged ESP-IDF image. The manifest requests an erase because this is a full firmware/partition-table reflash and stale OTA selection must not boot an old slot.
- The build retains the upstream code, models, HTML and SD-card configuration. The microSD contents are not part of the flash image.

## Limitations

This package has been prepared and its workflow/scripts reviewed, but the GitHub Actions build has not run yet because it must execute inside the user's GitHub repository. A successful build and first hardware flash must be confirmed before relying on the 8 MHz variant. If the workflow fails, its Actions log will identify the failing step.

The AI-on-the-Edge project has its own license terms. Review the upstream license before redistribution or commercial use.
