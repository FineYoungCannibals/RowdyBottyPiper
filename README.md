# **Creating SeleniumBase Scripts for the RBP Framework**

This guide explains how to write SeleniumBase (SB) scripts that integrate seamlessly with the **RowdyBottyPiper (RBP) wrapper framework**.

It focuses on:

* Exposing downloaded or generated files to the calling framework
* Implementing the required `run()` interface
* Reporting workflow progress, including automatic RBP progress bar support

---

## **1. Required Script Structure**

All SeleniumBase scripts **must implement a `run()` function** with the following signature:

```python
def run(config, progress_callback=None, file_download_callback=None):
    ...
```

**Parameters:**

* `config` → dictionary containing any configuration your script needs (e.g., URLs, filenames, options).
* `progress_callback` → optional function for reporting progress to the RBP wrapper.
* `file_download_callback` → optional function to report file paths to the RBP wrapper.

**Return Value:**

* Scripts should return a status message (e.g., `"Success"`) or relevant output at the end of the workflow.

---

## **2. Using SeleniumBase Context Manager**

Scripts should always create a SeleniumBase session using a context manager:

```python
from seleniumbase import SB

with SB(uc=True, browser='brave') as sb:
    # Your Selenium workflow goes here
    sb.open("https://example.com")
    ...
```

**Notes:**

* `uc=True` enables **undetected mode** for Chromium-based browsers.
* `browser` can be `'chrome'`, `'brave'`, `'firefox'`, etc.

---

## **3. Progress Reporting**

### **Manual Progress Callback**

Call `progress_callback` after meaningful steps to notify the RBP framework:

```python
if progress_callback:
    progress_callback(1)  # increments progress by one step
```

### **Automatic Progress via Comments**

RBP can also **parse special comments** in your code to calculate progress steps automatically:

```python
#@rbp_progbar_counter
```

* Place this **directly above significant workflow steps**.
* RBP will use these comments to update the progress bar automatically.
* This is especially useful for scripts that have **multiple sequential steps**, e.g., navigation, downloads, or form submissions.

---

## **4. Handling File Outputs**

Any files generated or downloaded by your SeleniumBase script **must be reported to the framework** using the `file_download_callback`.

```python
from pathlib import Path

file_path = Path("/path/to/generated/file.txt")
if file_download_callback:
    file_download_callback(file_path)
```

**Why:**

* The RBP wrapper can then process, move, or log these files.
* This is the **only way** for scripts to make files visible to the calling scripts or the framework.

---

### **Example Usage in a Script**

```python
from seleniumbase import SB
from pathlib import Path

def run(config, progress_callback=None, file_download_callback=None):
    with SB(uc=True, browser='brave') as sb:

        # Step 1: Navigate to page
        #@rbp_progbar_counter
        sb.open(config.get("url", "https://www.bing.com"))
        if progress_callback:
            progress_callback(1)

        # Step 2: Save screenshot
        #@rbp_progbar_counter
        download_path = Path.home() / "Downloads" / "screenshot.png"
        sb.save_screenshot("screenshot.png", folder=Path.home() / "Downloads")

        # Notify wrapper of downloaded file
        if file_download_callback:
            file_download_callback(download_path)
        
        if progress_callback:
            progress_callback(1)

    return "Success"
```

---

## **5. Guidelines for Writing New Scripts**

1. **Always implement a `run()` function** with the proper parameters.
2. **Use the `SB()` context manager** for browser setup/teardown.
3. **Report progress** either via `progress_callback` or by using `#@rbp_progbar_counter` comments.
4. **Notify the wrapper of any files created** via `file_download_callback`.
5. **Save files to predictable paths** (`Downloads` folder or configurable via `config`) to avoid conflicts.
6. **Return a meaningful status** at the end of the workflow.

---

## **6. Summary**

By following this pattern:

* The RBP framework can **track workflow progress** (manually or automatically using comments).
* Files generated or downloaded by scripts are **visible to the framework**.
* Scripts remain **modular, reusable, and testable**.

---