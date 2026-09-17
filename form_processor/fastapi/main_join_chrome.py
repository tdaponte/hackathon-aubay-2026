import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from playwright.async_api import async_playwright
from fastapi.middleware.cors import CORSMiddleware
from logging import Logger

app = FastAPI(title="Browser Form Automation API")

# Enable CORS so your standalone HTML page can call these API endpoints
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins for local hackathon/testing speed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Target port for your open Chrome session
CHROME_CDP_URL = "http://localhost:9222"


# Define the data structure expected by the fill endpoint
class FormSubmission(BaseModel):
    # Dictionary mapping element HTML ID string to its corresponding inner Tuple (Value, FieldType)
    # Example format: {"fullName": ["John Doe", "text"], "terms": [true, "checkbox"]}
    responses: dict[str, list]


# =====================================================================
# ENDPOINT 1: EXTRACT META DATA TO JSON
# =====================================================================


@app.get("/extract")
async def extract_fields():
    """
    Connects to your active live Chrome window, parses all available
    textboxes, dropdowns, and checkboxes, and serves it back over API.
    """
    async with async_playwright() as p:
        try:
            # Connect over the Chrome DevTools Protocol (CDP) port
            browser = await p.chromium.connect_over_cdp(CHROME_CDP_URL)

            # CRITICAL FIX: Ensure contexts and pages exist before index mapping
            if not browser.contexts:
                raise Exception("No active browser context found. Is Chrome open?")

            context = browser.contexts[0]
            if not context.pages:
                raise Exception("No active browser tabs found. Open a tab in your debug Chrome window.")

            page = context.pages[0]  # Grab the first active tab

            # # Query elements asynchronously
            # interactive_elements = page.locator(
            #     "input[type='text'], input[type='email'], input[type='checkbox'], input:not([type]), textarea, select"
            # )

            # Use the ultra-general locator string
            interactive_elements = page.locator(
                "input:not([type='hidden']):not([type='submit']):not([type='button']):not([type='image']):not([type='reset']), "
                "textarea, "
                "select"
            )
            count = await interactive_elements.count()

            form_fields = []

            # print(f"Extracted elements: {interactive_elements}")

            for i in range(count):
                element = interactive_elements.nth(i)
                element_id = await element.get_attribute("id")
                input_type = await element.get_attribute("type")

                tag_name = await element.evaluate("el => el.tagName.toLowerCase()")

                # 1. Standardize our classification logic
                if input_type == "checkbox":
                    field_type = "checkbox"
                elif input_type == "radio":
                    field_type = "radio"
                else:
                    field_type = tag_name  # 'select', 'textarea', or 'input' defaults

                # field_type = "checkbox" if input_type == "checkbox" else tag_name

                if element_id:
                    # 2. Label classification
                    label_element = page.locator(f"label[for='{element_id}']")
                    if await label_element.count() > 0:
                        label_text = await label_element.inner_text()
                    else:
                        nested_label = page.locator(f"label:has(input#{element_id})")
                        if await nested_label.count() > 0:
                            label_text = await nested_label.inner_text()
                        else:
                            label_text = f"Unnamed field ({element_id})"

                    # 3. Extract Placeholder
                    placeholder = await element.get_attribute("placeholder") or ""

                    # 4. Extract Max Character Limit (maxlength attribute)
                    max_length = await element.get_attribute("maxlength")
                    # If maxlength doesn't exist, we save it as None (null in JSON)
                    max_length = int(max_length) if max_length else 0

                    # 5. Extract Descriptions / Helper Text
                    description_text = ""

                    # Strategy A: Check accessibility tag (aria-describedby)
                    aria_desc_id = await element.get_attribute("aria-describedby")
                    if aria_desc_id:
                        desc_element = page.locator(f"#{aria_desc_id}")
                        if await desc_element.count() > 0:
                            description_text = await desc_element.inner_text()

                    # Strategy B: Fallback to reading nearby helper structural siblings (e.g. .help-block, .description, or small text)
                    if not description_text.strip():
                        # We target sibling text blocks or parents that commonly wrap instructions
                        sibling_desc = page.locator(
                            f"#{element_id} ~ .description, #{element_id} ~ .help-text, #{element_id} ~ small")
                        if await sibling_desc.count() > 0:
                            description_text = await sibling_desc.first.inner_text()

                    match field_type:
                        case "input" | "textarea":
                            return_type = "text"
                        case "select":
                            return_type = field_type
                        case "checkbox":
                            return_type = "checkbox"
                        case _:
                            return_type = ""

                    # field_data = {
                    #     "id": element_id,
                    #     "label": label_text.strip(),
                    #     "type": field_type,
                    #     "options": []
                    # }

                    field_data = {
                        "id": element_id,
                        "label": label_text.strip(),
                        "type": return_type,
                        "values": [],
                        "description": description_text,
                        "placeholder": placeholder,
                        "max_chars": max_length,
                        "optional": "false"
                    }

                    if field_type == "select":
                        options_locator = element.locator("option")
                        opt_count = await options_locator.count()
                        for j in range(opt_count):
                            opt_text = await options_locator.nth(j).inner_text()
                            if opt_text.strip():
                                field_data["values"].append(opt_text.strip())

                    form_fields.append(field_data)

                    print(f"Extracted data: {field_data}")


            return {"status": "success", "form_fields": form_fields}

        except Exception as e:
            # PRINT THE ACTUAL CRASH REASON TO YOUR TERMINAL
            print(f"❌ Internal Server Error Caught: {str(e)}")
            # Raise an explicit HTTP 500 so FastAPI safely preserves CORS headers
            raise HTTPException(status_code=500, detail=str(e))


