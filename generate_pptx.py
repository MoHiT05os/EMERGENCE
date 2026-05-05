from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
import os

def delete_slide(prs, slide):
    id_dict = { slide.id: [i, slide.rId] for i, slide in enumerate(prs.slides._sldIdLst) }
    slide_id = slide.slide_id
    prs.part.drop_rel(id_dict[slide_id][1])
    del prs.slides._sldIdLst[id_dict[slide_id][0]]

def add_times_new_roman_text(shape, text, font_size=18, is_title=False):
    text_frame = shape.text_frame
    text_frame.clear()
    p = text_frame.paragraphs[0]
    p.text = text
    font = p.font
    font.name = 'Times New Roman'
    font.size = Pt(font_size)
    if is_title:
        font.bold = True
        font.color.rgb = RGBColor(0, 0, 0)

# Load existing presentation
prs = Presentation('EMERGENCE- AN INTELLIGENT CLASSROOM LEARNING SYSTEM.pptx')

# Delete all slides after the first two (indices 0 and 1)
while len(prs.slides) > 2:
    delete_slide(prs, prs.slides[2])

# We use layout index 5 (Title Only) or 6 (Blank). Let's use 6 and add our own title box to be safe.
# Or better, use the same layout as Slide 1 (which is index 1). But wait, slide layouts are in prs.slide_layouts.
layout = prs.slide_layouts[5]

# Content definition
slides_data = [
    {
        "title": "The New Era of Teaching: Predictive Intelligence",
        "talk": "EMERGENCE utilizes state-of-the-art vision models to map out student behavior and engagement across the classroom, wrapped in a premium, accessible interface.",
        "image": r"C:\Users\TheRealMohitYadav\.gemini\antigravity\brain\196b4f51-f8b9-4082-b292-bde5706c5efe\landing_page_1777915783991.png"
    },
    {
        "title": "Automated Profiling & Leaderboards",
        "talk": "The system calculates student profiling on a daily basis, fusing real-time vision metrics with academic test scores to dynamically categorize students into Excelling, Developing, and Struggling cohorts.",
        "image": r"C:\Users\TheRealMohitYadav\.gemini\antigravity\brain\196b4f51-f8b9-4082-b292-bde5706c5efe\dashboard_final_1777915861977.png"
    },
    {
        "title": "Adaptive Curriculum Generation",
        "talk": "Powered by DeepSeek V3 and MiniMax M2.5, EMERGENCE autonomously generates hyper-personalized pedagogical interventions tailored to the specific needs of each performance cluster.",
        "image": r"C:\Users\TheRealMohitYadav\.gemini\antigravity\brain\196b4f51-f8b9-4082-b292-bde5706c5efe\modules_page_1777915854808.png"
    }
]

for data in slides_data:
    slide = prs.slides.add_slide(layout)
    
    # Add Title
    title_shape = slide.shapes.title
    if title_shape:
        add_times_new_roman_text(title_shape, data["title"], font_size=32, is_title=True)
    else:
        # Manually add title box if layout doesn't have one
        txBox = slide.shapes.add_textbox(Inches(0.5), Inches(0.5), Inches(9), Inches(1))
        add_times_new_roman_text(txBox, data["title"], font_size=32, is_title=True)

    # Add Image
    try:
        # Centered image, leaving room for title and text
        slide.shapes.add_picture(data["image"], Inches(1), Inches(1.5), width=Inches(8))
    except Exception as e:
        print(f"Failed to add image {data['image']}: {e}")

    # Add Talk Text
    txBox = slide.shapes.add_textbox(Inches(1), Inches(6), Inches(8), Inches(1.5))
    add_times_new_roman_text(txBox, data["talk"], font_size=20, is_title=False)

output_filename = 'EMERGENCE_Final_Presentation.pptx'
prs.save(output_filename)
print(f"Successfully generated {output_filename}")
