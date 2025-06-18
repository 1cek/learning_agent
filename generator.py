import os
import openai
from planner import calculate_units
from learning_rules import LEARNING_LOGIC
from web_search import search_web_snippets  
from web_search import fetch_youtube_videos
from text_utils import split_into_sections
from openai import OpenAI
from web_search import search_web_pages, extract_clean_text
openai.api_key = os.getenv("OPENAI_API_KEY")
from cache_utils import generate_cache_key, load_from_cache, save_to_cache

#def generate_learning_units(topic, level, daily_capacity, duration):
    #unit_count = calculate_units(level, daily_capacity, duration)
    #all_snippets = search_web_snippets(topic, max_results=unit_count * 2)
    
    #units = []
    #for i in range(unit_count):
        #text = all_snippets[i] if i < len(all_snippets) else "No content available."
        #sections = split_into_sections(text, max_sections=4)
        #units.append({
           # 'unit_number': i + 1,
           # 'title': f"{topic} - Unit {i+1}",
           # 'content': text,
          #  'sections': sections  
       # })
    #return units
def summarize_to_learning_sections(snippets, topic, unit_number, duration_minutes=120, feedback_action="great"):
    estimated_time = "two hours" if duration_minutes >= 90 else "one hour"
    
    # Add nuance based on feedback
    style_instruction = ""
    if feedback_action == "harder":
        style_instruction = "Go deeper into technical details, edge cases, or emerging challenges."
    elif feedback_action == "easier":
        style_instruction = "Use simpler explanations, analogies, and real-world examples to clarify complex points."

    prompt = f"""
You are an experienced academic tutor creating structured learning content for self-study.

Your task is to turn the following article excerpts into a complete learning unit on "{topic}" that will take a learner approximately {"two hours" if duration_minutes >= 90 else "one hour"} to study.

{style_instruction}

Split the content into **5 progressive sections**, starting with an introduction and moving toward more advanced, detailed analysis. Each section should have a **clear subheading and at least 3–5 paragraphs**.
    ...
   

Use accessible but intelligent language — the tone should resemble a university-level textbook chapter.

=== CONTENT TO SUMMARIZE AND STRUCTURE ===
{snippets}

=== OUTPUT FORMAT ===
Section 1: [Title]
[3–5 paragraphs]

Section 2: [Title]
[3–5 paragraphs]

... up to Section 5
""".strip()

    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful academic assistant."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
    )

    return response.choices[0].message.content.strip()



def generate_learning_units(topic, level, daily_capacity, duration, medium="text", feedback_action="great"):
    unit_count = calculate_units(level, daily_capacity, duration)
    units = []

    for i in range(unit_count):
        if medium in ["video", "videos"]:
            videos = fetch_youtube_videos(topic + f" part {i+1}", target_duration=3600, max_results=2)
            
            if not videos:
                content = "<p><em>No high-quality videos were found for this topic. Try another search.</em></p>"
                sections = [content]
            else:
                video_links = []
                for v in videos:
                    link = v.get("link", "")
                    title = v.get("title", "Untitled Video")
                    duration = v.get("duration", "Unknown")

                    video_links.append(f"""
                        <div class='video-entry'>
                            <a href='{link}' target='_blank'>
                                {v['title']} – {v['duration']}
                            </a>
                        </div>
                    """)

                content = "<h3>Take a close look at these videos:</h3>" + "".join(video_links)
                sections = [content]  # ✅ important: wrap in sections for segment display


        elif medium == "text":
            urls = search_web_pages(topic, max_results=2)
            articles = [extract_clean_text(url) for url in urls]
            combined = "\n\n".join([a for a in articles if a and a.strip()])

            if not combined.strip():
                content = "No useful articles could be extracted."
                sections = ["No content."]
            else:
                cache_key = generate_cache_key(f"{topic}-{medium}", i + 1, combined)
                cached = load_from_cache(cache_key)

                if cached:
                    full_text = cached
                else:
                    feedback = feedback_action
                    full_text = summarize_to_learning_sections(combined, topic, i + 1, duration_minutes=120, feedback_action=feedback)
                    save_to_cache(cache_key, full_text)
                parts = full_text.split("### ")
                sections = [p.strip() for p in parts if p.strip()] 
                content = ""  

        units.append({
            "unit_number": i + 1,
            "title": f"{topic}",
            "content": "",
            "sections": sections
        })

    return units



# test

#if __name__ == "__main__":
 #   for unit in generate_learning_units("AI ethics", "basic", "1-2 hours", "one-week", medium="video"):
  #      print(f"✔ Unit {unit['unit_number']}:")
   #     print(unit["content"])


    # test
if __name__ == "__main__":
    for unit in generate_learning_units("AI ethics", "basic", "1-2 hours", "one-week", medium="videos"):
        print(f"✔ Unit {unit['unit_number']}:")
        print(unit["content"])