# =====================================================================
# ENDPOINT 2: AUTOMATE INJECTION FROM INBOUND API PAYLOAD
# =====================================================================
@app.post("/fill")
async def fill_fields(payload: FormSubmission):
    """
    Accepts arbitrary mapping inputs and dynamically drives your open
    browser window tab to execute user selection actions natively.
    """
    async with async_playwright() as p:
        try:
            browser = await p.chromium.connect_over_cdp(CHROME_CDP_URL)
            page = browser.contexts[0].pages[0]

            for element_id, configuration in payload.responses.items():
                value, field_type = configuration[0], configuration[1]
                selector = f"#{element_id}"

                if field_type == "checkbox":
                    await page.set_checked(selector, bool(value))

                elif field_type == "select":
                    try:
                        # Attempt explicit visual text label string binding first
                        await page.select_option(selector, label=str(value))
                    except Exception:
                        # Fallback to index value tags
                        await page.select_option(selector, value=str(value))
                else:
                    await page.fill(selector, str(value))

            return {"status": "success", "message": "Form fields injected successfully."}

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to automate form: {str(e)}")


if __name__ == "__main__":
    import uvicorn

    # Bootstraps the local app runtime
    uvicorn.run(app, host="127.0.0.1", port=8000)



# @app.get("/extract")
# async def extract_fields():
#     """
#     Connects to your active live Chrome window, parses all available
#     textboxes, dropdowns, and checkboxes, and serves it back over API.
#     """
#     async with async_playwright() as p:
#         try:
#             # Connect over the Chrome DevTools Protocol (CDP) port
#             browser = await p.chromium.connect_over_cdp(CHROME_CDP_URL)
#             context = browser.contexts[0]
#
#             if not context.pages:
#                 raise HTTPException(status_code=404, detail="No active browser tabs found.")
#
#             page = context.pages[0]  # Grab the first visible tab
#
#             # Query elements asynchronously
#             interactive_elements = page.locator(
#                 "input[type='text'], input[type='email'], input[type='checkbox'], input:not([type]), textarea, select"
#             )
#             count = await interactive_elements.count()
#
#             form_fields = []
#
#             for i in range(count):
#                 element = interactive_elements.nth(i)
#                 element_id = await element.get_attribute("id")
#                 input_type = await element.get_attribute("type")
#
#                 # Fetch element tag name natively via async JavaScript evaluation
#                 tag_name = await element.evaluate("el => el.tagName.toLowerCase()")
#                 field_type = "checkbox" if input_type == "checkbox" else tag_name
#
#                 if element_id:
#                     # Match label associations
#                     label_element = page.locator(f"label[for='{element_id}']")
#                     if await label_element.count() > 0:
#                         label_text = await label_element.inner_text()
#                     else:
#                         nested_label = page.locator(f"label:has(input#{element_id})")
#                         if await nested_label.count() > 0:
#                             label_text = await nested_label.inner_text()
#                         else:
#                             label_text = f"Unnamed field ({element_id})"
#
#                     field_data = {
#                         "id": element_id,
#                         "label": label_text.strip(),
#                         "type": field_type,
#                         "options": []
#                     }
#
#                     # Read options array from dropdown configurations
#                     if field_type == "select":
#                         options_locator = element.locator("option")
#                         opt_count = await options_locator.count()
#                         for j in range(opt_count):
#                             opt_text = await options_locator.nth(j).inner_text()
#                             if opt_text.strip():
#                                 field_data["options"].append(opt_text.strip())
#
#                     form_fields.append(field_data)
#
#             return {"status": "success", "form_fields": form_fields}
#
#         except Exception as e:
#             raise HTTPException(status_code=500, detail=f"Failed to scrape browser session: {str(e)}")
