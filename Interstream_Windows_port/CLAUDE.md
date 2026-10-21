# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Interstream is a real-time multimedia application built on **Cycling '74's Max/MSP** platform, ported to Windows. It combines audio processing (MSP), visual/video processing (Jitter/OpenGL), and networking into an interactive environment. The main application logic lives in a compiled Max patch (`Interstream_Windows.mxf`) executed by the bundled runtime (`Interstream_Windows.exe`).

## Build & Development

### Running the Application
```
Interstream_Windows.exe
```
The executable is a standalone Max runtime that loads `Interstream_Windows.mxf` automatically.

### Compiling Java Extensions
Java source files (`.java`) and compiled classes (`.class`) coexist in `resources/java-classes/classes/`. The Max runtime compiles and loads these automatically, but they can also be compiled manually:
```
javac -cp "resources/java-classes/lib/max.jar;resources/java-classes/lib/jitter.jar" resources/java-classes/classes/YourFile.java
```
Required classpath JARs: `max.jar`, `jitter.jar` (in `resources/java-classes/lib/`).

### No Formal Test Suite
There is no test framework. Test classes (`JitterListenerTest.java`, `JitterGLTest.java`, `JitterListenerNetTest.java`, `WhichThread.java`) are ad-hoc Max objects that verify functionality when instantiated within a patch.

## Architecture

### Runtime Layers
- **Max Runtime** (`Interstream_Windows.exe` + `support/MaxAPI.dll`, `MaxAudio.dll`) — patch execution, scheduling, message routing
- **MSP** — real-time audio DSP engine
- **Jitter** (`support/jitlib.dll`) — real-time graphics, video, and matrix processing via OpenGL
- **VIDDLL Package** (`resources/packages/VIDDLL/`) — FFmpeg-based video codec support (libavcodec, libavformat, etc.)

### Java Extensions (`resources/java-classes/classes/`)
All custom Java objects extend `com.cycling74.max.MaxObject` or `com.cycling74.jitter.JitterObject`. Key subsystems:

- **Networking** (`net/`) — TCP (`net/tcp/`), UDP (`net/udp/`), multicast (`net/multi/`), and email (`net/mail/`) with async send/recv pairs using callback patterns
- **3D GUI System** — `JitterGuiTracker` manages focus and ray-casting for interactive 3D elements; `JitterGuiElement` is the base class; `JitterGuiSlider`/`jitgldock` are concrete controls
- **Particle/Physics** (`p/`) — `ParticleMatrix` defines a 13-plane Jitter matrix (ID, life, position, velocity, acceleration, mass, charge); `gravity`, `orbitgen`, `updater` operate on it
- **List Processing** (`list/`) — `ListProcessor` base class with ~20 subclasses for list manipulation (Sort, Shuffle, Slice, etc.)
- **Data Utilities** — `matrixlist` (thread-safe shared matrix registry using static HashMap), `sbuf` (string buffer with regex)

### Key Patterns
- **Message-driven**: Objects communicate via typed messages (bang, int, float, list, symbol). Implement handlers as methods named after the message type.
- **MaxQelem**: Used to marshal async callbacks (network, timers) safely onto the Max scheduler thread.
- **Static registries**: `matrixlist` uses a static `HashMap` so instances across the patch share matrix data by name.
- **JitterNotifiable**: Interface for receiving Jitter event callbacks (used by the 3D GUI interaction pipeline: screen coords → `screentoworld` → ray-cast → intersection → element callback).

### UI & Interfaces (`resources/interfaces/`)
- Max patch UI components (`.maxpat` files) for audio status, plugin editors, material browsers
- `maxinterface.json` defines color schemes, UI element styles, and dialog configurations
- `search/` contains a NodeJS API server (`@c74-search/api-server`) for unified search
- `www/` has web interface assets (JS, images)

### Native Externals (`resources/externals/`)
Pre-compiled DLLs organized by subsystem: `max/` (core), `msp/` (audio DSP), `jitter/` (graphics), `ad/` (audio drivers), `mididrivers/`. These are loaded by the runtime and are not source-editable.

### Support Libraries (`resources/support/`)
Runtime DLLs including MaxAPI, MaxAudio, jitlib, DirectX shader compiler (`d3dcompiler_47.dll`), Chromium integration, and SwiftShader (software GPU fallback).

## Key Files
- `Interstream_Windows.mxf` — Main application patch (binary Max format, not directly editable as text)
- `resources/java-classes/classes/` — All editable source code lives here
- `resources/java-classes/lib/max.jar` — Max Java API
- `resources/java-classes/lib/jitter.jar` — Jitter Java API
- `resources/init/max-objectlist.txt` — Registry of available Max objects
