import random

def generate_description(title, category=None):
    descriptions = [
        f"{title} is a modern application designed to solve real-world problems efficiently using advanced technologies.",
        f"This project, {title}, focuses on delivering high performance and scalability with a user-friendly interface.",
        f"{title} is an innovative solution that enhances productivity and simplifies complex tasks.",
        f"In this project, {title}, various modern tools and frameworks are used to build a reliable system.",
        f"{title} is developed to provide seamless user experience and optimized performance."
    ]

    category_based = {
        "web": f"{title} is a responsive web application built with modern frontend and backend technologies.",
        "ai": f"{title} leverages artificial intelligence techniques to deliver intelligent solutions.",
        "data": f"{title} focuses on data analysis, visualization, and insights generation.",
        "app": f"{title} is an application designed with user-centric design and smooth performance."
    }

    if category and category.lower() in category_based:
        return category_based[category.lower()]

    return random.choice(descriptions)


def generate_skills(title):
    title = title.lower()

    skills_map = {
        "portfolio": ["HTML", "CSS", "JavaScript", "Flask", "UI/UX"],
        "chat": ["Python", "API", "NLP", "Machine Learning"],
        "data": ["Python", "Pandas", "NumPy", "Excel", "Visualization"],
        "ai": ["Machine Learning", "Deep Learning", "Python", "TensorFlow"],
        "web": ["HTML", "CSS", "JavaScript", "Flask", "Backend"],
        "app": ["UI Design", "API Integration", "Database", "Testing"]
    }

    for key in skills_map:
        if key in title:
            return ", ".join(skills_map[key])

    return "Problem Solving, Programming, Development"