from playwright.sync_api import sync_playwright


def form_scraping(url: str, form_selector: str = "form") -> dict:
    schema: dict = {}

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url)

        form = page.query_selector(form_selector)
        if form is None:
            browser.close()
            raise ValueError(f"Aucun formulaire trouvé avec le sélecteur '{form_selector}'")

        elements = form.query_selector_all("input, textarea, select")

        # Pour regrouper correctement les radios/checkboxes de même name
        radio_options: dict[str, list] = {}
        checkbox_options: dict[str, list] = {}

        for idx, el in enumerate(elements):
            tag = el.evaluate("e => e.tagName.toLowerCase()")
            name = el.get_attribute("name")
            elem_id = el.get_attribute("id")
            key = name or elem_id or f"field_{idx}"

            if tag == "input":
                input_type = (el.get_attribute("type") or "text").lower()

                if input_type == "checkbox":
                    value = el.get_attribute("value") or "on"
                    same_name_count = sum(
                        1 for e in elements
                        if e.get_attribute("name") == name
                        and (e.get_attribute("type") or "").lower() == "checkbox"
                    )
                    if name and same_name_count > 1:
                        checkbox_options.setdefault(key, [])
                        checkbox_options[key].append(value)
                        schema[key] = f"choix multiple parmi {checkbox_options[key]}"
                    else:
                        schema[key] = "booléen (coché/non coché)"

                elif input_type == "radio":
                    value = el.get_attribute("value")
                    radio_options.setdefault(key, [])
                    if value is not None:
                        radio_options[key].append(value)
                    schema[key] = f"choix unique parmi {radio_options[key]}"

                else:
                    # text, email, number, date, tel, url, password, etc.
                    schema[key] = input_type

            elif tag == "textarea":
                schema[key] = "text (multiligne)"

            elif tag == "select":
                is_multiple = el.evaluate("e => e.multiple")
                options = el.evaluate(
                    "e => Array.from(e.options).map(o => o.value)"
                )
                if is_multiple:
                    schema[key] = f"choix multiple parmi {options}"
                else:
                    schema[key] = f"choix unique parmi {options}"

        browser.close()

    return schema

def fill_form(url: str, values: dict, form_selector: str = "form",
              submit: bool = False, headless: bool = False) -> None:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        page = browser.new_page()
        page.goto(url)
 
        form = page.query_selector(form_selector)
        if form is None:
            browser.close()
            raise ValueError(f"Aucun formulaire trouvé avec le sélecteur '{form_selector}'")
 
        for key, value in values.items():
            # On cherche le champ par name, sinon par id
            el = form.query_selector(f'[name="{key}"]') or form.query_selector(f'#{key}')
            if el is None:
                print(f"⚠️  Champ '{key}' introuvable dans le formulaire, ignoré.")
                continue
 
            tag = el.evaluate("e => e.tagName.toLowerCase()")
 
            if tag == "input":
                input_type = (el.get_attribute("type") or "text").lower()
 
                if input_type == "checkbox":
                    # value peut être bool (checkbox seule) ou liste (groupe)
                    if isinstance(value, list):
                        checkboxes = form.query_selector_all(f'[name="{key}"]')
                        for cb in checkboxes:
                            cb_value = cb.get_attribute("value")
                            if cb_value in value:
                                cb.check()
                    else:
                        if value:
                            el.check()
                        else:
                            el.uncheck()
 
                elif input_type == "radio":
                    radios = form.query_selector_all(f'[name="{key}"]')
                    for r in radios:
                        if r.get_attribute("value") == value:
                            r.check()
                            break
 
                else:
                    el.fill(str(value))
 
            elif tag == "textarea":
                el.fill(str(value))
 
            elif tag == "select":
                is_multiple = el.evaluate("e => e.multiple")
                if is_multiple and isinstance(value, list):
                    el.select_option(value=value)
                else:
                    el.select_option(value=str(value))
 
        if submit:
            submit_btn = form.query_selector('button[type="submit"], input[type="submit"]')
            if submit_btn:
                submit_btn.click()
            else:
                print("⚠️  Aucun bouton submit trouvé, formulaire rempli mais non envoyé.")
 
        if not headless:
            page.wait_for_timeout(10000)  # laisse le temps de voir le résultat
 
        browser.close()

if __name__ == "__main__":
    schema = form_scraping(
        "file:///C:/Users/Hackathon_user/Documents/GitHub/hackathon-aubay-2026/forms.html"
    )
    
    