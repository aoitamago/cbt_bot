import pdfplumber
import re
import os
from db import save_questions

def parse_pdf(file_path, category="default"):
    text = ""
    questions = []
    image_dir = f"images_{category}"

    os.makedirs(image_dir, exist_ok=True)

    with pdfplumber.open(file_path) as pdf:
        for page_num, page in enumerate(pdf.pages):

            t = page.extract_text()
            if t:
                text += t + "\n"

            for i, img in enumerate(page.images):
                bbox = (img["x0"], img["top"], img["x1"], img["bottom"])
                im = page.within_bbox(bbox).to_image()
                img_path = f"{image_dir}/p{page_num}_{i}.png"
                im.save(img_path, format="PNG")

    pattern = re.findall(
        r"(\d+-\d+.*?)(ａ.*?)(ｂ.*?)(ｃ.*?)(ｄ.*?)(ｅ.*?)解答：([a-e])",
        text,
        re.S
    )

    for idx, q in enumerate(pattern):
        question_text = re.sub(r"解答：.*", "", q[0])

        img_path = None
        possible = f"{image_dir}/p{idx}_0.png"
        if os.path.exists(possible):
            img_path = possible

        questions.append({
            "question": question_text.strip(),
            "choices": {
                "A": q[1].replace("ａ", "").strip(),
                "B": q[2].replace("ｂ", "").strip(),
                "C": q[3].replace("ｃ", "").strip(),
                "D": q[4].replace("ｄ", "").strip(),
                "E": q[5].replace("ｅ", "").strip()
            },
            "answer": q[6].upper(),
            "image": img_path
        })

    save_questions(category, questions)
    return len(questions)