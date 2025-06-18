from rake_nltk import Rake
import spacy

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

# Predefined sentences related to each topic
sentences = {
    "sustainable living": "Sustainable living includes practices such as recycling, using renewable energy, composting, water conservation, urban gardening, using energy-efficient appliances, adopting zero waste practices, using green transportation, buying eco-friendly products, and sustainable fashion.",
    "technology": "Technology encompasses areas like artificial intelligence, blockchain, cybersecurity, cloud computing, 5G technology, Internet of Things, virtual reality, quantum computing, robotics, and automation.",
    "health and wellness": "Health and wellness focus on mental health, nutrition, exercise, meditation, sleep hygiene, holistic health, preventive care, stress management, natural remedies, and physical fitness.",
    "education": "Education today involves online learning, educational technology, STEM education, critical thinking, lifelong learning, inclusive education, curriculum development, educational policy, student engagement, and digital literacy.",
    "business": "Business topics include entrepreneurship, digital marketing, e-commerce, business strategy, startup culture, market research, financial management, corporate social responsibility, leadership development, and innovation.",
    "environment": "Environmental issues cover climate change, conservation, biodiversity, sustainable agriculture, pollution control, renewable resources, environmental policy, wildlife protection, green energy, and carbon footprint reduction.",
    "travel": "Travel includes eco-tourism, cultural immersion, adventure travel, budget travel, travel photography, road trips, travel planning, solo travel, luxury travel, and digital nomad lifestyle.",
    "food and drink": "Food and drink topics include plant-based diets, food sustainability, international cuisine, home cooking, culinary arts, wine tasting, healthy eating, food technology, restaurant trends, and nutrition.",
    "science": "Science topics cover space exploration, genetics, climate science, physics, chemistry, biology, scientific research, innovation in science, nanotechnology, and astrophysics.",
    "art and culture": "Art and culture encompass contemporary art, art history, performance art, digital art, art criticism, cultural heritage, music genres, literature, film studies, and theater.",
    "sports": "Sports topics include fitness training, sports medicine, team dynamics, athlete nutrition, sports psychology, youth sports, sports technology, coaching strategies, professional leagues, and outdoor sports.",
    "fashion": "Fashion includes sustainable fashion, fashion design, trends forecasting, textile innovation, personal styling, fashion marketing, fashion photography, history of fashion, luxury brands, and streetwear.",
    "personal development": "Personal development covers goal setting, time management, self-discipline, emotional intelligence, mindfulness, productivity hacks, public speaking, confidence building, career growth, and financial literacy.",
    "finance": "Finance topics include investing, personal finance, cryptocurrency, financial planning, stock market, real estate investment, retirement planning, tax strategies, budgeting, and wealth management.",
    "automotive": "Automotive topics cover electric vehicles, autonomous driving, car design, automotive engineering, car maintenance, classic cars, motorsports, car safety, automotive technology, and eco-friendly vehicles.",
    "gaming": "Gaming includes game development, esports, virtual reality gaming, game design, indie games, gaming culture, board games, gaming hardware, mobile gaming, and video game history.",
    "home and garden": "Home and garden topics include interior design, landscaping, DIY projects, home automation, sustainable gardening, home improvement, houseplants, outdoor living, home organization, and smart home technology.",
    "relationships": "Relationships cover communication skills, conflict resolution, relationship building, family dynamics, dating advice, marriage counseling, friendship, work relationships, emotional support, and relationship psychology.",
    "pets and animals": "Pets and animals topics include pet care, animal behavior, wildlife conservation, exotic pets, pet training, animal rescue, pet nutrition, animal health, pet adoption, and therapy animals.",
    "literature": "Literature encompasses novel writing, poetry, literary analysis, classic literature, contemporary fiction, non-fiction writing, literary genres, publishing industry, book reviews, and literary awards."
}


# Function to generate new ideas based on a given topic using Rake for keyword extraction
def generate_ideas(topic):
    if topic not in sentences:
        return ["No ideas available for this topic."]

    # Extract keywords using Rake
    r = Rake()
    r.extract_keywords_from_text(sentences[topic])
    keywords = r.get_ranked_phrases()[:5]  # Get top 5 keywords

    ideas = []
    for keyword in keywords:
        idea = f"Explore {keyword} ."
        ideas.append(idea)

    return ideas


'''# Get user input for the topic
topic = input("Enter a topic: ").strip().lower()

# Generate ideas based on user input
ideas = generate_ideas(topic)
print(f"New ideas about {topic}:\n")
for idea in ideas:
    print(f"- {idea}")'''