OPTION_SELECTED = """
    function isOptionSelected(selectSelector, value) {{
        const select = document.querySelector(selectSelector);
        if (!select) return false;

        return Array.from(select.options).some(opt => opt.value === value && opt.selected);
    }}

    isOptionSelected('{select_id}', '{option}');
"""

FIELD_TEXT = """
    const input = document.querySelector('{input_id}')

    if (input && input.value.trim() !== '{text}') {{
        return false;
    }} else {{
        return true;
    }}
"""

CLEAR_TEXT_FIELD = """
    function() {{
        const input = document.querySelector('{input_id}');
        if (input) input.value = "";
    }}
"""

ELEMENT_VISIBLE_BY_XPATH = """
    function isElementVisibleByXPath(xpath) {{
        const elem = document.evaluate(xpath, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
        if (!elem) return false;

        const style = window.getComputedStyle(elem);
        if (style.display === "none" || style.visibility === "hidden" || style.opacity === "0") return false;

        const rect = elem.getBoundingClientRect();
        if (rect.width === 0 || rect.height === 0) return false;

        return (
            rect.bottom > 0 &&
            rect.right > 0 &&
            rect.top < (window.innerHeight || document.documentElement.clientHeight) &&
            rect.left < (window.innerWidth || document.documentElement.clientWidth)
        );
    }}

    // Пример использования:
    isElementVisibleByXPath('{xpath}');
"""

ELEMENT_VISIBLE_BY_ID = """
    const elem = document.getElementById('{element_id}')
    const isVisible = !!(elem && elem.offsetParent !== null)
    
    return isVisible;
"""
