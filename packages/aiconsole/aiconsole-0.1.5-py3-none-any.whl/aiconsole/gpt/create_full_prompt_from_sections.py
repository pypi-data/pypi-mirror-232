import re
from typing import List
from aiconsole.aic_types import StaticManual

def create_full_prompt_from_sections(intro: str, sections: List[StaticManual], outro: str = '', section_marker="####"):
    # Remove all section markers in intro, sections, and outro
    intro = re.sub(section_marker, '', intro)
    
    if outro:
        outro = re.sub(section_marker, '', outro)
    
    processed_sections = {f"{k.id} ({k.usage})": re.sub(section_marker, '', k.content) for k in sections}
    
    # Construct the full prompt
    section_strs = []
    for name, section in processed_sections.items():
        section_strs.append(f"{section_marker} {name} {section_marker}\n{section}")
    
    sub_str = '\n\n'
    full_prompt = f"{intro}\n\n{sub_str.join(section_strs)}\n\n{outro if outro else ''}".strip()
    
    return full_prompt